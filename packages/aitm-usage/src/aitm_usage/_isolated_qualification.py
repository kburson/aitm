"""Controlled scratch qualification. Ordinary monitor writers never load this module."""

from __future__ import annotations

import json
import os
import platform
import secrets
import stat
import subprocess
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from hashlib import file_digest, sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import RLock, get_ident
from time import monotonic
from typing import BinaryIO
from urllib.parse import quote

from ._monitor_qualification import _InstallationProof, _LiveProfile, _LiveSourceTuple
from .ledger import LedgerError, _check_acl, _pin_directory
from .monitor_registry import Registry, _directory
from .scopes import _publish, _read_private

_NAMESPACE = "aitm-isolated-owner-proposal-v1"
_PRINCIPAL = "aitm-qualification-owner"
_REVISION_FILE = "isolated-qualification.json"
_GROK_DIGEST = "197c66a63e5ac46e07450b0ca21d141ce665050a412180f185dadfae1c7a5b2a"
_MAX_VALIDITY = timedelta(minutes=10)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()


def _refuse() -> LedgerError:
    return LedgerError("Isolated source qualification is unavailable")


def _approved_pilot_tuple(digest: str) -> _LiveSourceTuple | None:
    if digest != _GROK_DIGEST:
        return None
    return _LiveSourceTuple("grok", "grok-build-macos", "Darwin", "arm64", "1.0.77", 1)


@dataclass(frozen=True, slots=True)
class _PilotLayout:
    paths: tuple[Path, ...]
    ids: tuple[tuple[int, int], ...]

    @classmethod
    def create(
        cls, control: Path, provider: Path, workspace: Path, image: Path, capture: Path
    ) -> _PilotLayout:
        paths = (control, provider, workspace, image, capture)
        roots = tuple(_directory(str(path), private=True) for path in paths)
        parent = control.parent
        if (
            any(
                str(path) != root.path or not path.is_relative_to(parent)
                for path, root in zip(paths, roots, strict=True)
            )
            or any(path.parent != parent for path in paths[:4])
            or len({root.identity for root in roots}) != len(paths)
            or capture.parent not in (parent, provider)
        ):
            raise _refuse()
        return cls(paths, tuple(root.identity for root in roots))

    @property
    def control(self) -> Path:
        return self.paths[0]

    @property
    def capture(self) -> Path:
        return self.paths[-1]

    def native_session(self, session: str) -> Path:
        if str(Path(session).name) != session or session in ("", ".", ".."):
            raise _refuse()
        return self.capture / quote(str(self.paths[2]), safe="") / session

    def check(self) -> None:
        if self.create(*self.paths) != self:
            raise _refuse()


@dataclass(frozen=True, slots=True)
class _OpenedExecutable:
    path: Path
    stream: BinaryIO
    identity: tuple[int, int]
    sha256: str

    @classmethod
    @contextmanager
    def copy(cls, source: Path, target: Path):
        source = source.resolve(strict=True)
        with _pin_directory(target.parent) as pin:
            flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
            with os.fdopen(os.open(source, flags), "rb") as original:
                info = os.fstat(original.fileno())
                if not stat.S_ISREG(info.st_mode) or not os.path.samestat(
                    info, source.lstat()
                ):
                    raise _refuse()
                data = original.read(256 * 1024 * 1024 + 1)
                if len(data) != info.st_size or len(data) > 256 * 1024 * 1024:
                    raise _refuse()
                digest = sha256(data).hexdigest()
                if _approved_pilot_tuple(digest) is None:
                    raise _refuse()
                original.seek(0)
                if file_digest(original, "sha256").hexdigest() != digest:
                    raise _refuse()
            fd = os.open(
                target.name,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                0o500,
                dir_fd=pin.fd,
            )
            with os.fdopen(fd, "wb") as output:
                output.write(data)
                output.flush()
                os.fsync(output.fileno())
            with os.fdopen(os.open(target.name, flags, dir_fd=pin.fd), "rb") as opened:
                copied = os.fstat(opened.fileno())
                image = cls(target, opened, (copied.st_dev, copied.st_ino), digest)
                pin.check()
                image.check()
                yield image

    def check(self) -> None:
        info = os.fstat(self.stream.fileno())
        if (
            not stat.S_ISREG(info.st_mode)
            or info.st_uid != os.geteuid()
            or stat.S_IMODE(info.st_mode) != 0o500
            or info.st_nlink != 1
            or (info.st_dev, info.st_ino) != self.identity
            or not os.path.samestat(info, self.path.lstat())
        ):
            raise _refuse()
        _check_acl(self.stream.fileno())
        self.stream.seek(0)
        if file_digest(self.stream, "sha256").hexdigest() != self.sha256:
            raise _refuse()


