# Session-owned agent activity and cost reporting

## Disposition

**Feasible for explicitly enrolled and supervised work.** A live agent can publish turn evidence to the owning story using short native reads, a private receipt spool, and ordinary Git publication. Use the known qualified provider routes. Keep capture, price estimation, and billing provenance distinct. The production implementation still needs a verified automatic publication path from the live chat and a recovery mechanism for turns that finish after the chat exits.

The pilot used the installed portable wheel from [PR #454](https://github.com/kburson/aitm/pull/454) and the macOS provider routes in the [#445 qualification matrix](../../445/attachments/qualification-matrix.md). The app's Codex live-chat and subagent records used exact local native turn reads in the probe. That readback extends the experimental evidence and leaves the released adapter matrix as recorded. The Claude and Grok XPR cases used AIPR 0.4.1, with verified participant fingerprints, sealed response digests, and exact usage readback. The Codex same-provider source review ran off-platform and returned a real HOLD on a disposable proposal. Codex sealed AIPR review retains the [#434 gap](../../434/story.md).

## Pilot results

A completed solo chat turn, an active orchestrator turn through a defined cutoff, a real supervised app subagent, a spawned Codex CLI worker, a Codex same-provider reviewer, four sealed Claude/Grok XPR rounds, and a cancelled Grok XPR produced ten exact observations. The 8,151,812 observed tokens include accumulated input context and two partial observations. Eight turns were complete. The active orchestrator excludes requests beyond the sampling cutoff, and cancelled Grok includes only the observed native frames. A separate missing-carrier control remained unresolved.

| Fixture story | Observed tokens | Evidence |
| --- | ---: | --- |
| Solo | 1,921,295 | Completed native chat turn |
| First active story | 5,774,779 | Live owner, subagent, headless and same-provider reviewer, first XPR rounds, and cancelled Grok |
| Second active story | 455,738 | Second XPR rounds after the story switch |

The caller saved the initial assignment before worker dispatch. The first-round AIPR calls started under the first story. The next round used the newly active story. Delivery occurred in reverse order. The first Claude round's later revision remained pending through a fresh reader process, settled to the original story after its predecessor arrived, and counted once. The missing enrollment stayed explicit. An overlapping inclusive-parent control added no duplicate usage. Replays preserved SQLite and the three frozen report representations byte for byte. All three disposable AIPR brokers read back offline.

The read and normalization pass took 131.689 ms, enrollment and staging took 15.789 ms, the fresh-process pending readback took 66.384 ms, settlement and remaining ingestion took 11.165 ms, and report and replay checks took 11.334 ms. These timings cover the specified local phases. Provider runtime and separate exact AIPR carrier readback sit outside those numbers. Capture, reconciliation, and publication requested zero extra model turns.

The Git probe ran two writers from the same base against one disposable local `planning` ref. Each produced a different immutable receipt for the same story. One push won and the stale push was refused. The second writer fetched, rebased and pushed without force. The coordinator published a digest-pinned manifest and read back both receipts. Same-byte retries were no-ops and altered same-identity payloads were refused. The local push race and retry took 248.058 ms. This test exercises Git semantics locally. Production permission and remote branch protection still need a controlled end-to-end check.

The sanitized receipt includes native evidence hashes, opaque observation IDs, token splits and timestamps. Native identifiers, prompts, paths and pseudonymization material were screened from the publication. The Codex rate input is a pinned GPT-6.2 Sol standard estimate per request, with short and long input tiers and separate cached input. Claude list-price equivalents, Grok ticks and verified billed amounts retain their own provenance. Verified billed amounts remain unknown. [Live-turn receipt](455-pilot-receipt.json) · [Publication receipt](455-publisher-receipt.json) · [OpenAI model rates](https://developers.openai.com/api/docs/models/gpt-6.2-sol)

## Reuse matrix

| Asset | Reuse for session-owned capture | Remaining work |
| --- | --- | --- |
| #436–#438 receipt store, attribution and capture | Keep immutable project/story/run/role enrollment, exact native identity, transactional receipt revisions and recovery. | Persist private session/attempt mapping across fresh chats and bind the recovery action to the enrolled source. Require exact launch and source authority. |
| #426–#434 research and #439–#441 adapters | Use configured native completion and exact readback for marked sessions. Retain supported model/build/surface coverage and interruption gaps. | Verify automatic end-of-turn integration and a bounded resume/compaction handoff on each advertised live-chat route. The prototype exercised a new reader process and real AIPR resumes. |
| #442 rollups | Reuse disjoint usage, late attribution, handoff evidence, summed engagement and separately bounded working wall. | Provide explicit clock provenance and record each expected child or review at dispatch. A late receipt settles its immutable assignment. |
| #443 effort CLI and canonical export | Reuse deterministic story views, provenance and read-only frozen legacy compatibility. | Pin each published report to the planning commit, exact receipt revisions, coverage, cutoff, and rate card. The shipped portable pricing fields remain unknown. |
| #444 AIPR companion reconciliation | Preserve separate review authority and correlate a sealed decision and usage through the enrolled attempt. | Keep failed/interrupted attempts measurable where possible, with their actual decision gap. |
| #442–#445 cost tables and dashboard registration | Reuse cached/new/output splits and evidence registration with existing Actual and coverage semantics. | Make the closeout automatic. Preserve per-request model, tier and cache categories for repeatable versioned pricing. Publish a bounded subtotal with an explicit expected-turn denominator. |
| #100 accounting, pricing, publication and source custody | Reuse narrow validation, rate provenance, replay protections and privacy canaries that fit the session path. | Qualify rate-card entries from the actual captured model/tier/context. The tested closeout estimate is separate from the existing runtime price allowlist. Global discovery, wake machinery and service adoption have no pilot dependency. |

## Recommended delivery path

1. **Session capture and publication.** The live agent enrolls its own turn and each dispatch under the story active at that boundary. A short-lived helper writes exact evidence to a private durable spool and periodically reconciles it to immutable per-turn receipt files. Use one scoped registration writer and ordinary fetch/rebase on a stale planning ref. Give pending, unavailable and unattributed outcomes explicit coverage. Prove identity and late recovery on a real active story, including handoff and resume/compaction checks.
2. **Pinned story and cost report.** Use the spool and #443 rollups to produce a report tied to a planning commit, usage cutoff, exact receipt/revision manifest and rate digest. Preserve per-request pricing inputs or a verified equivalent with reproducible provenance. Allow a known subtotal with coverage in the viewer. Apply the existing complete-price requirement before publishing Project Cost. Capture and Actual remain independently useful where evidence allows.
3. **Core integration only through the required producer contract.** Define the small deterministic producer against #51's receiver fixture, then qualify live reconciliation in #230 separately. Retain original identities and explicit conflict/unknown states. Legacy snapshots can remain readable with unresolved overlap visible.

See the [#100 disposition assessment](100-child-assessment.md) for the capability-by-capability recommendation and graph implications.
