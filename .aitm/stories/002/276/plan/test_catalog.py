import unittest

from catalog import CHILDREN, Outcome, admit_local


class CatalogTest(unittest.TestCase):
    def test_unobserved_catalog_is_refused(self):
        result = admit_local({})
        self.assertFalse(result["passed"])
        self.assertEqual(sorted(result["missing"]), sorted(CHILDREN))

    def test_success_claim_requires_controlled_process_evidence(self):
        result = admit_local({key: {"passed": True} for key in CHILDREN})
        self.assertFalse(result["passed"])
        self.assertEqual(sorted(result["invalid"]), sorted(CHILDREN))

    def test_failed_external_check_is_refused(self):
        result = admit_local({key: Outcome(False, "expected control") for key in CHILDREN})
        self.assertFalse(result["passed"])


if __name__ == "__main__":
    unittest.main()
