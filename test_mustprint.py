"""Self-tests for mustprint.py. Run: python3 test_mustprint.py"""

import subprocess
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "mustprint.py")

CASES = [
    # (argv after the tool, expected exit code, label)
    (["bash", "-c", "echo done"], 1, "no figures fails"),
    (["bash", "-c", "echo 'base USDC 10, sol 0.097471615'"], 0, "real reading passes"),
    (["bash", "-c", "echo 'reply 5ded71d2-9b4d-4b2a-882b-1c3f5e7a9b0d queued'"], 1,
     "uuid-only output is not a figure"),
    (["bash", "-c", "echo 'b5b3791988 198 stars'"], 1,
     "integer next to a hex id is a label, not a reading"),
    (["bash", "-c", "echo 'b5b3791988 sol 0.097471615'"], 0,
     "decimal next to a hex id still counts"),
    (["bash", "-c", "echo 'checked 2026-11-25T05:00:06Z'"], 1,
     "ISO timestamp is not a figure"),
    (["bash", "-c", "echo 'npm @hashshabbir/mcp-pack 0.3.0 shipped'"], 1,
     "dotted version is not a figure"),
    (["bash", "-c", "echo 'raw 10000000 display 10'"], 0,
     "pure-digit integers count when no hex id present"),
    (["bash", "-c", "echo 'raw 10000000 display 10 5ded71d2-9b4d-4b2a-882b-1c3f5e7a9b0d'"], 1,
     "integers stop counting once a hex id appears"),
    (["--min", "2", "--", "bash", "-c", "echo 'one 1 figure'"], 1, "--min 2 not met"),
    (["--min", "2", "--", "bash", "-c", "echo '1 and 2.5'"], 0, "--min 2 met"),
    (["--strict", "--", "bash", "-c", "echo 'sha b5b3791988 present'"], 1,
     "strict forbids hex ids"),
    (["bash", "-c", "exit 3"], 1, "failing command fails"),
]

failures = 0
for argv, want, label in CASES:
    got = subprocess.run([sys.executable, TOOL] + argv,
                         capture_output=True, text=True).returncode
    mark = "ok" if got == want else "FAIL"
    if got != want:
        failures += 1
    print(f"{mark}  want={want} got={got}  {label}")

print(f"\n{len(CASES) - failures}/{len(CASES)} pass")
sys.exit(1 if failures else 0)
