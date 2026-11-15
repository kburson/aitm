[06:22:09]
**REFINE_137: HOLD**

## What passes on the supplied evidence

- **Scope.** The text matches the hold record. #137 is Rank 350 under Epic #100, and its only prerequisite is #115, which is closed. #129 is still downstream and keeps its own host+architecture qualification. Epic #2, C01 and production cutover stay excluded.
- **Field shape.** The numbers agree with each other:
  - 3 distinct turns: 2 with a hook receipt, 1 hookless.
  - 2 retained native prefixes, each adding exactly 1 identity.
  - Usage reconciled for all 3 records, plus 3 private capture hashes.
  - `product_linux_adapter_cursor_proven: false` is stated honestly and left for implementation and Test.
- **Hook ordering and the hookless record.** `verified_boundary` returns `None` when there is no hook, when the hook comes after the update, or when the receipt fails to verify. So the hookless third turn already gets no story eligibility, which is what the proposal requires.
- **Estimate.** The four parts add up: 0.75 + 0.75 + 1.5 + 0.75 = 3.75 hours, which fits Size M. It holds only if blocker 3 is settled without new implementation work.

## Blockers

1. **The Linux transport's origin and timing aren't evidenced.** The only anchored record, the hold at trunk `011342493399…`, says no Linux sandbox, SSH alias, runner or admission was available, and that no paid request ran. The new observation doesn't give:
   - when it was captured relative to that hold;
   - which Linux host was used (pseudonymized is fine), its kernel or distro, or its admission record;
   - approval for the three paid model requests;
   - the trunk or #115 baseline the estimate assumes.

   A dated field record covering these is needed before the "authenticated Linux" claim can be accepted.

2. **Some fields the existing gates check aren't recorded.** `_qualified` requires `format_version == 1` (an int) and `lineage_id == session_id`. The Linux evidence reports neither, and doesn't say where the native session store lives on Linux.
   - Pin the exact tuple: `("Linux", "aarch64", "1.0.77", "50ca579fa996", "b30eee14a656…eed574")`. The host reports `aarch64`, while the package name and macOS use `arm64`. Either the raw value is kept or a normalization rule is written down.
   - The digest line is labeled only `binary`. Record the installed executable path that was hashed on the host, and the package's registry integrity value, so the "pinned official" claim is backed by evidence and not just asserted.

3. **Receipt issuance on Linux is not budgeted.** The process proof (`/proc` executable, start identity, ancestry) came from a scratch hook that was then removed. The 1.5-hour part covers only reading and preserving receipts.
   - Show from #115 evidence that the product hook and receipt issuer already work on Linux, or that `verify_receipt` (nonce plus HMAC) needs nothing platform-specific.
   - Otherwise, add and budget the Linux process-identity work, which may push the story past 3.75 hours / Size M, or exclude it explicitly and explain why.

To get PASS, resolve all three. Also add a JIT test for a hook event and an update with the same timestamp, since `hook.time > update.time` currently lets a tie through.
