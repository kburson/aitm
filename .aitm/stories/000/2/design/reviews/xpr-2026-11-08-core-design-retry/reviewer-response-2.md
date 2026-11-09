---
schema: "aitm.review-response/v0"
level: "xpr"
story: 2
role: "reviewer"
round: 2
artifact_path: ".aitm/stories/000/2/design/core-design.md"
artifact_base_commit: "63c7e85d66153db6dc03e5aa41fc8d8191845632"
artifact_digest: "sha256:a21126bb83c00fcc6eda84d7a603c030c926f7667d700acbab12291488a94102"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  effort: "high"
reviewer_session: "sha256:e0d3511c0e8892f6656236e16d87ffc3fe607a88aa81d9beda23cebc6be44f01"
session_identity_kind: "native-fingerprint"
started_at: "2026-11-09T06:11:17.385Z"
submitted_at: "2026-11-09T06:13:39.559Z"
start_basis: "prior-submit"
start_source: "author-response-1.md"
finding_ids: ["R2-F001", "R2-F002"]
answered_finding_ids: []
native_source: "native/spec/2026-11-09-core-design-review-095b15003bea70559dd3ce3bb285292a/review-095b15003bea70559dd3ce3bb285292a-reviewer-response-2.md"
native_source_digest: "sha256:3bc7995e2e452a255d2b4649c5696ddb1c6c6432937825863bca243937daabf7"
---

Mode: `normal`

## Summary

Revisions requested. Round 2 of the independent cross-provider (XPR) review by an Anthropic model. As the author response asked, I re-read the entire current FUR at the digest in the frontmatter above, not just a patch. That included every edit derived from the U observations and every acceptance row. I checked it against the author response, the parent architecture and my round-1 findings. I made no network calls. Statements about host platforms are reviewer knowledge and are labelled where they matter.

**Round-1 findings, verified against the current FUR:**

- **R1-F001 — resolved in substance.** Lines 433–437 now specify a private export outside registered worktrees, `[test] inputs` with capture-time expansion and digests, separate writable roots, a prepared environment, and diagnostic fallback. Line 319 now limits the no-worktree rule to registered story worktrees. The new lane leads to the feasibility gap raised as R2-F001 below.
- **R1-F002 — resolved.** The kind × slot matrix (lines 386–392), `bind --deliverable`, `deliverable validate` and `core.deliverable.validated` cover the spike in every slot, and the spike clock is defined explicitly. The epic row matches the epic paragraph, and the Kind/disposition acceptance row (line 632) tests the matrix.
- **R1-F003 — resolved for the fields it lists.** Line 119 separates anchor/routing fields from tip-effective policy and removes per-clone adoption of workflow policy, and lines 115 and 117 now say "anchor/routing". One configuration table remains unclassified (R2-F002).
- **R1-F004 — resolved.** Line 144 writes `/.aitm/`, keeps foreign entries and has `doctor` report an unanchored entry.
- **Optional suggestions O1–O4 — all adopted** (lines 97, 243, 283, 177). The `core.state.changed` row now covers every state-changing route. The Done-disposition model (line 357) and the single-transaction `signoff` (line 451) also remove a circular `signed-off` prerequisite that I had not raised.

**U-derived changes.** The author asked me to check four areas specifically:

- **Shared allocation (lines 533–535).** The rule is coherent. CAS on the shared ref is the authority. A losing candidate reallocates under the same semantic operation ID. No ID is exposed and no numbered story is eligible for work before publication, and the acceptance row (line 627) tests reallocation. It removes the earlier undefined takeover protocol without weakening the "one permanent identity per intent" rule.
- **Bootstrap ordering (lines 123, 142–145).** Publishing only after the anchor lands, and then protecting the branch, avoids a protected orphan from a rejected proposal. That is sound. One recovery sentence is unclear (optional suggestion 1).
- **Kind-specific effective-pass rules (lines 389–392, 441).** These are consistent with the matrix.
- **Verification lane feasibility.** This area yields the one substantive finding.

The remaining U-derived edits are internally consistent with the rest of the FUR and with the architecture: the activity-producer contract, the read freshness rules, the default publication behaviour, the exact `[#N] ` commit prefix and the code-clone topology.

New this round:

