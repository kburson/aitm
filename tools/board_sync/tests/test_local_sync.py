import unittest

from tools.board_sync import local_sync as sync
from tools.board_sync.blocked_by import Issue


class ScopeTests(unittest.TestCase):
    def test_single_includes_both_directions_while_batches_use_dependent_state(self):
        issues = {1: Issue("a", True, None), 2: Issue("b", False, None)}
        self.assertTrue(sync.in_scope("single", 2, (1, 2), issues))
        self.assertTrue(sync.in_scope("single", 2, (2, 1), issues))
        self.assertTrue(sync.in_scope("open", None, (1, 2), issues))
        self.assertFalse(sync.in_scope("open", None, (2, 1), issues))
        self.assertTrue(sync.in_scope("closed", None, (2, 1), issues))

    def test_replays_and_disjoint_changes_preserve_prior_result(self):
        edges = {(3, 1), (3, 2), (4, 1)}
        planning = {(3, 2), (4, 1), (4, 2)}
        github = {(3, 1), (4, 1)}
        issues = {n: Issue(str(n), True, None) for n in range(1, 5)}
        desired = sync.reconcile(edges, planning, github, "open", None, issues)
        self.assertEqual(desired, {(4, 1), (4, 2)})
        self.assertEqual(
            sync.reconcile(desired, desired, desired, "open", None, issues), desired
        )

    def test_unselected_drift_is_not_propagated(self):
        issues = {
            1: Issue("a", True, None),
            2: Issue("b", False, None),
            3: Issue("c", True, None),
        }
        self.assertEqual(
            sync.reconcile(set(), {(2, 1)}, {(3, 1)}, "open", None, issues),
            {(3, 1)},
        )


class FileTests(unittest.TestCase):
    def test_updates_only_frontmatter_and_preserves_body_bytes(self):
        original = "---\r\nid: 4\r\nblocked-by: [7, 8]\r\nblocking: []\r\n---\r\nScope references #8.\r\n"
        self.assertEqual(
            sync.update_index(original, "blocked-by", {7}, {8}, {9}),
            original.replace("blocked-by: [7, 8]", "blocked-by: [7, 9]"),
        )

    def test_planning_first_edit_repairs_reverse_index(self):
        paths = {1: "first", 2: "second"}
        files = {
            "first": "---\nid: 1\nblocked-by: []\nblocking: []\n---\n",
            "second": "---\nid: 2\nblocked-by: [1]\nblocking: []\n---\n",
        }
        edges = {(2, 1)}
        changes = sync.story_changes(paths, files, edges, edges, set(), edges)
        self.assertEqual(
            changes, {"first": files["first"].replace("blocking: []", "blocking: [2]")}
        )

    def test_baseline_requires_agreement_to_bootstrap(self):
        self.assertEqual(sync.read_baseline(None, {(2, 1)}, {(2, 1)}), {(2, 1)})
        with self.assertRaisesRegex(ValueError, "baseline"):
            sync.read_baseline(None, {(2, 1)}, set())
