# #289 Initial hosted dispatch diagnosis

[Diagnostic run 43670107921, attempt 1](https://github.com/kburson/aitm/actions/runs/43670107921/attempts/1) ran on prior reviewed trunk `59a92a8797d47bae6c9026cbfe145b9c95a4aff0`. Product passed all 1,215 cases. The complete helper suite reported 502 passes, four failures, and 34 setup errors. The runner image CLI did not meet the verifier's pinned GitHub CLI 2.97.0 contract. The signature fixtures check that version before verifying offline evidence.

The authenticated diagnostic consumer retained failed job 132678059140 with current verification and no artifact. The diagnostic event could not enter the scheduled incident route. Complete hosted logs and the exact readback were retained. The repair restores the pinned executable in the shadow runner and leaves #103 in place.
