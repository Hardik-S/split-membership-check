"""Independent checks against the freshly installed console command."""

import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import sysconfig

ROOT = Path(__file__).resolve().parent
SCRIPTS = Path(sysconfig.get_path("scripts"))
COMMAND = SCRIPTS / ("split-membership-check.exe" if os.name == "nt" else "split-membership-check")


def run(args):
    return subprocess.run([str(COMMAND), *map(str, args)], cwd=ROOT,
                          text=True, encoding="utf-8", capture_output=True)


def expect_file(name, output, code):
    result = run([ROOT / "examples" / name])
    assert result.returncode == code, (name, result.returncode)
    assert result.stderr == "", name
    assert json.loads(result.stdout) == output, name


assert COMMAND.is_file(), f"installed console entry point missing: {COMMAND}"
assert importlib.metadata.version("split-membership-check") == "0.1.0"
spec = importlib.util.find_spec("split_membership_check")
assert spec and spec.origin and "site-packages" in spec.origin.lower(), spec
expect_file("valid.jsonl", {"status": "valid", "record_count": 2, "overlap_lines": []}, 0)
expect_file("overlap.jsonl", {"status": "overlap", "record_count": 2, "overlap_lines": [1, 2]}, 1)
expect_file("invalid.jsonl", {"status": "invalid_input"}, 2)
help_result = run(["--help"])
assert help_result.returncode == 0 and "usage:" in help_result.stdout and help_result.stderr == ""
private = run(["/private/path/secret-id.jsonl", "another-secret"])
assert private.returncode == 2 and private.stdout == '{"status":"invalid_input"}\n' and private.stderr == ""

# The tests run with the installed module on the import path and report skips explicitly.
env = os.environ.copy()
env["PYTHONPATH"] = str(ROOT / "tests")
tests = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
                       cwd=ROOT, env=env, text=True, encoding="utf-8", capture_output=True)
print(tests.stdout, end="")
print(tests.stderr, end="")
assert tests.returncode == 0, "installed-package tests failed"
assert "skipped=" not in tests.stderr and "skipped=" not in tests.stdout
print("ACCEPTANCE PASS: installed package 0.1.0; demos 0/1/2, help and private bad argv; tests 0 skips")
