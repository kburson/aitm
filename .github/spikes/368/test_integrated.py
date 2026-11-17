from collections import Counter
from copy import deepcopy
import json
from types import SimpleNamespace
import unittest

from integrated import KEYGEN, NAMESPACE, SCRATCH, allow_observed, native_shape, read_native, validate_children


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


if __name__ == "__main__":
    unittest.main()
