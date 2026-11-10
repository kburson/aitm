# Native reviewer response, round 2

Native source SHA-256 `sha256:61b82f7d7495ac4a0623320d6229ea26dcaada751b964d19d58a6b23589060f2`. Submitted `2026-11-10T03:07:01.924Z`.

Mode: `normal`

## Summary

I read the entire revised spec (`multi-project-usage-monitor-design.md`, lines 1–85, blob `6700f972…`, digest `sha256:1a5e9bb3…`) and the author's turn-1 response. I checked each turn-1 finding and optional suggestion against the revised text. I then reread the full document for regressions and new contradictions, and found none.

**Turn-1 required findings: all resolved.**

1. **Interval time basis.** The adapter contract now declares "a versioned observation time basis" (line 43). Line 59 defines the precedence: a verified native start boundary where the qualified surface exposes one, otherwise the declared verified completion or qualified usage-event time. The basis is frozen with the observation, and "unknown observation time" stays as the residual gap. Grok uses verified native completion time, so a missing prompt hook no longer removes an eligible turn from interval totals (line 47). Line 80 adds a matching hookless-turn verification case, which counts the turn once with no story. Resolved.
2. **Contradictory marker versus registered anchor.** Line 21 makes a verified ordinary marker for A in B's registered checkout a conflict. The usage is held out of both totals, and generation zero is defined as the anchor project, so a dedicated handoff (line 23) is required to override it. Line 75 adds the two-project conflict-then-handoff case. This fits the unregistered-reviewer path on line 17 and "establish the project where checkout evidence is absent." Resolved.
3. **Unqualified surfaces in shared roots.** Line 17 validates the recorded surface, client version and format against the adapter's qualified matrix. Unsupported or unproven sources contribute no usage to totals and show a sanitized coverage reason. Line 11 explicitly places macOS Codex CLI outside the initial matrix. Line 75 adds a mixed-surface root case. Resolved.
4. **Privacy verification.** Line 78 adds sentinel-based scans of hook notifications, holds, service journal, recovery log, project ledgers, reports and all export formats against fixed allowlists, plus a cross-project export isolation check. Line 29 adds a matching rule: transient locator resolution, keyed persistence only, and retirement of consumed wake records. Resolved.

**Turn-1 optional suggestions: all addressed.** Grok project ownership is now separate from story attribution, and the turn is held when neither checkout context nor enrollment is proven (line 47). Wake-record retention is covered (line 29). Nesting is defined as overlap across different projects (line 15). The handoff receipt wording is no longer circular (line 23). The park issuer is named and park carries scheduling intent only (line 34). Production hook approval is stated (line 47).

**Regression check.** The new rules agree with the rest of the spec. Generation zero composes with the A→B→C handoff rule. The completion-time basis composes with "allocate an indivisible span once at its selected time" and with legacy-row preservation. The surface-qualification gate composes with the per-installation shared-root watching and the coverage-gap model. The privacy item matches line 17's persistence rules. I found no new required issues.

## Findings

None.

## Required changes

None.

## Optional suggestions

1. **Scope of a handoff when it resolves a conflict (line 21).** "Hold the affected usage … until a verified handoff or evidence-backed disposition resolves it" could be read as a handoff retroactively assigning the span held before it. Line 23 makes a handoff prospective: it takes effect at the first boundary after its receipt. Consider stating that a handoff resolves the conflict only from its effective boundary, and that the earlier held span needs an evidence-backed disposition or expires to a coverage gap. The line 75 case already exercises this behavior, so this is wording only.
2. **Grammar (line 17).** "contributes no usage totals" should read "contributes no usage to totals."

## Decision

accepted