@dataclass(frozen=True, slots=True)
class _NativeClosure:
    session: str
    prompt: str
    event: str
    process_started: datetime
    updates_sha256: str
    usage_sha256: str
    receipt_sha256: str


def _collect_host_installation(
    layout: _PilotLayout, image: _OpenedExecutable, closure: _NativeClosure
) -> str:
    if (
        platform.system() != "Darwin"
        or platform.machine() != "arm64"
        or type(closure) is not _NativeClosure
        or image.path.parent != layout.paths[3]
    ):
        raise _refuse()
    layout.check()
    image.check()
    session = layout.native_session(closure.session)
    with _pin_directory(session) as root:
        for filename, expected in (
            ("updates.jsonl", closure.updates_sha256),
            ("usage.json", closure.usage_sha256),
        ):
            raw = _read_private(root, filename)
            if raw is None or sha256(raw).hexdigest() != expected:
                raise _refuse()
    return sha256(
        _canonical(
            asdict(closure) | {"process_started": closure.process_started.isoformat()}
        )
    ).hexdigest()


def _public_signer(public: bytes) -> bytes:
    fields = public.split()
    if len(fields) < 2 or fields[0] != b"ssh-ed25519" or not 60 <= len(fields[1]) <= 80:
        raise _refuse()
    return _PRINCIPAL.encode() + b" " + fields[0] + b" " + fields[1] + b"\n"


