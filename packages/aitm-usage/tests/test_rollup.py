import hashlib
import json
import os
import stat
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from decimal import Context, Decimal, Inexact, Rounded, localcontext
from pathlib import Path
from threading import Event, current_thread
from uuid import UUID

import pytest

from aitm_usage import accounting, pricing, scopes
from aitm_usage import ledger as store
from aitm_usage.ledger import ConflictError, Ledger, LedgerError, WriterActive
from aitm_usage.rollup import rollup
from aitm_usage.scopes import (
    BoundaryEvidence,
    drain_inbox,
    enqueue_command,
    enqueue_marker,
)
from aitm_usage.types import (
    AdapterResult,
    Availability,
    BoundaryKind,
    ClientVersion,
    CommandReceipt,
    DraftAlias,
    InboxCommand,
    ItemKey,
    ItemKind,
    ItemParent,
    LedgerBatch,
    MarkerDisposition,
    ModelLabel,
    ProcessingTier,
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
        "import os, runpy, sys; from pathlib import Path; from uuid import UUID;"
        "from aitm_usage import cli, ledger;"
        f"ledger._control_root = lambda: Path({str(tmp_path / 'control')!r});"
        "if_id = os.environ.get('AITM_TEST_COMMAND_ID');"
        "cli.uuid4 = (lambda: UUID(if_id)) if if_id else cli.uuid4;"
        "runpy.run_path(str(Path(sys.executable).with_name('aitm-usage')), run_name='__main__')"
    )

    def invoke(path, command, *args, command_id=None):
        env = dict(os.environ)
        if command_id is not None:
            env["AITM_TEST_COMMAND_ID"] = str(command_id)
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
            env=env,
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )

    return invoke


def _canonical_json(payload):
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()


def _queue_cli(writer, item_cli, verb, first, second, *, command_id=None):
    options = ("--draft", "--issue") if verb == "alias" else ("--child", "--epic")
    result = item_cli(
        writer.root,
        verb,
        options[0],
        str(first.identifier),
        options[1],
        str(second.identifier),
        command_id=command_id,
    )
    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)
    assert response["status"] == "queued"
    actual_id = UUID(response["command_id"])
    if command_id is not None:
        assert actual_id == command_id
    path = _publication_path(writer, actual_id)
    assert stat.S_IMODE(path.parent.stat().st_mode) == 0o700
    assert stat.S_IMODE(path.stat().st_mode) == 0o600
    transport = json.loads(path.read_bytes())
    command = decode_command(_canonical_json(transport["command"]))
    assert command.project_id == PROJECT
    assert command.command_id == actual_id
    return command


def _publication_path(ledger, command_id):
    return ledger.root / "inbox" / f"{command_id}.json"


def _consume(
    writer, item_cli, verb, first, second, expected=MarkerDisposition.ACCEPTED
):
    command = _queue_cli(writer, item_cli, verb, first, second)
    command_id = command.command_id
    path = _publication_path(writer, command_id)
    [receipt] = drain_inbox(writer, ()).receipts
    assert receipt.command == command
    assert receipt.disposition is expected
    ack = path.parent / "acks" / path.name
    assert stat.S_IMODE(ack.stat().st_mode) == 0o600
    assert json.loads(ack.read_text()) == {
        "command_id": str(command_id),
        "digest": {"value": receipt.digest.value},
        "disposition": expected.value,
    }
    assert not path.exists()
    return receipt


def _usage_fixture(writer, item, output_tokens, *, review=False):
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
    marker = (
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
        )
        if item is not None
        else None
    )
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
    return marker, BoundaryEvidence(boundary), revision


def _record_usage(writer, item, output_tokens, *, review=False):
    marker, proof, revision = _usage_fixture(writer, item, output_tokens, review=review)
    if marker is not None:
        enqueue_marker(writer.root, marker)
        [receipt] = drain_inbox(writer, (proof,)).receipts
        assert receipt.disposition is MarkerDisposition.ACCEPTED
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


