# Launch and acceptance

From a fresh virtual environment, install this project with `python -m pip install .`.
Run `python acceptance.py` from the repository root to check the installed console
command, installed package metadata, examples, privacy behavior, and full test suite.
The script locates the console entry point through Python's `sysconfig` scripts
directory, so it works on Windows and Unix without shell-specific quoting.
