# #274 Exact-tree observation admission

The read-only prototype consumed a previously reviewed full macOS/APFS run and a separate provisional selected run. It used authenticated GitHub reads, pinned Git objects and independent review bytes. The policy admits evidence only for its exact tuple. It grants no CI, merge or deployment authority.

| Case | Result |
| --- | --- |
| [Full run 43366344563, attempt 1](https://github.com/kburson/aitm/actions/runs/43366344563/attempts/1) | Admitted as reviewed historical evidence. Checked 1,216 passing assignments, two required native children and all 24 retained streams. |
| [Selected run 43368532756, attempt 1](https://github.com/kburson/aitm/actions/runs/43368532756/attempts/1) | Verified provisionally while the selected evidence review was pending. Checked the four exact selected IDs, the unobserved complement, two required native children and all 38 retained streams. The verifier returned a distinct provisional status. |

Each run refused 11 deterministic controls. They changed the product tree, observer head, observer tree, controller file digest, requested attempt, GitHub attempt metadata, assignment, execution mode, archive bytes or approved policy bytes, or supplied a worker assertion without authoritative evidence. The requested tuple is rejected before evidence evaluation when it differs from policy. The changed observer tree and head are immutable Git objects from the previous trial. The inputs were changed in memory and did not dispatch another candidate. This tests intake decisions on live artifacts rather than hostile candidate execution.

## Scope and authority

The positive full policy binds the reviewed product commit and tree, exact observer commit and tree, locked inputs, workflow and job identity, macOS runner class and recorded APFS boundary, inventory and assignment, GitHub run and attempt, and exact artifact and receipt digests. The downloaded archive and its diagnostic streams are verified byte for byte. The published independent review links the full tuple and its digests. The same digest checks detect a policy modified in place when the expected digest is supplied separately. In this prototype that digest is an explicit operator argument. No policy signer, key custody, rotation or revocation was implemented.

For a production shadow trial, put policy authorization in a separately controlled signed manifest or versioned policy store. Verify the issuer independently of the test worker and pin the exact payload digest and repository/workflow identity. GitHub's artifact digest and job log bind downloaded bytes in this trial. A verified artifact attestation would add cryptographic provenance for bytes and workflow, with no additional guarantee about what happened inside a Python process. The two spike workflows have no attestation step. [GitHub artifact attestations](https://docs.github.com/en/actions/concepts/security/artifact-attestations)

This approach is suitable for consuming evidence after an exact execution input set has been independently reviewed. A future exact-tree candidate must additionally carry reviewed executable dependency closure, including the tests, candidate code, collection hooks, plug-ins, dynamically imported modules and native dependencies, along with runtime and observer identity. A new executable closure, changed observer, stale attempt or incompatible assignment needs refusal or fresh review. The admitted trust model presumes the approved executable closure behaves as reviewed. Source disk immutability and caller metadata alone cannot establish independent outcomes for arbitrary candidate code running inside pytest.

## Recommendation

Retain this verifier as a feasibility result and use it as an intake design for an explicitly reviewed shadow mode if that trust model is accepted. Keep #103 authoritative for normal PRs. #146's original production contract still requires a boundary that survives arbitrary candidate Python or a reviewed change to scope. The separate advisory-warning experiment can progress without treating candidate-side observations as merge authority. #148 and #267 remain on hold.

## Reproduction

Run the proof with a repository clone that contains the exact observation commits and planning publication, GitHub CLI authenticated to the repository, and Python 3.13 or newer.

```sh
python3 -m unittest -v
python3 run.py --repo-root "$AITM_REPO" --policy full-policy.json \
  --approved-policy-sha256 2ddcddc6d8395730829619df99f1d90ad6947c91bb47faf03c43fe83e1d6220a
python3 run.py --repo-root "$AITM_REPO" --policy selected-provisional-policy.json \
  --approved-policy-sha256 7ddb15049568fd0051062d510c9a87718c69ba02351c441aaae3768cb3b3ca0e \
  --provisional
```
