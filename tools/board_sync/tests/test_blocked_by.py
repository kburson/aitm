import json
import unittest
from unittest.mock import Mock

from tools.board_sync import blocked_by as sync


class ProjectionTests(unittest.TestCase):
    def test_61_only_keeps_independent_open_blockers(self):
        dependencies = {
            61: [39, 40, 41, 42, 45, 49, 57, 58, 79, 80],
            80: [79],
            79: [40, 41, 42, 45, 49],
            40: [39],
            57: [39],
            58: [40],
        }
        for issue in (39, 41, 42, 45, 49):
            dependencies[issue] = []
        stories = {
            number: sync.Story(tuple(links), False)
            for number, links in dependencies.items()
        }
        self.assertEqual(sync.project(stories, set(stories))[61], (57, 58, 80))

    def test_close_reopen_and_done_records(self):
        stories = {
            1: sync.Story((2, 3), False),
            2: sync.Story((3,), True),
            3: sync.Story((4,), False),
            4: sync.Story((), False),
        }
        self.assertEqual(
            sync.project(stories, {1, 2, 3, 4}), {1: (2,), 2: (), 3: (4,), 4: ()}
        )
        self.assertEqual(sync.project(stories, {1, 3, 4})[1], (3,))
        self.assertEqual(sync.project(stories, {1, 4})[1], ())

    def test_refuses_a_cycle_or_a_missing_prerequisite(self):
        with self.assertRaisesRegex(ValueError, "cycle"):
            sync.project(
                {1: sync.Story((2,), False), 2: sync.Story((1,), False)}, {1, 2}
            )
        with self.assertRaisesRegex(ValueError, "unknown blocker"):
            sync.project({1: sync.Story((2,), False)}, {1})

    def test_reads_dependency_fields_only_from_frontmatter(self):
        raw = '---\nid: 61\nstate: "backlog"\nblocked-by: [58, 80]\n---\nblocked-by: [1]\n'
        self.assertEqual(sync.read_story(raw, 61), sync.Story((58, 80), False))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            sync.read_story(raw.replace("state:", "id: 61\nstate:"), 61)


class PublicationTests(unittest.TestCase):
    def test_publish_same_values_on_both_surfaces_and_skip_equal_values(self):
        github = Mock()
        issues = {
            1: sync.Issue("issue1", True, "#2, #3"),
            2: sync.Issue("issue2", False, "#4"),
            3: sync.Issue("issue3", True, None),
            4: sync.Issue("issue4", True, "#3"),
        }
        desired = {1: (3,), 2: (), 3: (), 4: (3,)}
        github.branch_head.return_value = "abc"
        sync.publish(github, "abc", None, issues, desired, apply=True)
        head, data = github.commit_snapshot.call_args.args
        self.assertEqual(head, "abc")
        self.assertEqual(
            json.loads(data)["blocked_by"], {"1": [3], "2": [], "3": [], "4": [3]}
        )
        self.assertEqual(
            [call.args for call in github.write_blockers.call_args_list],
            [("issue1", "#3"), ("issue2", None)],
        )

    def test_read_only_mode_and_no_writes_after_planning_commit_fails(self):
        github = Mock()
        issues = {1: sync.Issue("issue1", True, "#2")}
        desired = {1: ()}
        sync.publish(github, "abc", None, issues, desired, apply=False)
        github.commit_snapshot.assert_not_called()
        github.write_blockers.assert_not_called()
        github.branch_head.return_value = "abc"
        github.commit_snapshot.side_effect = RuntimeError("head changed")
        with self.assertRaisesRegex(RuntimeError, "head changed"):
            sync.publish(github, "abc", None, issues, desired, apply=True)
        github.write_blockers.assert_not_called()
