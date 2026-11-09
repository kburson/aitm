import json
import stat
import subprocess
import sys
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from uuid import UUID

import pytest

from aitm_usage import ledger as store
from aitm_usage.ledger import ConflictError, Ledger, WriterActive
from aitm_usage.rollup import rollup
from aitm_usage.scopes import (
    BoundaryEvidence,
    drain_inbox,
    enqueue_command,
    enqueue_marker,
)
from aitm_usage.types import (
    Availability,
    BoundaryKind,
    ClientVersion,
    DraftAlias,
    InboxCommand,
    ItemKey,
    ItemKind,
    LedgerBatch,
    MarkerDisposition,
    Provider,
    ReviewRole,
    Revision,
    ScopeMarker,
    SourceBoundary,
    SourceRef,
    TokenCounts,
    UsageObservation,
    WorkPhase,
    decode_command,
    encode_command,
)

PROJECT = UUID(int=180)
EPIC = ItemKey(ItemKind.ISSUE, 83)
OTHER_EPIC = ItemKey(ItemKind.ISSUE, 90)
CHILD = ItemKey(ItemKind.ISSUE, 85)
SECOND = ItemKey(ItemKind.ISSUE, 86)
DRAFT = ItemKey(ItemKind.DRAFT, UUID(int=22))
NOW = datetime(2026, 11, 9, 16, tzinfo=UTC)


@pytest.fixture
def project(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "_control_root", lambda: tmp_path / "control")
    return Ledger.initialize(tmp_path / "unrelated local name", PROJECT)


