"""Validate item relationships against typed, read-only ledger evidence."""

from collections.abc import Callable, Iterable
from dataclasses import replace

from .types import (
    DraftAlias,
    ItemKey,
    ItemParent,
    LedgerView,
    MarkerDisposition,
    Revision,
    SourceRef,
)


class _RelationshipConflict(ValueError):
    """A proposal would leave contradictory relationships or a cycle."""


def _relationships(
    view: LedgerView,
) -> tuple[dict[ItemKey, ItemKey], dict[ItemKey, tuple[Revision, ItemParent]]]:
    aliases = {}
    links = {}
    for revision in view.current:
        record = revision.record
        if isinstance(record, DraftAlias) and record.project_id == view.project_id:
            aliases[record.draft] = record.issue
        elif isinstance(record, ItemParent) and record.project_id == view.project_id:
            links[record.child] = (revision, record)
    return aliases, links


def _canonical_parents(
    aliases: dict[ItemKey, ItemKey], links: Iterable[ItemParent]
) -> dict[ItemKey, ItemKey]:
    parents = {}
    for link in links:
        child = aliases.get(link.child, link.child)
        parent = aliases.get(link.parent, link.parent)
        if parents.setdefault(child, parent) != parent:
            raise _RelationshipConflict("Canonical item has contradictory parents")
    return parents


def _check_cycles(parents: dict[ItemKey, ItemKey]) -> None:
    visited = set()
    for child in parents:
        path = set()
        while child in parents and child not in visited:
            if child in path:
                raise _RelationshipConflict("Canonical item ancestry contains a cycle")
            path.add(child)
            child = parents[child]
        visited.update(path)


def canonical_relationships(
    view: LedgerView,
) -> tuple[dict[ItemKey, ItemKey], dict[ItemKey, ItemKey]]:
    """Project the canonical alias and parent maps from one snapshot."""
    aliases, links = _relationships(view)
    parents = _canonical_parents(aliases, (record for _, record in links.values()))
    _check_cycles(parents)
    return aliases, parents


def _relationship_effects(
    payload: DraftAlias | ItemParent,
    view: LedgerView,
    derive_ref: Callable[[str, str], SourceRef],
) -> tuple[Revision, ...]:
    aliases, links = _relationships(view)
    if isinstance(payload, DraftAlias):
        prior = aliases.get(payload.draft)
        if prior is not None and prior != payload.issue:
            raise _RelationshipConflict("Draft already has a different permanent issue")
        aliases[payload.draft] = payload.issue
        parents = _canonical_parents(aliases, (record for _, record in links.values()))
        _check_cycles(parents)
        key = derive_ref("item-alias", str(payload.draft.identifier))
        existing = next((entry for entry in view.current if entry.key == key), None)
        number = 1 if existing is None else existing.revision + 1
        return (Revision(key, number, payload),)

    child = aliases.get(payload.child, payload.child)
    parent = aliases.get(payload.parent, payload.parent)
    parents = _canonical_parents(aliases, (record for _, record in links.values()))
    parents[child] = parent
    _check_cycles(parents)
    # A graduation can join previously separate links with the same canonical
    # parent. A later reparent revises those links together in one commit.
    effects = []
    for raw_child, (revision, _) in links.items():
        if aliases.get(raw_child, raw_child) != child:
            continue
        key = _parent_key(derive_ref, raw_child)
        if key != revision.key:
            raise ValueError("Stored parent revision key mismatch")
        effects.append(
            Revision(key, revision.revision + 1, replace(payload, child=raw_child))
        )
    if effects:
        return tuple(effects)
    return (Revision(_parent_key(derive_ref, child), 1, replace(payload, child=child)),)


def _parent_key(
    derive_ref: Callable[[str, str], SourceRef], child: ItemKey
) -> SourceRef:
    return derive_ref("item-parent", f"{child.kind.value}:{child.identifier}")


def relationship_decision(
    payload: DraftAlias | ItemParent,
    view: LedgerView,
    derive_ref: Callable[[str, str], SourceRef],
) -> tuple[MarkerDisposition, tuple[Revision, ...]]:
    """Determine the final disposition and exact effects at a fixed ledger sequence."""
    if payload.project_id != view.project_id:
        raise ValueError("Relationship project mismatch")
    try:
        effects = _relationship_effects(payload, view, derive_ref)
    except _RelationshipConflict:
        return MarkerDisposition.CONFLICT, ()
    return MarkerDisposition.ACCEPTED, effects
