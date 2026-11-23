"""Already-verified frames for adapter policy tests."""

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from uuid import UUID

from aitm_usage.monitor_registry import _ServiceEvidence
from aitm_usage.monitor_types import NativeSurface
from aitm_usage.scopes import session_reference
from aitm_usage.sources import adapter
from aitm_usage.sources.scan import (
    CandidateSource,
    FrameBatch,
    SidebandFrame,
    SidebandKind,
    SourceFrame,
)
from aitm_usage.types import (
    ClientVersion,
    Eligibility,
    Provider,
    ProviderCheckpoint,
    SourceCursor,
)


class _AdapterEvidence(_ServiceEvidence):
    root = Path("/fixture/project")


@dataclass(frozen=True)
class AdapterFrames:
    provider: Provider
    client: ClientVersion
    session_id: UUID
    cutoff: datetime
    ledger = _AdapterEvidence(b"adapter-frame-policy-fixture")
    checkout = Path("/fixture/checkout")

    def read_monitor(self, rows, monkeypatch):
        frames = self.batch(rows)
        first = frames.frames[0]
        path = Path("/fixture/transcripts/native.jsonl")
        source = CandidateSource(
            self.provider,
            first.session_ref,
            first.stream_ref,
            frames.cursor.locator_ref,
            frames.cursor.incarnation_ref,
            path,
            ((1, 2), (1, 3)),
            adapter.SourceRoot(path.parent, self.cutoff, (self.checkout,), self.ledger),
            self.ledger,
            _native_surface={
                Provider.CODEX: NativeSurface.CODEX_DESKTOP_MACOS,
                Provider.CLAUDE: NativeSurface.CLAUDE_CODE_MACOS,
            }[self.provider],
            _monitor=True,
        )

        def read(candidate, checkpoint, cutoff, *, _capture_limit):
            assert candidate is source
            assert checkpoint is None and cutoff == self.cutoff
            assert _capture_limit is None
            return frames

        monkeypatch.setattr(adapter, "scan", read)
        monkeypatch.setattr(adapter.platform, "system", lambda: "Darwin")
        monkeypatch.setattr(adapter.platform, "machine", lambda: "arm64")
        return adapter.ProviderAdapter().read_delta(adapter.SourceLocator(source), None)

    def batch(self, rows, *, anchored=True):
        evidence = self.ledger
        session = session_reference(evidence, self.provider, str(self.session_id))
        stream = evidence.pseudonymize("fixture", "stream")
        segment = evidence.pseudonymize("fixture", "segment")
        anchor = evidence.pseudonymize("fixture", "checkout") if anchored else None
        frames = []
        sideband = []
        prefix = hashlib.sha256()
        offset = 0

        for ordinal, row in enumerate(rows):
            line = (json.dumps(row) + "\n").encode()
            offset += len(line)
            prefix.update(line)
            if self.provider is Provider.CLAUDE and row["type"] in (
                SidebandKind.COST_STATE,
                SidebandKind.SESSION_OWNER,
            ):
                if row["type"] == SidebandKind.SESSION_OWNER:
                    content = {
                        "account_ref": evidence.pseudonymize(
                            "claude-account", row["accountUuid"]
                        )
                    }
                else:
                    content = {"modelUsage": row["modelUsage"]}
                sideband.append(
                    SidebandFrame(
                        SidebandKind(row["type"]),
                        self.provider,
                        session,
                        stream,
                        ordinal,
                        segment,
                        frames[-1].ordinal,
                        content,
                        _prefix=prefix.hexdigest(),
                    )
                )
                continue

            observed_at = datetime.fromisoformat(row["timestamp"])
            frames.append(
                SourceFrame(
                    self.provider,
                    session,
                    stream,
                    ordinal,
                    observed_at,
                    self.client,
                    1,
                    segment,
                    anchor,
                    observed_at < self.cutoff,
                    row,
                    eligibility=Eligibility.ELIGIBLE
                    if anchored
                    else Eligibility.UNKNOWN,
                    _prefix=prefix.hexdigest(),
                    boundary_only=not anchored,
                )
            )

        cursor = SourceCursor(
            stream,
            evidence.pseudonymize("fixture", "locator"),
            evidence.pseudonymize("fixture", "incarnation"),
            offset if anchored else 0,
            evidence.pseudonymize(
                "fixture",
                prefix.hexdigest() if anchored else hashlib.sha256().hexdigest(),
            ),
        )
        return FrameBatch(
            frames=tuple(frames),
            commit_frames=tuple(frames) if anchored else (),
            cursor=cursor,
            provider_checkpoint=ProviderCheckpoint(
                self.provider, client_version=self.client, format_version=1
            ),
            sideband=tuple(sideband),
            commit_sideband=tuple(sideband) if anchored else (),
            observed_through=max(frame.observed_at for frame in frames),
        )
