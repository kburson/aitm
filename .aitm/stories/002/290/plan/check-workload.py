from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

root = Path(sys.argv[1])
receipt = json.loads(Path(sys.argv[2]).read_text())
s = importlib.util.spec_from_file_location("benchmark", Path(__file__).with_name("benchmark.py"))
m = importlib.util.module_from_spec(s)
s.loader.exec_module(m)
plan = m.build_manifest(root, receipt, 1203)
assert plan == m.build_manifest(root, receipt, 1203)
assert plan["assignment_count"] == 3020
full = plan["cohorts"]["full"]
added = plan["cohorts"]["projected"]
assert len(set(full)) == len(full) == 1817
assert len(set(added)) == len(added) == 1203
assert set(added) < set(full)
assert {x.split("::")[0] for x in added} == {x.split("::")[0] for x in full}
required = m.required_ids(root)
assert required <= set(added)
assert all(m.digest_text(x) == sha256(("\n".join(x)+"\n").encode()).hexdigest() for x in (full,added))
for invalid in (0, 1818):
    try:
        m.build_manifest(root, receipt, invalid)
    except ValueError:
        pass
    else:
        raise AssertionError(f"invalid sample size {invalid} accepted")
