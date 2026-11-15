# #289 independent SAR for the first scheduled slot

**Scheduled qualification remains incomplete.** GitHub's provider records contained zero scheduled runs for the 2026-11-15 03:47 UTC slot at the end of its 45-minute grace period. The independent readback at 04:32:17 UTC produced `status=incomplete`, `current_verified=false` and `artifact=null`, with the diagnostic `no run for the current schedule slot`. [#289](https://github.com/kburson/aitm/issues/289)

Signed by OpenAI Codex, independent review agent `/root/review148`.

- `kburson/aitm`, repository `1450406435`, protected default branch `trunk`, source `6b64ea873e438769c23e0a37b7fa7c0155629fbe`, tree `7eba00e5b2fb7a41f215392978fc6eb56be1c49c`. Workflow `418826440` was active at `.github/workflows/scheduled-full-shadow.yml`. [Workflow](https://github.com/kburson/aitm/actions/workflows/scheduled-full-shadow.yml)
- Independent branch- and event-filtered provider readback returned `total_count=0`. Unfiltered provider readback listed two runs, both `workflow_dispatch`. The original diagnostic `43670107921/1` failed before it could publish the full receipt. The corrected diagnostic `43671830880/1` passed on source `a76eecf856bdd42fbaeb7fdf13b57a0ec404d334`, with artifact `14144707069` and archive digest `sha256:ab48cdf0f556dbe44713799e8e2bbecdcb82d6d7d907f08c33f95395f6e5e9cb`. [Original diagnostic](https://github.com/kburson/aitm/actions/runs/43670107921/attempts/1) · [Corrected diagnostic](https://github.com/kburson/aitm/actions/runs/43671830880/attempts/1)
- Independent exact-source reader output, SHA-256 `f6500a0a057ac18b846fa6849c2c1a4cb686770f6a489a077305a72f3aa3e71c`. It matches the separate primary readback byte for byte. [Reader output](independent-schedule-gap.json)
- Independent provider record projection, SHA-256 `b51dc9ceb03fedac380cf6ceebeca3811b5316589a6f6735bd4716b4dc6eed7a`. [Provider projection](independent-schedule-gap-provider.json)

I independently collected 1,240 ordered product IDs and 540 ordered helper IDs from the exact protected tree before the slot. No hosted scheduled inventory, test outcomes or native-child receipt were available to reconcile. The incident adapter rejected the unverified gap as input for replay. Provider evidence establishes the absence of a registered scheduled run at the cutoff. The reason for the missing event remains unverified.

The five existing production control blobs and three effective branch rules exactly matched the pre-change baseline. #103 remains the production merge gate. A verified genuine scheduled run on the protected default branch and independent review of its evidence remain open for #289. [#103](https://github.com/kburson/aitm/issues/103)
