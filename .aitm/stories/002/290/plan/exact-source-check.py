"""Compare each measured source export with the exact protected Git tree."""
from hashlib import sha1, sha256
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

repo, bench = map(Path, sys.argv[1:3])
sha = sys.argv[3]
entries = subprocess.check_output(["git", "-C", str(repo), "ls-tree", "-rz", sha])
check = {"sha": sha, "tracked_paths_sha256": sha256(entries).hexdigest(), "layouts": {}}
for layout in ("source-1", "source-3"):
    count = 0
    for row in entries.rstrip(b"\0").split(b"\0"):
        metadata, name = row.split(b"\t", 1)
        mode, kind, expected = metadata.decode().split()
        path = bench / layout / os.fsdecode(name)
        assert kind == "blob"
        if mode == "120000":
            assert path.is_symlink()
            contents = os.fsencode(os.readlink(path))
        else:
            bits = path.lstat().st_mode
            assert stat.S_ISREG(bits)
            assert bool(bits & stat.S_IXUSR) == (mode == "100755")
            contents = path.read_bytes()
        header = f"blob {len(contents)}\0".encode()
        assert sha1(header + contents).hexdigest() == expected, str(path)
        count += 1
    check["layouts"][layout] = count
print(json.dumps(check, sort_keys=True, indent=2))
