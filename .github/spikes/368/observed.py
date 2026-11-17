"""Use the pinned #146 signal path for controller-observed native arguments."""

import json
import os
import subprocess
import sys

_original = subprocess.Popen.__init__


def observed_init(self, args, *options, **keywords):
    _original(self, args, *options, **keywords)
    argv = list(map(os.fsdecode, args)) if isinstance(args, (tuple, list)) else [os.fsdecode(args)]
    encoded = json.dumps(argv, separators=(",", ":"), ensure_ascii=True).replace(" ", r"\u0020")
    sys._aitm146_event("child-argument", f"{self.pid} {encoded} {argv[0]}")


subprocess.Popen.__init__ = observed_init