@pytest.mark.parametrize(
    ("context", "wide", "direct", "inclusive"),
    [
        (Context(prec=2), False, "0.0228", "0.0342"),
        (
            Context(prec=28),
            True,
            "91311303126417235628.2686107870208",
            "91311303126417235628.2800107870208",
        ),
        (
            Context(prec=2, Emin=-1, Emax=1, traps=[Inexact, Rounded]),
            True,
            "91311303126417235628.2686107870208",
            "91311303126417235628.2800107870208",
        ),
    ],
    ids=("ordinary-low-precision", "wide-default-precision", "wide-restricted-context"),
)
def test_rollup_sums_durable_prices_exactly(
    project, item_cli, context, wide, direct, inclusive
):
    standard = pricing.load_rate_card()
    astra = next(row for row in standard.entries if row.model is ModelLabel.GPT_6_ASTRA)
    custom = replace(
        standard,
        codex_long_context=replace(
            standard.codex_long_context, input_multiplier=Decimal("9.9")
        ),
        entries=(replace(astra, uncached_input=Decimal("999999.123456")),),
    )
    with project.writer() as writer:
        _consume(writer, item_cli, "parent", DRAFT, EPIC)
        _consume(writer, item_cli, "alias", DRAFT, CHILD)
        boundaries = []
        for index, (item, long_request) in enumerate(
            ((EPIC, wide), (EPIC, False), (DRAFT, False), (None, wide), (None, False)),
            start=1,
        ):
            marker, evidence, observation = _usage_fixture(writer, item, index)
            if marker is not None:
                enqueue_marker(writer.root, marker)
                boundaries.append(evidence)
            counts = (
                TokenCounts(2**63 - 1, 0, 0, 0, 0)
                if long_request
                else TokenCounts(500, 400, 0, 0, 200)
            )
            observed = replace(
                observation.record,
                tokens=counts,
                context_tokens=counts.input_tokens,
                model=ModelLabel.GPT_6_ASTRA,
                processing_tier=ProcessingTier.STANDARD,
            )
            batch = AdapterResult((replace(observation, record=observed),))
            writer.apply(
                accounting.account_observations(
                    batch, custom if long_request else standard, ledger=writer
                )
            )
        assert len(drain_inbox(writer, boundaries).receipts) == 3

    view = Ledger.open(project.root, PROJECT).as_of()
    reordered = replace(view, revisions=view.revisions[::-1])
    with localcontext(context):
        totals = rollup(EPIC, view)
        assert rollup(EPIC, reordered) == totals
    assert totals.direct.known_usd == Decimal(direct)
    assert totals.inclusive.known_usd == Decimal(inclusive)
    assert totals.unattributed.known_usd == Decimal(direct)
    for subtotal, count in (
        (totals.direct, 2),
        (totals.inclusive, 3),
        (totals.unattributed, 2),
    ):
        assert subtotal.observation_count == count
        assert subtotal.unknown_price_count == 0


def _command(payload):
    return InboxCommand(payload.command_id, payload.project_id, payload)


def _durable_bytes(project):
    return tuple(
        path.read_bytes()
        for path in (project.database_path, Path(f"{project.database_path}-wal"))
    )


@pytest.mark.parametrize("project_id", [PROJECT, UUID(int=912)])
@pytest.mark.parametrize("relation", ["alias", "parent"])
def test_public_batch_refuses_unreceipted_relationship(project, project_id, relation):
    with project.writer() as writer:
        _record_usage(writer, DRAFT, 7)
        before = writer.as_of()
        prior_bytes = _durable_bytes(project)
        if relation == "alias":
            record = DraftAlias(UUID(int=100), project_id, DRAFT, CHILD)
        else:
            record = ItemParent(UUID(int=100), project_id, DRAFT, EPIC)
        revision = Revision(writer.pseudonymize("fixture", relation), 1, record)
        with pytest.raises((LedgerError, ValueError)):
            writer.apply(LedgerBatch((revision,)))
        assert _durable_bytes(project) == prior_bytes
        assert writer.as_of() == before
        assert rollup(EPIC, writer.as_of()) == rollup(EPIC, before)
        assert rollup(CHILD, writer.as_of()) == rollup(CHILD, before)
        assert (
            writer.command_receipt(_command(replace(record, project_id=PROJECT)))
            is None
        )


