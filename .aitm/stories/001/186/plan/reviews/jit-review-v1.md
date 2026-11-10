# #186 Design, Plan and JIT review

Independent same-provider review by Codex `/root/pickup186` on 2026-11-10. Reviewed `pickup.md` lines 1–27, SHA-256 `212e6572cda08d48d5d2c93097079954bace77000e6c575a5f98030fa16a29d7`. This is a local review note. The installed `peer-review` help returned no skill path, and the installed CLI rejected `primary inspect` as an unknown command. No broker or native review session was opened.

Compared the #186 Backlog record and graduated A01 excerpt with the exact #181 plan at `fd5b22ff0c33c582dd9a0926435d071f09ac6156`, SHA-256 `147cbee5740f725c9c65df9c09034912220d179475dc1c707e0844316a6c1c80`, and the accepted design at `b99085f44c8c1f0a5acf5b1fbae02e834f4416fa`, SHA-256 `ed54c65d42aad04bde7a4f942894beb6a2280016d5fc2ff0b6411297ce5f46a5`.

## Design verdict

Changes requested. Lines 7 and 9 promise read-only pinned object access. Disabling replacements and caller directory overrides leaves Git's implicit missing-object fetch possible in promisor or partial repositories, where it can contact the remote and write retrieved objects. Specify an offline access profile with replacements and optional locks disabled, and either enforce no lazy fetch on the selected Git or fail closed for partial/promisor inputs. Exercise or explicitly qualify that profile before accepting the exact implementation.

The story and batch identity binding, capped regular-blob reads, replay and conflict handling, no observation outside the cutoff, canonical parent graph, and exact #181 legacy exception align with the accepted design. Verified the local legacy JSON digest `8d619b606cfd0142c46da7402ee52c20b95d3a78725894c12cc385309342b139`. Timing projection, usage assurance and Cost admission stay with their assigned leaves.

## Plan verdict

Changes requested. Lines 17–19 explicitly describe the timing example but leave the usage guide and fixture ambiguous. Accepted plan line 47 assigns A01 both v1 schema pins in the capture guide and validation fixtures, and documentation of the usage receipt's embedded verification fields. State that in the leaf tasks and include a focused usage validation fixture. Retain the single complete timing receipt/event example, prospective validation, exact-byte readback, and A06 ownership of live pilot and board projection.

## JIT verdict

Accept the proposed JIT and its scope. Develop remains gated on resolution and accepted review of the Design and Plan changes. The #186 record and accepted A01 plan both name no predecessor and estimate 3.75 implementation agent-hours, within the 4-hour cap including verification and independent source review. The isolated `codex/aitm-186-planning-evidence` checkout and local `origin/trunk` were both at `a495d60a87ac4ca764f019dc266e579f13f1787e`. The reviewed write set is the three new dashboard paths and the #186/#181 planning records, consistent with the pickup's #100/#133 overlap inspection. No external overlap or live-branch check was performed in this reviewer session.

The current workflow's Python and Ruff invocations are scoped to the usage package and named CI helper paths. Retain focused dashboard execution and lint for the exact candidate separately. The packet requires fresh exact-head/base hosted evidence and trusted verification, independent source review, normal PR merge, landed-source verification, retrospective and sign-off. Apply the manual checklist for attempt identity, evidence links, Project readback, and closure. Recheck the live trunk gate and owner-scoped planning bytes if concurrent work advances either target.
