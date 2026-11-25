# mustprint

Run a check command and fail unless its output carries at least one numeric
figure. A reading that prints "done" with no numbers is indistinguishable
from a clean one; this makes it fail loudly instead. Stdlib-only Python 3.

    python3 mustprint.py -- <command> [args...]
    python3 mustprint.py --min 2 -- <command>   # need >= 2 figures
    python3 mustprint.py --strict -- <command>  # also forbid hex-id tokens

## What counts as a figure

- a whole token that is a decimal (3.5, 0.007, -1.13), or a standalone
  integer (10, 198) when the payload holds no hex-id-looking token
- not a uuid, git sha or other hex id (8+ hex chars with an a-f letter),
  not an ISO date/time, not a dotted version (0.3.0)
- when the payload contains any hex id, bare integers stop counting:
  "<sha> 198 stars" is a label line, not a reading; only decimals pass

Exit 0 = figures found and command exited 0; exit 1 = no figures (or the
command failed); exit 2 = spawn/usage error.

## Why

Five wallet/usage readings on 24-25 nov 2026 completed without printing
figures and none of them flagged itself. Wrap the reading and it can't
look clean while saying nothing.

## Self-test

    python3 test_mustprint.py