@pytest.mark.parametrize(
    "defect",
    [
        "project",
        "command-project",
        "command-id",
        "command-type",
        "other-command",
        "alias-value",
        "parent-value",
        "revision-key",
        "revision-number",
        "canonical-child",
        "incomplete-effect-tuple",
        "invalid-graph",
        "false-rejection",
        "pending",
        "unexpected-boundary",
    ],
)
def test_guarded_commit_requires_exact_relationship_decision(project, item_cli, defect):
    with project.writer() as writer:
        _record_usage(writer, DRAFT, 7)
        alias = DraftAlias(UUID(int=100), PROJECT, DRAFT, CHILD)
        payload = alias
        alias_key = writer.pseudonymize("item-alias", str(DRAFT.identifier))
        effect = Revision(alias_key, 1, alias)
        status = MarkerDisposition.ACCEPTED
        boundary = None
        if defect == "project":
            effect = replace(effect, record=replace(alias, project_id=UUID(int=912)))
        elif defect == "command-project":
            payload = replace(alias, project_id=UUID(int=912))
        elif defect == "command-id":
            effect = replace(effect, record=replace(alias, command_id=UUID(int=999)))
        elif defect == "command-type":
            payload = ItemParent(alias.command_id, PROJECT, DRAFT, EPIC)
        elif defect == "alias-value":
            effect = replace(effect, record=replace(alias, issue=SECOND))
        elif defect == "parent-value":
            payload = ItemParent(alias.command_id, PROJECT, CHILD, EPIC)
            key = writer.pseudonymize("item-parent", "issue:85")
            effect = Revision(key, 1, replace(payload, parent=OTHER_EPIC))
        elif defect == "revision-key":
            effect = replace(effect, key=writer.pseudonymize("wrong", "alias"))
        elif defect == "revision-number":
            effect = replace(effect, revision=2)
        elif defect == "canonical-child":
            _consume(writer, item_cli, "alias", DRAFT, CHILD)
            payload = ItemParent(alias.command_id, PROJECT, DRAFT, EPIC)
            key = writer.pseudonymize("item-parent", "issue:85")
            effect = Revision(key, 1, payload)
        elif defect == "incomplete-effect-tuple":
            _consume(writer, item_cli, "parent", DRAFT, EPIC)
            _consume(writer, item_cli, "parent", CHILD, EPIC)
            _consume(writer, item_cli, "alias", DRAFT, CHILD)
            payload = ItemParent(alias.command_id, PROJECT, DRAFT, OTHER_EPIC)
            key = writer.pseudonymize("item-parent", f"draft:{DRAFT.identifier}")
            effect = Revision(key, 2, payload)
        elif defect == "invalid-graph":
            payload = ItemParent(alias.command_id, PROJECT, EPIC, EPIC)
            key = writer.pseudonymize("item-parent", "issue:83")
            effect = Revision(key, 1, payload)
        elif defect == "false-rejection":
            status = MarkerDisposition.CONFLICT
        elif defect == "pending":
            status = MarkerDisposition.PENDING
        elif defect == "unexpected-boundary":
            _, evidence, _ = _usage_fixture(writer, CHILD, 19)
            boundary = evidence.boundary

        command = _command(payload)
        if defect == "other-command":
            marker, _, _ = _usage_fixture(writer, CHILD, 19)
            command = InboxCommand(marker.marker_id, PROJECT, marker)
        before = writer.as_of()
        prior_bytes = _durable_bytes(project)
        prior_rollup = rollup(EPIC, before)
        effects = (effect,) if status is MarkerDisposition.ACCEPTED else ()
        if defect == "command-project":
            with pytest.raises(LedgerError):
                writer.commit_command(
                    CommandReceipt(
                        command, writer.validate_command(_command(alias)), status
                    ),
                    effects,
                    expected_sequence=before.sequence,
                )
        else:
            receipt = CommandReceipt(
                command, writer.validate_command(command), status, boundary
            )
            with pytest.raises((LedgerError, ValueError)):
                writer.commit_command(
                    receipt, effects, expected_sequence=before.sequence
                )
            assert writer.command_receipt(command) is None
        assert _durable_bytes(project) == prior_bytes
        assert writer.as_of() == before
        assert rollup(EPIC, writer.as_of()) == prior_rollup


