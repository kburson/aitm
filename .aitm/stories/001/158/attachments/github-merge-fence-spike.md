# #158 · GitHub merge fence endpoint measurements

**Disposition.** The synchronous REST endpoint rejected the stale head and accepted the stale base in the authorized controls below. #158 qualification remains **pickup held**. The owner-authorized repository supported the endpoint controls with its OAuth owner. The qualification still requires a repository that supports the accepted rulesets and the dedicated App, reviewer, check publisher, ordinary writer, and automation identities. #159 remains held on #158 and still requires #157. The production full PR gate remains in force.

## Scope and fixture

- Accepted #158 inputs at `b62000a647dccd1343573deaddf436ca179a5177`. Raw SHA-256 values are design `4f390fc1c0f20c8c08b8be2b6ca90ccbe74d48c46e7a202a215bfb7dfd61b4d9`, plan `53c09ab58c857d04384eb9ac08e0c206c4b71b502e509b0b48ea96eaabcc5a38` and JIT `101ef7993f01e5c5e242e8c8f5945a166a7f3b207b100d2e8476f7a328678685`. [Planning tree](https://github.com/kburson/aitm/tree/b62000a647dccd1343573deaddf436ca179a5177/.aitm/stories/001/158)
- Disposable repository `kburson/aitm-158-merge-fence-a3a6eed8`, ID `1453246444`, private personal owner `kburson`. The OAuth actor had repository admin and push permissions. Each hosted write followed fresh identity and repository ID readback. The fixture default branch `refs/heads/trunk` remained at `ac75c69f3933386fdc156664d71599fd1a96c930`. The separate target and head branches contained synthetic files only.
- The fixture advertised merge commits, squash, and rebase as enabled, with auto-merge disabled. Both probes requested `merge` explicitly. Effective rules, ruleset listing, and legacy protection reads returned HTTP 403 with a private-repository entitlement error. Branch metadata reported `protected: false` and protection disabled. The account response omitted the subscription plan. OAuth's separate installation-list request returned HTTP 403 requiring GitHub App authorization. The companion JSON preserves the observations and request IDs. [Ruleset availability](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)
- The measurement window ran from `2026-11-10T22:14:07.463+00:00` to `2026-11-10T22:22:24.474+00:00` UTC, including two read-only preflight stops. The first exposed an overly specific local assertion on the App authorization error. The second recorded the private-fixture entitlement denial. Once PR #1 was open, its REST mergeability became clean while `merge_commit_sha` remained null. The run resumed on the same open PR using GraphQL `potentialMergeCommit` and the host's `refs/pull/<number>/merge`. Each recorded test merge had matching GraphQL and fetched Git OIDs, exact ordered parents, and matching tree. The resume followed verified state readback and preceded both merge submissions.
- The synchronous `PUT /repos/{owner}/{repo}/pulls/{number}/merge` selected API version `2026-03-10`. GitHub documents `sha` as the expected PR head and supplies no expected-base or stop-version parameter in this request contract. Each PUT was sent once. GitHub returned definitive responses, and REST ref, PR and independent Git readback reconciled both outcomes. [GitHub REST pull-request merge](https://docs.github.com/en/rest/pulls/pulls?apiVersion=2026-03-10#merge-a-pull-request)

## M08 supplemental control · stale head refused

PR #1 (`5249872167`, `PR_kwDOVp7H7M8AAAABOOqxJw`) targeted `refs/heads/m08-target`. The fixture pinned base `ac75c69f3933386fdc156664d71599fd1a96c930`, head `b457c31f9bbe58ae9f4d69a9b7c55736da84dc12`, and GitHub test merge `92d5284b32849b493d936d662980d39ba5535ee0` with ordered parents `B,H` and tree `6eff4325a02cdfc98e09e55852643092492f4405`. A fast-forward head push replaced `H` with its same-tree descendant `cc09b3ec534be7849b42eb945859bf3bcafa27c2`. GitHub then exposed test merge `34d870350098de40862ecd271d4d8fb87b42e761` with the new head as second parent and the same tree.

The original `sha=H` request returned **409** and `Head branch was modified. Review and try the merge again.` (request `CD2C:11366D:5A1C33:11807AB:6AF39805`). The target remained at the reserved base in REST and Git (REST requests `CD24:36EA8E:5CCD55:12178AB:6AF39803` and `CD2D:2EA2DF:59ED26:117EC33:6AF39806`). PR readback `CD30:1F25E7:5C3886:1200109:6AF39807` showed it open and unmerged. This supplemental head control **passed**.

## M09 supplemental control · stale base accepted

PR #2 (`5249895324`, `PR_kwDOVp7H7M8AAAABOOsLnA`) targeted `refs/heads/m09-target`. The fixture prebuilt `B → B′ → H` and pinned the original tuple below. After reservation the owner advanced the target from `B` to the ancestor `B′` in a fixture setup push. The head stayed at `H`. The PR was clean and mergeable on the moved base. REST PR `base.sha` and GraphQL `baseRefOid` continued to expose `B`. The run resumed on the same PR and verified `B′` through the live REST and Git target ref, GraphQL `baseRef.target.oid` and the first parent of the host test merge. The driver then sent the original `sha=H` with the merge-commit method.

| Object | Git OID | Ordered parents or tree |
| --- | --- | --- |
| Reserved base B | `ac75c69f3933386fdc156664d71599fd1a96c930` | |
| Intervening base B′ | `7c83794ccc8eede0394abca3bc58a4c1e4bc910a` | `B` |
| Reserved and current head H | `e8ba388261eaceac49013f1fe67ec2ecd42af78b` | `B′` |
| Reserved test merge | `d8e58cf819e0efbc951800f2f5226d5134acd8fc` | `B,H` |
| Test merge after base advance | `886590de9a5daa81d9618d821d5d9f33d3c555e1` | `B′,H` |
| Landed merge | `685e186e4a087ed66cad085f0d2781a5163db967` | `B′,H` |
| Tree of all three merge commits | `f95616d2421689b30c37666fdce6f387ddadada6` | |

GitHub returned **200** with `merged: true` (request `CEB9:88BDA:615BBF:12EBA1C:6AF398B8`). The merge response, GraphQL merged PR readback `CF8C:1F25E7:63E25E:137E571:6AF3991B`, target ref readback `CEBE:46D75:5D9705:121CB7E:6AF398BC`, and independent Git ref all identified the landed commit. REST PR readback `CEC8:11FF4:639501:1341D6B:6AF398BD` confirmed the PR was merged and again reported a null `merge_commit_sha`. The target read immediately before dispatch showed `B′` (request `CEAE:3086AD:66C978:13D7590:6AF398B7`). Fetching the landed commit confirmed `B′,H` and the pinned tree. The setup push completed and the changed target and host test merge were observed before dispatch. The supplemental native base control **failed**. Tree equality still allowed a different first parent. The result rules out using the synchronous REST call alone to enforce the reservation's expected base. Exclusive App-backed serialization, strict checks and protected-target retarget behavior require separate evidence.

## Accepted matrix disposition

| Case | Status | Evidence or missing condition |
| --- | --- | --- |
| M01 | Unrun | Dedicated App, independent reviewer, trusted check source and active fixture rules unavailable. |
| M02 | Unrun | Role-separated approval and trusted-source check negatives require the qualification configuration. |
| M03 | Unrun | Direct updates require scoped writer and App controls under the active rules. M09 setup used an owner push on the unprotected fixture. |
| M04 | Unrun | Ordinary collaborator and admin merge denials require the active rules and distinct writer. |
| M05 | Unrun | Write-capable ordinary automation identity and active rules unavailable. |
| M06 | Unrun | Auto-merge was disabled in repository flags. No web/API arming or terminality case ran. |
| M07 | Unrun | App-backed method denial and credential custody require the qualification configuration. |
| M08 | Unrun | The supplemental owner-token endpoint control passed. App-backed enforcement remains unmeasured. |
| M09 | Unrun | The supplemental ancestor-base case failed native binding. Divergent-base, retarget, competing exclusive merge, and rule-drift cases remain unmeasured. |
| M10 | Unrun | No driver stop/dispatch barrier was armed. |
| M11a | Unrun | No response suppression or incident-baseline ordering case ran. |
| M11b | Unrun | No provider operation overlapped a stop. Host ordering remains unproved. |

The fixture submitted no deferred merge request. Both synchronous PUTs have terminal responses and independently reconciled target state. The coordinator owns the authorized fixture deletion. This draft predates deletion verification and independent evidence review.

## Evidence custody

The local observation transcript contains the projected provider responses, request identifiers, Git commands and their output. The Git bundle preserves synthetic host and fixture Git objects for offline replay after teardown. The SHA-256 manifest records custody for the observation transcript, preflights, experiment harness, bundle and replay evidence. The published planning evidence and any closure require their own authorized delivery and readback.
