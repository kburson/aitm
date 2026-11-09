"""Canonical item relationships and usage at a fixed ledger sequence."""

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, fields, replace
from decimal import Decimal
from typing import Protocol, runtime_checkable

from .ledger import ConflictError, Ledger
from .scopes import resolve_scope
from .types import (
    DraftAlias,
    ItemKey,
    ItemParent,
    LedgerView,
    Revision,
    SourceRef,
    TokenCounts,
    UsageObservation,
)


@runtime_checkable
class PriceProjection(Protocol):
    """Structural interface for U06's typed API-equivalent price record.

    The containing Revision has its own ledger key. observation_key is the
    UsageObservation's Revision key and observation_revision is its exact
    revision number. rate_basis is a nonempty identifier for the versioned
    pricing basis.
    usd is a finite nonnegative Decimal or None when pricing is unavailable.
    Rollups read only current records from the supplied view. An observation
    with conflicting evidence or multiple bases has unknown pricing.
    """

    @property
    def observation_key(self) -> SourceRef: ...

    @property
    def observation_revision(self) -> int: ...

    @property
    def rate_basis(self) -> str: ...

    @property
    def usd(self) -> Decimal | None: ...


@dataclass(frozen=True, slots=True)
class RollupTotals:
    """Sums of measured categories, with unmeasured categories absent."""

    tokens: dict[str, int]
    known_usd: Decimal
    unknown_price_count: int
    observation_count: int


@dataclass(frozen=True, slots=True)
class UsageRollup:
    """The canonical item, its totals and a separate view-wide unassigned bucket."""

    root: ItemKey
    direct: RollupTotals
    inclusive: RollupTotals
    unattributed: RollupTotals


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
            raise ConflictError("Canonical item has contradictory parents")
    return parents


def _check_cycles(parents: dict[ItemKey, ItemKey]) -> None:
    visited = set()
    for child in parents:
        path = set()
        while child in parents and child not in visited:
            if child in path:
                raise ConflictError("Canonical item ancestry contains a cycle")
            path.add(child)
            child = parents[child]
        visited.update(path)


def relationship_revisions(
    ledger: Ledger, payload: DraftAlias | ItemParent, view: LedgerView
) -> tuple[Revision, ...]:
    """Validate an inbox proposal and prepare its atomic revision effects."""
    aliases, links = _relationships(view)
    if isinstance(payload, DraftAlias):
        prior = aliases.get(payload.draft)
        if prior is not None and prior != payload.issue:
            raise ConflictError("Draft already has a different permanent issue")
        aliases[payload.draft] = payload.issue
        parents = _canonical_parents(aliases, (record for _, record in links.values()))
        _check_cycles(parents)
        key = ledger.pseudonymize("item-alias", str(payload.draft.identifier))
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
    effects = tuple(
        Revision(revision.key, revision.revision + 1, replace(payload, child=raw_child))
        for raw_child, (revision, _) in links.items()
        if aliases.get(raw_child, raw_child) == child
    )
    if effects:
        return effects
    key = ledger.pseudonymize("item-parent", f"{child.kind.value}:{child.identifier}")
    return (Revision(key, 1, replace(payload, child=child)),)


def _descendants(root: ItemKey, parents: dict[ItemKey, ItemKey]) -> set[ItemKey]:
    children = defaultdict(list)
    for child, parent in parents.items():
        children[parent].append(child)
    included = {root}
    pending = [root]
    while pending:
        for child in children[pending.pop()]:
            included.add(child)
            pending.append(child)
    return included


def _prices(
    current: tuple[Revision, ...],
) -> dict[tuple[SourceRef, int], Decimal | None]:
    candidates = defaultdict(set)
    for revision in current:
        record = revision.record
        if not isinstance(record, PriceProjection):
            continue
        key, number = record.observation_key, record.observation_revision
        basis, usd = record.rate_basis, record.usd
        if (
            type(key) is SourceRef
            and type(number) is int
            and number > 0
            and type(basis) is str
            and basis.strip()
            and (usd is None or (type(usd) is Decimal and usd.is_finite() and usd >= 0))
        ):
            candidates[key, number].add((basis, usd))
    return {
        identity: next(iter(bases))[1]
        for identity, bases in candidates.items()
        if len(bases) == 1
    }


def _totals(
    observations: Iterable[tuple[TokenCounts, Decimal | None]],
) -> RollupTotals:
    token_fields = fields(TokenCounts)
    tokens = {}
    known = Decimal(0)
    unknown = count = 0
    for counts, usd in observations:
        count += 1
        if usd is None:
            unknown += 1
        else:
            known += usd
        for field in token_fields:
            quantity = getattr(counts, field.name)
            if quantity is not None:
                tokens[field.name] = tokens.get(field.name, 0) + quantity
    return RollupTotals(tokens, known, unknown, count)


def rollup(root: ItemKey, view: LedgerView) -> UsageRollup:
    """Count each current observation once against canonical fixed-view items."""
    aliases, links = _relationships(view)
    root = aliases.get(root, root)
    parents = _canonical_parents(aliases, (record for _, record in links.values()))
    _check_cycles(parents)
    included = _descendants(root, parents)
    current = view.current
    prices = _prices(current)
    direct, inclusive, unattributed = [], [], []
    for revision in current:
        observation = revision.record
        if not isinstance(observation, UsageObservation):
            continue
        scope = resolve_scope(observation, view).scope
        usage = observation.tokens, prices.get((revision.key, revision.revision))
        if scope is None:
            unattributed.append(usage)
            continue
        item = scope.marker.item
        item = aliases.get(item, item)
        if item == root:
            direct.append(usage)
        if item in included:
            inclusive.append(usage)
    return UsageRollup(root, _totals(direct), _totals(inclusive), _totals(unattributed))
