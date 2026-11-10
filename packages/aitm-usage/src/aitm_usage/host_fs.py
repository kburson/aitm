"""Host filesystem operations for private state and writer guards."""

import ctypes
import errno
import os
import pwd
import stat
import sys
from functools import cache
from pathlib import Path

_ACL_TYPE_EXTENDED = 0x100
_ACL_EMPTY = b"!#acl 1\n"
# The default macOS home ancestry carries this non-inheriting delete protection.
_ACL_DENY_DELETE = (
    _ACL_EMPTY + b"group:ABCDEFAB-CDEF-ABCD-EFAB-CDEF0000000C:everyone:12:deny:delete\n"
)


class HostFilesystemError(RuntimeError):
    """The host could not safely access or publish private filesystem state."""


@cache
def _mac_acl() -> ctypes.CDLL:
    try:
        lib = ctypes.CDLL(None, use_errno=True)
        lib.acl_get_link_np.argtypes = [ctypes.c_char_p, ctypes.c_int]
        lib.acl_get_link_np.restype = ctypes.c_void_p
        lib.acl_get_fd_np.argtypes = [ctypes.c_int, ctypes.c_int]
        lib.acl_get_fd_np.restype = ctypes.c_void_p
        lib.acl_to_text.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ssize_t)]
        lib.acl_to_text.restype = ctypes.c_void_p
        lib.acl_free.argtypes = [ctypes.c_void_p]
        lib.acl_free.restype = ctypes.c_int
    except (AttributeError, OSError):
        raise HostFilesystemError("Private ACL validation is unavailable") from None
    return lib


def _check_mac_acl(target: Path | int, *, ancestor: bool) -> None:
    lib = _mac_acl()
    ctypes.set_errno(0)
    if isinstance(target, Path):
        acl = lib.acl_get_link_np(os.fsencode(target), _ACL_TYPE_EXTENDED)
    else:
        acl = lib.acl_get_fd_np(target, _ACL_TYPE_EXTENDED)
    if not acl:
        if ctypes.get_errno() == errno.ENOENT:
            return
        raise HostFilesystemError("Unable to validate private ACL")
    try:
        text = lib.acl_to_text(acl, None)
        if not text:
            raise HostFilesystemError("Unable to classify private ACL")
        try:
            value = ctypes.string_at(text)
        finally:
            lib.acl_free(text)
    finally:
        lib.acl_free(acl)
    if value != _ACL_EMPTY and not (ancestor and value == _ACL_DENY_DELETE):
        raise HostFilesystemError("Unsafe private ACL")


def _check_linux_acl(target: Path | int) -> None:
    getxattr = getattr(os, "getxattr", None)
    if getxattr is None:
        raise HostFilesystemError("Private ACL validation is unavailable")
    is_path = isinstance(target, Path)
    try:
        info = target.lstat() if is_path else os.fstat(target)
    except OSError:
        raise HostFilesystemError("Unable to validate private ACL") from None
    attributes = ("system.posix_acl_access",)
    # Only directories can carry a default ACL for newly created descendants.
    if stat.S_ISDIR(info.st_mode):
        attributes += ("system.posix_acl_default",)
    for attribute in attributes:
        try:
            getxattr(target, attribute, follow_symlinks=not is_path)
        except OSError as exc:
            if exc.errno != errno.ENODATA:
                raise HostFilesystemError("Unable to validate private ACL") from None
        else:
            raise HostFilesystemError("Unsafe private ACL")


def check_private_acl(target: Path | int, *, ancestor: bool = False) -> None:
    """Check the ACL on a path without following its leaf, or on an open descriptor."""
    if sys.platform == "darwin":
        _check_mac_acl(target, ancestor=ancestor)
    elif sys.platform == "linux":
        _check_linux_acl(target)
    else:
        raise HostFilesystemError("Private ACL validation is unavailable")


def account_control_root(uid: int) -> Path:
    """Resolve the per-account writer guard independently of the environment."""
    if sys.platform == "darwin":
        suffix = Path("Library", "Application Support")
    elif sys.platform == "linux":
        suffix = Path(".local", "state")
    else:
        raise HostFilesystemError("Unable to resolve private account control location")
    try:
        home = Path(pwd.getpwuid(uid).pw_dir)
    except (KeyError, OSError):
        raise HostFilesystemError(
            "Unable to resolve private account control location"
        ) from None
    if not home.is_absolute():
        raise HostFilesystemError("Unable to resolve private account control location")
    return home / suffix / "aitm-usage-control"


@cache
def _native_rename(symbol: str):
    try:
        rename = getattr(ctypes.CDLL(None, use_errno=True), symbol)
    except (AttributeError, OSError):
        raise HostFilesystemError("Atomic filesystem rename is unavailable") from None
    rename.argtypes = [
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_uint,
    ]
    rename.restype = ctypes.c_int
    return rename


def _rename_entries(
    src_dir: int, src: str, dst_dir: int, dst: str, *, exchange: bool
) -> bool:
    for name in (src, dst):
        if name in ("", ".", "..") or "/" in name or "\0" in name:
            raise HostFilesystemError("Atomic filesystem rename requires entry names")
    if sys.platform == "darwin":
        rename = _native_rename("renameatx_np")
        flags = 0x2 if exchange else 0x4  # RENAME_SWAP / RENAME_EXCL
    elif sys.platform == "linux":
        rename = _native_rename("renameat2")
        flags = 0x2 if exchange else 0x1  # RENAME_EXCHANGE / RENAME_NOREPLACE
    else:
        raise HostFilesystemError("Atomic filesystem rename is unavailable")
    source, destination = os.fsencode(src), os.fsencode(dst)
    ctypes.set_errno(0)
    if rename(src_dir, source, dst_dir, destination, flags) == 0:
        return True
    if not exchange and ctypes.get_errno() == errno.EEXIST:
        return False
    raise HostFilesystemError("Unable to rename private entries atomically")


def publish_noreplace(src_dir: int, src: str, dst_dir: int, dst: str) -> bool:
    """Move an entry atomically, returning False only for an existing destination."""
    return _rename_entries(src_dir, src, dst_dir, dst, exchange=False)


def exchange_entries(src_dir: int, src: str, dst_dir: int, dst: str) -> None:
    """Swap two entries atomically or raise. Callers sync the affected parents."""
    _rename_entries(src_dir, src, dst_dir, dst, exchange=True)
