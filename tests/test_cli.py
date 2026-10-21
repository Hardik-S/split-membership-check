import json
import unittest

from split_membership_check.cli import check_bytes


def encoded(*rows, end="\n"):
    return (end.join(json.dumps(row, ensure_ascii=True) for row in rows) + (end if rows else "")).encode()


class CheckerTests(unittest.TestCase):
    def test_empty_and_valid(self):
        self.assertEqual(check_bytes(b""), ({"status": "valid", "record_count": 0, "overlap_lines": []}, 0))
        result, code = check_bytes(encoded({"id": "a", "split": "train"}, {"id": "b", "split": "test"}))
        self.assertEqual((result["status"], result["record_count"], code), ("valid", 2, 0))

    def test_overlap_reports_every_occurrence_sorted(self):
        data = encoded({"id": "a", "split": "train"}, {"id": "b", "split": "train"},
                       {"id": "a", "split": "test"}, {"id": "a", "split": "validation"})
        result, code = check_bytes(data)
        self.assertEqual((result, code), ({"status": "overlap", "record_count": 4,
                                           "overlap_lines": [1, 3, 4]}, 1))

    def test_duplicate_pair_invalid_even_after_overlap(self):
        data = encoded({"id": "a", "split": "train"}, {"id": "a", "split": "test"},
                       {"id": "a", "split": "train"})
        self.assertEqual(check_bytes(data), ({"status": "invalid_input"}, 2))

    def test_all_splits_and_newline_forms(self):
        for delimiter in ("\n", "\r", "\r\n"):
            result, code = check_bytes(encoded({"id": "a", "split": "train"},
                                               {"id": "a", "split": "validation"},
                                               {"id": "a", "split": "test"}, end=delimiter))
            self.assertEqual((result["overlap_lines"], code), ([1, 2, 3], 1))

    def test_invalid_rows_and_privacy_independent_result(self):
        bad = [b"\xff", b"\n", b'{"id":"x","split":"train","x":1}',
               b'{"id":"x","id":"y","split":"train"}',
               b'{"id":"x","split":"bad"}', b'{"id":"","split":"train"}',
               b'{"id":"x","split":"train"}' + "\u2028".encode() + b'{"id":"y","split":"test"}',
               b'{"id":"x","split":"train"}\n{"id":"x","split":"train"}',
               b'{"id":"x","split":NaN}', b'{"id":"x","split":Infinity}',
               b'{"id":"x","split":"train"}\n\n', b'{"id":"x","split":"train"',
               b'{"id":"x","split":"train","extra":null}',
               b'{"id":7,"split":"train"}', b'{"id":"x","split":null}',
               b'{"id":"\\ud800","split":"train"}']
        for data in bad:
            with self.subTest(data=data[:20]):
                self.assertEqual(check_bytes(data), ({"status": "invalid_input"}, 2))

    def test_deep_json_decoder_error_is_contained(self):
        data = (b'{"id":"x","split":"train","extra":' + b"[" * 3000 + b"0" + b"]" * 3000 + b"}")
        self.assertEqual(check_bytes(data), ({"status": "invalid_input"}, 2))


if __name__ == "__main__":
    unittest.main()
