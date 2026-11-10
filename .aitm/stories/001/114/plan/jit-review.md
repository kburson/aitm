# #114 independent pickup review

Declared-manual Claude Code review. The provider reported `claude-opus-5-5`, with high effort requested. The first two exact drafts and the third accepted revision are retained. The initial round-three invocation was interrupted before a verdict. A separate invocation reviewed the same exact packet.

## Round 1

### FAIL: AITM #114 design, split and JIT

The split structure follows the accepted plan. The JIT still needs these required fixes before pickup. None of them needs new Linux evidence.

#### What I reviewed

- **JIT text:** the exact JIT as you supplied it. I did not recompute its SHA-256 (`c5e6ede9…ae688`) or the plan hash (`8899a4d1…5f21`).
- **Accepted plan:** the M04 and M19 sections.
- **macOS evidence:** the #96 activation summary, the #88 Desktop carrier acceptance and the Claude startup-prefix diagnostic, as excerpts.
- **Linux limits:** the #102 environment and evidence boundaries.
- **Supplied facts:** the live issue and board facts and the pinned code facts.

**Not checked:** I had no tools, so I did not check live GitHub, issue links or board state, the trunk commit `dc037364…`, raw provider records, fixtures or source code.

#### What passes

- **Split permission:** M04 allows the split at JIT when a Linux carrier is unavailable. #102 proves only credential-free command surfaces and kernel primitives, with no authenticated carrier, adjoining request or durable cursor. Splitting into M04-LC and M04-LA is correct.
- **Dependencies:**
  - LC and LA each depend on #114.
  - Both become direct prerequisites of #129, alongside #128.
  - #115 and #116 stay on #114.
  - The parent plan bytes are preserved.
  - This satisfies "make the corresponding M19 qualification depend on the accepted slice", provided #129 really is M19 (see advisory 1).
- **macOS scope:** the exact pins are Codex Desktop 0.167.0-alpha.3.2 and Claude Code 2.1.318 format 1. Mac Codex CLI is excluded even in a shared root, and Linux surfaces stay disabled in #114. Same client version alone does not carry the Desktop proof over to the CLI, which matches #102.
- **Unsupported surfaces:** they return a sanitized diagnostic, zero observations and no cursor advance.
- **Ownership boundaries:** M07 owns scope admission. Root reconciliation, durable claims and routing are deferred. There is no production activation.
- **Estimate:** 3.75 hours with a reopen trigger is under the 4-hour cap, but tight (see advisory 4).

#### Required findings

1. **Name the files.** M04 requires creating `S/sources/adapter.py` and `T/test_monitor_adapters.py`, and the JIT names neither. Bind the contract to `adapter.py` and the three plan tests to `test_monitor_adapters.py`. Keep `test_scan.py`, `test_codex.py` and `test_claude.py` as regression checks.

2. **Define the exact surface tuple and test the rejections.** "Host, client and format" is looser than the plan's "qualified host, client version and format tuple." Spell it out:
   - **Host:** OS and architecture. The evidence is from arm64 Macs only, so x86-64 Mac is not implied.
   - **Client identity:** for Codex Desktop this must be the conjunction `originator=Codex Desktop` and `source=vscode`. `source=vscode` alone could admit an IDE-extension surface.
   - **Exact client version and exact format.**

   Add rejection cases that each yield zero observations and the fixed diagnostic:
   - a different `originator` with `source=vscode`;
   - Desktop or Claude Code with the version or format bumped by one;
   - an x86-64 Mac;
   - Linux Codex CLI and Linux Claude Code at the pinned versions, proving they are disabled in #114.

3. **Specify the marker recognizer in neutral mode.** Today the marker parsers match the legacy command against a known exact state root, and the monitor bridge has no project state root. Say what the recognizer does under the neutral read authority. It should emit receipt and boundary evidence without matching against, or authorizing for, any project root, and it must never fall back to the monitor root as an authorizer. Add a bridge-path test showing:
   - a Desktop receipt yields boundary evidence;
   - nothing is authorized;
   - the legacy path's marker behavior is unchanged.

4. **Keep project context row-derived.** "A monitor root supplies its … proven checkout context" must not become default attribution for rows in that root. State that root context is used only to verify each row's own checkout evidence. A row without verified checkout evidence gets absent project context. Add a negative test where the read context fails if any project ledger is selected, opened or persisted on the bridge path.

