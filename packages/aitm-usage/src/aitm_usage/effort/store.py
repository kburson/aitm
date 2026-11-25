"""A local project database for trusted, normalized effort evidence."""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, fields
from enum import StrEnum
from pathlib import Path
from uuid import UUID

from ..types import Availability, _decode, _encode
from .assignments import Attribution, Handoff, MarkerKind, ScopeMarker
from .receipts import Enrollment, Outcome, UsageReceipt, UsageScope

_APPLICATION_ID = 0x41495445  # AITE
_SCHEMA = (
    """CREATE TABLE IF NOT EXISTS metadata (
        singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
        project TEXT NOT NULL, schema_version INTEGER NOT NULL,
        generation INTEGER NOT NULL DEFAULT 0
    )""",
    """CREATE TABLE IF NOT EXISTS enrollments (
        attempt TEXT PRIMARY KEY, payload TEXT NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS revisions (
        observation TEXT NOT NULL, revision INTEGER NOT NULL, digest TEXT NOT NULL,
        attempt TEXT NOT NULL REFERENCES enrollments(attempt), payload TEXT NOT NULL,
        PRIMARY KEY (observation, revision)
    )""",
    """CREATE TABLE IF NOT EXISTS pending (
        digest TEXT PRIMARY KEY, observation TEXT NOT NULL, revision INTEGER NOT NULL,
        attempt TEXT NOT NULL REFERENCES enrollments(attempt), payload TEXT NOT NULL
    )""",
    "CREATE INDEX IF NOT EXISTS pending_for_observation ON pending(observation, revision)",
    "CREATE INDEX IF NOT EXISTS pending_for_attempt ON pending(attempt)",
    """CREATE TABLE IF NOT EXISTS effective (
        observation TEXT PRIMARY KEY, revision INTEGER NOT NULL,
        attempt TEXT NOT NULL UNIQUE REFERENCES enrollments(attempt),
        FOREIGN KEY (observation, revision) REFERENCES revisions(observation, revision)
    )""",
    """CREATE TABLE IF NOT EXISTS conflicts (
        digest TEXT PRIMARY KEY, reason TEXT NOT NULL, payload TEXT NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS attributions (
        observation TEXT PRIMARY KEY REFERENCES effective(observation),
        payload TEXT NOT NULL
    )""",
)

_TRAIL_SCHEMA = (
    """CREATE TABLE IF NOT EXISTS scope_markers (
        observation TEXT NOT NULL, attempt TEXT NOT NULL REFERENCES enrollments(attempt),
        kind TEXT NOT NULL, payload TEXT NOT NULL,
        PRIMARY KEY (observation, kind), UNIQUE (attempt, kind)
    )""",
    """CREATE TABLE IF NOT EXISTS handoffs (
        predecessor TEXT PRIMARY KEY, successor TEXT NOT NULL UNIQUE, payload TEXT NOT NULL
    )""",
)


_COVERAGE_RANK = {
    Availability.UNKNOWN: 0,
    Availability.PARTIAL: 1,
    Availability.COMPLETE: 2,
}


class EffortError(ValueError):
    pass


class Disposition(StrEnum):
    INSERTED = "inserted"
    REPLAYED = "replayed"
    PENDING = "pending"
    REFINED = "refined"
    CONFLICTED = "conflicted"


@dataclass(frozen=True, slots=True)
class StoryObservation:
    receipt: UsageReceipt
    enrollment: Enrollment
    story: int | None
    epic: int | None
    attribution: Attribution | None


@dataclass(frozen=True, slots=True)
class ReceiptConflict:
    receipt: UsageReceipt
    reason: str


@dataclass(frozen=True, slots=True)
class Snapshot:
    project_id: UUID
    generation: int
    enrollments: tuple[Enrollment, ...]
    attributed: tuple[StoryObservation, ...]
    pending: tuple[UsageReceipt, ...]
    conflicts: tuple[ReceiptConflict, ...]
    markers: tuple[ScopeMarker, ...] = ()
    handoffs: tuple[Handoff, ...] = ()


