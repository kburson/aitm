"""C92 resolves only pinned, declared Markdown and never activates a provider."""

from hashlib import sha256
from types import SimpleNamespace

import pytest

from aitm_core.config import CommittedFile, PolicyUnavailable
from aitm_core.ext.api import (
    CapabilityScope,
    CapabilitySlot,
    DirectiveRegistration,
    Extension,
)
from aitm_core.ext.directives import (
    DirectiveSnapshot,
    DirectiveStatus,
    resolve_directive,
)
from aitm_core.ext.registry import load_extensions
from aitm_core.machine.profile import ProfileSource
from aitm_core.models.config import ExtensionConfig

PATH = ".aitm/directives/verify.md"
RULE = "fixture.directive.verify"
SOURCE = ProfileSource(
    path=".aitm/workflows/delivery.toml",
    revision="a" * 40,
    tree="b" * 40,
    digest="c" * 64,
)
RAW = b"# Verify candidate\r\n\r\nRetain exact evidence.\r\n"


def registry(*, enabled=True, kind="directive", path=PATH):
    def effect():
        raise AssertionError("directive read must never enter a provider")

    slot = CapabilitySlot(
        id=RULE,
        version=2,
        kind=kind,
        placements=("onExit",) if kind == "guard" else ("action",),
        execution="queued" if kind == "action" else None,
        scope=CapabilityScope(state_ids=("review",), story_kinds=("story",)),
    )
    extensions = ExtensionConfig(enabled=("fixture",) if enabled else ())
    policy = SimpleNamespace(config=SimpleNamespace(extensions=extensions))
    output = (
        {
            "directives": (
                DirectiveRegistration(
                    slot=slot,
                    markdown=path,
                    requested_evidence=("exact-ci", "reviewed-tree"),
                ),
            )
        }
        if kind == "directive"
        else {"capabilities": (slot,)}
    )
    manifest = Extension(
        name="fixture",
        namespace="fixture",
        version="0.1",
        requires_core=">=0.1,<0.2",
        cli_factory=effect,
        githost_factory=effect,
        backlog_factory=effect,
        **output,
    )
    return load_extensions(policy, (manifest,))


def test_enabled_directive_returns_exact_content_identity_and_scope():
    reads = []

    def file(tree, path):
        reads.append((tree, path))
        return CommittedFile(path, RAW)

    view = resolve_directive(
        registry(), DirectiveSnapshot(SOURCE, file), RULE, version=2
    )
    assert view.status is DirectiveStatus.AVAILABLE
    assert view.capability_id == RULE and view.version == 2
    assert view.scope.state_ids == ("review",)
    assert view.scope.story_kinds == ("story",)
    assert view.requested_evidence == ("exact-ci", "reviewed-tree")
    assert view.content.path == PATH
    assert view.content.revision == SOURCE.revision and view.content.tree == SOURCE.tree
    assert view.content.digest == sha256(RAW).hexdigest()
    assert view.content.markdown.encode() == RAW
    assert reads == [(SOURCE.tree, PATH)]


@pytest.mark.parametrize(
    ("options", "identifier", "version", "status"),
    [
        ({"enabled": False}, RULE, 2, DirectiveStatus.DISABLED),
        ({}, RULE, 1, DirectiveStatus.INCOMPATIBLE),
        ({}, "fixture.directive.missing", 2, DirectiveStatus.MISSING),
        ({"kind": "action"}, RULE, 2, DirectiveStatus.INCOMPATIBLE),
        ({"kind": "guard"}, RULE, 2, DirectiveStatus.INCOMPATIBLE),
    ],
    ids=("disabled-owner", "wrong-version", "missing-id", "action", "guard"),
)
def test_unavailable_registrations_never_read_content(
    options, identifier, version, status
):
    def prohibited(*_):
        raise AssertionError("unavailable directive should not read a file")

    view = resolve_directive(
        registry(**options),
        DirectiveSnapshot(SOURCE, prohibited),
        identifier,
        version=version,
    )
    assert view.status is status and view.reason
    assert view.content is None


@pytest.mark.parametrize(
    ("file", "reason"),
    [
        (None, "missing"),
        (CommittedFile(".aitm/directives/other.md", RAW), "path"),
        (CommittedFile(PATH, b"\xff"), "UTF-8"),
        (CommittedFile(PATH, None), "bytes"),
    ],
    ids=("missing-content", "foreign-path", "malformed-encoding", "non-byte-evidence"),
)
def test_read_failure_or_mismatched_evidence_stays_unavailable(file, reason):
    view = resolve_directive(
        registry(), DirectiveSnapshot(SOURCE, lambda *_: file), RULE
    )
    assert view.status is DirectiveStatus.UNAVAILABLE
    assert view.content is None and reason in view.reason


def test_pinned_file_error_remains_unavailable():
    def missing_from_tree(*_):
        raise PolicyUnavailable("regular file missing from pinned tree")

    result = resolve_directive(
        registry(), DirectiveSnapshot(SOURCE, missing_from_tree), RULE
    )
    assert result.status is DirectiveStatus.UNAVAILABLE
    assert "regular file missing" in result.reason


def test_nonnormalized_declared_path_does_not_reach_file_reader():
    def prohibited(*_):
        raise AssertionError("malformed declaration reached file reader")

    result = resolve_directive(
        registry(path=".aitm//directives/verify.md"),
        DirectiveSnapshot(SOURCE, prohibited),
        RULE,
    )
    assert result.status is DirectiveStatus.UNAVAILABLE
    assert result.content is None and "path" in result.reason