5. **Define the next safe cursor.** It must never advance past:
   - an incomplete trailing record;
   - the earliest row held in the boundary-only frontier for unproven scope;
   - a Claude message whose streamed usage may still be revised.

   Otherwise M07 loses rows it could later admit. Assert this in the Claude streamed-revision test and in a held-frontier case.

6. **Use an allowlist, not a denylist.** The plan says to discard anything outside the field allowlist. "Keep raw transcripts and internal paths out" is weaker. Name the allowlisted `AdapterBatch` fields: lineage, boundary, time basis, usage revision, project context, diagnostics and cursor. Assert that a serialized batch and its diagnostics contain only those fields, with no paths, session text or command bodies.

7. **Say what happens if Linux evidence needs a contract change.** M04 says to obtain evidence before fixing the interface, and #114 fixes the contract on macOS evidence alone. State that LC and LA must fit the delivered #114 contract. If Linux-native evidence needs a contract change, planning reopens and the impact on #115 and #116 is assessed, rather than the contract changing silently inside a leaf.

8. **Preserve the Claude startup prefix through the bridge.** The native ordering in which the first segment has no checkout appeared in 13 retained files and was qualified in #87/PR #99. Add a bridge-path Claude fixture with that ordering. It should show that the first segment stays held and boundary-only and the target boundary is still emitted, with no admission and no dropped later usage.

#### Advisory

1. **Name the milestone:** #129 is OPEN with predecessor #128, and the plan places M19 after M18. The JIT should say explicitly that #129 is M19 and #128 is M18. I cannot confirm this.
2. **Label fixture provenance:** mark which fixtures come directly from the retained native evidence and which are deterministic derivations, such as the copied-archive replay. The macOS evidence does not include a native archive copy.
3. **Make service references root-independent:** assert that stable service references don't depend on the root path, so later root reconciliation can deduplicate overlapping roots.
4. **Recheck the estimate:** findings 2–8 add tests and must fit the 0.25-hour margin. Add a checkpoint: if the neutral read authority isn't green on the legacy suites by about the midpoint, reopen planning instead of compressing review.

## Round 2

### FAIL: AITM #114 revised design, split and JIT

Seven of the eight required findings are resolved. One blocker is left, in the Claude cursor rule from finding 5.

**Scope:** I reviewed the supplied JIT text (`e4bff8e4…f79a3`), the prior review, the accepted M04 section and the preflight facts. I did not recompute either hash, access GitHub, inspect raw native records, fixtures or source, or execute code.

#### Required findings

| # | Finding | Result | Basis in the revised JIT |
|---|---|---|---|
| 1 | Files | **PASS** | It creates `sources/adapter.py` and `tests/test_monitor_adapters.py`. The three plan tests are in `test_monitor_adapters.py`. `test_scan.py`, `test_codex.py` and `test_claude.py` remain the green regression gate. |
| 2 | Exact tuple and rejections | **PASS** | The tuple is pinned to Darwin arm64. Codex Desktop needs both `originator=Codex Desktop` and `source=vscode`, plus the exact version and format 1. Claude Code needs `2.1.318` and format 1. Mismatched version, format, originator or architecture is refused, as are Mac CLI and both Linux providers. Each refusal gives a fixed diagnostic, zero observations and no cursor advance, and the JIT says to test every rejected tuple. Origin is rechecked per locator. |
| 3 | Neutral marker recognizer | **PASS** | It matches only the exact canonical command shape and linked result, and discards the declared path. It emits opaque receipt and boundary evidence. Neither the declared path nor the neutral root authorizes a project, and the legacy exact-root check is unchanged. A bridge test covers this. |
| 4 | Project context from each row | **PASS** | Root configuration only verifies each row's own checkout evidence. An unverified row gets absent project context. The read context fails the test if any destination ledger is opened, selected or written. |
| 5 | Safe cursor | **FAIL (narrow)** | See the blocker below. The incomplete-trailing-record and held-frontier limits are correct. |
| 6 | Allowlist | **PASS** | The JIT names the allowlisted fields, and sentinel tests cover paths, session text and command bodies. |
| 7 | Linux contract change | **PASS** | LC and LA must fit the #114 contract. A needed change reopens planning, with #115 and #116 assessed first. |
| 8 | Claude startup prefix | **PASS** | An unresolved first segment stays boundary-only and still emits the following verified boundary. It replays from the held cursor without losing later usage, and a test asserts this. |

All four advisories from the prior review are now covered: M18 #128 and M19 #129 are named, fixture provenance is labeled, lineage is independent of root paths, and there's a two-hour checkpoint.

