# Capture timing and verify a board update

Use this manual workflow while the local dashboard reads evidence from planning. The recorder publishes scoped observations. The board operator projects the value from an independently rebuilt snapshot.

## Capture and publish

1. Choose a story, a stable agent pseudonym, a phase, a role and an attempt. Record the verified start and end of the story-bound turn, the tool execution and return boundaries inside that turn, and any explicit request and response from the owner. A tool span belongs inside its turn. Record a switch at the verified boundary and keep work after the switch on its own story. Preserve an unresolved endpoint as a gap. See the [capture checklist](capture.md) for the receipt and journal schemas.
2. Keep raw session records and usage exports in private storage. Record only safe source references or digests and the observed UTC timestamps. Mark partial observations and incomplete workflow coverage. An owner request without a verified response cannot establish a completed wait. A gap in activity cannot establish a turn.
3. Validate the exact candidate receipt and registration against a full local clone with the current planning commit. Keep the UTC cutoff at or after the pinned commit and all registration timestamps. Use the private files and the exact intended branch head.

   ```sh
   python -m tools.story_dashboard.evidence \
     --repo "$reader" --commit "$planning_sha" --as-of "$cutoff_utc" \
     --receipt "$private_dir/receipt.json" \
     --registration "$private_dir/registration.json"
   ```

4. Publish the receipt bytes and the one journal entry in the same expected-head planning commit. Read both back at that commit. On an uncertain result, read the current branch and compare the exact bytes, digest and journal entry before retrying. An exact replay is complete when the existing bytes and the single registration match. Resolve any mismatched or incomplete publication before continuing.
5. Fetch the pinned planning commit into a separate clean Git reader. Build and retain the prior and new views with explicit cutoffs. Use an external output directory for each view.

   ```sh
   python -m tools.story_dashboard.snapshot \
     --repo "$reader" --commit "$published_sha" --as-of "$cutoff_utc" \
     --output "$private_dir/post-capture"
   shasum -a 256 "$private_dir/post-capture/snapshot.json"
   ```

   Match the result to `snapshot_sha256` in `validation.json`. Check the story ID, timing coverage, evidence-through UTC and the receipt digest on its Actual measure. Check the contribution appears once. Confirm the reported owner wait separately. Compare estimates only against complete evidence for the same phase and agent scope.

## Project Actual to AITM-PY

Resolve the AITM-PY project and item by repository and issue number. Verify the numeric Actual and Cost fields and the text Actual coverage field. Record their IDs, existing values, the planning pin, snapshot digest and applicable evidence-through. Confirm the story is still the intended board target and that its planning evidence has not changed since the snapshot. Hold the write if it is stale, if fields are missing, or if the projected Actual is Unknown.

Divide the snapshot's `timing.actual.milliseconds` by 3,600,000 and round once to four decimal hours. Derive the coverage label from that same measure and include its evidence cutoff when known. Use these readback pairs in sequence.

| Checkpoint | Actual | Actual coverage |
| --- | --- | --- |
| Before the write | Original value | Original label |
| Before changing Actual | Original value | Pending verification |
| After changing Actual | Target value | Pending verification |
| Final | Target value | Target label |

Write and read back the interim label first. Write Actual and read back the numeric value and interim label. Only then write the final coverage label. Read both fields back again. After an interruption or ambiguous response, reread the item and continue from the exact matching checkpoint. Hold on any conflicting pair and reconcile the evidence before changing fields. Preserve the original pair when the target cannot be established.

Read Cost independently. A populated Cost requires a verified monitor export and complete pricing coverage for the exact report selector and target scope. An empty, unpriced Cost stays blank. Tool duration contributes to Actual within the qualified turn. A usage receipt supplies any measured cost.

## Verified pilot

The authorized #191 pilot observed 4,891 ms of agent engagement. That includes 3,896 ms for a tool executed inside the turn. A separately recorded switch ended #191 activity before work on #192. The owner request was observed. The response boundary was missing at publication, so Owner wait is Unknown. The timing receipt is partial and excluded from calibration.

A separate clean reader rebuilt the [published pilot commit](https://github.com/kburson/aitm/commit/527dce9bd7847181a67dc23c6bb2c9844f15c87f) at `2026-11-11T04:45:27Z`. The prior view had Unknown Actual. The new view contained one contribution from the [immutable receipt](https://github.com/kburson/aitm/blob/527dce9bd7847181a67dc23c6bb2c9844f15c87f/.aitm/stories/001/191/attachments/timing/live-pilot-a06-191.json) and one exact registration. Replaying the same bytes and entry left planning unchanged. The new snapshot SHA-256 is `94a2c286b3de1bce4e49eb38cc1b35128ce470de83c644e65f843809a33f6fe9`.

The [AITM-PY item](https://github.com/users/kburson/projects/24) for [#191](https://github.com/kburson/aitm/issues/191) began with all three fields blank. The operator stopped and independently reread after writing the interim coverage label and again after writing the numeric Actual. The final readback was **0.0014 h**, **Partial** through `2026-11-11T04:43:35.855Z`, and blank Cost. This readback records the one-turn pilot.
