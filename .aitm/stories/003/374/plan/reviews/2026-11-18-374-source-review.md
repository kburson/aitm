# #374 source review

## Independent review

**PASS** for the supervisor, public restore, and external Grok hook in [PR #381](https://github.com/kburson/aitm/pull/381). Base `ac756be7ce8b94ec76d84a430991e566cf23da12`, head `0c19643632c6bdffde5d7fd429c03dd0121ba896`, candidate tree `06aecaada0792e8ad38bce2b261e1c1ccd5529dd`.

- The detached owner confirms a live child through its subprocess handle and the private liveness socket. Status tolerates atomic record replacement. Stop holds the lease until the owner reaps the child and durably removes the matching record. An old LaunchAgent or stale process record requires explicit recovery. Restore requires the same project and writer exclusion and rechecks stopped state before the swap.
- The hook repeats the process and executable verification after confirming the ancestry. Linux verifies the executable observed through procfs against the file at the resolved path. Darwin preserves the existing process-reference encoding and requires repeated matching native path, birth, and file metadata.
- Exact-source independent tests passed on both platforms. Five lifecycle and restore tests passed on each. The Darwin receipt suite passed 36 tests with two Linux-only skips. The Linux receipt suite passed 38 tests, including real process ancestry from an external launch using the test carrier profile.
- Linux converts procfs start ticks with the reported boot time. A wall-clock adjustment between stage and hook can invalidate a receipt and require staging again.

## Grok review of the findings

Grok reviewed the original findings and subsequent plan revisions at the owner's request. The first review confirmed the ownership split, external Grok design, and public restore approach. It asked for explicit lease handoff, child reaping before release, stale-record recovery, private liveness proof, and separate Darwin adapter scope. The second review called out executable identity and retaining custody after kill until reap. Planning commits `bca3fe4d` and `7252b5ad` clarify those requirements. The implementation confirms the Linux executable through procfs and repeats stable observations on Darwin. It retains the expressly required external ancestry walk.
