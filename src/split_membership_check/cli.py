"""Offline split membership checker."""

import json
import sys
from collections import defaultdict
from pathlib import Path

_HELP = """usage: split-membership-check ASSIGNMENTS.jsonl

Check normalized synthetic dataset split assignments (train, validation, test).
Exit status: 0 valid, 1 overlap, 2 invalid input.
"""


def _reject_constant(_value):
    raise ValueError


def _pairs_no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError
        result[key] = value
    return result


def _lines(text):
    """Split only on physical CR/LF delimiters; retain interior blank rows."""
    rows = []
    start = 0
    i = 0
    while i < len(text):
        if text[i] in "\r\n":
            rows.append(text[start:i])
            if text[i] == "\r" and i + 1 < len(text) and text[i + 1] == "\n":
                i += 1
            start = i + 1
        i += 1
    if start < len(text):
        rows.append(text[start:])
    return rows


def _valid_string(value):
    return bool(value) and not any(0xD800 <= ord(char) <= 0xDFFF for char in value)


def check_bytes(data):
    """Return the public result and status code without exposing input data."""
    try:
        text = data.decode("utf-8", errors="strict")
        seen = defaultdict(set)
        occurrences = defaultdict(list)
        count = 0
        for line_number, row in enumerate(_lines(text), 1):
            if not row.strip():
                raise ValueError
            obj = json.loads(row, object_pairs_hook=_pairs_no_duplicates,
                             parse_constant=_reject_constant)
            # Iterative shape validation avoids recursion in our own validator.
            if not isinstance(obj, dict) or set(obj) != {"id", "split"}:
                raise ValueError
            identifier, split = obj["id"], obj["split"]
            if not isinstance(identifier, str) or not _valid_string(identifier):
                raise ValueError
            if not isinstance(split, str) or split not in {"train", "validation", "test"}:
                raise ValueError
            if split in seen[identifier]:
                raise ValueError
            seen[identifier].add(split)
            occurrences[identifier].append(line_number)
            count += 1
        overlap_lines = sorted(
            line for identifier, split_set in seen.items() if len(split_set) > 1
            for line in occurrences[identifier]
        )
        status = "overlap" if overlap_lines else "valid"
        return {"status": status, "record_count": count, "overlap_lines": overlap_lines}, (1 if overlap_lines else 0)
    except (UnicodeError, ValueError, TypeError, RecursionError, json.JSONDecodeError):
        return {"status": "invalid_input"}, 2


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv in ( ["-h"], ["--help"] ):
        sys.stdout.write(_HELP)
        return 0
    if len(argv) != 1:
        sys.stdout.write('{"status":"invalid_input"}\n')
        return 2
    try:
        data = Path(argv[0]).read_bytes()
        result, code = check_bytes(data)
    except (OSError, ValueError, TypeError):
        result, code = {"status": "invalid_input"}, 2
    sys.stdout.write(json.dumps(result, ensure_ascii=True, separators=(",", ":")) + "\n")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
