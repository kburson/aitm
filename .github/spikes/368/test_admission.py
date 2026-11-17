import unittest

from admission import reconcile


class AdmissionTraceTests(unittest.TestCase):
    def setUp(self):
        self.rows = "READY 32\nU 32 368\nP 32 33\nX 32 33\nS 32 33 0\nR 32 33 1\n"

    def test_exact_trace_matches_real_wait_and_child(self):
        self.assertEqual(reconcile(self.rows, "WAIT 32 33 0\n", 32), 33)

    def test_missing_or_duplicate_process_record_refuses(self):
        for rows in (self.rows.replace("X 32 33\n", ""), self.rows + "P 32 33\n"):
            with self.assertRaises(ValueError):
                reconcile(rows, "WAIT 32 33 0\n", 32)

    def test_unexpected_usdt_process_and_failed_wait_refuse(self):
        with self.assertRaises(ValueError):
            reconcile(self.rows.replace("U 32", "U 34"), "WAIT 32 33 0\n", 32)
        with self.assertRaises(ValueError):
            reconcile(self.rows, "WAIT 32 33 1\n", 32)


if __name__ == "__main__":
    unittest.main()
