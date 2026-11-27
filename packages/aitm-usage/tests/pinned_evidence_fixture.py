"""In-memory Git object responses for tests of pinned evidence policy."""

from hashlib import sha1
from pathlib import Path, PurePosixPath

import pytest

from aitm_usage.effort.pinned_inputs import PinnedTree


class PinnedEvidence:
    path = Path("/fixture-planning-repository")

    def __init__(self, story_root, story):
        self.work = {f"{story_root}/story.md": f"---\nid: {story}\n---\n".encode()}
        self.commits = {}

    def __str__(self):
        return str(self.path)

    def write(self, path, raw):
        self.work[path] = raw

    def append(self, path, raw):
        self.write(path, self.work.get(path, b"") + raw)

    def pin(self):
        commit = f"{len(self.commits) + 1:040x}"
        self.commits[commit] = self.work.copy()
        return commit

    @staticmethod
    def oid(raw):
        return sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

    def response(self, tree, *args, limit, operation="Git read"):
        assert tree.repository is self or tree.repository == self.path
        snapshot = self.commits[tree.commit]
        match args:
            case "rev-parse", "--verify", revision:
                assert revision == f"{tree.commit}^{{commit}}"
                raw = tree.commit.encode() + b"\n"
            case "ls-tree", "-z", commit, "--", path:
                assert commit == tree.commit
                if path in snapshot:
                    blob = self.oid(snapshot[path])
                    raw = f"100644 blob {blob}\t{path}\0".encode()
                elif any(name.startswith(path + "/") for name in snapshot):
                    raw = f"040000 tree {'0' * 40}\t{path}\0".encode()
                else:
                    raw = b""
            case "ls-tree", "-rz", "--name-only", commit, "--", prefix:
                assert commit == tree.commit
                raw = b"".join(
                    name.encode() + b"\0"
                    for name in sorted(snapshot)
                    if PurePosixPath(prefix) in PurePosixPath(name).parents
                )
            case "cat-file", mode, object_id:
                (blob,) = {
                    value for value in snapshot.values() if self.oid(value) == object_id
                }
                assert mode in {"-s", "blob"}
                raw = f"{len(blob)}\n".encode() if mode == "-s" else blob
            case _:
                raise AssertionError(f"Unexpected Git read: {args!r}")
        assert len(raw) <= limit, operation
        return raw


@pytest.fixture
def pinned_evidence(monkeypatch):
    def fixture(story_root, story):
        evidence = PinnedEvidence(story_root, story)

        def git_read(tree, *args, **kwargs):
            return evidence.response(tree, *args, **kwargs)

        monkeypatch.setattr(PinnedTree, "_read", git_read)
        return evidence

    return fixture