def test_final_relationship_replay_checks_effect_identity_without_revalidating_graph(
    project, item_cli
):
    with project.writer() as writer:
        accepted = _consume(writer, item_cli, "parent", CHILD, EPIC)
        _consume(writer, item_cli, "parent", CHILD, OTHER_EPIC)
        original = Revision(
            writer.pseudonymize("item-parent", "issue:85"), 1, accepted.command.payload
        )
        before = writer.as_of()
        assert (
            writer.commit_command(accepted, (original,), expected_sequence=0)
            == accepted
        )
        forged = replace(
            original, record=replace(original.record, command_id=UUID(int=999))
        )
        with pytest.raises((LedgerError, ValueError)):
            writer.commit_command(accepted, (forged,), expected_sequence=0)
        assert writer.as_of() == before


def _conflicting_links(writer, item_cli):
    _consume(writer, item_cli, "parent", DRAFT, EPIC)
    _consume(writer, item_cli, "parent", CHILD, OTHER_EPIC)


def test_relationship_cli_drains_in_publication_order(project, item_cli):
    with project.writer() as writer:
        _conflicting_links(writer, item_cli)
        _record_usage(writer, DRAFT, 7)
        before = writer.as_of()
        first = _queue_cli(
            writer, item_cli, "parent", CHILD, EPIC, command_id=UUID(int=300)
        )
        alias = _queue_cli(
            writer, item_cli, "alias", DRAFT, CHILD, command_id=UUID(int=100)
        )
        first_path = _publication_path(writer, first.command_id)
        original = first_path.read_bytes()
        assert enqueue_command(writer.root, first) is None
        assert first_path.read_bytes() == original
        changed = replace(first, payload=replace(first.payload, parent=OTHER_EPIC))
        with pytest.raises(ConflictError):
            enqueue_command(writer.root, changed)
        assert first_path.read_bytes() == original

        results = drain_inbox(writer, ()).receipts
        assert [(r.command, r.disposition) for r in results] == [
            (first, MarkerDisposition.ACCEPTED),
            (alias, MarkerDisposition.ACCEPTED),
        ]
        for receipt in results:
            canonical = encode_command(receipt.command)
            assert (
                receipt.digest.value
                == "sha256:" + hashlib.sha256(canonical).hexdigest()
            )
        after_alias = writer.as_of()
        assert rollup(CHILD, after_alias).direct.tokens == {"output_tokens": 7}
        assert rollup(CHILD, writer.as_of(before.sequence)).direct.tokens == {}

        earlier = _queue_cli(
            writer, item_cli, "parent", CHILD, OTHER_EPIC, command_id=UUID(int=400)
        )
        later = _queue_cli(
            writer, item_cli, "parent", CHILD, EPIC, command_id=UUID(int=200)
        )
        results = drain_inbox(writer, ()).receipts
        assert [r.command for r in results] == [earlier, later]
        assert rollup(
            OTHER_EPIC, writer.as_of(after_alias.sequence + 1)
        ).inclusive.tokens == {"output_tokens": 7}
        assert rollup(EPIC, writer.as_of()).inclusive.tokens == {"output_tokens": 7}
        assert rollup(EPIC, writer.as_of(after_alias.sequence)) == rollup(
            EPIC, after_alias
        )


def test_failed_relationship_commit_leaves_later_commands_uncommitted(
    project, item_cli, monkeypatch
):
    with project.writer() as writer:
        _conflicting_links(writer, item_cli)
        first = _queue_cli(
            writer, item_cli, "parent", CHILD, EPIC, command_id=UUID(int=300)
        )
        second = _queue_cli(
            writer, item_cli, "alias", DRAFT, CHILD, command_id=UUID(int=100)
        )
        prior = writer.as_of()
        append = store._append_revisions

        def interrupt_first(conn, sequence, revisions):
            if revisions[-1].record.command == first:
                append(conn, sequence, revisions[:1])
                raise OSError("controlled relationship append failure")
            return append(conn, sequence, revisions)

        with monkeypatch.context() as patch:
            patch.setattr(store, "_append_revisions", interrupt_first)
            with pytest.raises(OSError, match="controlled relationship append failure"):
                drain_inbox(writer, ())
        assert writer.as_of() == prior
        for command in (first, second):
            assert writer.command_receipt(command) is None
            assert _publication_path(writer, command.command_id).is_file()

    with Ledger.open(project.root, PROJECT).writer() as writer:
        result = drain_inbox(writer, ()).receipts
        assert [(receipt.command, receipt.disposition) for receipt in result] == [
            (first, MarkerDisposition.ACCEPTED),
            (second, MarkerDisposition.ACCEPTED),
        ]


