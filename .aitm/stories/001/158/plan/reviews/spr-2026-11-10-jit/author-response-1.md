---
schema: "aitm.review-response/v0"
story: 158
round: 1
level: "spr"
execution: "declared-manual"
input_commit: "28083f277b96e2c259ea67fb537ecd3d906015cd"
inputs: {"design": {"path": ".aitm/stories/001/158/design/2026-11-10-158-qualify-github-merge-fence-design.md", "sha256": "45e0e365d87a3c5f46154c16d7c26c42277e9d0d1f645b3f2b06ca27435ca8a8", "lines": 118}, "plan": {"path": ".aitm/stories/001/158/plan/2026-11-10-158-qualify-github-merge-fence.md", "sha256": "d3d0dbb77b0a4be1a9543add36ae8220270f23c2153af81a83d06fe8e62bde57", "lines": 162}, "jit": {"path": ".aitm/stories/001/158/plan/2026-11-10-158-jit.md", "sha256": "ee647c591f4583785f1aa49bbece533a4eb792885ae37e9ed843321abf75af7c", "lines": 104}}
role: "author"
role_session: "codex-collaboration:/root/prep158"
answered_finding_ids: ["R1-F001", "R1-F002"]
outputs: {"design": {"path": ".aitm/stories/001/158/design/2026-11-10-158-qualify-github-merge-fence-design.md", "sha256": "4f390fc1c0f20c8c08b8be2b6ca90ccbe74d48c46e7a202a215bfb7dfd61b4d9", "lines": 128}, "plan": {"path": ".aitm/stories/001/158/plan/2026-11-10-158-qualify-github-merge-fence.md", "sha256": "53c09ab58c857d04384eb9ac08e0c206c4b71b502e509b0b48ea96eaabcc5a38", "lines": 191}, "jit": {"path": ".aitm/stories/001/158/plan/2026-11-10-158-jit.md", "sha256": "101ef7993f01e5c5e242e8c8f5945a166a7f3b207b100d2e8476f7a328678685", "lines": 127}}
---

# #158 author response to independent SPR round 1

Author `codex-collaboration:/root/prep158`. Revised the design, plan
and JIT derived from candidate `28083f277b96e2c259ea67fb537ecd3d906015cd`.

- `R1-F001` — resolved. M10 now places the adversarial barrier
  after the final authority check and before any external merge
  request bytes. A serialized route must show contention, actual
  ordering and the transport result. M11a still covers a known
  earlier provider commit with lost acknowledgment. M11b requires
  causal overlap or a documented, independently verified host
  invariant covering an already-sent request. Response-only
  delay cannot pass M11b. Unresolved intent remains durable and
  fenced, and unproved ordering refuses qualification. M06 also
  follows a terminal enqueue response to the queue's own outcome.
- `R1-F002` — resolved. The plan and JIT name the isolated
  `codex/aitm-158-merge-fence-evidence` branch from authenticated
  `origin/planning` and the literal `planning` delivery target,
  separate from the disposable GitHub fixture. The exact
  candidate commit and file digests, real matrix validation,
  independent evidence review, authorized publication, remote
  mapping/readback, and sign-off precede closure.

The owner-only sandbox, roles, permissions and execution hold
remain. No persistent live #158 fixture mutation or hosted probe
occurred in this review round.