1. As specified, the authoritative test lane is available only on hosts and projects that pass an OS containment probe. When the probe fails, there is no policy-governed alternative and no defined preparation command. On such a host every story, in both modes, can end only as `done/unverified` (R2-F001).
2. The new configuration classification omits `[providers]`. The migration section treats the numbering/provider namespace as an adoption-level identity, but a trunk merge could change it as tip-effective policy (R2-F002).

Both fixes are bounded text changes. Neither reopens an owner decision or settles an open question.

## Findings

### R2-F001 — The authoritative test lane has no supported route when OS containment is unavailable, and no defined preparation command

**Where:** Lines 433–437 (M1 verification lane), line 110 (`network = "deny"`), line 381 and line 388 (Test exit needs an authoritative receipt), line 443 (sign-off re-evaluates previously waived requirements before `done/delivered`), line 409 (only `done/delivered` satisfies a dependency), the CLI table on lines 572–581, line 631 (acceptance) and the Intent on line 22 ("never the reason a story can't close").

**Problem:** The lane makes OS-enforced containment a precondition for any authoritative pass ("neither adapter may fall back to an unsandboxed authoritative run … if the host cannot enforce the profile, report unavailable/diagnostic"). It also leaves any project that needs undeclared services or source-directory writes diagnostic until "a later capability". Three consequences follow, and the FUR does not address any of them.

- **Common hosts can fail the probe.** On Linux, Ubuntu 23.10+ and 24.04 ship AppArmor restrictions on unprivileged user namespaces by default (`kernel.apparmor_restrict_unprivileged_userns`). An unprivileged process there can create a user namespace but cannot gain the capabilities needed for the mount namespace and read-only bind mounts the adapter relies on, unless an AppArmor profile permits it. This is reviewer knowledge, not verified this round, but it describes default desktop installs and, I believe, common hosted CI images. On macOS, `sandbox-exec` is marked deprecated in its own man page and its profile language is undocumented. It still works today, but it is a fragile sole route. The design probes and refuses correctly. The problem is what follows from refusing.
- **A failed probe permanently blocks verified closure in both modes.** Advisory mode only waives the Test exit guard. Line 443 makes sign-off re-check every waived requirement before `done/delivered`, so on a non-conforming host every story ends `done/unverified`. Under line 409 that also leaves every dependent blocked until someone records an explicit scope resolution. Enforce mode cannot leave Test at all. The same holds for any project whose tests need a local database, a network fixture or writes into the source tree. The one stated remedy is "a later capability". The architecture and Intent make tool-caused blocking an explicit anti-goal. Here the tool's own sandbox requirement, not missing work evidence, decides whether delivery can be verified.
- **Preparation has no route.** Line 437 says missing lock/environment material is "preparation-unavailable with a supported provisioning instruction", and that dependency retrieval "may occur only in an explicitly reported preparation step permitted by policy". No CLI command performs preparation: the table has `test` and `deliverable validate`, and nothing like `test prepare`. No configuration key permits network access for preparation either, since `network = "deny"` is defined only for the authoritative lane. The FUR also distrusts "global mutable caches" without saying whether a hash-verified lockfile install from the uv cache is acceptable. If it is not, every run re-downloads, and every run fails offline. A builder cannot implement "a supported provisioning instruction" from this text.

**Why it matters for this design:** R1-F001 asked for an authoritative lane whose inputs cannot change under it. The private export plus capture-time digests already gives that against other worktree writers. OS containment adds denial of undeclared reads and of network access. Those are valuable, but they are a stronger assurance class, and the FUR makes that stronger class the only class that counts.

**Required change:** Make lane assurance an explicit, committed-policy decision with a defined fallback, and specify preparation. For example:

1. Define at least two named lane assurance levels, recorded in every receipt. `captured-export` is the private immutable export with declared inputs, separate writable roots and no source sharing, without OS confinement. `contained` is the current OS-enforced profile. Tip-effective `[test]` policy names which level satisfies `test-passing` (for example `assurance = "contained"` or `"captured-export"`). A probe failure under a `contained` policy stays diagnostic, as specified now. A policy that accepts `captured-export` gives an authoritative pass labelled with its weaker assurance. Do not degrade silently, and keep "never fall back without policy".
2. Alternatively, state plainly that `done/delivered` for verification-bearing kinds requires a host that passes the containment probe. `init`/`doctor` must report that probe as a readiness condition up front, and the Intent and Goals must carry the caveat. In that case, record that this choice makes the probe a precondition for closure.
3. Either way, name the preparation route (for example `aitm test prepare`, or a preparation phase of `aitm test`). Give it its own policy key for preparation network access. State whether reusing an installer cache is acceptable when every artifact is verified against lockfile hashes, and what the "supported provisioning instruction" names.

