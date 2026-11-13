# #274 independent review

**Accepted for read-only admission of exact historical evidence.** The manifest SHA-256 is `ffffbd477d0cc01f33330a6a10d86fcfdc10d9d46760bcbaa06800b09447c899`. I verified all ten listed files, ran all three unit tests, and reproduced both policy outputs byte for byte from fresh authenticated GitHub reads and the pinned Git objects. [#274](https://github.com/kburson/aitm/issues/274)

| Exact evidence | Reproduced decision |
| --- | --- |
| [Full run 43366344563 attempt 1](https://github.com/kburson/aitm/actions/runs/43366344563/attempts/1), [artifact 14010642704](https://github.com/kburson/aitm/actions/runs/43366344563/artifacts/14010642704) | Reviewed observation admitted. 1,216 passing assignments, 24 verified diagnostic streams and both required native children. The verifier bound the published independent review to this tuple and checked the archive and receipt digests. |
| [Selected run 43368532756 attempt 1](https://github.com/kburson/aitm/actions/runs/43368532756/attempts/1), [artifact 14012080289](https://github.com/kburson/aitm/actions/runs/43368532756/artifacts/14012080289) | Provisional transport and observation verified. Four passing assignments, 38 verified diagnostic streams and both required native children. The verifier required the assignment and unobserved complement to reproduce the complete inventory. This policy carries no review binding. |

Each path refused all 11 mismatch controls. I verified that requested scope goes through the tuple check before GitHub evidence is fetched. A missing evidence envelope, mismatched run attempt, altered archive, unapproved observer file digest and changed policy bytes fail at their respective admission checks. The historical alternate observer IDs are real immutable objects. The controls changed metadata or bytes in memory and did not dispatch a different tree.

This prototype authenticates the consumed artifact and review only for an externally supplied approved policy digest. It validates declared observed outcomes against that policy and matches diagnostic stream bytes. It does not independently parse their event semantics or establish authorization for a new tree, policy signer, runtime, or live merge. It intentionally admits an exact historical attempt. A production gate must independently reject stale evidence relative to live admission, rebind reviewed executable dependencies and protect the policy issuer. The current receipt trust applies to reviewed exact inputs. Arbitrary candidate Python and a production selected CI gate remain unqualified. Keep #103 authoritative and preserve the #148/#267 holds.

Signed by Codex agent `/root/warning275`, independent reviewer for #274.
