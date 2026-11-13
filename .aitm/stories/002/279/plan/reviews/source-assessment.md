# #279 signed independent source assessment

**Source verdict: no material findings.** Signed by OpenAI Codex, independent review agent `/root/review148`. I reviewed all changed files in a separate exact-head export and validated the operator's shadow recovery using actual GitHub and protected planning evidence. Formal admission depends on the exact #103 evidence.

- [PR #284](https://github.com/kburson/aitm/pull/284) targets literal `trunk` at base `8148a449afc6596d09e6a4ae5f3543fea70a903d`.
- Candidate head `2add334f14cd95abc6103f73cca7d9de17ef2905`.
- Tested synthetic merge `fe72c76c71c861e4cbb1875bef5fabf9c03333dd`.
- Candidate and tested tree `80037776910c7e5a3eefaa3a6aca0375a790d5fe`.
- Reviewed plan SHA-256 `6b15d6b03e4eba2a64f9853fc320314200de35f7b201d582bee7c2a301be26f4`.
- Independent plan review SHA-256 `3c67edcd2b3668110709a402777ea7b88b12a9754fcf1201f0b9a8b1abf9cd7b`.

The repair path verifies the operator-selected delivery receipt and accepting independent review against exact retained blobs at a commit reachable from protected planning. It cross-checks the #103 premerge receipt, GitHub merged PR, exact head, and ordered base/head parents and matching tree for the synthetic and landed commits. A serialized #277 read independently establishes a complete current green push newer than the incident, on the exact landed protected trunk after the repair merge. The infrastructure-only route requires an explicit operator reason and time, no retained authenticated failure for the incident, and a fresh same-SHA green. [#103](https://github.com/kburson/aitm/issues/103)

An explicit check issues a fresh proof token. Acknowledgment rechecks the repair and current push evidence under the same SQLite transaction and binds exact attempt, artifact ID and digest, start time, incident version and token. Unavailable, stale, rolled-back or conflicting observations cannot acknowledge. A failed acknowledgment cannot rearm an invalidated token. Late authenticated failure can clear stale active recovery even while current-target verification is unavailable. Successful acknowledgment is retained across later incidents. The operator owns the actual pause, repair merge and resume decisions.

An isolated exact-head suite passed **186 tests** across recovery, incident, advisory, policy and verifier. Ruff lint and formatting and exact-range Git whitespace checks passed. I independently repeated the newer diagnostic-red revocation case and verified that the old green token cannot acknowledge.

The isolated shadow rehearsal verified the immutable #278 delivery receipt and accepting review, the actual landed repair PR #283 and the current protected trunk push `43416445402/1`. Trusted push replay used artifact `14032945742`, SHA-256 `8f578baffc7781ae7e5c0f3154efaed81725d2db856eab25a084ca21dc164c9d`. The rehearsal kept the synthetic incident active through successful check, then closed it only after explicit shadow-operator acknowledgment. It used a disposable database. The independent rehearsal output SHA-256 is `032e144f1eabb38024dd95381f492a40a97a2bbd029e0ec2383ea8c13c3a7526`. [Repair delivery receipt](https://github.com/kburson/aitm/blob/42ae4ea8215432618da5cc610256d345db5f2034/.aitm/stories/002/278/plan/delivery.json) · [Post-merge push](https://github.com/kburson/aitm/actions/runs/43416445402/attempts/1)
