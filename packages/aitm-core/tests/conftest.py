"""Keep imports within this regular tests package."""

import sys
from pathlib import Path

TESTS_INIT = Path(__file__).resolve().with_name("__init__.py")
loaded = sys.modules.get("tests")
if loaded is not None:
    origin = getattr(loaded, "__file__", None)
    if origin is None or Path(origin).resolve() != TESTS_INIT:
        raise ImportError("a foreign tests package is already loaded")

package_root = str(TESTS_INIT.parent.parent)
if package_root not in sys.path:
    sys.path.insert(0, package_root)
