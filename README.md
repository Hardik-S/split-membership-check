# Split Membership Check

An offline, standard-library CLI for checking explicit normalized synthetic dataset split assignments. It detects whether an exact ID appears in more than one of `train`, `validation`, and `test`, and reports every physical input row for each overlapping ID. It does not generate splits or assess semantic similarity, leakage, data quality, or model quality.

Blank physical rows are invalid. Each JSONL row must contain exactly `id` (a nonempty string) and `split` (one of the three names). Repeating the same ID and split is invalid input. IDs compare as exact Unicode strings without normalization. Input is validated in full before a result is printed.

Install with `python -m pip install .`, then run:

```text
split-membership-check ASSIGNMENTS.jsonl
```

The sole JSON result is `{"status":"valid"|"overlap","record_count":N,"overlap_lines":[...]}`. Exit codes are 0 for valid, 1 for overlap, and 2 for invalid input. Invalid input always prints only `{"status":"invalid_input"}` to stdout and nothing to stderr. `--help` prints usage and exits 0. Examples are synthetic; the tool's memory use grows with the input size.

For a fresh installed-package acceptance run, see [LAUNCH.md](LAUNCH.md).
