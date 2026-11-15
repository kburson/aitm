"""Reproduce the first benchmark layout's native ctime invalidation."""
from pathlib import Path
from tempfile import TemporaryDirectory

from aitm_usage.sources.scan import _probe


with TemporaryDirectory() as scratch:
    base = Path(scratch).resolve()
    out = base / "evidence"
    fixtures = base / "native-fixtures"
    out.mkdir()
    fixtures.mkdir()
    under_evidence = out / "fixture"
    under_evidence.mkdir()
    unsafe = under_evidence / "sample.jsonl"
    safe = fixtures / "sample.jsonl"
    for stream in (unsafe, safe):
        stream.write_text("{}\n")
    old_unsafe, old_safe = map(_probe, (unsafe, safe))
    (out / ".coverage.simulated.pid123.log").touch()
    new_unsafe, new_safe = map(_probe, (unsafe, safe))
    assert old_unsafe.identity == new_unsafe.identity
    assert not old_unsafe.same_path(new_unsafe)
    assert old_safe.same_path(new_safe)
    print("Adding coverage under a fixture ancestor invalidates native custody. A sibling fixture path stays stable.")
