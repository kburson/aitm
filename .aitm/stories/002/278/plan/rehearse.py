"""Rehearse a lost response with retained #277 provider observations."""
from hashlib import sha256
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

import ci_incident as ci


def main():
    records = json.loads(Path(sys.argv[1]).read_bytes())
    red = records["historical"]["decision"]
    late = records["missing_artifact"]["decision"]
    with TemporaryDirectory() as scratch:
        root = Path(scratch)
        db = root / "warnings.db"
        sink = ci.DirectorySink(root / "operator")
        store = ci.Store(db, "shadow")
        assert store.observe(red) == "warning"
        assert store.observe(red) == "duplicate"

        def lost(name, content):
            sink(name, content)
            raise OSError("simulated lost delivery response")

        try:
            store.deliver(lost, directory=sink.directory)
        except OSError as exc:
            assert str(exc) == "simulated lost delivery response"
        else:
            raise AssertionError("lost response was not exercised")
        [warning] = sink.directory.glob("*.md")
        body = warning.read_bytes()
        assert store.status()["warnings"][0]["delivered"] is None
        restart = ci.Store(db, "shadow")
        assert restart.deliver(sink) == 1
        assert restart.deliver(sink) == 0
        assert list(sink.directory.glob("*.md")) == [warning]
        assert warning.read_bytes() == body
        version = restart.status()["incident"]["version"]
        restart.nominate(version, "shadow-operator", 281)
        old_state = restart.status()
        try:
            restart.nominate(version, "duplicate-shadow-operator", 281)
        except ValueError:
            pass
        else:
            raise AssertionError("multiple owners were nominated")
        assert restart.status() == old_state
        assert restart.observe(late) == "warning"
        current = restart.status()
        assert current["incident"]["nomination"] is None
        assert current["incident"]["failures"] == ["collect-evidence:failure"]
        assert restart.observe(red) == "stale"
        assert restart.deliver(sink) == 1
        print(json.dumps({
            "provenance": "shadow",
            "lost_response_recovered": True,
            "warning_count_before_new_attempt": 1,
            "warning_count_after_new_attempt": len(list(sink.directory.glob("*.md"))),
            "published_warning": warning.name,
            "published_sha256": sha256(body).hexdigest(),
            "published_text": body.decode(),
            "nomination_invalidated": True,
            "status": restart.status(),
        }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
