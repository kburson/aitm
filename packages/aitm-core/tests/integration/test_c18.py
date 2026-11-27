"""Exercise pinned snapshot readback, WAL replacement and installed read commands."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from hashlib import sha256
from json import dumps, loads
from os import environ
from shlex import quote
from shutil import which
from sqlite3 import connect
from subprocess import run

from aitm_core.cli.read import handle
from aitm_core.description import DescriptionInput, DescriptionTarget, describe
from aitm_core.index.build import index_snapshot
from aitm_core.index.query import Query, query
from aitm_core.services import refresh
from tests.integration.test_c08 import PLANNING, git
from tests.integration.test_c08 import topology as topology
from tests.unit.test_c15 import DESCRIPTION, EVENTS, OWNER, POLICY, STAMP, graduated

IDEA = ".aitm/ideas/2026-11/idea.md"
DRAFT = ".aitm/drafts/2026-11/session/draft.md"


def seed(topology):
    initial = graduated()
    operation = describe(
        DescriptionTarget(
            16, {EVENTS: initial, DESCRIPTION: None}, OWNER, POLICY, "desc", STAMP
        ),
        DescriptionInput(
            title="Pinned orchard",
            actor="operator",
            want="deterministic readback",
            so_that="I can verify",
            scope="Select the pear snapshot.",
        ),
    )
    events = initial + operation.change.events[0].records[0] + b"\n"
    lesson = {
        "v": 1,
        "story": 16,
        "id": "first-lesson",
        "ts": STAMP,
        "type": "core.outcome.recorded",
        "actor": {"kind": "tool"},
        "operation_id": "outcome",
        "sequence": 3,
        "prior_log_digest": sha256(events).hexdigest(),
        "data": {
            "phase": "refine",
            "workflow": loads(initial)["data"]["initial_state"],
            "disposition": "refined",
            "actual_agent_hours": None,
            "qualification": "unknown",
            "lessons": ["Pineapple verification"],
            "proof_refs": [],
        },
    }
    events += dumps(lesson).encode() + b"\n"
    topology.advance_planning(EVENTS, events)
    topology.advance_planning(DESCRIPTION, operation.change.writes[0].content)
    topology.advance_planning(IDEA, b"# Lemon idea\n\nCitrus scouting.")
    topology.advance_planning(DRAFT, b"# Orange draft\n\nReview the proposal.")
    installation = topology.policy.installation
    assert refresh(installation).shared.status == "verified"
    return installation


def test_index_snapshot_is_atomic_with_exact_fallback(topology, tmp_path):
    installation = seed(topology)
    repo = installation.repository
    database = tmp_path / "index.sqlite"
    original = index_snapshot(repo.tip(), repository=repo, database=database)

    for search, kind in (
        ("orchard", "story"),
        ("pear", "story"),
        ("pineapple", "story"),
        ("citrus", "idea"),
        ("proposal", "draft"),
    ):
        indexed = query(original, Query(text=search))
        assert [item.kind for item in indexed.rows] == [kind]
        absent = replace(original, database=tmp_path / "absent" / "index.sqlite")
        assert query(absent, Query(text=search)).rows == indexed.rows

    corrupt = tmp_path / "corrupt.sqlite"
    corrupt.write_bytes(b"not a database")
    assert query(replace(original, database=corrupt), Query(text="lemon")).rows == (
        query(original, Query(text="lemon")).rows
    )
    connection = connect(database)
    try:
        assert connection.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
        connection.execute("BEGIN")
        assert (
            connection.execute("SELECT tree FROM metadata").fetchone()[0]
            == original.snapshot.tree
        )
        topology.advance_planning(IDEA, b"# Fig idea\n\nNew orchard notes.")
        assert refresh(installation).shared.status == "verified"
        with ThreadPoolExecutor(max_workers=1) as workers:
            new = workers.submit(
                index_snapshot, repo.tip(), repository=repo, database=database
            ).result()
        assert (
            connection.execute("SELECT tree FROM metadata").fetchone()[0]
            == original.snapshot.tree
        )
        assert query(original, Query(text="lemon")).rows
        assert not query(new, Query(text="lemon")).rows
        assert query(new, Query(text="fig")).rows
        old_wal = database.with_name(database.name + "-wal").read_bytes()
        stale_wal = corrupt.with_name(corrupt.name + "-wal")
        stale_wal.write_bytes(old_wal)
        rebuilt = index_snapshot(original.snapshot, repository=repo, database=corrupt)
        assert rebuilt.database != corrupt
        assert corrupt.read_bytes() == b"not a database"
        assert stale_wal.read_bytes() == old_wal
        with connect(rebuilt.database) as recovered:
            assert (
                recovered.execute("SELECT tree FROM metadata").fetchone()[0]
                == original.snapshot.tree
            )
        reopened = query(replace(new, database=corrupt), Query(text="fig"))
        assert (
            reopened.source == "index"
            and reopened.rows == query(new, Query(text="fig")).rows
        )
    finally:
        connection.close()

    index_snapshot(original.snapshot, repository=repo, database=database)
    writer = connect(database)
    try:
        writer.execute("BEGIN IMMEDIATE")
        locked = query(new, Query(text="fig"))
        assert locked.source == "tree"
        assert (
            locked.rows
            == query(
                replace(new, database=tmp_path / "missing" / "index.sqlite"),
                Query(text="fig"),
            ).rows
        )
    finally:
        writer.close()


def test_installed_queries_pin_freshness_without_transport(topology, tmp_path):
    installation = seed(topology)
    code = which("aitm")
    git_executable = which("git")
    assert code and git_executable
    anchor = tmp_path / "anchor.json"
    anchor.write_text(installation.store.model_dump_json())
    descriptor = tmp_path / "install.json"
    descriptor.write_text(
        dumps(
            {
                "code_repository": installation.code_repository,
                "planning_repository": installation.planning_repository,
                "bootstrap_source": installation.bootstrap_source,
                "issuer": installation.issuer.model_dump(),
                "code_remote": installation.code_remote,
                "code_remote_ref": installation.code_remote_ref,
            }
        )
    )
    shim = tmp_path / "shim"
    shim.mkdir()
    guard = shim / "git"
    log = tmp_path / "transport"
    guard.write_text(
        f"""#!/bin/sh
