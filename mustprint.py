#!/usr/bin/env python3
"""mustprint: run a command, fail unless its output carries at least one figure.

Born from five wallet/usage readings on 24-25 nov 2026 that exited 0 with the
word "done" and no numbers in them; every one looked clean and none was.

Usage:
    mustprint.py [--min N] [--strict] -- <command> [args...]

Rules a figure must satisfy:
  - a whole token that is a decimal (3.5, 0.007, -1.13) or, when the payload
    holds no hex-id-looking token, a standalone integer (10, 198)
  - not a uuid, git sha or other hex id (has an a-f letter, 8+ chars),
    not an ISO date/time, not a dotted version (0.3.0)
  - when the payload contains any hex-id-looking token, bare integers do
    not count at all: "<sha> 198 stars" is a label line, not a reading;
    only decimals pass there.

Exit codes: 0 figures found, 1 none found (or command failed), 2 spawn/usage.
Stdlib only.
"""

import argparse
import re
import subprocess
import sys

# hex ids (uuid, git sha, api id): 8+ hex chars, at least one a-f letter,
# so pure-digit decimals like 10000000 are never mistaken for ids
HEXISH = re.compile(r"\b(?=[0-9a-fA-F]{8,}\b)(?=[0-9a-fA-F]*[a-fA-F])[0-9a-fA-F]{8,}\b")
# ISO dates and times: 2026-11-25, 05:00:06, 2026-11-25T05:00:06Z
ISOTIME = re.compile(r"\d{4}-\d{2}-\d{2}|\d{2}:\d{2}(:\d{2})?(\.\d+)?Z?\b")
# bare 4-digit years left over after ISO strip
YEAR = re.compile(r"(?<![\w.])(19|20)\d{2}(?![\w.])")
DECIMAL = re.compile(r"-?\d+\.\d+|-?\.\d+")
INTEGER = re.compile(r"-?\d+")
STRIP = ".,;:!?()[]{}\"'`*"


def figures_in(text: str):
    """Return (count, had_hex_ids). Figures are counted per whitespace token."""
    had_hex = bool(HEXISH.search(text))
    scrubbed = HEXISH.sub(" ", text)
    scrubbed = ISOTIME.sub(" ", scrubbed)
    scrubbed = YEAR.sub(" ", scrubbed)
    n = 0
    for tok in scrubbed.split():
        tok = tok.strip(STRIP)
        if DECIMAL.fullmatch(tok):
            n += 1
        elif not had_hex and INTEGER.fullmatch(tok):
            n += 1
    return n, had_hex


def main() -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--min", type=int, default=1, metavar="N",
                    help="fewer than N figures in the output fails (default 1)")
    ap.add_argument("--strict", action="store_true",
                    help="also fail on any hex-id-looking token (uuid/sha)")
    ap.add_argument("cmd", nargs=argparse.REMAINDER, help="command to run")
    args = ap.parse_args()
    if not args.cmd:
        ap.error("no command given")
    if args.cmd and args.cmd[0] == "--":
        args.cmd = args.cmd[1:]
    try:
        out = subprocess.run(args.cmd, capture_output=True, text=True, timeout=120)
    except OSError as e:
        print(f"mustprint: spawn failed: {e}", file=sys.stderr)
        return 2
    except subprocess.TimeoutExpired:
        print("mustprint: command timed out after 120s", file=sys.stderr)
        return 2
    payload = (out.stdout or "") + (out.stderr or "")
    n, had_hex = figures_in(payload)
    if args.strict and had_hex:
        print("mustprint: strict mode forbids hex-id tokens in output", file=sys.stderr)
        return 1
    if out.returncode != 0:
        print(f"mustprint: command exited {out.returncode}; figures seen: {n}",
              file=sys.stderr)
        return 1
    if n < args.min:
        print(f"mustprint: {n} figures in output, needed {args.min} "
              f"(command: {' '.join(args.cmd)})", file=sys.stderr)
        return 1
    sys.stdout.write(payload)
    print(f"mustprint: {n} figures, ok", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