#### Remaining blocker: where the retained Claude revision state lives

The cursor rule itself is right. The JIT lets the cursor cross an unfinalized Claude message only when "the checkpoint retains the exact request prefix and message identity needed to revise it after restart". Otherwise the cursor stays before that message. That matches the existing durable request-prefix revision behavior and doesn't treat a partial message as final.

Two things are still unclear:

1. **The cursor and the retained state could get out of step.** `read_delta(locator, cursor)` receives only the `StreamCursor`, and the JIT doesn't say where "the checkpoint" comes from on restart. If the cursor and the retained prefix and identity are saved separately, a crash between the two saves can leave the cursor past a message with nothing kept to revise it. That message's usage would then be lost or charged twice.
2. **The retained state conflicts with the allowlist.** The safe cursor is one of the allowlisted fields, and those fields must hold no provider ID. Claude message and request identities are provider IDs. As written, crossing either breaks the allowlist or can never be allowed.

**Required fix:**
- State that the retained prefix and message identity are part of the `StreamCursor`'s durable state and are saved in the same write as the position.
- State that they are held in keyed form, so the cursor still satisfies the allowlist.
- Add a provider-ID sentinel to the allowlist test.
- In `test_claude_streamed_revision_and_nested_overlap`, test both branches:
  - with the state retained, the cursor crosses the message, and after a restart the message is revised with no double charge;
  - without it, the cursor stays before the message.

#### Non-blocking notes

- Add a rejection case with `originator=Codex Desktop` and a `source` other than `vscode`.
- Add a test that a row without verified checkout evidence gets absent project context.

## Round 3

### PASS: AITM #114 JIT revision 3 (`4b3a626d…77b04cf2`)

Revision 3 resolves the Round 2 Claude cursor blocker, and none of the seven passed items has regressed.

**Scope:** I reviewed only the text you supplied: revision 3, the Round 2 review and the delivered type shapes. I did not recompute the hash, access GitHub, inspect source or fixtures, or run anything.

#### The blocker

| Required fix | Result | What revision 3 says |
|---|---|---|
| Revision state saved with the position in one durable write | **Resolved** | `StreamCursor` carries the complete `SourceCheckpoint` as one durable value: position, provider checkpoint, keyed request prefix and keyed message identity. The caller must save it atomically with the accepted frontier. After a restart, `read_delta` rebuilds the prefix from that same value. This means the cursor and its revision state can't be saved separately. |
| Kept in keyed form to satisfy the allowlist | **Resolved** | The request prefix and message identity are keyed, and "Raw request and message IDs never leave the adapter." This matches the delivered shape: `RequestPrefix.request_ref` and `message_ref` are `SourceRef`, and `ProviderCheckpoint.request_prefix` already holds them. No schema or version change is needed (`version == 1` still holds). |
| Provider-ID sentinel in the allowlist test | **Resolved** | "path, raw provider ID, session text and command-body sentinels." |
| Both branches tested | **Resolved** | With the keyed prefix kept atomically, a streamed revision after restart is tested with no double charge. Without it, the cursor stays before the provisional message. |

Both earlier non-blocking notes are also covered: a Desktop originator with a `source` other than `vscode` is now a rejection case, and a row without proof gets absent project context.

#### Seven passed items: no regression

Items 1 to 4 and 6 to 8 read the same as in Round 2, or stronger. The new cursor text agrees with the allowlist, because the safe cursor now contains only keyed refs, token counts and ordinals. It doesn't affect tuple refusal, the neutral recognizer, per-row project context, Linux contract fit or the held startup prefix.

#### Actual limits (none blocking)

1. **The atomic save is the caller's job.** #114 can state the rule and simulate a restart in a test. The real atomic write with the frontier belongs to the later durable-claim owner, so its acceptance gate should check it.
2. **Rebuilding the prefix after restart depends on stable keys.** The text says the read context gives "stable pseudonyms", which covers this. It doesn't say what happens if that key changes between runs.
3. **The branch tests aren't tied to a named test.** The two cursor branches aren't explicitly placed in `test_claude_streamed_revision_and_nested_overlap`, as Round 2 asked. They're still required in the verification contract, so this is only about where they go.
4. **I couldn't check the shape of `StreamCursor`.** The supplied type shapes stop before it. I took "carries the complete existing `SourceCheckpoint`" to mean it is a new wrapper in `adapter.py` around that existing type.

