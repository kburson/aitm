# #227 independent qualification review · revision 2

**Verdict — accepted.** Signed 2026-11-11 UTC by Codex `/root/pickup186`, a separate reviewer from the implementer. The exact revised evidence passes the read-only C01 qualification. Native admission, automatic publication, fenced production Cost and hosted viewer qualification remain assigned to their later gates.

| Reviewed artifact | SHA-256 |
| --- | --- |
| `qualification.md` | `46063c751ca157875c4852da21d2a2ff1a184064f5394b13c1425e8f26de5469` |
| `qualification.json` | `c1bcaa084074749e7717043d9e402d29bf9626032ee70eb6c1059ea8caa507bf` |
| `shared-fixtures.json` | `0be5a5036654abb09ba32d0277428ee41564d5de863300fa2202fa34a1c88b80` |

Compared with accepted #227 Design, Plan and JIT and parent C01. The initial changes-requested review is retained locally in `qualification-review-v1.md`, SHA-256 `6be1f15dea01b0dbb2fdccf9d311ace5bb1821fc67ebca9dd94f82668f261e2f`. [Accepted C01](https://github.com/kburson/aitm/blob/20ae85e8e38fd3417e1ec0acd6e4e9f99b5cb22b/.aitm/stories/001/181/plan/2026-11-11-181-slice-c-implementation-plan.md#c01-freeze-input-and-parity-evidence)

## Findings resolved

1. The manifest now carries project, ancestry, actor, logical turn, role, attempt, phase, coverage and explicit hold outcomes. The additional adjacent turn and nested tool share their logical turn and scope. The six-case runner reproduced the exact manifest bytes against the delivered code. The shared evidence remains synthetic, and the pre-held timing case demonstrates downstream exclusion while native admission stays with C03.
2. The paired local test builds two distinct pinned views with different admitted timing evidence and the same selected usage receipt digest. Epic Actual goes from 3,600,000 to 3,660,000 ms and Cost stays exactly $0.0125. I independently reconstructed the pair from the manifest in a separate disposable Git fixture and verified the same epic delta, the corresponding #186 direct Actual change from 900,000 to 960,000 ms, and the unchanged exact story and inclusive Cost. The revision note preserves the initial unsupported-supersession result and explains why the final input is an adjacent turn.

## Historical parity and live limits

The published initial machine record has the exact first-round digest. Its only differences from the revised machine record are the fixture digest, paired readback and fixture revision description under verification. Historical and capability evidence is unchanged. The first-round independent checks reproduced all five historical artifacts, all 27 admitted timing receipt digests and the legacy seed, and all nine reported board rounding mappings. #181 retains 10,605,711 ms partial Actual, with 13,754 ms direct and 10,591,957 ms descendant. #111 retains 774,000 ms implementation elapsed and Unknown all-phase elapsed. The dashboard test log reports 61 passing tests.

Live readback showed #203 Closed Completed and Done at PR #211 merge `b0f8ac79b8bd3f178b1d47dc2e66650f1f54e0d5`. The current-source disposable report probe reproduced exit 1 and `monitor-report-unavailable`. #123, #124 and C44 #51 remain open. The qualification records the existing manual Project values, the absent Elapsed and Owner wait fields, and independent Cost coverage. [Initial machine record](https://github.com/kburson/aitm/blob/3cca154e98014483ceb2d9bc42a870f180ccbad1/.aitm/stories/002/227/attachments/qualification.json) · [Fenced report](https://github.com/kburson/aitm/issues/123) · [Compatible export](https://github.com/kburson/aitm/issues/124) · [Core usage ingress](https://github.com/kburson/aitm/issues/51)
