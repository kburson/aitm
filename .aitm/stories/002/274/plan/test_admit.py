import copy
import unittest

from admit import admit, authorize, Refusal


class Controls(unittest.TestCase):
    def setUp(self):
        self.approved = {
            "repository": "example/repo",
            "workflow_id": 1,
            "workflow_path": ".github/workflows/test.yml",
            "head": "observer-head",
            "observer_tree": "observer-tree",
            "product_tree": "product-tree",
            "product_commit": "product-commit",
            "run": 2,
            "attempt": 1,
            "assignment_sha256": "assignment",
            "mode": "full",
        }
        self.request = dict(self.approved)

    def test_exact_request_is_admitted(self):
        self.assertEqual(authorize(self.approved, self.request), self.approved)

    def test_changed_scope_is_refused(self):
        for field in ("product_tree", "observer_tree", "attempt", "assignment_sha256", "mode"):
            with self.subTest(field=field), self.assertRaisesRegex(Refusal, field):
                request = copy.deepcopy(self.request)
                request[field] = "different"
                authorize(self.approved, request)

    def test_no_assertion_only_admission(self):
        with self.assertRaisesRegex(Refusal, "evidence"):
            admit(self.approved, self.request, None, None)


if __name__ == "__main__":
    unittest.main()
