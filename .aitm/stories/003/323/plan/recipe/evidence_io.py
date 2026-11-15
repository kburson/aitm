"""Small GitHub REST and raw-record helpers for the rehearsal recipe."""

import json
from pathlib import Path
import subprocess


def write(path, doc):
    Path(path).write_text(json.dumps(doc, sort_keys=True, indent=2) + "\n")


def read(path):
    return json.loads(Path(path).read_bytes())


def gh(*args, method="GET", body=None):
    cmd = ["gh", "api", "--hostname", "github.com", "--method", method, *args]
    if body is not None:
        cmd.extend(("--input", str(body)))
    return subprocess.check_output(cmd)


def route(repo, path):
    return f"repos/{repo}/{path}".rstrip("/")


def raw(repo, path):
    return gh(route(repo, path))


def get(repo, path, out):
    data = raw(repo, path)
    Path(out).write_bytes(data)
    return json.loads(data)


def pages(repo, path, key, out):
    data = gh("--paginate", "--slurp", route(repo, path))
    Path(out).write_bytes(data)
    pages = json.loads(data)
    rows = [row for page in pages for row in page[key]]
    if any(page["total_count"] != len(rows) for page in pages):
        raise ValueError("incomplete or inconsistent " + key)
    return rows
