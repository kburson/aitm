# #139 implementer correction handoff

I corrected the three source review findings against PR #197 head
`6687ba0262df6eb99e76c66509bf32262017d5b5`. Develop readback was
`8961f1bac3e273f4402bb12efd2d70adbd7fd6ee`.

- Collection validation requires a final `]` when a pytest parameter suffix
  opens. The locked pytest producer and focused cases confirm that its interior
  can contain unmatched brackets, slashes, delimiters and Unicode.
- Hosted binding validation now checks fully qualified Git ref syntax in the
  offline projection. The 402 synthetic ref probes agreed with Git 2.42.1.
- Suite policy validation requires the exact `cli-help` and `service-one-shot`
  selectors and label set. The regression cases cover transposition and
  omission from both policy documents.

The focused correction reproduced 16 failures on the reviewed source and
passed all 47 cases after correction. The verified #182 replay and 1,049-row
local inventory were byte-identical before and after the correction. The
frozen correction is `ffed933cc343700e65a83bbebcaa344071c05308`, tree
`d1c8cc8a02a959c9fd310fd854ead10f5daf6028`, with 1,183 passing tests on
the staged tree that became that exact commit.

The #194 target refresh merged exact `c4ea6b0d6c548830a3ad05d0bb76ec48625d1ca2`
into the corrected branch and preserved all three owned blobs byte-for-byte.
Candidate `36f700e330c07dc8750dfcfa9fe8841c49e35877` has tree
`13f338628918c14f41b56f0c1ef52649b126fc41`. Its first parent is the frozen
correction, and its second parent and target merge-base are exact #194 trunk.
The correction remains a descendant of the previously reviewed PR head.

The clean #194 target snapshot produced 877 exact product and CLI IDs and
182 helper IDs. The product set adds ten tests in the existing install module
and removes none. Product and CLI IDs match the verified #194 push. Helpers
match the retained advisory helper collection. The 1,059-obligation local
advisory inventory has SHA-256
`014424d5c140c939f6ef19c9cd4c7b5a05cc25c979050aefe3ed77526f8f73f9`.
The five comparison projections, original outcomes and coverage receipts
retain their separate provenance.

The exact candidate checkout was clean before and after 1,193 passing tests.
Focused and neighboring runs passed 47 and 87 cases respectively. Product
and tooling Ruff, actionlint and tracked-file checks passed. Raw replay and
test outputs remain in private custody. Fresh hosted verification and
independent source review apply to the refreshed candidate.

Signed by `codex-collaboration:/root/impl139`, original #139 implementer.
