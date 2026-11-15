# #289 Pre-admission controls

Candidate `bc68225a55fad492f99618a724e1a297b1269a0d` and tree `ab2358a0db272ec60310999f407c5c05f07e09ae`. The isolated consumer and adjacent advisory, incident, recovery and verifier suites passed 149 tests. Bash syntax, Ruff checks and unchanged #103 workflow and policy verification passed. The runner refused a feature/planning checkout ref before producing a receipt.

Fixtures exercise a full green result, missing artifacts, mismatched job attempts, delayed delivery, an older result on a different trunk revision, pending job registration, and canonical slot timestamp drift. An authenticated failed job survives missing artifacts. The bridge sends only verified scheduled observations to the existing shadow store and exercises warning delivery and an explicit acknowledgment after fresh green. Manual dispatch is diagnostic and cannot enter that bridge. Actual schedule qualification follows checked deployment.
