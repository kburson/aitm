"""Caller-owned enrollment, exact settlement and sanitized publication inputs."""

import hashlib
import hmac
import io
import json
import os
import re
import secrets
from dataclasses import dataclass, replace
from datetime import datetime
from pathlib import Path
from uuid import UUID

from ..types import Availability, SourceRef, TokenCounts, _decode, _encode
from .assignments import ScopeMarker
from .capture import (
    CaptureAdapter,
    CaptureLimits,
    CaptureResult,
    HarnessCommand,
    Observation,
    capture,
    recover,
)
from .receipts import (
    Enrollment,
    NativeTurn,
    Outcome,
    ReviewBinding,
    Role,
    TimeBasis,
    UsageReceipt,
    UsageScope,
    require_digest,
    require_item,
)
from .review_receipts import (
    ReviewAttempt,
    ReviewCompanion,
    SealedDecision,
    reconcile_review_receipts,
)
from .store import Disposition, EffortError, EffortStore

_SCHEMA = "aitm.session-turn/v1"
_ROUTES = {
    "codex": {
        "0.171.0-alpha.13": {"exec", "cli"},
        "0.171.0-alpha.13.2": {"exec", "cli", "desktop", "desktop-subagent"},
    },
    "claude": {"2.1.331": {"print", "cli"}},
    "grok": {"1.0.92": {"usage"}},
}
_MODELS = {
    "codex": {"gpt-6.2-sol", "gpt-6.2-astra", "gpt-6.1-sol", "gpt-6-astra"},
    "claude": {"claude-sonnet-5-5", "claude-opus-5-5"},
    "grok": {"grok-4.7-build-fast"},
}
_MAX_PUBLIC_BYTES = 2 << 20
_STATEMENTS = (
    """CREATE TABLE IF NOT EXISTS session_project (
        singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
        secret BLOB NOT NULL, remote TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS session_selections (
        session TEXT PRIMARY KEY, story INTEGER NOT NULL, epic INTEGER
    )""",
    """CREATE TABLE IF NOT EXISTS session_expectations (
        attempt TEXT PRIMARY KEY REFERENCES enrollments(attempt),
        session TEXT NOT NULL REFERENCES session_selections(session),
        launch TEXT NOT NULL, native TEXT, observation TEXT UNIQUE
    )""",
    """CREATE TABLE IF NOT EXISTS session_parent_links (
        child TEXT PRIMARY KEY REFERENCES session_expectations(attempt),
        parent TEXT NOT NULL REFERENCES session_expectations(attempt)
    )""",
    """CREATE TABLE IF NOT EXISTS session_dispatches (
        attempt TEXT PRIMARY KEY REFERENCES session_expectations(attempt)
    )""",
    """CREATE TABLE IF NOT EXISTS session_codex_callbacks (
        attempt TEXT PRIMARY KEY REFERENCES session_expectations(attempt),
        payload TEXT NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS session_rate_evidence (
        digest TEXT PRIMARY KEY,
        payload TEXT NOT NULL
    )""",
)


@dataclass(frozen=True, slots=True)
class Expectation:
    enrollment: Enrollment
    launch: SourceRef
    native: NativeTurn | None


@dataclass(frozen=True, slots=True)
class RateEvidence:
    model: str
    requests: tuple[TokenCounts, ...] | None = None

    def __post_init__(self):
        _label(self.model)
        if self.requests is not None and not self.requests:
            raise EffortError("Rate evidence must contain at least one request")


def _label(value: str) -> None:
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._+-]{0,95}", value):
        raise EffortError("Invalid public provider metadata")