class EffortStore:
    """Use an application-owned private directory on a local filesystem.

    The caller authenticates enrollment, provider evidence and late attribution
    before invoking this API. A digest or project-keyed reference is an identity
    aid, not authentication. Do not point this store at an untrusted directory.
    """

    def __init__(
        self, database: Path, project_id: UUID, *, read_only: bool = False
    ) -> None:
        if type(project_id) is not UUID:
            raise EffortError("Expected a project UUID")
        if (
            not database.parent.is_dir()
            or database.parent.is_symlink()
            or database.is_symlink()
        ):
            raise EffortError("Expected a database in an existing private directory")
        self.database = database.absolute()
        self.project_id = project_id
        self._read_only = read_only
        if read_only:
            return
        with self._transaction(write=True, initialize=True) as connection:
            app_id = connection.execute("PRAGMA application_id").fetchone()[0]
            if app_id != _APPLICATION_ID:
                if (
                    app_id != 0
                    or connection.execute(
                        "SELECT 1 FROM sqlite_schema LIMIT 1"
                    ).fetchone()
                ):
                    raise EffortError("Existing file is not an effort database")
                for statement in _SCHEMA:
                    connection.execute(statement)
                connection.execute(f"PRAGMA application_id={_APPLICATION_ID}")
                connection.execute(
                    "INSERT INTO metadata VALUES (1, ?, 1, 0)",
                    (str(self.project_id),),
                )
            self._generation(connection)
            for statement in _TRAIL_SCHEMA:
                connection.execute(statement)

    @contextmanager
    def _transaction(
        self, *, write: bool = False, initialize: bool = False
    ) -> Iterator[sqlite3.Connection]:
        # Subsequent opens must not silently create a replacement store.
        target = self.database.absolute().as_uri()
        if self._read_only:
            if write or initialize:
                raise EffortError("Cannot write to a read-only effort store")
            target += "?mode=ro"
        elif not initialize:
            target += "?mode=rw"
        connection = sqlite3.connect(target, uri=True, isolation_level=None, timeout=10)
        try:
            connection.execute("PRAGMA foreign_keys=ON")
            connection.execute("BEGIN IMMEDIATE" if write else "BEGIN")
            if not initialize:
                self._generation(connection)
            yield connection
            connection.commit()
        except BaseException:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _generation(self, connection: sqlite3.Connection) -> int:
        if connection.execute("PRAGMA application_id").fetchone()[0] != _APPLICATION_ID:
            raise EffortError("Existing file is not an effort database")
        row = connection.execute(
            "SELECT project, schema_version, generation FROM metadata"
        ).fetchone()
        if row is None or row[0] != str(self.project_id):
            raise EffortError("Effort store project does not match")
        if row[1] != 1:
            raise EffortError("Unsupported effort store schema")
        return row[2]

    def _require_project(self, project_id: UUID) -> None:
        if project_id != self.project_id:
            raise EffortError("Evidence project does not match the effort store")

    @staticmethod
    def _advance_generation(connection: sqlite3.Connection) -> None:
        connection.execute("UPDATE metadata SET generation = generation + 1")

    def enroll(self, enrollment: Enrollment) -> Disposition:
        self._require_project(enrollment.project_id)
        attempt = str(enrollment.attempt_id)
        payload = _encode(enrollment, Enrollment)
        with self._transaction(write=True) as db:
            existing = db.execute(
                "SELECT payload FROM enrollments WHERE attempt=?", (attempt,)
            ).fetchone()
            if existing:
                return (
                    Disposition.REPLAYED
                    if existing[0] == payload
                    else Disposition.CONFLICTED
                )
            if enrollment.parent_attempt_id is not None:
                parent = self._enrollment(db, str(enrollment.parent_attempt_id))
                if parent.run_id != enrollment.run_id:
                    raise EffortError("Parent attempt belongs to a different run")
            db.execute("INSERT INTO enrollments VALUES (?, ?)", (attempt, payload))
            self._advance_generation(db)
            return Disposition.INSERTED

    @staticmethod
    def _enrollment(db: sqlite3.Connection, attempt: str) -> Enrollment:
        row = db.execute(
            "SELECT payload FROM enrollments WHERE attempt=?", (attempt,)
        ).fetchone()
        if not row:
            raise EffortError("Receipt has no enrolled attempt")
        return _decode(row[0], Enrollment)

    @staticmethod
    def _conflict(db: sqlite3.Connection, receipt: UsageReceipt, reason: str) -> None:
        db.execute(
            "INSERT INTO conflicts VALUES (?, ?, ?)",
            (receipt.digest, reason, receipt.to_json()),
        )

    @staticmethod
    def _effective(db: sqlite3.Connection, observation: str) -> UsageReceipt | None:
        row = db.execute(
            """SELECT r.payload FROM effective e JOIN revisions r
               USING (observation, revision) WHERE e.observation=?""",
            (observation,),
        ).fetchone()
        return UsageReceipt.from_json(row[0]) if row else None

    @staticmethod
    def _revision_conflict(
        previous: UsageReceipt | None, candidate: UsageReceipt
    ) -> str | None:
        if previous is None:
            return None
        if candidate.attempt_id != previous.attempt_id:
            return "turn-attempt"
        if candidate.previous_digest != previous.digest:
            return "revision-lineage"
        if _COVERAGE_RANK[candidate.coverage] < _COVERAGE_RANK[previous.coverage]:
            return "revision-coverage"
        counts = [
            (
                getattr(previous.tokens, field.name),
                getattr(candidate.tokens, field.name),
            )
            for field in fields(previous.tokens)
        ]
        counts.extend(
            (
                (previous.grok_cost_usd_ticks, candidate.grok_cost_usd_ticks),
                (
                    previous.grok_cache_creation_tokens,
                    candidate.grok_cache_creation_tokens,
                ),
            )
        )
        for before, after in counts:
            if before is not None and (
                after is None
                or (previous.coverage == Availability.COMPLETE and after != before)
            ):
                return "revision-usage"
        if (
            previous.outcome != Outcome.UNKNOWN
            and candidate.outcome != previous.outcome
        ):
            return "revision-outcome"
        if previous.scope != UsageScope.UNKNOWN and candidate.scope != previous.scope:
            return "revision-scope"
        return None

    def _advance(
        self, db: sqlite3.Connection, observation: str, previous: UsageReceipt | None
    ) -> UsageReceipt | None:
        while True:
            revision = 1 if previous is None else previous.revision + 1
            rows = db.execute(
                "SELECT payload FROM pending WHERE observation=? AND revision=?",
                (observation, revision),
            ).fetchall()
            candidates = []
            for (payload,) in rows:
                candidate = UsageReceipt.from_json(payload)
                reason = self._revision_conflict(previous, candidate)
                if reason:
                    self._conflict(db, candidate, reason)
                else:
                    candidates.append(candidate)
            db.execute(
                "DELETE FROM pending WHERE observation=? AND revision=?",
                (observation, revision),
            )
            if len(candidates) != 1:
                for candidate in candidates:
                    self._conflict(db, candidate, "revision-conflict")
                return previous
            candidate = candidates[0]
            attempt = str(candidate.attempt_id)
            db.execute(
                "INSERT INTO revisions VALUES (?, ?, ?, ?, ?)",
                (observation, revision, candidate.digest, attempt, candidate.to_json()),
            )
            db.execute(
                """INSERT INTO effective VALUES (?, ?, ?)
                   ON CONFLICT(observation) DO UPDATE SET revision=excluded.revision""",
                (observation, revision, attempt),
            )
            previous = candidate

    def _reject_incompatible_pending(
        self, db: sqlite3.Connection, observation: str, attempt: str
    ) -> None:
        rows = db.execute(
            """SELECT digest, payload FROM pending
               WHERE (observation=? AND attempt<>?) OR (attempt=? AND observation<>?)""",
            (observation, attempt, attempt, observation),
        ).fetchall()
        for digest, payload in rows:
            self._conflict(db, UsageReceipt.from_json(payload), "turn-attempt")
            db.execute("DELETE FROM pending WHERE digest=?", (digest,))

    @staticmethod
    def _scope_marker(
        db: sqlite3.Connection, observation: str, kind: MarkerKind
    ) -> ScopeMarker | None:
        row = db.execute(
            "SELECT payload FROM scope_markers WHERE observation=? AND kind=?",
            (observation, kind),
        ).fetchone()
        return _decode(row[0], ScopeMarker) if row else None

    def mark_scope(self, marker: ScopeMarker) -> Disposition:
        self._require_project(marker.project_id)
        observation = marker.turn.identity
        attempt = str(marker.attempt_id)
        payload = _encode(marker, ScopeMarker)
        with self._transaction(write=True) as db:
            enrollment = self._enrollment(db, attempt)
            if enrollment.story is None and enrollment.epic is None:
                raise EffortError("Scope markers require an assigned attempt")
            existing = db.execute(
                """SELECT payload FROM scope_markers
                   WHERE kind=? AND (observation=? OR attempt=?)""",
                (marker.kind, observation, attempt),
            ).fetchall()
            if existing:
                return (
                    Disposition.REPLAYED
                    if existing == [(payload,)]
                    else Disposition.CONFLICTED
                )
            if marker.kind == MarkerKind.START:
                for table in ("effective", "pending"):
                    if db.execute(
                        f"SELECT 1 FROM {table} WHERE observation=? OR attempt=?",
                        (observation, attempt),
                    ).fetchone():
                        raise EffortError("Start must precede receipt ingestion")
            else:
                start = self._scope_marker(db, observation, MarkerKind.START)
                if (
                    start is None
                    or start.attempt_id != marker.attempt_id
                    or start.clock != marker.clock
                    or start.at > marker.at
                ):
                    raise EffortError("End must match the exact start and clock")
            db.execute(
                "INSERT INTO scope_markers VALUES (?, ?, ?, ?)",
                (observation, attempt, marker.kind, payload),
            )
            self._advance_generation(db)
            return Disposition.INSERTED

    def handoff(self, handoff: Handoff) -> Disposition:
        self._require_project(handoff.project_id)
        predecessor = handoff.predecessor.identity
        successor = handoff.successor.identity
        payload = _encode(handoff, Handoff)
        with self._transaction(write=True) as db:
            existing = db.execute(
                "SELECT payload FROM handoffs WHERE predecessor=? OR successor=?",
                (predecessor, successor),
            ).fetchall()
            if existing:
                return (
                    Disposition.REPLAYED
                    if existing == [(payload,)]
                    else Disposition.CONFLICTED
                )
            detach = self._scope_marker(db, predecessor, MarkerKind.END)
            attach = self._scope_marker(db, successor, MarkerKind.START)
            if detach is None or attach is None:
                raise EffortError("Handoff requires exact detach and attach markers")
            old = self._enrollment(db, str(detach.attempt_id))
            new = self._enrollment(db, str(attach.attempt_id))
            if (old.story, old.epic) != (new.story, new.epic):
                raise EffortError("Handoff must preserve assignment")
            if detach.clock == attach.clock and detach.at > attach.at:
                raise EffortError("Detach follows attach on the same clock")
            if db.execute(
                """WITH RECURSIVE chain(turn) AS (
                    VALUES (?) UNION SELECT h.successor FROM handoffs h
                    JOIN chain ON h.predecessor=chain.turn
                ) SELECT 1 FROM chain WHERE turn=?""",
                (successor, predecessor),
            ).fetchone():
                raise EffortError("Handoff would create a cycle")
            db.execute(
                "INSERT INTO handoffs VALUES (?, ?, ?)",
                (predecessor, successor, payload),
            )
            self._advance_generation(db)
            return Disposition.INSERTED

    def ingest(self, receipt: UsageReceipt) -> Disposition:
        self._require_project(receipt.project_id)
        attempt = str(receipt.attempt_id)
        observation = receipt.observation_id
        payload, digest = receipt.to_json(), receipt.digest
        with self._transaction(write=True) as db:
            self._enrollment(db, attempt)
            if db.execute(
                "SELECT 1 FROM conflicts WHERE digest=?", (digest,)
            ).fetchone():
                return Disposition.REPLAYED
            if db.execute("SELECT 1 FROM pending WHERE digest=?", (digest,)).fetchone():
                return Disposition.REPLAYED
            occupied = db.execute(
                "SELECT digest FROM revisions WHERE observation=? AND revision=?",
                (observation, receipt.revision),
            ).fetchone()
            if occupied and occupied[0] == digest:
                return Disposition.REPLAYED

            active = self._effective(db, observation)
            other = db.execute(
                "SELECT observation FROM effective WHERE attempt=? AND observation<>?",
                (attempt, observation),
            ).fetchone()
            wrong_marker = db.execute(
                """SELECT 1 FROM scope_markers
                   WHERE (observation=? AND attempt<>?) OR (attempt=? AND observation<>?)""",
                (observation, attempt, attempt, observation),
            ).fetchone()
            if wrong_marker:
                reason = "turn-marker"
            elif (active and active.attempt_id != receipt.attempt_id) or other:
                reason = "turn-attempt"
            elif occupied:
                reason = "revision-conflict"
            else:
                reason = None

            self._advance_generation(db)
            if reason:
                self._conflict(db, receipt, reason)
                return Disposition.CONFLICTED

            db.execute(
                "INSERT INTO pending VALUES (?, ?, ?, ?, ?)",
                (digest, observation, receipt.revision, attempt, payload),
            )
            selected = self._advance(db, observation, active)
            if not selected or selected.revision < receipt.revision:
                rejected = db.execute(
                    "SELECT 1 FROM conflicts WHERE digest=?", (digest,)
                ).fetchone()
                return Disposition.CONFLICTED if rejected else Disposition.PENDING
            if active is None:
                self._reject_incompatible_pending(db, observation, attempt)
            if selected.revision > 1:
                return Disposition.REFINED
            return Disposition.INSERTED

    def attribute(self, link: Attribution) -> Disposition:
        self._require_project(link.project_id)
        payload = _encode(link, Attribution)
        with self._transaction(write=True) as db:
            receipt = self._effective(db, link.observation_id)
            if receipt is None:
                raise EffortError("Attribution requires an effective observation")
            if receipt.scope != UsageScope.BOUNDED:
                raise EffortError("Observation scope does not support late attribution")
            enrollment = self._enrollment(db, str(receipt.attempt_id))
            if enrollment.story is not None:
                raise EffortError("The original story assignment is immutable")
            if enrollment.epic is not None and link.epic != enrollment.epic:
                raise EffortError("Attribution does not match the enrolled epic")
            existing = db.execute(
                "SELECT payload FROM attributions WHERE observation=?",
                (link.observation_id,),
            ).fetchone()
            if existing:
                return (
                    Disposition.REPLAYED
                    if existing[0] == payload
                    else Disposition.CONFLICTED
                )
            db.execute(
                "INSERT INTO attributions VALUES (?, ?)", (link.observation_id, payload)
            )
            self._advance_generation(db)
            return Disposition.INSERTED

    def snapshot(self) -> Snapshot:
        with self._transaction() as db:
            trail_tables = {
                name
                for (name,) in db.execute(
                    "SELECT name FROM sqlite_schema WHERE type='table' "
                    "AND name IN ('scope_markers', 'handoffs')"
                )
            }
            if trail_tables and len(trail_tables) != 2:
                raise EffortError("Incomplete effort trail schema")
            markers = ()
            handoffs = ()
            if trail_tables:
                markers = tuple(
                    _decode(payload, ScopeMarker)
                    for (payload,) in db.execute(
                        "SELECT payload FROM scope_markers ORDER BY observation, kind DESC"
                    )
                )
                handoffs = tuple(
                    _decode(payload, Handoff)
                    for (payload,) in db.execute(
                        "SELECT payload FROM handoffs ORDER BY predecessor"
                    )
                )
            open_scopes = {
                marker.turn.identity
                for marker in markers
                if marker.kind == MarkerKind.START
            } - {
                marker.turn.identity
                for marker in markers
                if marker.kind == MarkerKind.END
            }
            return Snapshot(
                self.project_id,
                self._generation(db),
                tuple(
                    _decode(payload, Enrollment)
                    for (payload,) in db.execute(
                        "SELECT payload FROM enrollments ORDER BY attempt"
                    )
                ),
                tuple(
                    self._story_observation(
                        receipt, enrollment, link, observation in open_scopes
                    )
                    for receipt, enrollment, link, observation in db.execute(
                        """SELECT r.payload, a.payload, t.payload, e.observation
                           FROM effective e JOIN revisions r USING (observation, revision)
                           JOIN enrollments a ON a.attempt=e.attempt
                           LEFT JOIN attributions t ON t.observation=e.observation
                           ORDER BY e.observation"""
                    )
                ),
                tuple(
                    UsageReceipt.from_json(row[0])
                    for row in db.execute(
                        "SELECT payload FROM pending ORDER BY observation, revision, digest"
                    )
                ),
                tuple(
                    ReceiptConflict(UsageReceipt.from_json(payload), reason)
                    for payload, reason in db.execute(
                        "SELECT payload, reason FROM conflicts ORDER BY digest"
                    )
                ),
                markers,
                handoffs,
            )

    @staticmethod
    def _story_observation(
        receipt_data: str, enrollment_data: str, link_data: str | None, open_scope: bool
    ) -> StoryObservation:
        receipt = UsageReceipt.from_json(receipt_data)
        enrollment = _decode(enrollment_data, Enrollment)
        link = _decode(link_data, Attribution) if link_data else None
        story, epic = enrollment.story, enrollment.epic
        if link:
            story, epic = link.story, link.epic
        if open_scope or receipt.scope not in (
            UsageScope.BOUNDED,
            UsageScope.INCLUSIVE,
        ):
            story, epic = None, None
        return StoryObservation(receipt, enrollment, story, epic, link)
