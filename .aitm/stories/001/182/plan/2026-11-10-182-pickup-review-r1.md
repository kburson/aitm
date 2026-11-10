# #182 independent pickup review, round 1

Reviewer **Claude Opus 5.5, high**. Off-platform, exact pickup and split on November 10, 2026.

# Review of #182 M07b pickup and M07c launcher split

I reviewed only the packet you sent and used no tools. That includes the pickup (`72625a50…`) and the split (`a0bcf8cb…`).

## Verdict

- **M07b pickup: HOLD.** Six fixes are needed, and all of them are changes to the pickup text. None requires reworking the parent plan or moving work into M11 or M16 if the fixes are worded as below.
- **M07c split: PASS.** Three conditions carry into its own pickup.

## M07b blockers

**H1. Residual from prior B1: the adoption check is not named.** The memo now moves under the legacy lock, which fixes the original race. But the pickup never says what durable record "recheck adoption" reads.
- **Fix:** name one durable, one-way adoption record in the verified pinned ledger. The legacy lock is held both when it is read and when it is committed.
- **Ownership:** M07b adds only the reader and a test-fixture writer that takes the legacy lock. M16 owns the production writer.
- **No-record case:** state that when no adoption record exists, behavior and output are exactly what they are today. The pre-adoption legacy path must not read the monitor registry, so a missing or corrupt registry cannot break today's commands.
- **Lock order:** state where `remember_claude_session` fits in the lock order. It must stay lease-free while the legacy publication lock is held. The collector holds its lease and then takes this same lock to retire commands, so a lease taken inside the lock could deadlock.

**H2. Revoking a grant can race with admission.** Witness renewal and revocation take the monitor publication lock, but revoking, rebinding or rotating a grant does not. A change to the project directory or ledger key doesn't either.
- **Risk:** a producer checks a grant, a revocation commits, and the producer still publishes.
- **Fix:** every change that removes or rebinds a grant takes the lock in the order coordinator lease, then publication lock. Alternatively, it revokes the bound witness under that lock in the same step.
- **Test:** revoke between the producer's read and its publish.
- **Registry bytes:** state that existing registry bytes, which have no grants or witnesses, decode and re-encode unchanged.

**H3. Retries may not reproduce identical bytes.** Retries must reuse the original ID with identical bytes, but witnesses are renewed. If the seal covers the witness, a time, or a nonce, a legitimate retry after renewal becomes a conflict.
- **Fix:** state that the envelope and its seal are computed only from the request, the grant and the protocol, with a fixed MAC and no randomness.
- **Test:** a retry across a witness renewal returns the same ID and the same bytes.

**H4. The reader capability is not a real proof yet (prior B2).** "Actual verified reader capability" is still something the writer simply asserts.
- **Fix:** witness issuance must take a typed capability value. Only the typed inbox reader can create that value, and only after it has verified a sealed probe envelope under the lease.
- **Test:** issuance cannot be reached any other way.
- **Validity window:** state its maximum length as a constant, and reject witnesses whose issue time is in the future beyond a set clock-skew limit.
- **Threat model:** say plainly that the witness is a correctness gate between processes run by the same user, not protection against a forging producer.

**H5. Terminal status reporting reaches into M11.** "Return ordinary terminal state through the same status shape" would fix a scope terminal format before M11 writes it. M07a also requires a durable `ProofHold` to stay distinct from a rejected result returned on immediate retry, with the first stored outcome kept.
- **Fix, option 1:** M07b reads only through a closed outcome type that already includes hold and rejected, tested with a fixture writer, and M11 owns the production writer.
- **Fix, option 2:** say that M07b reports only queued or unavailable for scope commands.
- **Either way,** M11 does not need rework.

**H6. The adopted legacy envelope may lose information (reaches into M16).** The adopted route skips the Claude session memo.
- **Fix:** state that the typed legacy envelope sent through the monitor route carries the verified Claude session identity the memo would have recorded. It must also carry the exact `encode_command` bytes, so M16 can interpret it without any legacy-side state.
- **Relationship ordering:** say that the halt and order checks in the legacy relationship queue are not run on the adopted route. M06 ordinals give the total order, and M16 owns any halt semantics.

## M07b items that pass

- **Prior B1 core:** memo and command are written under one lock, there is no nested monitor lock, the losing path makes no legacy write, and the race test is required. This passes once H1 is fixed.
- **Prior B2 core:**
  - One witness gate covers both producers.
  - The check runs under the publication lock just before any acknowledgement.
  - Refusal is sanitized and creates no state or lease.
  - The queue is capped at 256 entries without consuming control capacity.
  - The drain skips scope entries without retiring them or blocking controls.
  - A scope entry ahead of a control command is tested.
  - This passes once H3 and H4 are fixed.
- **M06 wire format and mixed queue:**
  - The existing control and receipt bytes are pinned by tests.
  - ID conflicts are detected across control and scope formats.
  - Retirement is left to M11.
- **CLI and native receipt grammar:**
  - Exact neutral grammar, with legacy readers kept on the old form.
  - Abbreviations disabled on the new leaf parsers, and strict per-action requests.
  - The first native target is joined once.
  - Add negative cases for `--request=FILE`, reordered flags, non-canonical shell quoting, chained or redirected commands, and env-prefixed calls.
  - Pin the exact receipt bytes, including separators and the trailing newline.
- **Dormant separation:** confirmed. Runtime admission stays unavailable because no witness issuer runs. The one live change is the pre-adoption legacy lock reorder, and H1 has to make it behave identically.
- **#118 direct gates:** confirmed. The direct dependencies #117→#118 and #182→#118 are kept, M07c blocks #118 and depends on #182, and the ranks are 215, 217 and 220.
- **Non-blocking:** the pickup should record your verified baseline as the non-regression floor for its gates:
  - 748 product and CLI tests plus 182 helper tests.
  - 9096/9981 product lines (91.13%) and 778/821 helper lines (94.76%).
  - Ruff and whitespace clean on the exact delivered base.

## Conditions for the M07c pickup

1. **Choose the launcher by receipt.** Verification uses the variant or digest recorded in the receipt, never "accept either". Test that each launcher variant is refused against the other variant's receipt, and test upgrading an old-variant install to the new one.
2. **Use hostile thread ID values.** Generate the token with `${CODEX_THREAD_ID+"CODEX_THREAD_ID=$CODEX_THREAD_ID"}`, outside `shlex.join`. Test values containing spaces, quotes, `$()`, backticks, newlines and a leading `-`, alongside the matching, wrong, absent, empty and arbitrary-env cases.
3. **Keep it local.** There is no production install or service change, and you asked me not to add any.

## Estimate and checkpoint

- **3.75 hours for M07b:** credible but tight. The fixes add roughly 0.1 to 0.2 hours to the first bucket (grants, witness and mixed queue), which comes out of the 0.45 reserve. The four-hour reopen is the real control.
- **Two-hour checkpoint:** the arithmetic doesn't quite work. Its gates span the first two buckets, which are allocated 2.15 hours. Either move it to 2.25 hours or keep it as a deliberate stretch. Either way, name the action on a miss, for example: stop and split the CLI and native recognizers into their own leaf before spending any reserve.
- **1.25 to 1.75 hours for M07c:** credible, since the code already pins launcher bytes at wheel verification and install.
