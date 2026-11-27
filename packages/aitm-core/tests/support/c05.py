"""Recording fixture validation gate for the Git backend."""

from contextlib import contextmanager
from threading import Lock

REF = "refs/heads/planning"


class FixtureGate:
    def __init__(self):
        self.lock = Lock()
        self.observed = []

    @contextmanager
    def __call__(self, repo, target):
        assert repo.ref == target == REF
        with self.lock:
            yield self.validate

    def validate(self, before, candidate):
        self.observed.append((before, candidate))
        if candidate is not None:
            assert before.store == candidate.store
            assert before.revision != candidate.revision