### R2-F002 — The configuration classification omits `[providers]` and the numbering namespace

**Where:** Line 119 (configuration classes), lines 100–102 (`[providers] backlog/githost`), line 181 (`store.json` "local-number namespace"), lines 533–535 (local allocation), line 602 and line 604 (migration: the committed declaration's "numbering/provider namespace is the single cross-clone authority … an interrupted or competing apply cannot choose a new … numbering/provider namespace"), and line 622 (acceptance: "store UUID/provider namespace anchored in committed code policy").

**Problem:** Line 119 lists the anchor/routing fields (code repository and default ref, planning remote/repository/ref, store UUID, genesis or legacy root) and the tip-effective fields (mode, limits, extensions, test, review policy). `[providers]` falls in neither list. Under the line 119 default, a merged change is either tip-effective or unsupported, and the text does not say which applies. Yet the migration section and the Init acceptance row treat the provider/numbering namespace as an anchor-level identity that a competing actor cannot change. If `backlog` changed from `local` to `github` (or back) by an ordinary trunk merge, it would take effect at the next command as tip-effective policy, with no reconfiguration. New graduations would then switch identity issuers mid-store, which is the "fallback to local numbering" that line 535 prohibits, and it would happen without the old/new anchor validation that line 119 requires for identity-bearing settings. `githost` affects publication and delivery observation, but not identity, so it can reasonably stay tip-effective.

**Required change:** Classify `[providers]` explicitly. Recommended: treat the identity-issuing backlog provider and its repository/namespace as anchor/routing fields, so that a change goes through `init --reconfigure` with explicit continuity for existing IDs (the existing "no renumbering" rule). Treat `githost` and other non-identity provider settings as tip-effective policy. If a different split is intended, say so and state how the line 604 and line 622 namespace guarantees hold under it.

## Required changes

1. **R2-F001:** Make lane assurance a committed-policy choice with at least a `captured-export` level and a `contained` level, both recorded in receipts. Or state explicitly that `done/delivered` requires a host that passes the containment probe, with `init`/`doctor` readiness reporting and a matching caveat in the Intent and Goals. In either case, define the preparation command or phase, its network-policy key, and the cache-trust rule.
2. **R2-F002:** Classify `[providers]` in the configuration classes. Make the identity-issuing backlog provider and namespace anchor/routing fields (reconfigure-only), and make `githost` tip-effective. Alternatively, explain how the migration and acceptance namespace guarantees hold under a different split.

## Optional suggestions

1. Line 145: the paragraph about rejected and absent bootstrap proposals is not indented. It sits between steps 5 and 6 but describes steps 3–4. It also says to "fetch the exact retained objects from the initializer", but those objects exist only in the initializing clone, and no transport for fetching them is defined. Consider moving the paragraph after step 4, and saying "the initializing clone's verifying rerun publishes them; other clones report `bootstrap-pending` until it does, or until explicit reconfiguration replaces the anchor".
2. Line 437: Python writes `__pycache__` next to sources, and pytest writes `.pytest_cache` under its rootdir. With a read-only source root, the first is silently skipped and the second produces warnings that `-W error` configurations turn into failures. The retained "exact command transformation" could name the standard redirections (`PYTHONDONTWRITEBYTECODE=1` or `PYTHONPYCACHEPREFIX`, and pytest's `cache_dir` or `-p no:cacheprovider` pointed at a writable root), so the nominal fixture does not trip on them.
3. Line 435: `doctor` could report the macOS adapter's dependence on the deprecated `sandbox-exec`, and the Linux probe result with its specific missing capability (user namespace, mount or AppArmor), so that an unavailable lane is diagnosable before the first `aitm test`.

## Decision

revisions-requested
