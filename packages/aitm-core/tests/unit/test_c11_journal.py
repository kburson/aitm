"""Recover durable installation intent without Git, a shell or a network."""

from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from aitm_core.setup.journal import BootstrapProposal, prepare_file


@pytest.fixture
def journal():
    return {
        "schema_version": "aitm.bootstrap/v1",
        "operation_id": "a" * 32,
        "anchor": {
            "store_uuid": "store",
            "code_default_ref": "refs/heads/trunk",
            "planning_ref": "refs/heads/project/records",
            "planning_remote": None,
            "root_commit": "a" * 40,
        },
        "initial_tip": "b" * 40,
        "code_repository": "code",
        "planning_repository": "records",
        "issuer": {
            "backlog": "local",
            "backlog_repository": "backlog",
            "numbering_namespace": "numbers",
        },
        "config": "[store]\n",
        "workflow": "[lifecycle]\n",
        "code_remote": None,
        "activated_revision": None,
        "replacement": None,
    }


def test_proposal_round_trip_keeps_exact_bytes_and_coordinates(journal):
    proposal = BootstrapProposal.model_validate(journal)
    recovered = BootstrapProposal.model_validate_json(proposal.model_dump_json())
    assert recovered.model_dump() == journal


@pytest.mark.parametrize(
    "field",
    [
        "operation_id",
        "anchor",
        "initial_tip",
        "code_repository",
        "planning_repository",
        "issuer",
        "config",
        "workflow",
    ],
)
def test_proposal_cannot_resume_with_a_required_field_missing(journal, field):
    del journal[field]
    with pytest.raises(ValidationError, match=field):
        BootstrapProposal.model_validate(journal)


@pytest.mark.parametrize(
    ("field", "content"),
    [
        ("schema_version", "aitm.bootstrap/v2"),
        ("operation_id", 12),
        ("operation_id", ""),
        ("operation_id", "x" * 32),
        ("initial_tip", "c" * 39),
        ("initial_tip", "c" * 41),
        ("initial_tip", "C" * 40),
        ("initial_tip", "z" * 40),
        ("code_repository", ""),
        ("planning_repository", " "),
        ("config", ""),
        ("workflow", " "),
        ("config", ["[store]"]),
        ("workflow", {}),
        ("extra", "unrecognized"),
    ],
)
def test_proposal_rejects_damaged_or_unknown_fields(journal, field, content):
    journal[field] = content
    with pytest.raises(ValidationError, match=field):
        BootstrapProposal.model_validate(journal)


def test_proposal_preserves_sha256_object_format(journal):
    journal["initial_tip"] = "b" * 64
    journal["anchor"]["root_commit"] = "a" * 64
    proposal = BootstrapProposal.model_validate(journal)
    assert proposal.initial_tip == "b" * 64
    assert proposal.anchor.root_commit == "a" * 64


def test_prepare_file_is_idempotent_and_never_leaves_a_temporary_peer(tmp_path):
    target = tmp_path / "policy"
    prepare_file(target, b"exact\n")
    prepare_file(target, b"exact\n")
    assert sorted(tmp_path.iterdir()) == [target]
    assert target.read_bytes() == b"exact\n"


@pytest.mark.parametrize("kind", ["file", "directory", "symlink", "dangling-symlink"])
def test_prepare_file_preserves_a_foreign_destination(tmp_path, kind):
    target = tmp_path / "policy"
    foreign = tmp_path / "foreign"
    if kind == "file":
        target.write_bytes(b"foreign")
    elif kind == "directory":
        target.mkdir()
    else:
        if kind == "symlink":
            foreign.write_bytes(b"exact")
        target.symlink_to(foreign)
    original = SimpleNamespace(stat=target.lstat(), entries=sorted(tmp_path.iterdir()))
    with pytest.raises(ValueError, match="differs from the proposal"):
        prepare_file(target, b"exact")
    assert target.lstat() == original.stat
    assert sorted(tmp_path.iterdir()) == original.entries


@pytest.mark.parametrize(
    ("slot", "method"),
    [
        ("init_hooks", "install"),
        ("init_doctor", "check"),
        ("init_provider", "initialize"),
    ],
)
@pytest.mark.parametrize("registered", [False, True])
def test_init_reports_each_readiness_step_explicitly(slot, method, registered):
    from aitm_core.services import ServicePorts
    from aitm_core.setup.init import _readiness

    calls = []
    context = SimpleNamespace(store=SimpleNamespace(planning_remote=None))

    def perform(received):
        calls.append(received)
        return (f"observed:{slot}",)

    provider = SimpleNamespace(**{method: perform})
    ports = ServicePorts(**{slot: provider if registered else None})
    messages, pending = _readiness(context, ports)
    if registered:
        assert calls == [context]
        assert f"observed:{slot}" in messages
        assert slot not in pending
    else:
        assert calls == []
        assert f"observed:{slot}" not in messages
        assert slot in pending


@pytest.mark.parametrize(
    "slot", ["init_hooks", "init_doctor", "init_provider", "init_git_host"]
)
def test_init_readiness_ports_distinguish_unavailable_from_registered(slot):
    from aitm_core.services import ServicePorts, UnavailablePort

    with pytest.raises(UnavailablePort, match=slot):
        ServicePorts().require(slot)
    supplied = object()
    assert ServicePorts(**{slot: supplied}).require(slot) is supplied


@pytest.mark.parametrize(
    "record",
    [
        None,
        b"",
        b"[]",
        b"{}",
        b'{"schema":"aitm.store/v2","store_uuid":"original"}',
        b'{"schema":"aitm.store/v1","store_uuid":"foreign"}',
        b'{"schema":"aitm.store/v1","store_uuid":"original","root_commit":"foreign"}',
        b'{"schema":"aitm.store/v1","store_uuid":"original","root_commit":null}',
        b'{"schema":"aitm.store/v1","store_uuid":"original","store_uuid":"foreign"}',
    ],
)
def test_store_identity_refuses_missing_or_foreign_metadata(record):
    from aitm_core.setup.init import _check_store_identity

    anchor = SimpleNamespace(store_uuid="original", root_commit="root")
    with pytest.raises(ValueError, match="Planning store"):
        _check_store_identity(anchor, record)


@pytest.mark.parametrize("include_root", [False, True])
def test_store_identity_accepts_metadata_bound_to_the_trusted_history(include_root):
    from json import dumps

    from aitm_core.setup.init import _check_store_identity

    anchor = SimpleNamespace(store_uuid="original", root_commit="root")
    record = {"schema": "aitm.store/v1", "store_uuid": anchor.store_uuid}
    if include_root:
        record["root_commit"] = anchor.root_commit
    _check_store_identity(anchor, dumps(record).encode())
