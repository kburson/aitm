# #368 exact hosted ancestry execution packet

The [accepted ancestry implementation plan](2026-11-17-368-hosted-ancestry-implementation-plan.md) binds SHA-256
`361618e5244f2c64aaffb98a31a3ea291ee62797f27c700304f41bc7b225885f`. This packet authorizes a fresh synthetic worker and integrated observation on the previously
admitted image `20261112.0504.1`. It carries the exact 30-ID comment-only closure and 74 expected direct native processes from the preceding
reviewed packet. The earlier 7/23 result remains the baseline.

## Bounded preflight and timed dispatch

Plan acceptance was `2026-11-17T12:31:32Z`. The conservative cumulative charge at acceptance was 2.776 hours.
At packet submission the conservative total is 2.851 hours and cumulative admission/preflight is
2.227 hours, with 0.273 hours remaining for this phase. The exact product dispatch deadline is
`2026-11-17T12:52:24Z`, computed from plan acceptance plus the floor of 0.348 hours in seconds (1252 seconds). The reviewed input file
carries that exact UTC instant. It does not change across an exact-head job retry. Immediately before product dispatch, following boundary,
runtime, replays and all calibrations, the controller records its UTC decision and requires a valid canonical UTC deadline with decision time
at or before the bound instant. Missing or malformed UTC input and an expired deadline produce HOLD and leave product launch unset.
The fail-first tests demonstrated the missing pre-dispatch authorization, then passed exact equality, expiration, malformed, and absent input
controls. Twelve existing tests plus the new dispatch test passed. The remaining window includes the completion of independent review and
hosted admission. Any earlier expiration ends with a bounded HOLD and retained local evidence.

## Ancestry isolation and evidence

The only net additions to the generated sandbox profile are literal `file-read-metadata` grants for `/`, `/Users` and `/Users/Shared`.
The existing admission-root metadata grant and Darwin root data-read exception remain scoped to their literal paths. In the real VM the
controller stages root:wheel 0755 admission root and a direct worker:staff 0700 scratch child. The ordinary-account diagnostic uses local
ownership under its own synthetic root. The live controller compares matching pathname, owner class, full mode, and ACL classes for all five
paths using the exact compiled probe outside and inside Seatbelt. The worker's real and effective UID must match the pinned worker UID. The
no-follow ACL predicate is the exact text admitted by the product, and the comparison catches a sandbox-masked ACL. The probe prints classes
only. [Ledger ancestry](https://github.com/kburson/aitm/blob/8218a69ad6d9d9f33c6383bd5a6cd4930bef21d7/packages/aitm-usage/src/aitm_usage/ledger.py#L193) · [Darwin ACL implementation](https://github.com/kburson/aitm/blob/8218a69ad6d9d9f33c6383bd5a6cd4930bef21d7/packages/aitm-usage/src/aitm_usage/host_fs.py#L41) · [Physical directory check](https://github.com/kburson/aitm/blob/8218a69ad6d9d9f33c6383bd5a6cd4930bef21d7/packages/aitm-usage/src/aitm_usage/monitor_registry.py#L736).

The strict EPERM controls cover directory opens on `/Users`, `/Users/Shared`, and the admission root, metadata and ACL of the actual
controller home's directory and public prefix-sharing sibling, and data from the synthetic mode-0644 sibling. The controller creates only
that synthetic sibling atomically with EXCL and NOFOLLOW, then verifies its identity and public bytes. Existing checkout, controller-home,
credential, controller evidence, scratch-only write, same-named executable, trace device, and loopback controls still run. The C probe is
compiled with the admitted compiler and SDK. Its screened export is bound to the SHA-256 of the root-owned worker binary.

The exact previous and revised policy generators ran under the ordinary local account on copied pinned source. The initial ledger call
reported `LedgerError: Private ledger ancestry is unavailable`. The revised generator returned a six-identity chain and the pinned Python
resolver returned its exact synthetic physical directory, with all new EPERM controls. The 39-source manifest is checked byte-for-byte
against product Git. No product IDs ran locally. [Local evidence and driver](../attachments/2026-11-17-368-ancestry-local-reproduction.json) at SHA-256 `cf32ba754af1be84396cb0ca63b0a0292eb3144a1dee9df142ad3e29498037ac`.

## Runtime and exact code

Authenticated run `44024930299/1`, submitted head `e38d67d0254c0bac77761a48561c7ee5ecad315e`, artifact `14302787413`.
The available archive SHA-256 is `3841df4cfeca31523065b63d6b66ba72aec58aad4041e91854225d36564936ca`, manifest `1a5e9f5df23ffba83417532c4d67e9f51bb72f78570c7078027712fa238f11fd` and runtime
`402dda5423f9a0f97cf3b7c3ca25228503a101d552c4772b68ee5d0bc3d441dd`. Its 393 directories, 8,570 regular files and 10 confined symlinks match the manifest. The trusted preflight
verified GitHub identity, workflow, and success against the stored archive with no absolute member paths, hardlinks or unsupported types.
The runtime installer rechecks its manifest and resolved links before use. The fresh job must repeat the boundary checks, independent
observer and attached worker process, report replays, calibrated outcomes, scoped execution, and custody. Mixed-image allocations refuse
before qualification. Any new runtime identity comes through the accepted re-admission policy.
[Stage A artifact](https://github.com/kburson/aitm/actions/runs/44024930299/artifacts/14302787413).

Workflow head `f5f1cf8f48804c364375042ba32426a3125b9749` and tree `4c9cc4a50b74a552a8c8c33eb2aa6821839486cf`, on product base `8218a69ad6d9d9f33c6383bd5a6cd4930bef21d7`. The exact allowed set is the previous ten-path branch-only scope.
The only changes from the last integrated workflow head are below. Review committed content with
`git -C /Users/kpburson/.codex/worktrees/aitm-344-functional-tia/trunk diff d06b0e7f21a447cabbcd808364377a6736d16892 f5f1cf8f48804c364375042ba32426a3125b9749 -- .github/spikes/368`.

| Changed path | Git blob | SHA-256 |
| --- | --- | --- |
| `.github/spikes/368/admission.py` | `a2eba713235965d4dd1d4599441d9beef5df7df4` | `c71ebaa05c671b86eb7905130a7e6346d2011baab541f05a21ae68416ca9f169` |
| `.github/spikes/368/integrated.py` | `f062072aecd7ba08f3fcd9072130a673767a0c67` | `528463754382e5d40a16905a5f1123b5f4845e7e71c9fd9f1c743a4285066d21` |
| `.github/spikes/368/qualification.c` | `fb1de64f440f4b944deac431fe195639be78fd35` | `2764393a64bde17d42f78b9fa1f8b77eb28d39e3ea3384d2f8c4e7ffed4ff7b0` |
| `.github/spikes/368/stage-b-inputs.json` | `804c28c85e236839ac397eb277918f48c059d0d8` | `91fdd9f241b09fb71260c36ed64f693956b40e76f3789e879909e284ed7a1754` |
| `.github/spikes/368/test_integrated.py` | `a720cad19c229fb11bfb7f9a0d31d47241ad5c77` | `e4177c8e5210571741b08d0f8d4624c96822182d75a4e5de241d67e11be061f8` |

#368 remains open and #355 stays blocked. Local execution and resistance to unreviewed candidate code are outside the hosted PASS scope.