@dataclass(frozen=True, slots=True)
class PublicReceipt:
    schema: str
    project: UUID
    story: int
    identity: str
    revision: int
    attempt: str
    role: Role
    provider: str
    version: str
    surface: str
    observed_at: datetime
    started_at: datetime | None
    ended_at: datetime | None
    time_basis: TimeBasis
    coverage: Availability
    outcome: Outcome
    usage_scope: UsageScope
    tokens: TokenCounts
    evidence_sha256: str
    previous_receipt_sha256: str | None
    model: str | None
    rate_inputs: tuple[TokenCounts, ...] | None
    reported_grok_usd_ticks: int | None
    grok_cache_creation_tokens: int | None

    def __post_init__(self):
        if self.schema != _SCHEMA or self.provider not in _ROUTES:
            raise EffortError("Unexpected publication receipt schema or provider")
        if type(self.story) is not int or self.story < 1 or self.revision < 1:
            raise EffortError("Expected a positive story and revision")
        for digest in (self.identity, self.attempt, self.evidence_sha256):
            require_digest(digest)
        if (self.revision == 1) != (self.previous_receipt_sha256 is None):
            raise EffortError("Missing publication revision lineage")
        if self.previous_receipt_sha256 is not None:
            require_digest(self.previous_receipt_sha256)
        if self.surface not in _ROUTES[self.provider].get(self.version, ()):
            raise EffortError("Unrecognized public provider route")
        if self.model is not None:
            if self.model not in _MODELS[self.provider]:
                raise EffortError("Unrecognized public provider model")
        elif self.rate_inputs is not None:
            raise EffortError("Request rate inputs require a verified model")
        if self.usage_scope not in (UsageScope.BOUNDED, UsageScope.INCLUSIVE) and (
            self.coverage != Availability.UNKNOWN
            or self.tokens != TokenCounts()
            or self.time_basis != TimeBasis.UNKNOWN
            or self.model is not None
            or self.reported_grok_usd_ticks is not None
        ):
            raise EffortError("Unattributed revision must be coverage-only")
        if self.started_at and self.ended_at and self.ended_at < self.started_at:
            raise EffortError("Invalid observation interval")
        if self.time_basis == TimeBasis.UNKNOWN and (self.started_at or self.ended_at):
            raise EffortError("Observation interval requires a time basis")
        grok = (self.reported_grok_usd_ticks, self.grok_cache_creation_tokens)
        if grok != (None, None) and (
            self.provider != "grok"
            or any(type(value) is not int or not 0 <= value < 2**63 for value in grok)
        ):
            raise EffortError("Invalid reported Grok usage")


def validate_public_receipt(data: bytes) -> dict:
    """Validate the closed receipt shape and canonical bytes before publication."""
    if len(data) > _MAX_PUBLIC_BYTES:
        raise EffortError("Publication receipt exceeds its byte limit")
    value = _decode(data, PublicReceipt)
    if data != _encode(value, PublicReceipt).encode():
        raise EffortError("Expected a canonical publication receipt")
    return json.loads(data)


