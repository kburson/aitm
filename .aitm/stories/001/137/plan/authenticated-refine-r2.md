[06:27:11]
**REFINE_137: HOLD**

## Resolved since the last hold

- **Capture origin and timing.** The capture window is 2026-11-15T11:52:11Z to 11:52:23Z, after the November 11 hold. The host is `scratch-grok-linux-arm64`, running the `7.0.12-linuxkit` kernel on aarch64 with Debian 12. That fits the owner's scratch Docker VM. The baseline is frozen at trunk `4cfb4181…` and #115 merge `37a22922…`.
- **Tuple spelling.** The packet now pins `("Linux", "aarch64", "1.0.77", "50ca579fa996", "b30eee14…eed574")` and states that the raw `aarch64` is canonical. No normalization rule is needed.
- **Receipt issuance.** The source confirms that `verify_receipt` is an injected callable. `verified_boundary` has no platform-specific code. Excluding a Linux issuer and owner setup, with #129 owning target-native proof, is explicit and justified. Because of that exclusion, the 3.75-hour, Size M estimate stands.
- **Tie test.** A test for a same-timestamp hook and update, with ordinal precedence, is now in scope. Today `hook.time > update.time` lets a tie through, so this replaces that comparison. It fits in the JIT part of the estimate.

## Remaining blockers

1. **The executable hash isn't tied to `/probe`.** The SHA-256 line is labeled `binary`, but the provider path is `/probe`. Nothing observed shows the hash was taken of `/probe`. Both `sha512-Kb4y…` lines match each other, but that value is the integrity of the npm tarball, not of the executable. Nothing records that `binary` came out of that tarball. Needed:
   - `sha256sum /probe` output from the capture;
   - a record that the executable was extracted from `@xai-official/grok-linux-arm64@1.0.77`, with that executable's SHA-256 shown next to the matched integrity.
2. **Several gated fields appear only in the prose.** The observed JSON is the same as at the last hold. None of the following appear in it:
   - `format_version == 1`;
   - `lineage_id == session_id`;
   - both resumes keeping the same session and lineage;
   - one process-bound receipt per marked turn;
   - the v1 update and accounting decoders accepting 3 rows and 3 snapshots;
   - the `GROK_HOME/sessions/<percent-encoded checkout>/<UUID>/updates.jsonl` plus `usage.json` store layout.

   Add these as booleans or counts to the qualification record, alongside the existing capture hashes.
3. **There's no record approving the three paid model turns.** The owner continuation and account handoff are only stated in the packet. Attach a dated owner-approval reference that covers the two marked turns and one hookless turn.

Resolve all three to get PASS. Scope, exclusions and estimate need no changes.
