# #187 Design, Plan and JIT review

Independent same-provider review by Codex `/root/pickup186` on 2026-11-10. Reviewed `pickup.md` lines 1–25, SHA-256 `b842d1f9059544fe25738f021ff9aabe04847a7e433076ca2bf4d3bfd8beb2a7`. This is a local off-platform review by a separate Codex agent.

Compared the #187 record and accepted A02 with the parent design at `b99085f44c8c1f0a5acf5b1fbae02e834f4416fa`, the parent plan at `fd5b22ff0c33c582dd9a0926435d071f09ac6156` with SHA-256 `147cbee5740f725c9c65df9c09034912220d179475dc1c707e0844316a6c1c80`, and #186's delivered reader and capture guide.

## Design verdict

Changes requested.

1. Lines 11 and 13 use tool intervals to hold conflicting positive work before A03 qualifies their relation to a turn. An unattended tool span on story X could remove the same actor's evidenced turn on story Y. It could also remove same-story legacy work. Use positive turn intervals for A02 conflict detection and preserve tool evidence for A03. If tool evidence participates in holds, first restrict it to evidenced in-turn spans in its own scope. The same rule applies to claims already held in full that participate in an overlap check.
2. Line 11 needs a separate pending confirmation watermark. The A01 format permits an observation to inherit a receipt-level recording time. A delayed receipt does not extend the wait. Carry an explicit observation-level pending confirmation or observed pending bound when present. Keep the latest evidenced pending checkpoint distinct from the earliest eligible recording used to replay an occurrence. The accepted parent design requires positive pending evidence.
3. Line 9 makes the hold on a superseding receipt appear conditional on finding its target. Hold the unsupported superseding receipt whenever it claims a revision. Also hold the referenced receipt only if digest, project and direct story match. Keep a foreign or unrelated target available.

The stable project/observation identity, normalized assignment replay and full identity conflicts, scoped gaps, direct versus inclusive boundary, and the two-file implementation align with A02. The exact historical seed has ten stories and 114 direct intervals at watermark `2026-11-10T19:35:05Z`, SHA-256 `8d619b606cfd0142c46da7402ee52c20b95d3a78725894c12cc385309342b139`. Its actor/turn/bounds identities are distinct. No same-actor seed intervals overlap, and the direct interval sums match the ten retained direct millisecond values. Confirmed admission through the delivered reader at `17761cc1928fd916cf32a9c078d4a742bfcb32b8`.

## Plan verdict

Changes requested. Extend line 17 with focused regressions for an unattended tool overlapping a valid cross-story turn, a delayed pending batch without positive checkpoint evidence, and a superseding receipt with a missing or foreign target. The other proposed red and green tests and real seed parity checks cover the A02 scope. Preserve full dashboard tests, focused exact-candidate evidence, existing signed hosted verification, and independent source review.

## JIT verdict

Accepted for the proposed pickup scope. Develop remains gated on accepted Design and Plan revisions. Verified #186 Done on planning, #187's only predecessor, and the #186 delivery commit as an ancestor of the clean `codex/aitm-187-timing-attribution` pickup at `5324a80bad7730b2bdb4a2b87acf00f7171305c0`. The local `origin/trunk` ref matches that pin. The 3.75 implementation agent-hour estimate includes verification and review and fits the four-hour cap.

The two attribution paths and #187 planning record are isolated from the locally available active monitor and TIA branch diffs inspected. Live PR and base claims use the author's recorded overlap inspection and the required live recheck before merge. Expected-head planning publication, refreshed exact source and hosted proof after candidate drift, independent source review, verified merge, signed retrospective and issue and Project readback remain required.