if [ "$3" = ls-remote ] || [ "$3" = push ]; then printf '%s\\n' "$3" >> {quote(str(log))}; fi
exec {quote(git_executable)} "$@"
"""
    )
    guard.chmod(0o755)
    model_calls = tmp_path / "model-calls"
    harness = shim / "codex"
    harness.write_text(
        f"#!/bin/sh\nprintf called > {quote(str(model_calls))}\nexit 1\n"
    )
    harness.chmod(0o755)
    env = dict(environ, PATH=f"{shim}:{environ['PATH']}")

    def invoke(*route):
        result = run(
            [
                code,
                "--json",
                *route,
                "--anchor",
                str(anchor),
                "--installation",
                str(descriptor),
            ],
            cwd=topology.local,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        return loads(result.stdout)

    rebuilt = invoke("index", "rebuild")
    assert rebuilt["local"] == "completed", rebuilt
    before = installation.repository.tip()
    for route in (("show", "16"), ("list",), ("search", "pear")):
        found = invoke(*route)
        assert found["local"] == "completed", found
        assert found["read"]["tree"] == before.tree
        assert found["read"]["rows"][0]["title"] == "Pinned orchard"
        assert found["read"]["commit"] == before.revision

    explained = invoke("explain", "16")
    assert explained["local"] == "unavailable"
    assert explained["read"]["tree"] == before.tree
    unregistered = handle(
        ("explain",),
        (
            "16",
            "--anchor",
            str(anchor),
            "--installation",
            str(descriptor),
            "--repository",
            str(topology.local),
        ),
        explanation=None,
    )
    assert unregistered.local == "unavailable"
    assert unregistered.read.tree == before.tree
    assert not unregistered.read.rows
    assert any("explanation" in line for line in explained["evidence"])
    discussed = invoke("discuss", "16")
    assert discussed["local"] == "completed"
    assert discussed["read"]["context"]["suggested_invocation"]
    assert "Pinned orchard" in discussed["read"]["context"]["title"]
    assert not log.exists()
    assert not model_calls.exists()
    assert git(topology.local, "rev-parse", PLANNING) == before.revision

    topology.advance_planning(IDEA, b"# Lime idea\n\nNext observed view.")
    updated = invoke("search", "lime", "--refresh")
    assert updated["local"] == "completed", updated
    assert updated["read"]["tree"] != before.tree
    assert log.read_text().splitlines() and set(log.read_text().splitlines()) == {
        "ls-remote"
    }

    shared = installation.repository.tip()
    unpublished = installation.repository.create_commit(
        shared, {IDEA: b"# Unpublished nectarine idea"}, "unpublished-idea"
    )
    git(topology.local, "update-ref", PLANNING, unpublished.revision, shared.revision)
    diverged = invoke("search", "nectarine", "--refresh")
    assert diverged["read"]["tree"] == unpublished.tree
    assert diverged["read"]["shared_freshness"] == "verified"
    assert diverged["read"]["shared_commit"] == shared.revision
    assert diverged["read"]["matches_shared_tip"] is False
