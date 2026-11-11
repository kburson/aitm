# #189 Design, Plan and JIT review

Signed 2026-11-10 America/Chicago (2026-11-11 UTC) by Codex `/root/pickup186`, a separate same-provider reviewer. Reviewed all 26 lines of `pickup.md`, SHA-256 `36871078bf8a44d7c2c59188621b01e158c4f97ac0881c742f6a2d254f95f286`, against the accepted #181 design and A04, and the delivered #186 reader and capture guide.

## Design verdict

Changes requested. Line 11 makes the original export digest comparison conditional on a separately declared receipt source digest. The delivered reader accepts a ref-only source for shape validation and otherwise compares the verification digest with itself. Cost needs a fixed source binding under the accepted A04 contract. Require the receipt's `source.sha256` to match `verification.source_sha256` and retain the exact receipt digest in the matching named operator's attributable registration. An opaque source ref remains useful provenance. A ref-only receipt with a self-contained digest in verification remains Unknown for Cost. The export stays private and the existing operator and registration contract supplies the assurance.

Selector isolation, matching operator and sanitized payload, chronology, source conflict, deterministic supersession, exact decimal price and separate graph coverage otherwise fit A04.

## Plan verdict

Changes requested. Add a focused case for a ref-only receipt with a matching operator and otherwise consistent verification and assert Unknown Cost. The existing mismatch, replay, supersession, source conflict, exact decimals and coverage cases otherwise cover the agreed scope.

## JIT verdict

Accepted for scope. Verified #186 Done at the recorded planning pin and its delivery merge reachable from the clean `codex/aitm-189-usage-view` checkout at `e4701f2e89d34f93f13d717199254b66aa3f0457`, matching local `origin/trunk`. The usage files are disjoint from #188's timing paths. The 3.00-hour estimate fits the four-hour cap including verification and review. Live overlap, expected-head planning publication, exact candidate CI and independent source review remain the coordinator's delivery gates. Develop is gated on the Design and Plan correction.
