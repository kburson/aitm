from collections import Counter
from copy import deepcopy
import errno
from hashlib import sha256
from io import BytesIO
import json
import os
from pathlib import Path
import stat
import tarfile
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from admission import ROOT, boundary_profile

from integrated import (
    KEYGEN, NAMESPACE, SCRATCH, allow_observed, describe_os_error, extract_runtime, native_shape,
    read_native, validate_children,
)


class NativeIntakeTest(unittest.TestCase):
    def setUp(self):
        self.argv = [KEYGEN, "-q", "-t", "ed25519", "-N", "", "-f", str(SCRATCH / "case/owner")]

    def test_generation_paths_are_scoped(self):
        self.assertEqual(native_shape(self.argv), "generate")
        for invalid in ("owner", "/tmp/owner", str(SCRATCH / "../owner"), str(SCRATCH / "case/another")):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                native_shape([*self.argv[:-1], invalid])

    def test_signing_namespace_is_exact(self):
        argv = [KEYGEN, "-Y", "sign", "-n", NAMESPACE, "-f", str(SCRATCH / "case/control/owner")]
        self.assertEqual(native_shape(argv), "sign")
        argv[4] = "changed"
        with self.assertRaises(ValueError):
            native_shape(argv)

    def test_verified_principal_and_sibling_paths_are_exact(self):
        root = SCRATCH / "case/control/tmp"
        argv = [KEYGEN, "-Y", "verify", "-f", str(root / "allowed"), "-I", "aitm-qualification-owner",
                "-n", NAMESPACE, "-s", str(root / "signature")]
        self.assertEqual(native_shape(argv), "verify")
        for index, substitute in ((6, "changed"), (10, str(root / "other/signature"))):
            wrong = list(argv)
            wrong[index] = substitute
            with self.subTest(index=index), self.assertRaises(ValueError):
                native_shape(wrong)

    def test_direct_child_lifecycle_is_required(self):
        row = {"test": "id", "phase": "setup", "arguments": [{"argument": json.dumps(self.argv), "executable": KEYGEN}],
               "exec": ["ssh-keygen"], "os_exit_status": 0, "os_exit_reason": 1}
        approved = Counter({("id", "setup", "generate"): 1})
        self.assertEqual(validate_children({4: row}, approved), [["id", "setup", "generate", 1]])
        for key, value in (("os_exit_status", 2), ("os_exit_reason", 2), ("exec", ["ssh-keygen"] * 2),
                           ("exec", ["unexpected"]), ("phase", "call")):
            modified = deepcopy(row)
            modified[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                validate_children({4: modified}, approved)

    def test_failed_setup_and_call_still_enter_teardown(self):
        for failed in ("setup-failed", "call-failed"):
            with self.subTest(failed=failed):
                mock = SimpleNamespace()
                read_native(mock, lambda *args: ([], {15: {}}))
                source = f"1 E 18 start id\n2 E 18 {failed} id\n3 P 18 15\n".encode()
                _, children = mock.parse_trace(source, 18, "")
                self.assertEqual(children[15]["phase"], "teardown")

    def test_observer_rejects_an_ambiguous_origin_filter(self):
        anchor = '&& copyinstr(arg0) == "child-argument")'
        observer = SimpleNamespace(dtrace_program=lambda *args: anchor, parse_trace=lambda *args: ([], {}))
        allow_observed(observer)
        self.assertIn('"observed_init"', observer.dtrace_program())
        for body in ("", anchor * 2):
            observer = SimpleNamespace(dtrace_program=lambda *args: body, parse_trace=lambda *args: ([], {}))
            allow_observed(observer)
            with self.assertRaises(ValueError):
                observer.dtrace_program()


class BoundaryProfileTest(unittest.TestCase):
    def test_metadata_grant_applies_to_the_literal_admission_root_only(self):
        self.assertNotIn("allow file-read-metadata", boundary_profile())
        rules = [line for line in boundary_profile(admitted_executables=(KEYGEN,)).splitlines()
                 if line.startswith("(allow file-read-metadata")]
        self.assertEqual(rules, [f'(allow file-read-metadata (literal "{ROOT}"))'])


class RuntimeRestoreTest(unittest.TestCase):
    def test_symlink_mode_is_restored_under_private_umask(self):
        with TemporaryDirectory() as stage:
            root = Path(stage)
            data = b"verified synthetic runtime"
            files = {
                "runtime": {"kind": "directory", "mode": "0755"},
                "runtime/regular": {"kind": "file", "mode": "0644", "sha256": sha256(data).hexdigest()},
                "runtime/symlink": {"kind": "symlink", "mode": "0755", "target": "regular"},
            }
            archive = root / "runtime.tar.gz"
            with tarfile.open(archive, "w:gz") as bundle:
                for name, details in files.items():
                    entry = tarfile.TarInfo(name)
                    entry.mode = int(details["mode"], 8)
                    if details["kind"] == "directory":
                        entry.type = tarfile.DIRTYPE
                    elif details["kind"] == "symlink":
                        entry.type = tarfile.SYMTYPE
                        entry.linkname = details["target"]
                    else:
                        entry.size = len(data)
                    bundle.addfile(entry, BytesIO(data) if entry.isfile() else None)
            out = root / "extract"
            out.mkdir(mode=0o700)
            old = os.umask(0o077)
            try:
                extract_runtime(archive, out, files, [Path("runtime")])
            finally:
                os.umask(old)
            for name, details in files.items():
                self.assertEqual(stat.S_IMODE((out / name).lstat().st_mode), int(details["mode"], 8))
            self.assertEqual((out / "runtime/symlink").readlink(), Path("regular"))

    def test_diagnostic_pins_the_spike_frame_and_relative_path(self):
        private = Path("/private/tmp/368-evidence")
        hidden = private / "extracted/runtime"
        refusal = PermissionError(errno.EACCES, "refused", hidden)
        with patch.object(tarfile, "open", side_effect=refusal):
            try:
                extract_runtime(hidden, hidden, {}, [])
            except PermissionError as received:
                details = describe_os_error(received, private)
            else:
                self.fail("permission refusal did not reach diagnostic")
        self.assertEqual(details["errno"], errno.EACCES)
        self.assertEqual(details["spike"]["function"], "extract_runtime")
        self.assertEqual(details["path"], "private/extracted/runtime")
        self.assertNotIn("path", describe_os_error(PermissionError(errno.EACCES, "refused", "/private/unapproved"), private))


if __name__ == "__main__":
    unittest.main()
