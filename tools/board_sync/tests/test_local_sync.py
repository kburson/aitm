import unittest
from unittest.mock import Mock, call, patch

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


class PublicationTests(unittest.TestCase):
    def test_reconciles_again_after_a_concurrent_close_overlaps_board_write(self):
        baseline = '{"schema":"aitm.dependency-baseline/v1","edges":[[1,2]]}\n'
        stories = {
            ".aitm/stories/000/1/story.md": "---\nid: 1\nstate: backlog\nblocked-by: [2]\n---\n",
            ".aitm/stories/000/2/story.md": "---\nid: 2\nstate: backlog\nblocked-by: []\n---\n",
            sync.BASELINE: baseline,
        }
        hosted = {
            **stories,
            sync.board.PROJECTION: sync.board.projection_text({1: (), 2: ()}),
        }
        github = Mock(ref="refs/heads/planning")
        github.branch_head.side_effect = [
            "base",
            "local",
            "hosted",
            "hosted",
            "hosted",
            "hosted",
        ]
        github.issues.side_effect = [
            {1: Issue("a", True, None), 2: Issue("b", True, None)},
            {1: Issue("a", True, "#2"), 2: Issue("b", False, None)},
        ]
        github.relationships.return_value = {(1, 2)}
        github.commit_files.return_value = "local"
        with patch.object(
            sync.board,
            "read_planning_files",
            side_effect=[("base", stories), ("hosted", hosted)],
        ):
            self.assertEqual(sync.run(github, "origin", "open", None), {1: (), 2: ()})

        self.assertEqual(
            github.write_blockers.call_args_list, [call("a", "#2"), call("a", None)]
        )
        github.commit_files.assert_called_once()
