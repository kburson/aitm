"""Canonical item relationships and usage at a fixed ledger sequence."""

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, fields
from decimal import Context, Decimal
from typing import Protocol, runtime_checkable

from .relationships import canonical_relationships
from .scopes import resolve_scope
from .types import (
    ItemKey,
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
    # U06 admits up to 24 integer and 13 fractional digits per price.
    # Even the full 64-bit SQLite row ID space adds at most 20 digits to a sum.
    usd_context = Context(prec=64, Emin=-64, Emax=64)
    known = Decimal(0)
    unknown = count = 0
    for counts, usd in observations:
        count += 1
        if usd is None:
            unknown += 1
        else:
            known = usd_context.add(known, usd)
        for field in token_fields:
            quantity = getattr(counts, field.name)
            if quantity is not None:
                tokens[field.name] = tokens.get(field.name, 0) + quantity
    return RollupTotals(tokens, known, unknown, count)


def rollup(root: ItemKey, view: LedgerView) -> UsageRollup:
    """Count each current observation once against canonical fixed-view items."""
    aliases, parents = canonical_relationships(view)
    root = aliases.get(root, root)
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
