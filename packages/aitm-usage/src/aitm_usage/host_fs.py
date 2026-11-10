"""Host filesystem checks for private state and writer guards."""

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
    """The host could not establish safe private filesystem access."""


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
