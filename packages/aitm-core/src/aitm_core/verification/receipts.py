"""Retain exact verification execution facts beside the process logs."""

from hashlib import sha256
from pathlib import Path
from typing import Literal

import rfc8785
from pydantic import Field

from aitm_core.execution.admission import ExecutionRequest
from aitm_core.models.attempts import AttemptFact, ObjectId, SourceSnapshot, Text
from aitm_core.models.events import DIGEST
from aitm_core.store.gate import _atomic_write
from aitm_core.verification.lanes import Assurance


class VerificationReceipt(AttemptFact):
    schema_version: Literal["aitm.managed-verification/v1"] = Field(
        default="aitm.managed-verification/v1", alias="schema"
    )
    request: ExecutionRequest
    admission_commit: ObjectId
    source: SourceSnapshot
    capture_manifest: DIGEST
    policy_digest: DIGEST
    environment_identity: DIGEST
    environment_inventory: DIGEST
    selected_assurance: Assurance
    proven_assurance: Assurance
    command: tuple[Text, ...]
    result: Literal["passed", "failed", "diagnostic"]
    exit_code: int
    stdout_sha256: DIGEST
    stderr_sha256: DIGEST

    def retain(self, path: Path) -> str:
        wire = self.model_dump(mode="json", by_alias=True)
        digest = sha256(rfc8785.dumps(wire)).hexdigest()
        _atomic_write(path, wire)
        return f"verification-receipt:{digest}"