class _Issuer:
    def __init__(
        self,
        writer: Registry,
        layout: _PilotLayout,
        image: _OpenedExecutable,
        source: _LiveSourceTuple,
        witness: str,
        closure: _NativeClosure,
        public: bytes,
    ):
        self._writer = writer
        self._lease = writer.lease
        self._layout = layout
        self._image = image
        self._root = _directory(str(writer.root), private=True)
        self._owner = _public_signer(public)
        self._witness = witness
        self._closure = closure
        self._evidence = writer.source_evidence()
        self._installation = _InstallationProof(
            _directory(str(layout.capture), private=True),
            source,
            self._evidence.pseudonymize("isolated-executable-v1", image.sha256),
        )
        self._run = secrets.token_hex(24)
        self._generation = 0
        self._owner_thread = get_ident()
        self._revoked = False
        self._deadline = 0.0
        self._expires: datetime | None = None
        self._committed: bytes | None = None
        self._lock = RLock()

    def proposal(self, operation: str, generation: int, expires: datetime) -> bytes:
        return _canonical(
            {
                "operation": operation,
                "generation": generation,
                "valid_until": expires.isoformat(),
                "owner_sha256": sha256(self._owner).hexdigest(),
                "run": self._run,
                "source": asdict(self._installation.source),
                "image_sha256": self._image.sha256,
                "image_identity": self._image.identity,
                "closure": self._witness,
                "writer": asdict(self._root),
                "physical_roots": list(
                    zip(map(str, self._layout.paths), self._layout.ids, strict=True)
                ),
            }
        )

    def _check_custody(self) -> None:
        if (
            get_ident() != self._owner_thread
            or self._writer.lease is not self._lease
            or _directory(str(self._writer.root), private=True) != self._root
        ):
            raise _refuse()
        self._layout.check()

    def _sealed(self, payload: bytes) -> bytes:
        digest = sha256(payload).hexdigest()
        revision = _canonical(
            {"proposal": json.loads(payload), "owner_proposal_sha256": digest}
        )
        signature = self._evidence.pseudonymize(
            "isolated-issuer-revision-v1", revision.decode()
        )
        return _canonical(
            {"revision": json.loads(revision), "writer_seal": signature.value}
        )

    def _verify_owner(self, payload: bytes, signature: bytes) -> None:
        if len(signature) > 4096:
            raise _refuse()
        with TemporaryDirectory(dir=self._layout.control) as path:
            signers = Path(path) / "allowed"
            detached = Path(path) / "signature"
            for location, content in ((signers, self._owner), (detached, signature)):
                fd = os.open(
                    location,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                    0o600,
                )
                with os.fdopen(fd, "wb") as out:
                    out.write(content)
            result = subprocess.run(
                [
                    "/usr/bin/ssh-keygen",
                    "-Y",
                    "verify",
                    "-f",
                    str(signers),
                    "-I",
                    _PRINCIPAL,
                    "-n",
                    _NAMESPACE,
                    "-s",
                    str(detached),
                ],
                input=payload,
                capture_output=True,
                timeout=10,
                check=False,
            )
            if (
                result.returncode != 0
                or signers.read_bytes() != self._owner
                or detached.read_bytes() != signature
            ):
                raise _refuse()

    def _commit(
        self, payload: bytes, signature: bytes, allowed: tuple[str, ...]
    ) -> int:
        """Publish the next authorized revision while the owning caller holds the lock."""
        try:
            with _pin_directory(self._writer.root) as pin:
                self._check_custody()
                self._image.check()
                proposal = json.loads(payload)
                operation = proposal["operation"]
                generation = proposal["generation"]
                expires = datetime.fromisoformat(proposal["valid_until"])
                now = datetime.now(UTC)
                if (
                    self._revoked
                    or operation not in allowed
                    or type(generation) is not int
                    or generation != self._generation + 1
                    or operation
                    not in (
                        ("activate",)
                        if self._generation == 0
                        else ("replace", "revoke")
                    )
                    or expires.utcoffset() != timedelta(0)
                    or not timedelta(0) < expires - now <= _MAX_VALIDITY
                    or payload != self.proposal(operation, generation, expires)
                    or _read_private(pin, _REVISION_FILE) != self._committed
                ):
                    raise _refuse()
                self._verify_owner(payload, signature)
                record = self._sealed(payload)
                self._check_custody()
                deadline = monotonic() + (expires - datetime.now(UTC)).total_seconds()
                if deadline <= monotonic():
                    raise _refuse()
                if not _publish(
                    pin,
                    _REVISION_FILE,
                    record,
                    replace_pending=True,
                    before_commit=self._check_custody,
                ):
                    raise _refuse()
                self._committed = record
                self._generation = generation
                self._deadline = deadline
                self._expires = expires
                return generation
        except Exception:
            raise _refuse() from None

    def revoke(self, payload: bytes, signature: bytes) -> None:
        with self._lock:
            self._commit(payload, signature, ("revoke",))
            # The last profile supplies private refusal provenance but cannot be reactivated.
            self._revoked = True
            self._deadline = 0.0

    def current(self, installation: _InstallationProof, generation: int) -> bool:
        try:
            with self._lock, _pin_directory(self._writer.root) as pin:
                self._check_custody()
                if (
                    installation is not self._installation
                    or generation != self._generation
                    or self._revoked
                    or self._expires is None
                    or monotonic() >= self._deadline
                    or datetime.now(UTC) >= self._expires
                ):
                    return False
                if (
                    _collect_host_installation(self._layout, self._image, self._closure)
                    != self._witness
                ):
                    return False
                record = _read_private(pin, _REVISION_FILE)
                if record is None or record != self._committed:
                    return False
                proposal = _canonical(json.loads(record)["revision"]["proposal"])
                return self._sealed(proposal) == record
        except Exception:
            return False


def _prepare_isolated_issuer(
    writer: Registry,
    layout: _PilotLayout,
    image: _OpenedExecutable,
    closure: _NativeClosure,
    public: bytes,
) -> _Issuer:
    if (
        writer._live_profile is not None
        or writer.root.parent != layout.control.parent
        or writer.root in layout.paths
    ):
        raise _refuse()
    source = _approved_pilot_tuple(image.sha256)
    if source is None:
        raise _refuse()
    witness = _collect_host_installation(layout, image, closure)
    return _Issuer(writer, layout, image, source, witness, closure, public)


def _install_isolated_profile(
    issuer: _Issuer, payload: bytes, signature: bytes
) -> _InstallationProof:
    """Install the exact proof after an authenticated activation or replacement."""
    with issuer._lock:
        generation = issuer._commit(payload, signature, ("activate", "replace"))
        proof = issuer._installation
        issuer._writer._live_profile = _LiveProfile(
            issuer._root,
            issuer._lease,
            issuer._evidence.pseudonymize(
                "isolated-issuer-generation-v1", f"{issuer._run}:{generation}"
            ),
            (proof,),
            lambda installation: issuer.current(installation, generation),
        )
        return proof
