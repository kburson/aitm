"""Verify atomic review import and both installed document acceptance routes in Git."""

import json
from datetime import UTC, datetime
from difflib import unified_diff
from pathlib import Path
from subprocess import run
from sys import executable

from aitm_core.events import core_reducers, fold
from aitm_core.models.binding import StoryRef
from aitm_core.services import preflight_policy
from aitm_core.setup.init import _record_installation
from aitm_core.store.objects import Repository
from aitm_core.store.workspace import Workspace
from tests.integration.test_c08 import (
    DEFAULT,
    PLANNING,
    PLANNING_REMOTE,
    commit_file,
    git,
)
from tests.integration.test_c08 import topology as topology
from tests.unit.test_c15 import EVENTS, graduated
from tests.unit.test_c24 import digest

PLAN = ".aitm/stories/000/16/plan/current.md"
DESIGN = ".aitm/stories/000/16/design/current.md"


def cli(root, *arguments):
    result = run(
        (str(Path(executable).with_name("aitm")), "--json", *arguments),
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.stdout, result.stderr
    return json.loads(result.stdout)


def _document(role, text):
    header = json.dumps(
        {"schema": "aitm.doc/v1", "story": 16, "role": role, "title": "Review"}
    )
    return f"---\n{header}\n---\n{text}\n".encode()


def _review(root, path, level, base, final):
    root.mkdir()
    rounds = 1 if base == final else 2
    identity = f"story: 16\nlevel: {level}\nartifact_path: {path}\n"
    (root / "review-manifest.md").write_text(
        f"---\nschema: aitm.review-manifest/v0\n{identity}"
        f"base_digest: {digest(base)}\nfinal_digest: {digest(final)}\nrounds: {rounds}\n"
        "outcome: exhausted\nauthority_assurance: declared-manual\n---\n"
    )
    base_patch = (
        f"diff --git a/{path} b/{path}\nnew file mode 100644\n--- /dev/null\n+++ b/{path}\n"
        f"@@ -0,0 +1,{len(base.splitlines())} @@\n"
    ).encode() + b"".join(b"+" + line for line in base.splitlines(keepends=True))
    (root / "patch-000.diff").write_bytes(base_patch)
    end = datetime.now(UTC).isoformat()
    for index in range(1, rounds + 1):
        if index < rounds:
            delta = "".join(
                unified_diff(
                    base.decode().splitlines(keepends=True),
                    final.decode().splitlines(keepends=True),
                    fromfile=f"a/{path}",
                    tofile=f"b/{path}",
                )
            )
            (root / f"patch-{index:03d}.diff").write_bytes(
                f"diff --git a/{path} b/{path}\n{delta}".encode()
            )
        else:
            (root / f"patch-{index:03d}.diff").write_bytes(b"")
        for role in ("reviewer", "author"):
            actor = "other" if level == "xpr" and role == "reviewer" else "fixture"
            data = base if role == "reviewer" and index == 1 else final
            verdict = "accepted" if index == rounds else "revisions-requested"
            extra = f"patch: patch-{index:03d}.diff\n" if role == "author" else ""
            body = f"## Decision\n\n{verdict}\n" if role == "reviewer" else ""
            (root / f"{role}-response-{index}.md").write_text(
                f"---\nschema: aitm.review-response/v0\n{identity}role: {role}\nround: {index}\n"
                f"artifact_digest: {digest(data)}\n{role}_session: {actor}\n"
                "session_identity_kind: recorded-session\n"
                f"submitted_at: {end}\nagent: {{host: fixture, provider: {actor}, model_id: fixture, effort: high}}\n"
                f"{extra}---\n{body}"
            )


def _state(repo):
    events = repo.read_blobs(repo.tip().tree, (EVENTS,))[EVENTS]
    return fold(events.splitlines(keepends=True), core_reducers())


def test_exact_content(topology, tmp_path):
    plan_a, plan_b = _document("plan", "A"), _document("plan", "B")
    design = _document("design", "Own design")
    topology.advance_planning(EVENTS, graduated())
    topology.advance_planning(PLAN, plan_a)
    topology.advance_planning(DESIGN, design)
    installation = topology.policy.installation
    observed = preflight_policy(installation)
    assert observed.policy is not None, observed.reason
    _record_installation(installation, observed.policy.revision)
    bound = cli(
        topology.local,
        "bind",
        "16",
        "--session",
        "reviewer",
        "--path",
        PLAN,
        "--path",
        DESIGN,
    )
    assert bound["local"] == "completed", bound
    lease = json.loads(bound["evidence"][0])
    options = (
        "--story",
        "16",
        "--binding",
        lease["identity"],
        "--generation",
        str(lease["generation"]),
        "--session",
        "reviewer",
    )
    anchor = tmp_path / "anchor.json"
    anchor.write_text(installation.store.model_dump_json())
    mapping = tmp_path / "mapping.json"
    mapping.write_text(
        json.dumps(
            {
                "evidence": "fixture identities",
                "bindings": [
                    {
                        "participant": {
                            "namespace": "recorded-session",
                            "session": name,
                            "provider": name,
                        },
                        "session_id": name,
                        "provider_family": name,
                    }
                    for name in ("fixture", "other")
                ],
            }
        )
    )
    repo = Repository(topology.local, PLANNING)
    opened = cli(
        topology.local,
        "review",
        "open",
        "--anchor",
        str(anchor),
        "--story",
        "16",
        "--doc",
        PLAN,
        "--level",
        "sar",
    )
    assert opened["local"] == "completed", opened
    (plan_review,) = _state(repo).domains["evidence"].document_reviews
    source = tmp_path / "plan-review"
    _review(source, PLAN, "sar", plan_a, plan_b)
    provisional = cli(
        topology.local,
        "review",
        "turn",
        "--anchor",
        str(anchor),
        "--record",
        plan_review,
        "--response",
        str(source / "reviewer-response-1.md"),
    )
    assert provisional["local"] == "completed", provisional
    initial = (
        _state(repo)
        .domains["evidence"]
        .document_reviews[plan_review]
        .turns[(1, "reviewer")]
    )

    old = repo.tip().revision
    workspace = Workspace(installation)
    scope = StoryRef(story=16)
    original_binding = workspace.lookup(scope)
    assert original_binding is not None
    import_options = (
        "review",
        "import",
        str(source),
        *options,
        "--doc",
        PLAN,
        "--expected-base",
        digest(plan_a).removeprefix("sha256:"),
        "--identity-map",
        str(mapping),
        "--record",
        plan_review,
    )
    imported = cli(topology.local, *import_options)
    assert imported["local"] == "completed" and imported["publication"] == "verified", (
        imported
    )
    new = repo.tip().revision
    assert git(topology.local, "rev-parse", f"{new}^") == old
    assert (
        git(
            Path(git(topology.local, "remote", "get-url", PLANNING_REMOTE)),
            "rev-parse",
            PLANNING,
        )
        == new
    )
    assert repo.read_blobs(repo.tip().tree, (PLAN,))[PLAN] == plan_b
    assert (topology.local / PLAN).read_bytes() == plan_b
    state = _state(repo)
    record = state.domains["evidence"].document_reviews[plan_review]
    assert len(record.turns) == 4 and record.turns[(1, "reviewer")] == initial
    assert not state.domains["lifecycle"].accepted_documents
    assert record.completion is not None

    # Restore the local state left by an interruption between the atomic
    # planning publication and workspace projection. The remote remains real.
    (topology.local / PLAN).write_bytes(plan_a)
    with workspace.lock():
        workspace.persist(original_binding)
    projection = cli(topology.local, *import_options)
    assert projection["local"] == "completed", projection
    assert projection["publication"] == "verified", projection
    assert (topology.local / PLAN).read_bytes() == plan_b
    assert repo.tip().revision == new

    changed = source / "reviewer-response-2.md"
    preserved = changed.read_bytes()
    changed.write_bytes(preserved + b"\nA different retained original.\n")
    changed_options = tuple(
        digest(plan_b).removeprefix("sha256:")
        if arg == digest(plan_a).removeprefix("sha256:")
        else arg
        for arg in import_options
    )
    refused = cli(topology.local, *changed_options)
    assert refused["local"] == "conflict", refused
    assert repo.tip().revision == new
    changed.write_bytes(preserved)

    accepted = cli(
        topology.local,
        "plan",
        "accept",
        *options,
        "--doc",
        PLAN,
        "--review",
        plan_review,
        "--identity-map",
        str(mapping),
    )
    assert accepted["local"] == "completed", accepted
    first = _state(repo).domains["lifecycle"].accepted_documents["plan"]
    mapping_path = f".aitm/stories/000/16/evidence/review-identities/{digest(mapping.read_bytes()).removeprefix('sha256:')}.json"
    assert first.plan_generation == 1
    assert first.source_planning_sha == new
    assert first.policy_digest == observed.policy.source.digest
    assert first.raw_digest == digest(plan_b).removeprefix("sha256:")
    assert first.review_refs == (record.completion.manifest_path, mapping_path)
    assert first.levels == ("sar",)

    capped = tmp_path / "capped-review"
    _review(capped, PLAN, "sar", plan_b, _document("plan", "Unaccepted cap output"))
    manifest = capped / "review-manifest.md"
    manifest.write_bytes(
        manifest.read_bytes().replace(b"outcome: exhausted", b"outcome: round-cap")
    )
    response = capped / "reviewer-response-2.md"
    response.write_bytes(
        response.read_bytes().replace(b"accepted", b"revisions-requested")
    )
    retained_cap = cli(
        topology.local,
        "review",
        "import",
        str(capped),
        *options,
        "--doc",
        PLAN,
        "--expected-base",
        digest(plan_b).removeprefix("sha256:"),
    )
    assert retained_cap["local"] == "completed", retained_cap
    caps = [
        key
        for key, record in _state(repo).domains["evidence"].document_reviews.items()
        if record.completion and record.completion.outcome == "round-cap"
    ]
    assert len(caps) == 1
    assert (topology.local / PLAN).read_bytes() == plan_b
    assert repo.read_blobs(repo.tip().tree, (PLAN,))[PLAN] == plan_b
    unaccepted = cli(
        topology.local,
        "plan",
        "accept",
        *options,
        "--doc",
        PLAN,
        "--review",
        caps[0],
        "--identity-map",
        str(mapping),
    )
    assert unaccepted["local"] != "completed", unaccepted

    source = tmp_path / "design-review"
    _review(source, DESIGN, "xpr", design, design)
    imported_design = cli(
        topology.local,
        "review",
        "import",
        str(source),
        *options,
        "--doc",
        DESIGN,
        "--expected-base",
        digest(design).removeprefix("sha256:"),
        "--identity-map",
        str(mapping),
    )
    assert imported_design["local"] == "completed", imported_design
    state = _state(repo)
    design_review = next(
        key
        for key, record in state.domains["evidence"].document_reviews.items()
        if record.path == DESIGN
    )
    accepted_design = cli(
        topology.local,
        "design",
        "accept",
        *options,
        "--doc",
        DESIGN,
        "--review",
        design_review,
        "--identity-map",
        str(mapping),
    )
    assert accepted_design["local"] == "completed", accepted_design
    assert set(_state(repo).domains["lifecycle"].accepted_documents) == {
        "plan",
        "design",
    }

    tip = repo.tip().revision
    stale = cli(
        topology.local,
        "review",
        "import",
        str(tmp_path / "plan-review"),
        *options,
        "--doc",
        PLAN,
        "--expected-base",
        digest(plan_a).removeprefix("sha256:"),
        "--identity-map",
        str(mapping),
        "--record",
        plan_review,
    )
    assert stale["local"] == "conflict", stale
    assert repo.tip().revision == tip

    # Simulate generated metadata regeneration on the planning ref. The
    # ordinary authored sync intentionally does not own generated fields.
    metadata = plan_b.replace(
        b'"title": "Review"', b'"title": "Review", "updated": "2026-11-28T00:00:00Z"'
    )
    git(topology.planning, "pull", "-q", "--ff-only", "origin", PLANNING)
    generated = topology.advance_planning(PLAN, metadata)
    (topology.local / PLAN).write_bytes(metadata)
    original_acceptance = _state(repo).domains["lifecycle"].accepted_documents["plan"]
    repeated = cli(
        topology.local,
        "plan",
        "accept",
        *options,
        "--doc",
        PLAN,
        "--review",
        plan_review,
        "--identity-map",
        str(mapping),
    )
    assert repeated["local"] == "completed", repeated["evidence"]
    assert repo.tip().revision == generated
    assert (
        _state(repo).domains["lifecycle"].accepted_documents["plan"]
        == original_acceptance
    )

    policy_path = topology.code / ".aitm.toml"
    prior_policy = policy_path.read_bytes()
    changed_policy = prior_policy.replace(
        b'assurances = ["declared-manual"]',
        b'assurances = ["native-consensus-authority-unavailable"]',
        1,
    )
    assert changed_policy != prior_policy
    commit_file(topology.code, ".aitm.toml", changed_policy)
    git(topology.code, "push", "-q", "origin", f"HEAD:{DEFAULT}")
    source = tmp_path / "historical-manual"
    _review(source, DESIGN, "xpr", design, _document("design", "Historical output"))
    historical = cli(
        topology.local,
        "review",
        "import",
        str(source),
        *options,
        "--doc",
        DESIGN,
        "--expected-base",
        digest(design).removeprefix("sha256:"),
        "--identity-map",
        str(mapping),
    )
    assert historical["local"] == "completed", historical
    assert any(
        "without current acceptance eligibility" in e for e in historical["evidence"]
    )
    assert (topology.local / DESIGN).read_bytes() == design
    assert repo.read_blobs(repo.tip().tree, (DESIGN,))[DESIGN] == design
    historical_record = next(
        key
        for key, review in _state(repo).domains["evidence"].document_reviews.items()
        if review.path == DESIGN and key != design_review
    )
    refused = cli(
        topology.local,
        "design",
        "accept",
        *options,
        "--doc",
        DESIGN,
        "--review",
        historical_record,
        "--identity-map",
        str(mapping),
    )
    assert refused["local"] == "refused", refused