class SessionStore(EffortStore):
    """One private effort database and planning remote per project."""

    def __init__(self, database: Path, project_id: UUID):
        if os.name == "posix" and database.parent.stat().st_mode & 0o077:
            raise EffortError("Session state requires a private database directory")
        super().__init__(database, project_id)
        with self._transaction(write=True) as db:
            for statement in _STATEMENTS:
                db.execute(statement)
            row = db.execute("SELECT secret FROM session_project").fetchone()
            if row is None:
                self._secret = secrets.token_bytes(32)
                db.execute(
                    "INSERT INTO session_project VALUES (1, ?, NULL)", (self._secret,)
                )
            else:
                self._secret = row[0]

    def _pseudonym(self, namespace: str, raw: str) -> str:
        data = json.dumps([str(self.project_id), namespace, raw], separators=(",", ":"))
        return hmac.new(self._secret, data.encode(), "sha256").hexdigest()

    def reference(self, namespace: str, raw: str) -> SourceRef:
        return SourceRef(
            f"hmac-sha256:{self._pseudonym('key', '')}:{self._pseudonym(namespace, raw)}"
        )

    def select(
        self, session: UUID, story: int, remote: str, *, epic: int | None = None
    ) -> None:
        require_item(story)
        require_item(epic)
        if (
            story is None
            or not remote
            or remote != remote.strip()
            or any(ord(c) < 32 for c in remote)
        ):
            raise EffortError("Expected a story and configured planning remote")
        with self._transaction(write=True) as db:
            previous = db.execute("SELECT remote FROM session_project").fetchone()[0]
            if previous not in (None, remote):
                raise EffortError(
                    "Planning remote does not match the configured project"
                )
            db.execute("UPDATE session_project SET remote=?", (remote,))
            db.execute(
                "INSERT INTO session_selections VALUES (?, ?, ?) "
                "ON CONFLICT(session) DO UPDATE SET story=excluded.story, epic=excluded.epic",
                (str(session), story, epic),
            )

    def remote(self) -> str:
        with self._transaction() as db:
            remote = db.execute("SELECT remote FROM session_project").fetchone()[0]
            if remote is None:
                raise EffortError("No planning remote configured")
            return remote

    def expect(
        self,
        session: UUID,
        attempt: UUID,
        role: Role,
        launch: SourceRef,
        *,
        parent: UUID | None = None,
        review: ReviewBinding | None = None,
        defer_story: bool = False,
    ) -> Expectation:
        if defer_story and (
            role != Role.WORKER or parent is not None or review is not None
        ):
            raise EffortError("Only a verified desktop child may defer its story")
        with self._transaction(write=True) as db:
            selection = db.execute(
                "SELECT story, epic FROM session_selections WHERE session=?",
                (str(session),),
            ).fetchone()
            if selection is None:
                raise EffortError("Select a story for this session first")
            old = db.execute(
                "SELECT session, launch, native FROM session_expectations WHERE attempt=?",
                (str(attempt),),
            ).fetchone()
            if old is not None:
                old_session, old_launch, _ = old
                expected = self._expected(db, session, attempt)
                enrolled = expected.enrollment
                if (
                    old_session != str(session)
                    or old_launch != launch.value
                    or enrolled.role != role
                    or (not defer_story and enrolled.parent_attempt_id != parent)
                    or enrolled.review != review
                ):
                    raise EffortError("Conflicting attempt enrollment")
                return expected
            story, epic = (None, None) if defer_story else selection
            enrollment = Enrollment(
                self.project_id, session, attempt, role, story, epic, parent, review
            )
            if self._enroll(db, enrollment) is not Disposition.INSERTED:
                raise EffortError("Attempt already belongs to another enrollment")
            db.execute(
                "INSERT INTO session_expectations VALUES (?, ?, ?, NULL, NULL)",
                (str(attempt), str(session), launch.value),
            )
            return Expectation(enrollment, launch, None)

    def _expected(self, db, session: UUID, attempt: UUID) -> Expectation:
        row = db.execute(
            "SELECT launch, native FROM session_expectations WHERE session=? AND attempt=?",
            (str(session), str(attempt)),
        ).fetchone()
        if row is None:
            raise EffortError("Attempt is not enrolled in this session")
        launch, native = row
        return Expectation(
            self._enrollment(db, str(attempt)),
            SourceRef(launch),
            None if native is None else _decode(native, NativeTurn),
        )

    def expected(self, session: UUID, attempt: UUID) -> Expectation:
        with self._transaction() as db:
            return self._expected(db, session, attempt)

    def attach_parent(self, session: UUID, child: UUID, parent: UUID) -> None:
        """Record an exact parent discovered from the enrolled child's native record."""
        with self._transaction(write=True) as db:
            child_enrollment = self._expected(db, session, child).enrollment
            owner = self._expected(db, session, parent).enrollment
            if (
                child_enrollment.role != Role.WORKER
                or owner.role != Role.ORCHESTRATOR
                or owner.story is None
                or child_enrollment.parent_attempt_id not in (None, parent)
                or child_enrollment.story not in (None, owner.story)
            ):
                raise EffortError("Native parent does not match the enrolled role")
            old = db.execute(
                "SELECT parent FROM session_parent_links WHERE child=?", (str(child),)
            ).fetchone()
            if old is not None and old[0] != str(parent):
                raise EffortError("Conflicting native parent")
            if child_enrollment.story is None:
                enrollment = replace(
                    child_enrollment,
                    story=owner.story,
                    epic=owner.epic,
                    parent_attempt_id=parent,
                )
                db.execute(
                    "UPDATE enrollments SET payload=? WHERE attempt=?",
                    (_encode(enrollment, Enrollment), str(child)),
                )
                self._advance_generation(db)
            db.execute(
                "INSERT OR IGNORE INTO session_parent_links VALUES (?, ?)",
                (str(child), str(parent)),
            )

    def bind(
        self, session: UUID, attempt: UUID, launch: SourceRef, turn: NativeTurn
    ) -> None:
        """Attach the exact reference verified by the authorized caller."""
        with self._transaction(write=True) as db:
            self._bind(db, self._expected(db, session, attempt), launch, turn)

    @staticmethod
    def _bind(db, expected: Expectation, launch: SourceRef, turn: NativeTurn) -> None:
        if turn.provider not in _ROUTES:
            raise EffortError("Unsupported provider binding")
        if expected.enrollment.story is None:
            raise EffortError("Attempt has no verified story assignment")
        if not hmac.compare_digest(expected.launch.value, launch.value):
            raise EffortError("Native reference does not match the launch binding")
        if expected.native is not None:
            if expected.native != turn:
                raise EffortError("Conflicting native binding")
            return
        if db.execute(
            "SELECT 1 FROM session_expectations WHERE observation=?",
            (turn.identity,),
        ).fetchone():
            raise EffortError("Native turn already belongs to another binding")
        db.execute(
            "UPDATE session_expectations SET native=?, observation=? WHERE attempt=?",
            (
                _encode(turn, NativeTurn),
                turn.identity,
                str(expected.enrollment.attempt_id),
            ),
        )

    def retain_codex_callback(self, session: UUID, attempt: UUID, payload: str) -> None:
        with self._transaction(write=True) as db:
            self._expected(db, session, attempt)
            old = db.execute(
                "SELECT payload FROM session_codex_callbacks WHERE attempt=?",
                (str(attempt),),
            ).fetchone()
            if old is not None and old[0] != payload:
                raise EffortError("Conflicting Codex terminal callback")
            db.execute(
                "INSERT OR IGNORE INTO session_codex_callbacks VALUES (?, ?)",
                (str(attempt), payload),
            )

    def codex_callback(self, session: UUID, attempt: UUID) -> bytes:
        with self._transaction() as db:
            self._expected(db, session, attempt)
            row = db.execute(
                "SELECT payload FROM session_codex_callbacks WHERE attempt=?",
                (str(attempt),),
            ).fetchone()
            if row is None:
                raise EffortError("Attempt has no retained Codex terminal callback")
            return row[0].encode()

    def accept(
        self, session: UUID, receipt: UsageReceipt, rates: RateEvidence | None = None
    ) -> Disposition:
        with self._transaction(write=True) as db:
            expected = self._expected(db, session, receipt.attempt_id)
            if expected.native != receipt.turn:
                raise EffortError("Receipt does not match the exact bound native turn")
            disposition = self._ingest(db, receipt)
            if (
                disposition
                in (Disposition.INSERTED, Disposition.REFINED, Disposition.PENDING)
                and rates
            ):
                db.execute(
                    "INSERT INTO session_rate_evidence VALUES (?, ?)",
                    (receipt.digest, _encode(rates, RateEvidence)),
                )
            if disposition is Disposition.REPLAYED and rates:
                row = db.execute(
                    "SELECT payload FROM session_rate_evidence WHERE digest=?",
                    (receipt.digest,),
                ).fetchone()
                if row is None or row[0] != _encode(rates, RateEvidence):
                    raise EffortError(
                        "Conflicting rate evidence for an immutable revision"
                    )
            return disposition

    def _settle_capture(self, session: UUID, observation: Observation) -> None:
        receipt = observation.receipt
        if receipt is not None:
            rates = None
            if observation.model in _MODELS[receipt.turn.provider]:
                rates = RateEvidence(observation.model, observation.request_usage)
            self.accept(session, receipt, rates)

    async def run_owned(
        self,
        session: UUID,
        attempt: UUID,
        launch: SourceRef,
        adapter: CaptureAdapter,
        command: HarnessCommand,
        limits: CaptureLimits = CaptureLimits(),
        *,
        expected_turn: NativeTurn | None = None,
    ) -> CaptureResult:
        """Launch an already enrolled attempt at most once and bind its native result."""
        with self._transaction(write=True) as db:
            expected = self._expected(db, session, attempt)
            if expected.enrollment.story is None:
                raise EffortError("Attempt has no verified story assignment")
            if not hmac.compare_digest(expected.launch.value, launch.value):
                raise EffortError("Launch does not match the enrollment")
            if db.execute(
                "SELECT 1 FROM session_dispatches WHERE attempt=?", (str(attempt),)
            ).fetchone():
                raise EffortError("Attempt already dispatched")
            if expected_turn is not None:
                self._bind(db, expected, launch, expected_turn)
            elif expected.native is not None:
                raise EffortError(
                    "Attempt already bound without an explicit native reference"
                )
            db.execute("INSERT INTO session_dispatches VALUES (?)", (str(attempt),))
        result = await capture(
            adapter, enrollment=expected.enrollment, command=command, limits=limits
        )
        receipt = result.observation.receipt
        if receipt is not None:
            self.bind(session, attempt, launch, receipt.turn)
            self._settle_capture(session, result.observation)
        return result

    def recover(
        self, session: UUID, attempt: UUID, adapter: CaptureAdapter, evidence: bytes
    ) -> Observation:
        expected = self.expected(session, attempt)
        if expected.native is None:
            raise EffortError("Attempt has no exact native binding")
        observation = recover(
            adapter,
            enrollment=expected.enrollment,
            expected_turn=expected.native,
            evidence=io.BytesIO(evidence),
            max_bytes=max(len(evidence), 1),
        )
        self._settle_capture(session, observation)
        return observation

    def review_companion(
        self, session: UUID, attempt: ReviewAttempt, decision: SealedDecision | None
    ) -> ReviewCompanion:
        """Reconcile already-authenticated AIPR evidence without changing its authority."""
        expected = self.expected(session, attempt.identity.enrollment.attempt_id)
        if attempt.identity.enrollment != expected.enrollment or (
            attempt.observation_id is not None
            and (
                expected.native is None
                or attempt.observation_id != expected.native.identity
            )
        ):
            raise EffortError("Review attempt does not match the exact session binding")
        (companion,) = reconcile_review_receipts(
            self.snapshot(), (attempt,), () if decision is None else (decision,)
        )
        return companion

    def status(self, session: UUID) -> dict[UUID, str]:
        with self._transaction() as db:
            result = {}
            for attempt, native, payload in db.execute(
                """SELECT s.attempt, s.native, r.payload FROM session_expectations s
                   LEFT JOIN effective e ON e.attempt=s.attempt
                   LEFT JOIN revisions r ON r.observation=e.observation AND r.revision=e.revision
                   WHERE s.session=? ORDER BY s.attempt""",
                (str(session),),
            ):
                if payload is None:
                    state = "pending-binding" if native is None else "pending-evidence"
                else:
                    receipt = UsageReceipt.from_json(payload)
                    state = (
                        "unavailable"
                        if receipt.coverage is Availability.UNKNOWN
                        else "observed"
                    )
                result[UUID(attempt)] = state
            return result

    def public_receipts(self, session: UUID) -> tuple[bytes, ...]:
        with self._transaction() as db:
            results = []
            previous = {}
            story_scopes = (UsageScope.BOUNDED, UsageScope.INCLUSIVE)
            markers = {}
            for observation, kind, payload in db.execute(
                "SELECT observation, kind, payload FROM scope_markers"
            ):
                markers.setdefault(observation, {})[kind] = _decode(
                    payload, ScopeMarker
                )
            for payload, enrollment, rate_payload, effective_payload in db.execute(
                """SELECT r.payload, a.payload, v.payload, current.payload FROM revisions r
                   JOIN session_expectations s ON s.attempt=r.attempt
                   JOIN enrollments a ON a.attempt=r.attempt
                   JOIN effective e ON e.observation=r.observation
                   JOIN revisions current ON current.observation=e.observation
                                          AND current.revision=e.revision
                   LEFT JOIN session_rate_evidence v ON v.digest=r.digest
                   WHERE s.session=? ORDER BY r.observation, r.revision""",
                (str(session),),
            ):
                native = UsageReceipt.from_json(payload)
                assignment = _decode(enrollment, Enrollment)
                rate = (
                    None
                    if rate_payload is None
                    else _decode(rate_payload, RateEvidence)
                )
                scope = markers.get(native.observation_id, {})
                start, end = scope.get("start"), scope.get("end")
                outside = start is not None and (
                    end is None
                    or any(
                        point is not None and not start.at <= point <= end.at
                        for point in (native.started_at, native.ended_at)
                    )
                )
                if (
                    assignment.story is None
                    or UsageReceipt.from_json(effective_payload).scope
                    not in story_scopes
                    or outside
                ):
                    continue
                coverage_only = native.scope not in story_scopes
                if coverage_only:
                    rate = None
                if rate is not None and rate.model not in _MODELS[native.turn.provider]:
                    rate = None
                identity = self._pseudonym("publication", native.observation_id)
                public = PublicReceipt(
                    _SCHEMA,
                    self.project_id,
                    assignment.story,
                    identity,
                    native.revision,
                    self._pseudonym("attempt", str(native.attempt_id)),
                    assignment.role,
                    native.turn.provider,
                    native.turn.version,
                    native.turn.surface,
                    native.observed_at,
                    None if coverage_only else native.started_at,
                    None if coverage_only else native.ended_at,
                    TimeBasis.UNKNOWN if coverage_only else native.time_basis,
                    Availability.UNKNOWN if coverage_only else native.coverage,
                    native.outcome,
                    native.scope,
                    TokenCounts() if coverage_only else native.tokens,
                    native.source_sha256,
                    previous.get(identity),
                    None if rate is None else rate.model,
                    None if rate is None else rate.requests,
                    None if coverage_only else native.grok_cost_usd_ticks,
                    None if coverage_only else native.grok_cache_creation_tokens,
                )
                data = _encode(public, PublicReceipt).encode()
                previous[identity] = hashlib.sha256(data).hexdigest()
                results.append(data)
            return tuple(results)
