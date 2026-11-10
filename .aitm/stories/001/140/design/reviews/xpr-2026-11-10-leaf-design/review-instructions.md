# Leaf design cross-provider review for #138 and #140

Use the sealed invitation and native join and submit commands. Edit only
the authorized pending reviewer response. Do not use Git or change the
artifact, implement, or publish. For every round, retrieve all current
artifact lines in fresh numbered Read calls of at most 40 lines, using
the exact invitation path. Report actual ranges through EOF. Recover
any truncated range before deciding. Later rounds check the author
dispositions against a fresh full read.

Verify the leaf against the accepted #133 design and its exact parent
plan section. Check the scope, evidence and failure boundaries, bounded
estimate, and independent implementation paths. For #138, distinguish
existing signed PR evidence from push-run comparison evidence, exact
attempt custody, and timing Unknown. For #140, check exact hosted
identity and fail-closed local snapshot and path behavior. Record
material issues with native finding IDs such as R1-F001 and accept
only once no required changes remain. This review precedes refinement
and gives no implementation or activation authority.

For broker-extractable findings use level-three Markdown headings such
as `### R1-F001 — Title` in `## Findings`. Keep required dispositions
under their exact numbered headings. In addition to resolver behavior,
check the `tia` import/namespace boundary and exact #103 test coverage and
delivery claim. The following evidence comes from source at pinned trunk
`37a22922f072e39c35434ae645a1c20692b8da01`. The workflow helper lane
explicitly runs `test_python_gate.py`, `test_pytest_evidence.py`,
`test_verify_pr.py` and `test_file_checks.py` under `tools/ci/tests`.
The coverage collector scans `tools/ci`, but `python_gate._line_totals`
sums only `policy["helpers"]`: `python_gate.py`, `pytest_evidence.py`,
`verify_pr.py`, and `file_checks.py`. A controlled locked helper run
verified that a new unmeasured `tools/ci/tia/` file leaves the policy
counts at 778/821. The paired #138 author revision specifies an implicit
`tia` namespace with no initializer, `PYTHONPATH="$PWD/tools/ci"`,
`python -m pytest` for focused tests and separate exact-head #103 and
focused evidence. Review the exact #140 artifact independently.
