"""Prove execution retains independent baseline and candidate authority."""

import pytest

from aitm_core.reducers.attempts import AttemptIntegrityError
from tests.unit.test_c55 import SOURCE, execution, replay, start_clock


def test_execution_retains_a_distinct_candidate_through_every_phase():
    candidate = {
        "source": {"commit": "e" * 40, "tree": "f" * 40},
        "capture_manifest": "d" * 64,
    }
    prepared = execution("prepared", candidate=candidate)
    admitted = execution("admitted", candidate=candidate, proof="verified")
    started = execution("started", candidate=candidate)
    attempt = replay(start_clock(), [prepared], [admitted], [started])
    phases = attempt.executions["exec-1"]
    assert [phase.source.model_dump() for phase in phases] == [SOURCE] * 3
    assert [phase.candidate.model_dump() for phase in phases] == [candidate] * 3

    for replacement in (
        None,
        {**candidate, "capture_manifest": "c" * 64},
        {**candidate, "source": SOURCE},
    ):
        with pytest.raises(AttemptIntegrityError, match="retained authority"):
            replay(
                start_clock(),
                [prepared],
                [admitted],
                [execution("started", candidate=replacement)],
            )

    legacy = replay(start_clock(), [execution("prepared")])
    assert legacy.executions["exec-1"][0].candidate is None
    with pytest.raises(AttemptIntegrityError, match="retained authority"):
        replay(start_clock(), [execution("prepared")], [admitted])
