# Record story timing on planning

Use this checklist to prepare a sanitized, immutable receipt for one story. The validator reads the pinned planning tree and reports admitted inputs and evidence gaps. It does not compute Actual or Cost, publish receipts, or update the board.

1. Bind the story, phase, role, and attempt before work begins. Record any evidenced scope change before switching. Split a batch by proven story scope; keep unresolved or pre-graduation scope private until it can be linked.
2. Use the same project namespace, batch ID, pseudonymous actor and stable observation IDs on retries. An observation ID names the source observation independently of its story, phase, role, or attempt. An explicit revision belongs in a new batch and names the old receipt's exact SHA-256 in `supersedes`. Keep the old bytes.
3. Capture the evidenced UTC boundaries of agent turns, in-turn tools, explicit owner requests and responses, idle gaps, and workflow start or delivery. Keep occurrence and recording times separate. Use half-open intervals at millisecond precision. Tool intervals belong inside Actual where qualified; overlapping tool and turn intervals count once. Owner wait and idle are separate evidence. Use `null` for unknown bounds or scope and give an opaque `missing_reason` for an incomplete interval. A workflow or request/response boundary may have one endpoint. No elapsed minutes imply token usage.
4. Keep raw transcripts, provider IDs and handles, private paths, prompts, credentials, and tool output outside planning. Use an approved stable pseudonym or digest. `source` has a safe opaque `ref`, a lowercase SHA-256 in `sha256`, or both. Each observation can override the receipt's source and recording UTC when known. Its occurrence bounds must be at or before its own recording time. Coverage is `complete`, `partial`, or `unknown`. Use the `basis` field to identify the kind of verified evidence.
5. Use the same story ID in the containing journal, registration, registration scope, receipt subject, and filename. Write timing receipts with schema `aitm.story-timing-receipt/v1` and usage receipts with `aitm.story-usage-receipt/v1`. The registration kinds are `story-timing-receipt` and `story-usage-receipt`, respectively. Use an event with `v: 0`, the recording actor's kind, `provenance.route: manual-bootstrap`, and `provenance.runtime_transition: false` as shown below. An epic's receipt carries its own direct observations. Store a child receipt with its child.
6. Work in a private temporary directory outside the tracked checkout. Record the full 40-character planning commit SHA and choose an explicit UTC as-of at or after both the pinned commit time and the registration recording time. Use a complete local Git repository. The reader disables optional locks, replacement objects and lazy fetch; it refuses partial/promisor repositories and alternate object stores.

## Example: one timing receipt and its registration

These values are illustrative. Use the verified values and timestamps for your story. Save the following block as `receipt.json` with its final newline.

```json
{
  "schema": "aitm.story-timing-receipt/v1",
  "project": "aitm",
  "subject": 186,
  "batch": "example-1",
  "recorded_at_utc": "2026-11-10T22:10:00Z",
  "source": {"ref": "manual:example-checkpoint"},
  "observations": [
    {
      "observation_id": "example-source.turn-1",
      "actor": "agent-1",
      "turn": "turn-1",
      "phase": "implement",
      "role": "implementer",
      "attempt": "attempt-1",
      "kind": "agent-turn",
      "coverage": "complete",
      "basis": "verified-turn-boundaries",
      "start_utc": "2026-11-10T22:00:00Z",
      "end_utc": "2026-11-10T22:06:00Z"
    },
    {
      "observation_id": "example-source.tool-1",
      "actor": "agent-1",
      "turn": "turn-1",
      "phase": "implement",
      "role": "implementer",
      "attempt": "attempt-1",
      "kind": "tool",
      "coverage": "complete",
      "basis": "verified-tool-boundaries",
      "start_utc": "2026-11-10T22:02:00Z",
      "end_utc": "2026-11-10T22:03:00Z"
    },
    {
      "observation_id": "example-source.wait-1",
      "actor": "agent-1",
      "phase": "implement",
      "role": "implementer",
      "attempt": "attempt-1",
      "kind": "owner-wait",
      "coverage": "complete",
      "basis": "verified-owner-request-response",
      "start_utc": "2026-11-10T22:06:00Z",
      "end_utc": "2026-11-10T22:09:00Z"
    }
  ]
}
```

Hash the exact file bytes (`shasum -a 256 receipt.json`). Create `registration.json` with this event as one line. Substitute your own digest if you change any receipt bytes.

```json
{"v":0,"ts":"2026-11-10T22:10:00Z","story":186,"type":"core.evidence.recorded","actor":{"kind":"agent","harness":"codex","on-behalf-of":"authorized-operator"},"provenance":{"route":"manual-bootstrap","runtime_transition":false},"data":{"kind":"story-timing-receipt","path":"attachments/timing/example-1-186.json","sha256":"eaaa9792cd9ac45a291f1600eae46f5d70dd474e01ef541f14899605830a4915","scope":{"story":186,"project":"aitm"}}}
```

Run this command from the checkout that contains the validator. The two file paths point to your private copies.

```sh
python -m tools.story_dashboard.evidence \
  --repo "$planning_repo" --commit "$planning_sha" --as-of "$as_of_utc" \
  --receipt "$private_dir/receipt.json" --registration "$private_dir/registration.json"
```

A successful check includes the exact story, project, receipt path, schema and digest under `prospective`. Resolve any collision or incomplete scope before publication. For the example, the committed paths would be `.aitm/stories/001/186/attachments/timing/example-1-186.json` and `.aitm/stories/001/186/events.jsonl`. An authorized recorder commits the receipt and appends its event to the existing journal in **one** planning publication, with the expected branch head. A proven cross-story batch must be published together by someone authorized for every affected story.

After publication, read the branch back, verify the exact receipt bytes and registration, and rerun with the published commit and a cutoff at or after publication. Omit both file options to validate the registered tree; read the receipt list and gaps, even on exit zero. If publication is uncertain, check the exact bytes and event at the remote head before retrying. If both match, the operation is already recorded. A conflicting digest or a partially published pair needs reconciliation before a retry; never overwrite a registered path.

## Usage receipt verification

A usage receipt has the same project, subject, batch, recorded UTC, and source fields. Its `selector` fixes `project`, `report_id` (the original fixed report or sequence identity), `window_start_utc`, `window_end_utc`, `cutoff_utc`, `rate_card`, and `pricing_basis`. Its direct `usage` contains a `tokens` map of token categories to nonnegative integers and `priced_usd` as a decimal string or `null`. Record `coverage` separately. An optional `supersedes` names the earlier receipt digest. Tool runtime has no price of its own.

For a verified monitor export, embed `verification` with:

| Field | Recorded evidence |
| --- | --- |
| `operator_ref` | Safe pseudonym of the operator who checked the source and story attribution. |
| `verified_at_utc` | UTC time of verification against the pinned report. |
| `source_report_id` | Original report identity, matching the selector. |
| `source_sha256` | SHA-256 of the original private export, matching the receipt source digest when provided. |
| `verified_story` | Direct subject ID checked against the export. |
| `selector` | Exact copy of the receipt's report selector. |
| `pricing_basis` | Pricing basis from that selector. |
| `coverage` | Verified coverage for the same scope as the receipt. |
| `sanitized_data_sha256` | SHA-256 of the direct `usage` object as compact, sorted UTF-8 JSON with no trailing newline. |

The operator compares the private source with the sanitized payload and the registration. The validator checks shape and binding. The later usage projector also checks source assurance and selection before admitting Cost. An unverified receipt, a self-asserted flag, or a missing price cannot establish complete Cost.
