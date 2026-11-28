"""Run one exact captured candidate through durable execution admission."""

from hashlib import file_digest
from json import dumps
from pathlib import Path
from subprocess import DEVNULL, Popen
from tempfile import TemporaryDirectory, mkdtemp
from uuid import uuid4

from aitm_core.execution.admission import AdmissionService, ExecutionRequest
from aitm_core.execution.executor import (
    ExecutionResult,
    Executor,
    ProcessOutcome,
    dispatch,
)
from aitm_core.models.binding import StoryRef
from aitm_core.models.common import CommandResult, LocalOutcome
from aitm_core.services import preflight_policy
from aitm_core.setup.journal import state_directory
from aitm_core.store.installation import Installation
from aitm_core.store.objects import GitCommandError
from aitm_core.store.workspace import BindingConflict, Workspace
from aitm_core.verification.capture import _discard, capture_inputs
from aitm_core.verification.lanes import LaunchResources, select_lane
from aitm_core.verification.provision import provision, validate_environment
from aitm_core.verification.receipts import VerificationReceipt

EXECUTOR = "core.managed-verification/v1"


def _log_digest(path: Path) -> str:
    with path.open("rb") as stream:
        return file_digest(stream, "sha256").hexdigest()


def verification_command(
    execution: ExecutionResult, receipt: Path | None
) -> CommandResult:
    command = execution.command
    local = command.local
    evidence = command.evidence
    if receipt is not None:
        evidence = (dumps({"receipt": str(receipt)}), *evidence)
    if local == LocalOutcome.COMPLETED:
        if receipt is None:
            local = LocalOutcome.UNAVAILABLE
            evidence = (*evidence, "The claimed launch has no qualified receipt.")
        elif not execution.effective:
            local = LocalOutcome.REFUSED
    return command.model_copy(update={"local": local, "evidence": evidence})


def run_verification(
    installation: Installation,
    story: int,
    binding_id: str,
    generation: int,
    session: str,
) -> CommandResult:
    operation = uuid4().hex

    def result(local: LocalOutcome, reason: str, pending: tuple[str, ...] = ()):
        return CommandResult(
            operation_id=operation, local=local, pending=pending, evidence=(reason,)
        )

    capture = None
    try:
        checked = preflight_policy(installation)
        policy = checked.policy
        if checked.outcome != LocalOutcome.COMPLETED or policy is None:
            return result(
                LocalOutcome.UNAVAILABLE, "Current verification policy is unavailable."
            )
        test = policy.config.test
        lane = select_lane(test.assurance)
        capability = lane.probe()
        if capability.assurance != test.assurance:
            return result(LocalOutcome.UNAVAILABLE, capability.reason, ("lane-probe",))

        workspace = Workspace(installation)
        with workspace.lock():
            binding = workspace.require(
                StoryRef(story=story), binding_id, generation, session
            )
        capture = capture_inputs(installation, binding, policy)
        prepared = provision(installation, binding, policy, capture, offline=True)
        environment = prepared.prepared
        if environment is None:
            return result(
                LocalOutcome.UNAVAILABLE,
                prepared.reason or "Run aitm test prepare first.",
            )

        def inputs_current():
            return (
                validate_environment(
                    installation, binding, policy, capture, environment
                ).status
                == "ready"
            )

        def verify_capture(candidate):
            return candidate.candidate == capture.candidate and inputs_current()

        request = ExecutionRequest(
            story=story,
            attempt=capture.manifest.attempt,
            generation=generation,
            binding=binding_id,
            session=session,
            request_id=operation,
            action_key="core.verify.local-pre-push",
            executor=EXECUTOR,
            candidate=capture.candidate,
        )
        with TemporaryDirectory(prefix="aitm-verification-") as scratch:
            launch = lane.command(
                LaunchResources(capture, environment, Path(scratch), test.command)
            )
            service = AdmissionService(installation, verify_capture=verify_capture)
            decision = service.admit(request)
            admission = decision.admission
            if admission is None:
                return decision.command
            logs = state_directory(installation.repository) / "verification" / "runs"
            logs.mkdir(parents=True, exist_ok=True, mode=0o700)
            directory = Path(mkdtemp(prefix=f"{request.execution_id}-", dir=logs))
            stdout = directory / "stdout.log"
            stderr = directory / "stderr.log"
            receipt_path = directory / "receipt.json"

            def start(_request):
                with stdout.open("xb") as out, stderr.open("xb") as err:
                    process = Popen(
                        launch.argv,
                        cwd=launch.cwd,
                        env=launch.environment,
                        stdin=DEVNULL,
                        stdout=out,
                        stderr=err,
                        start_new_session=True,
                    )

                def wait():
                    code = process.wait()
                    verdict = "passed" if code == 0 else "failed"
                    if not inputs_current():
                        verdict = "diagnostic"
                    receipt = VerificationReceipt(
                        request=request,
                        admission_commit=admission.admission_commit,
                        source=request.candidate.source,
                        capture_manifest=capture.manifest.digest,
                        policy_digest=policy.source.digest,
                        environment_identity=environment.receipt.identity.digest,
                        environment_inventory=environment.receipt.inventory_digest,
                        selected_assurance=test.assurance,
                        proven_assurance=capability.assurance,
                        command=launch.argv,
                        result=verdict,
                        exit_code=code,
                        stdout_sha256=_log_digest(stdout),
                        stderr_sha256=_log_digest(stderr),
                    )
                    proof = receipt.retain(receipt_path)
                    return ProcessOutcome(
                        "passed" if verdict == "passed" else "failed", proof
                    )

                return wait

            executed = dispatch(service, admission, Executor(EXECUTOR, start))
            return verification_command(
                executed, receipt_path if receipt_path.is_file() else None
            )
    except BindingConflict as error:
        return result(LocalOutcome.REFUSED, str(error))
    except (OSError, ValueError, GitCommandError) as error:
        return result(LocalOutcome.UNAVAILABLE, str(error))
    finally:
        if capture is not None:
            _discard(capture.directory)