def test_relationship_conflict_is_final_and_does_not_block_next(project, item_cli):
    with project.writer() as writer:
        _conflicting_links(writer, item_cli)
        alias = _queue_cli(
            writer, item_cli, "alias", DRAFT, CHILD, command_id=UUID(int=300)
        )
        repair = _queue_cli(
            writer, item_cli, "parent", CHILD, EPIC, command_id=UUID(int=100)
        )
        prior = writer.as_of()
        rejected, accepted = drain_inbox(writer, ()).receipts
        assert (
            rejected.command == alias
            and rejected.disposition is MarkerDisposition.CONFLICT
        )
        assert (
            accepted.command == repair
            and accepted.disposition is MarkerDisposition.ACCEPTED
        )
        current = writer.as_of()
        assert (
            writer.commit_command(rejected, (), expected_sequence=prior.sequence)
            == rejected
        )
        assert enqueue_command(writer.root, alias) == rejected
        assert writer.as_of() == current


def test_relationship_snapshot_releases_mutex_and_preserves_order_after_restart(
    project, item_cli, monkeypatch
):
    with project.writer() as writer:
        first = _queue_cli(
            writer, item_cli, "parent", CHILD, EPIC, command_id=UUID(int=500)
        )
        second = _queue_cli(
            writer, item_cli, "parent", CHILD, OTHER_EPIC, command_id=UUID(int=400)
        )
        third = _command(ItemParent(UUID(int=300), PROJECT, CHILD, EPIC))
        first_path = _publication_path(writer, first.command_id)
        second_path = _publication_path(writer, second.command_id)
        read = scopes._read_publications
        lock = scopes._publication
        acknowledge = scopes._acknowledge
        owner = current_thread()
        publisher_started = Event()
        publisher_locked = Event()
        owner_locked = Event()
        submitted = []

        @contextmanager
        def observe_lock(inbox):
            if current_thread() is not owner:
                publisher_started.set()
            with lock(inbox):
                if current_thread() is not owner:
                    publisher_locked.set()
                    yield
                else:
                    owner_locked.set()
                    try:
                        yield
                    finally:
                        owner_locked.clear()

        def capture_snapshot(inbox, ledger):
            if current_thread() is owner and not submitted:
                assert owner_locked.is_set()
                submitted.append(pool.submit(enqueue_command, writer.root, third))
                assert publisher_started.wait(timeout=5)
                assert not publisher_locked.is_set()
            return read(inbox, ledger)

        def interrupt_before_retirement(inbox, acks, receipt, *args):
            assert not owner_locked.is_set()
            assert submitted[0].result(timeout=5) is None
            if receipt.command == second:
                assert not first_path.exists()
                fourth = _queue_cli(
                    writer,
                    item_cli,
                    "parent",
                    CHILD,
                    OTHER_EPIC,
                    command_id=UUID(int=200),
                )
                submitted.append(fourth)
                raise OSError("controlled relationship retirement interruption")
            return acknowledge(inbox, acks, receipt, *args)

        with ThreadPoolExecutor(max_workers=1) as pool, monkeypatch.context() as patch:
            patch.setattr(scopes, "_publication", observe_lock)
            patch.setattr(scopes, "_read_publications", capture_snapshot)
            patch.setattr(scopes, "_acknowledge", interrupt_before_retirement)
            with pytest.raises(
                OSError, match="controlled relationship retirement interruption"
            ):
                drain_inbox(writer, ())
        fourth = submitted[1]
        second_receipt = writer.command_receipt(second)
        assert second_receipt.disposition is MarkerDisposition.ACCEPTED
        assert not first_path.exists() and second_path.exists()
        assert writer.command_receipt(third) is None
        assert writer.command_receipt(fourth) is None
        for command, order in ((second, 2), (third, 3), (fourth, 4)):
            transport = json.loads(
                _publication_path(writer, command.command_id).read_bytes()
            )
            assert transport == {
                "order": order,
                "command": json.loads(encode_command(command)),
            }

    with Ledger.open(project.root, PROJECT).writer() as writer:
        fifth = _command(ItemParent(UUID(int=100), PROJECT, CHILD, EPIC))
        last_name = _publication_path(writer, fourth.command_id).name
        unlink = os.unlink
        submitted.clear()
        publisher_started.clear()
        publisher_locked.clear()

        def publish_during_last_retirement(name, *, dir_fd=None):
            if current_thread() is owner and name == last_name:
                assert owner_locked.is_set()
                submitted.append(pool.submit(enqueue_command, writer.root, fifth))
                assert publisher_started.wait(timeout=5)
                assert not publisher_locked.is_set()
            return unlink(name, dir_fd=dir_fd)

        with ThreadPoolExecutor(max_workers=1) as pool, monkeypatch.context() as patch:
            patch.setattr(scopes, "_publication", observe_lock)
            patch.setattr(scopes.os, "unlink", publish_during_last_retirement)
            restart = drain_inbox(writer, ()).receipts
            assert submitted[0].result(timeout=5) is None
        assert [r.command for r in restart] == [second, third, fourth]
        assert restart[0] == second_receipt
        assert all(r.disposition is MarkerDisposition.ACCEPTED for r in restart)
        assert writer.command_receipt(fifth) is None
        assert (
            json.loads(_publication_path(writer, fifth.command_id).read_bytes())[
                "order"
            ]
            == 1
        )
        assert drain_inbox(writer, ()).receipts[0].command == fifth


