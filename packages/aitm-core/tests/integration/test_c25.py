"""Exercise installed review commands with a real worktree, store, and Git replay."""

import json
from datetime import UTC, datetime
from pathlib import Path
from shutil import which
from subprocess import run

from aitm_core.events import core_reducers, fold
from aitm_core.store.objects import Repository
from tests.integration.test_c08 import PLANNING
from tests.integration.test_c09 import describe_args
from tests.integration.test_c09 import topology as topology
from tests.unit.test_c15 import EVENTS, graduated
from tests.unit.test_c24 import digest

DOC = ".aitm/stories/000/16/plan/current.md"
FUR = b'---\n{"schema":"aitm.doc/v1","story":16,"role":"plan","title":"Capsule"}\n---\nReview this plan.\n'


def _invoke(topology, args, command, *fields):
    executable = which("aitm")
    assert executable is not None
    result = run(
        [executable, "--json", "review", command, *fields, *args],
        cwd=topology.local,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.stdout, result.stderr
    return json.loads(result.stdout)


def _read(topology):
    repository = Repository(topology.local, PLANNING)
    events = repository.read_blobs(repository.tip().tree, (EVENTS,))[EVENTS]
    return fold(events.splitlines(keepends=True), core_reducers()).domains["evidence"]


def _bundle(folder):
    folder.mkdir()
    digest_value = digest(FUR)
    identity = f"level: sar\nstory: 16\nartifact_path: {DOC}\n"
    manifest = (
        f"---\nschema: aitm.review-manifest/v0\n{identity}"
        f"base_digest: {digest_value}\nfinal_digest: {digest_value}\n"
        "rounds: 1\noutcome: exhausted\nauthority_assurance: declared-manual\n---\n"
    )
    (folder / "review-manifest.md").write_text(manifest)
    end = datetime.now(UTC).isoformat()
    for role in ("reviewer", "author"):
        patch = "patch: patch-001.diff\n" if role == "author" else ""
        decision = "## Decision\n\naccepted\n" if role == "reviewer" else ""
        response = (
            f"---\nschema: aitm.review-response/v0\n{identity}"
            f"role: {role}\nround: 1\nartifact_digest: {digest_value}\n"
            f"{role}_session: fixture\nsession_identity_kind: recorded-session\n"
            f"submitted_at: {end}\nagent: {{host: fixture, provider: fixture, model_id: fixture, effort: high}}\n"
            f"{patch}---\n{decision}"
        )
        (folder / f"{role}-response-1.md").write_text(response)
    base = (
        f"diff --git a/{DOC} b/{DOC}\nnew file mode 100644\n--- /dev/null\n+++ b/{DOC}\n"
        f"@@ -0,0 +1,{len(FUR.splitlines())} @@\n"
    ).encode() + b"".join(b"+" + line for line in FUR.splitlines(keepends=True))
    (folder / "patch-000.diff").write_bytes(base)
    (folder / "patch-001.diff").write_bytes(b"")


def test_live_backfill_same_fact(topology, tmp_path):
    topology.advance_planning(EVENTS, graduated())
    scratch = tmp_path / "review-input"
    options = describe_args(topology, scratch)[-4:]
    fur = Path(topology.local) / DOC
    fur.parent.mkdir(parents=True, exist_ok=True)
    fur.write_bytes(FUR)

    opened = _invoke(
        topology, options, "open", "--story", "16", "--doc", DOC, "--level", "sar"
    )
    assert opened["local"] == "completed", opened["evidence"]
    state = _read(topology)
    record_id, initial = next(iter(state.document_reviews.items()))
    assert initial.opening is not None and initial.turns == {}
    assert initial.completion is None
    assert Path(fur).read_bytes() == FUR

    folder = scratch / "bundle"
    _bundle(folder)
    mapping = scratch / "mapping.json"
    mapping.write_text(
        json.dumps(
            {
                "evidence": "fixture participant registry",
                "bindings": [
                    {
                        "participant": {
                            "namespace": "recorded-session",
                            "session": "fixture",
                            "provider": "fixture",
                        },
                        "session_id": "fixture",
                        "provider_family": "fixture",
                    }
                ],
            }
        )
    )
    response = folder / "reviewer-response-1.md"
    turn = _invoke(
        topology, options, "turn", "--record", record_id, "--response", str(response)
    )
    assert turn["local"] == "completed", turn
    prior = _read(topology).document_reviews[record_id].turns[(1, "reviewer")]
    first_bytes = response.read_bytes()
    response.write_bytes(first_bytes + b"\nChanged evidence.\n")
    conflict = _invoke(
        topology, options, "turn", "--record", record_id, "--response", str(response)
    )
    assert conflict["local"] == "conflict", conflict
    response.write_bytes(first_bytes)

    fields = (
        "--record",
        record_id,
        "--bundle",
        str(folder),
        "--identity-map",
        str(mapping),
    )
    for _ in range(2):
        completed = _invoke(topology, options, "complete", *fields)
        assert completed["local"] == "completed", completed
    final = _read(topology).document_reviews[record_id]
    assert set(final.turns) == {(1, "reviewer"), (1, "author")}
    assert final.turns[(1, "reviewer")] == prior
    assert final.opening == initial.opening
    assert final.completion.started_at == initial.opening.opened_at
    assert final.turns[(1, "reviewer")].start_basis == "unknown"