@pytest.fixture
def item_cli(tmp_path):
    # Use the actual installed entry point in a second interpreter with
    # the same isolated project guard used by the test collector.
    runner = (
        "import runpy, sys; from pathlib import Path; from aitm_usage import ledger;"
        f"ledger._control_root = lambda: Path({str(tmp_path / 'control')!r});"
        "runpy.run_path(str(Path(sys.executable).with_name('aitm-usage')), run_name='__main__')"
    )

    def invoke(path, command, *args):
        return subprocess.run(
            [
                sys.executable,
                "-c",
                runner,
                "--project",
                str(path),
                "item",
                command,
                *args,
                "--json",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

    return invoke


def _consume(
    writer, item_cli, verb, first, second, expected=MarkerDisposition.ACCEPTED
):
    options = ("--draft", "--issue") if verb == "alias" else ("--child", "--epic")
    result = item_cli(
        writer.root,
        verb,
        options[0],
        str(first.identifier),
        options[1],
        str(second.identifier),
    )
    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)
    assert response["status"] == "queued"
    command_id = UUID(response["command_id"])
    inbox = writer.root / "inbox"
    path = inbox / f"{command_id}.json"
    assert stat.S_IMODE(inbox.stat().st_mode) == 0o700
    assert stat.S_IMODE(path.stat().st_mode) == 0o600
    command = decode_command(path.read_bytes())
    assert command.project_id == PROJECT
    assert command.command_id == command_id
    [receipt] = drain_inbox(writer, ()).receipts
    assert receipt.command == command
    assert receipt.disposition is expected
    ack = inbox / "acks" / path.name
    assert stat.S_IMODE(ack.stat().st_mode) == 0o600
    assert json.loads(ack.read_text()) == {
        "command_id": str(command_id),
        "digest": {"value": receipt.digest.value},
        "disposition": expected.value,
    }
    assert not path.exists()
    return receipt


def _record_usage(writer, item, output_tokens, *, review=False):
    def ref(label):
        return writer.pseudonymize("rollup-test", f"{output_tokens}:{label}")

    provider = Provider.CLAUDE if review else Provider.CODEX
    marker_id = UUID(int=output_tokens)
    boundary = SourceBoundary(
        provider,
        ref("stream"),
        ref("session"),
        1,
        BoundaryKind.REQUEST,
        ref("boundary"),
        receipt_ref=writer.pseudonymize("scope-receipt", str(marker_id)),
    )
    if item is not None:
        enqueue_marker(
            writer.root,
            ScopeMarker(
                marker_id,
                provider,
                boundary.session_ref,
                1,
                boundary.kind,
                boundary.boundary_ref,
                NOW,
                item,
                WorkPhase.DOCUMENT_REVIEW if review else WorkPhase.PLANNING,
                ref("participant"),
                PROJECT,
                role=ReviewRole.REVIEWER if review else None,
                receipt_ref=boundary.receipt_ref,
                review_ref=ref("review") if review else None,
            ),
        )
        [receipt] = drain_inbox(writer, (BoundaryEvidence(boundary),)).receipts
        assert receipt.disposition is MarkerDisposition.ACCEPTED
    revision = Revision(
        ref("observation"),
        1,
        UsageObservation(
            boundary,
            NOW,
            ClientVersion.UNKNOWN,
            1,
            TokenCounts(output_tokens=output_tokens),
            Availability.COMPLETE,
        ),
    )
    writer.apply(LedgerBatch((revision,)))
    return revision


def test_graduation_and_inclusive_rollup(project, item_cli):
    with project.writer() as writer:
        with pytest.raises(WriterActive), project.writer():
            pass
        _consume(writer, item_cli, "parent", DRAFT, EPIC)
        _consume(writer, item_cli, "parent", CHILD, EPIC)
        _consume(writer, item_cli, "parent", SECOND, EPIC)
        grandchild = ItemKey(ItemKind.ISSUE, 99)
        _consume(writer, item_cli, "parent", grandchild, SECOND)
        _record_usage(writer, grandchild, 3)
        _record_usage(writer, EPIC, 11)
        _record_usage(writer, DRAFT, 7)
        _record_usage(writer, SECOND, 13)
        _record_usage(writer, CHILD, 5, review=True)
        _record_usage(writer, None, 17)
        before = writer.as_of()
        receipt = _consume(writer, item_cli, "alias", DRAFT, CHILD)
        graduated = writer.as_of()
        assert enqueue_command(writer.root, receipt.command) == receipt
        assert writer.as_of().sequence == graduated.sequence

    assert rollup(DRAFT, before).direct.tokens == {"output_tokens": 7}
    assert rollup(CHILD, before).direct.tokens == {"output_tokens": 5}
    assert rollup(CHILD, graduated).direct.tokens == {"output_tokens": 12}
    assert rollup(DRAFT, graduated) == rollup(CHILD, graduated)
    second = rollup(SECOND, graduated)
    assert second.direct.tokens == {"output_tokens": 13}
    assert second.inclusive.tokens == {"output_tokens": 16}
    total = rollup(EPIC, graduated)
    assert total.direct.tokens == {"output_tokens": 11}
    assert total.inclusive.tokens == {"output_tokens": 39}
    assert total.inclusive.observation_count == 5
    assert total.unattributed.tokens == {"output_tokens": 17}

    reopened = Ledger.open(project.root, PROJECT)
    with reopened.writer() as writer:
        reparented = _consume(writer, item_cli, "parent", DRAFT, OTHER_EPIC)
        current = writer.as_of()
        assert enqueue_command(writer.root, reparented.command) == reparented
        assert writer.as_of() == current
    assert rollup(EPIC, reopened.as_of()).inclusive.tokens == {"output_tokens": 27}
    assert rollup(OTHER_EPIC, reopened.as_of()).inclusive.tokens == {
        "output_tokens": 12
    }
    assert rollup(EPIC, reopened.as_of(graduated.sequence)) == total
    assert rollup(DRAFT, reopened.as_of(before.sequence)).direct.tokens == {
        "output_tokens": 7
    }


def test_item_inbox_refuses_alias_conflicts_and_canonical_cycles(project, item_cli):
    with project.writer() as writer:
        _consume(writer, item_cli, "parent", DRAFT, EPIC)
        _consume(writer, item_cli, "parent", SECOND, OTHER_EPIC)
        _consume(writer, item_cli, "alias", DRAFT, SECOND, MarkerDisposition.CONFLICT)
        _consume(writer, item_cli, "parent", SECOND, CHILD)
        cycle_draft = ItemKey(ItemKind.DRAFT, UUID(int=23))
        _consume(writer, item_cli, "parent", CHILD, cycle_draft)
        # Only one alias endpoint has a parent. The alias would close a cycle.
        rejected = _consume(
            writer, item_cli, "alias", cycle_draft, SECOND, MarkerDisposition.CONFLICT
        )
        _consume(writer, item_cli, "parent", CHILD, DRAFT)
        accepted = _consume(writer, item_cli, "alias", DRAFT, OTHER_EPIC)

    reopened = Ledger.open(project.root, PROJECT)
    with reopened.writer() as writer:
        assert enqueue_command(writer.root, rejected.command) == rejected
        _consume(writer, item_cli, "alias", DRAFT, CHILD, MarkerDisposition.CONFLICT)
        _consume(writer, item_cli, "parent", EPIC, SECOND, MarkerDisposition.CONFLICT)
        _consume(
            writer, item_cli, "parent", DRAFT, OTHER_EPIC, MarkerDisposition.CONFLICT
        )
        # Exact command identity cannot acquire new bytes.
        changed = replace(
            accepted.command, payload=replace(accepted.command.payload, issue=CHILD)
        )
        with pytest.raises(ConflictError):
            enqueue_command(writer.root, changed)
        assert enqueue_command(writer.root, accepted.command) == accepted


def test_item_wire_envelope_is_closed_and_project_bound(project, item_cli):
    with project.writer() as writer:
        receipt = _consume(writer, item_cli, "alias", DRAFT, CHILD)
        command = receipt.command
        serialized = json.loads(encode_command(command))
        payload = serialized["payload"]["command"]
        payload["private_note"] = "raw-item-canary"
        with pytest.raises(ValueError):
            decode_command(json.dumps(serialized).encode())
        del payload["private_note"]
        payload["issue"]["identifier"] = True
        with pytest.raises(ValueError):
            decode_command(json.dumps(serialized).encode())
        foreign = UUID(int=999)
        with pytest.raises(ValueError):
            InboxCommand(
                command.command_id,
                PROJECT,
                replace(command.payload, project_id=foreign),
            )
        with pytest.raises(store.LedgerError):
            enqueue_command(
                writer.root,
                InboxCommand(
                    command.command_id,
                    foreign,
                    replace(command.payload, project_id=foreign),
                ),
            )
        with pytest.raises(ValueError):
            DraftAlias(command.command_id, PROJECT, CHILD, DRAFT)
    assert b"raw-item-canary" not in project.database_path.read_bytes()


@pytest.mark.parametrize(
    "defect",
    ["missing", "identity", "other-project", "schema", "sidecar", "guard", "key"],
)
def test_item_cli_refuses_untrusted_state(project, item_cli, tmp_path, defect):
    root = project.root
    if defect == "missing":
        root = tmp_path / "missing"
    elif defect in ("identity", "other-project", "schema"):
        with store._connection(project.database_path, write=True) as conn, conn:
            if defect == "schema":
                conn.execute("PRAGMA user_version = 999")
            else:
                stored = (
                    "private-identity-canary"
                    if defect == "identity"
                    else str(UUID(int=80))
                )
                conn.execute("UPDATE identity SET project_id = ?", (stored,))
    elif defect == "sidecar":
        Path(f"{project.database_path}-wal").chmod(0o644)
    elif defect == "guard":
        store._guard_path(root, PROJECT).unlink()
    else:
        project.key_path.write_bytes(PROJECT.bytes + b"x" * 32)
    result = item_cli(root, "alias", "--draft", str(DRAFT.identifier), "--issue", "85")
    assert result.returncode != 0
    assert result.stdout == ""
    assert "private-identity-canary" not in result.stderr
    assert str(root) not in result.stderr
    assert result.stderr == "aitm-usage: invalid private inbox command or project\n"
    assert not (root / "inbox").exists()
    if defect == "missing":
        assert not root.exists()


@dataclass(frozen=True, slots=True)
class _Price:
    observation_key: SourceRef
    observation_revision: int
    rate_basis: str
    usd: Decimal | None


def _priced_view(project, view, *prices):
    revisions = tuple(
        Revision(project.pseudonymize("price-test", str(index)), 1, price)
        for index, price in enumerate(prices)
    )
    return replace(
        view, sequence=view.sequence + 1, revisions=(*view.revisions, *revisions)
    )


def test_rollup_prices_only_current_observations_in_its_view(project, item_cli):
    with project.writer() as writer:
        _consume(writer, item_cli, "parent", DRAFT, EPIC)
        _consume(writer, item_cli, "alias", DRAFT, CHILD)
        request = _record_usage(writer, DRAFT, 17)
        unavailable = _record_usage(writer, CHILD, 19)
        older = writer.as_of()
        current = replace(
            request,
            revision=2,
            record=replace(
                request.record,
                tokens=TokenCounts(
                    input_tokens=0, output_tokens=23, reasoning_output_tokens=3
                ),
            ),
        )
        writer.apply(LedgerBatch((current,)))
        revised = writer.as_of()

    stale = _Price(request.key, 1, "v1", Decimal("0.006"))
    price = _Price(request.key, 2, "v1", Decimal("0.024"))
    wrong_key = _Price(
        project.pseudonymize("price-test", "absent"), 2, "v1", Decimal("15")
    )
    no_price = _Price(unavailable.key, 1, "v1", None)
    priced = _priced_view(project, revised, stale, price, wrong_key, no_price)
    with pytest.raises(ValueError):
        project.apply(LedgerBatch(priced.revisions[len(revised.revisions) :]))
    assert project.as_of() == revised
    totals = rollup(CHILD, priced).direct
    assert totals == rollup(EPIC, priced).inclusive
    assert totals.known_usd == Decimal("0.024")
    assert totals.unknown_price_count == 1
    assert totals.observation_count == 2
    assert totals.tokens == {
        "input_tokens": 0,
        "output_tokens": 42,
        "reasoning_output_tokens": 3,
    }
    assert rollup(EPIC, older).inclusive.tokens == {"output_tokens": 36}
    assert rollup(EPIC, older).inclusive.known_usd == Decimal(0)
    assert rollup(EPIC, revised).inclusive.unknown_price_count == 2

    mismatched = _priced_view(project, revised, stale, wrong_key, no_price)
    assert rollup(CHILD, mismatched).direct.unknown_price_count == 2
    for other in (replace(price, rate_basis="v2"), replace(price, usd=Decimal("0.03"))):
        ambiguous = rollup(CHILD, _priced_view(project, revised, price, other)).direct
        assert ambiguous.known_usd == Decimal(0)
        assert ambiguous.unknown_price_count == 2
        assert ambiguous.tokens == totals.tokens
    zero = replace(price, usd=Decimal(0))
    free = rollup(CHILD, _priced_view(project, revised, zero, zero)).direct
    assert free.known_usd == Decimal(0)
    assert free.unknown_price_count == 1