@pytest.mark.parametrize(
    "defect", ["duplicate", "malformed", "missing", "unclassifiable"]
)
def test_invalid_relationship_order_halts_only_relationships(project, item_cli, defect):
    with project.writer() as writer:
        first = _queue_cli(writer, item_cli, "parent", CHILD, EPIC)
        second = _queue_cli(writer, item_cli, "parent", CHILD, OTHER_EPIC)
        third = _queue_cli(writer, item_cli, "alias", DRAFT, CHILD)
        path = _publication_path(writer, second.command_id)
        transport = {"command": json.loads(encode_command(second)), "order": 2}
        if defect == "duplicate":
            damaged = _canonical_json({**transport, "order": 1})
        elif defect == "malformed":
            damaged = _canonical_json({**transport, "order": True})
        elif defect == "missing":
            damaged = encode_command(second)
        else:
            damaged = b"unclassifiable-private-canary"
        path.write_bytes(damaged)
        marker, proof, _ = _usage_fixture(writer, EPIC, 7)
        enqueue_marker(writer.root, marker)
        marker_path = _publication_path(writer, marker.marker_id)
        assert marker_path.read_bytes() == encode_command(
            InboxCommand(marker.marker_id, PROJECT, marker)
        )

        report = drain_inbox(writer, (proof,))
        assert report.relationship_halted
        assert report.invalid_publications >= 1
        assert "unclassifiable-private-canary" not in repr(report)
        assert [(r.command.command_id, r.disposition) for r in report.receipts] == [
            (marker.marker_id, MarkerDisposition.ACCEPTED),
        ]
        for command in (first, second, third):
            assert writer.command_receipt(command) is None
            assert _publication_path(writer, command.command_id).exists()


def test_retirement_compares_the_complete_captured_transport(
    project, item_cli, monkeypatch
):
    with project.writer() as writer:
        command = _queue_cli(writer, item_cli, "parent", CHILD, EPIC)
        path = _publication_path(writer, command.command_id)
        original = path.read_bytes()
        commit = Ledger.commit_command
        replacement = _canonical_json(
            {"command": json.loads(encode_command(command)), "order": 2}
        )

        def change_order_after_commit(ledger, *args, **kwargs):
            receipt = commit(ledger, *args, **kwargs)
            path.write_bytes(replacement)
            return receipt

        with monkeypatch.context() as patch:
            patch.setattr(Ledger, "commit_command", change_order_after_commit)
            with pytest.raises(ConflictError):
                drain_inbox(writer, ())
        assert path.read_bytes() == replacement
        assert not (path.parent / "acks" / path.name).exists()
        view = writer.as_of()
        receipt = writer.command_receipt(command)
        assert receipt.disposition is MarkerDisposition.ACCEPTED
        path.write_bytes(original)
        assert drain_inbox(writer, ()).receipts == (receipt,)
        assert writer.as_of() == view
        assert not path.exists()
