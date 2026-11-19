"""Read the decoder body and child-canary contexts from one pytest data file."""
import ast
import json
from pathlib import Path
import sys

from coverage import Coverage

repo, database, output = map(Path, sys.argv[1:])
product = repo / "packages/aitm-usage"
config = product / "pyproject.toml"
coverage = Coverage(data_file=str(database), config_file=str(config))
if "subprocess" not in coverage.get_option("run:patch"):
    raise ValueError("subprocess coverage is disabled")
if not database.is_file():
    raise ValueError("observed coverage data file is missing")
coverage.load()
data = coverage.get_data()

def body_lines(file, function):
    tree = ast.parse((product / "src" / file).read_bytes())
    node, = (part for part in tree.body if isinstance(part, ast.FunctionDef) and part.name == function)
    return set(range(node.body[0].lineno, node.end_lineno + 1))

def observations(suffix, wanted):
    result = []
    for source in sorted(data.measured_files()):
        if not source.replace("\\","/").endswith(suffix):
            continue
        contexts = data.contexts_by_lineno(source)
        for line in sorted(wanted.intersection(contexts)):
            result.append({"line": line, "contexts": sorted(contexts[line])})
    return result

decoder = "aitm_usage/sources/grok.py"
headless = observations(decoder, body_lines(decoder, "_headless_tokens"))
cli = "aitm_usage/cli.py"
child = observations(cli, {min(body_lines(cli,"main"))})
output.write_text(json.dumps({
    "subprocess_patch": True,
    "decoder": headless,
    "console_main_entry": child,
}, sort_keys=True, indent=2) + "\n")
