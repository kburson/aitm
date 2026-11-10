# #138 · Verified serial CI baseline

The canonical `aitm.tia-baseline/v1` record has SHA-256
`f085f922a6fffadf98900a514b6129aa7bc9315ecd1029cf9a219213fce47731`.
Two offline projections of the same closure-owner-verified inputs produced identical bytes.
The canonical record, original receipts, protected replay results and normalized input envelopes are in private custody. The verified CI and timing envelope SHA-256 values, respectively, are
`a87e30bf56de25472daa67de4b16f77529af599ba2bf9682aeb2b0116e27b4b9` and
`975e5c25372ea57edc43949a5805a41cf4a31ced51b5a9b06b1810274c714bf9`.

## Historical proof

Repository `kburson/aitm` (ID `1450406435`), workflow
`.github/workflows/ci.yml` (ID `412848571`).

| Role | Attempt and check suite | Checkout | Tree |
| --- | --- | --- | --- |
| PR [#179](https://github.com/kburson/aitm/pull/179) candidate, `refs/pull/179/merge` | [42869601092 attempt 1](https://github.com/kburson/aitm/actions/runs/42869601092/attempts/1), suite `116101474724` | `2b5208ebca881bc1b383f71af0e8e9355b4839bc` | `c1c9bc00e7845278b805d4f2828de3663a79c18e` |
| Trusted PR base, isolated `python-base` | Same PR attempt and suite, [job 130016998755](https://github.com/kburson/aitm/actions/runs/42869601092/job/130016998755) | `9b12927da1a368f254537277f7fdc7139f90cc44` | `5ca29c2890eefadd8fc8000aff442144335c4cae` |
| Delivered trunk push, `refs/heads/trunk` | [42871778928 attempt 1](https://github.com/kburson/aitm/actions/runs/42871778928/attempts/1), suite `116107403358` | `37a22922f072e39c35434ae645a1c20692b8da01` | `c1c9bc00e7845278b805d4f2828de3663a79c18e` |

The tested merge and delivered push have ordered parents
`9b12927da1a368f254537277f7fdc7139f90cc44` (PR base) and
`ddf87559f352a1f62f947b683e512d68348a1ecc` (PR head). The
[retained #115 checkpoint](../../115/plan/delivery-checklist.md#snapshot-repair-review-checkpoint)
records the original passing verifier disposition from before the merge, with
[independent review](../../115/plan/post-ci-source-review.md). The checkpoint
is the retained premerge evidence available for this report. At #138
implementation the protected verifier certificate check independently passed on
the historical signed subject, and the protected historical Python gate passed
in both PR and push modes. Those later checks corroborate the historical
records. The collector and signed `candidate.json` were byte-identical;
subject SHA-256
`28d8102a38ca8c130e8c5c5f95eeea8a2d34d648d7fef96367e58c09c68811e2`.
The signed subject binds the raw candidate observer, product source inventory
and trusted base receipt listed below. The push proof has its own job and
archive custody and independently replayed gate result.

| Historical archive | Original ZIP SHA-256 |
| --- | --- |
| [PR base 13789881233](https://github.com/kburson/aitm/actions/runs/42869601092/artifacts/13789881233) | `ef902445d3fa71f9b35f9e2417e69a6f0b841a2bce6e8312b227b87ea593fde2` |
| [PR Python 13788603444](https://github.com/kburson/aitm/actions/runs/42869601092/artifacts/13788603444) | `927e1113fc7b02dfafb587c43e71490448c0d24781bc366fbad9dec242415f78` |
| [PR collector 13788903030](https://github.com/kburson/aitm/actions/runs/42869601092/artifacts/13788903030) | `70f2df3db8aa241cae9f7f98ef79a70e8acf18563085ae53e57672d16b7293a4` |
| [PR signed 13790255902](https://github.com/kburson/aitm/actions/runs/42869601092/artifacts/13790255902) | `3ab42fd5de5735616dc4c500e85ce933159ddd373f576effc9296f1449d8d264` |
| [Push Python 13788584397](https://github.com/kburson/aitm/actions/runs/42871778928/artifacts/13788584397) | `aab36e6826ad136601408cbfc6f830513cbd9f8b201986997a8d5c356e8cd631` |

| Job | PR candidate attempt | Trunk push attempt |
| --- | ---: | ---: |
| `python-base` | 130016998755 passed | 130024573152 expected skip |
| `python` | 130016998564 passed | 130024571344 passed |
| `quality` | 130016998329 passed | 130024570847 passed |
| `file-checks` | 130016998616 passed | 130024571234 passed |
| `collect-evidence` | 130022068436 passed | 130025880805 passed |
| `aitm-ci` | 130022162949 passed | 130025989566 expected skip |

The two tested roles used `macos-26`, Darwin/APFS, image
`macos26:20261102.0473.1`, Xcode 26.6 build 17F113, Python 3.13.9 and
uv 0.10.6. The exact historical and current delivery base control blob
identities are pinned in the [pickup inputs](../plan/2026-11-10-138-jit.md#current-delivery-base-and-gate).
The trusted base records its own checkout, observer, policy, lock,
configuration and runtime. Its archived policy bytes matched its trusted
Git object.

| Control bytes | SHA-256 |
| --- | --- |
| Policy | `323498224344b7852da7c02299ff7e5812e3d9fbd1557c4e950de0b7dd8ba776` |
| Observer | `dd08c448cafe1ef0e6f5b8eba660d8485bfe76657c109c5249e86efd735025d1` |
| Lock | `c6eec029d208a44d6e25cf78e0fb1bf5484387cab2503d9f38ab3a65aec5e0d2` |
| Package configuration | `0ca837d80aabe44113d4fc7cc985985bcfd8bf76e4d3fa1736542ae29a058232` |

## Inventories and outcomes

| Role | Classified outcomes | Original test receipt SHA-256 | Sorted compact node array SHA-256 |
| --- | ---: | --- | --- |
| PR candidate | 630 passed | `88d9fa4ac64ad38c33c94c748f4ab560b89702d2bcd6459facae8bfed0dddaa0` | `f2cd0560357641dfbb9a1286137a2e5e1e6c5837af7ad0ca803336442b0c1b5b` |
| Trusted PR base | 592 passed | `e7883daefb59e7baf50284709d8a98b3ee531cc13a22cc98481d57ea2a3283dc` | `e712a4ccb6d349bd1a8ea18f39a1c2a9a9196d11e866d444e03376b30e49b7d0` |
| Trunk push | 630 passed | `b90f011014fd85422bdba48d1c02758365a88d8ade8683ad1fb77a8261ae432e` | `f2cd0560357641dfbb9a1286137a2e5e1e6c5837af7ad0ca803336442b0c1b5b` |

The candidate and push each covered the same 22 tracked product source files.
Original `product-inventory.json` SHA-256:
`e88eb92e4c385030daf62777ffdddc048baccc874bb5fe508b390325ac3b2afc`.
Their product and CLI observer scopes include
`tools/ci/tests/test_cli_evidence.py::test_usage_console_help`, absent
from the product-only base. The PR comparison retained all 592 base
outcomes.

| Role and coverage scope | Covered/executable lines | Covered/executable branches | Original coverage SHA-256 |
| --- | ---: | ---: | --- |
| PR candidate product | 7,146/7,825 | 2,070/2,578 | `a6d463bf157e0fcfe23fe6ed66b1ebf81de4de61561590a79620d07cec3ebddd` |
| PR candidate helpers | 778/821 | 231/262 | `cc97eb36821f0bd58dddef1d58b36b5bf44fc56e32036b854845802d98db0745` |
| Trunk push product | 7,146/7,825 | 2,070/2,578 | `b5b337c3aba8b9e055b85abc460721dfb1a90221272d4f7772082c7d2863d65b` |
| Trunk push helpers | 778/821 | 231/262 | `079b3a2f7769a75d5836d22479306ac740e9b62395113b6c0a56b93ed9f91ff8` |

The protected replay passes the unrounded 90% line floors in both scopes.
The helper denominator is the four policy files `tools/ci/python_gate.py`,
`tools/ci/pytest_evidence.py`, `tools/ci/verify_pr.py` and
`tools/ci/file_checks.py`. Branch counts remain scoped evidence.

Both tested roles record normal exits for `cli-help` and
`service-one-shot`. Child receipt SHA-256 is
`a113d1ab9bf03e77de375c2c29490d98a6f21dc85d9e869396cede24c798f7b8`
for the candidate and
`db9cfeb9390d5b5197f936b837ccbb2c915a14731e62324a33eb9f2b4bd73c1e`
for the push. Wheel SHA-256 is
`5bf6b420aec2d15948a75921b284f3b56a9cb84158c98191a91172857071ab0a`
in both roles, with successful installed-wheel smoke at
[PR Python step 6](https://github.com/kburson/aitm/actions/runs/42869601092/job/130016998564#step:6:1)
and [push Python step 6](https://github.com/kburson/aitm/actions/runs/42871778928/job/130024571344#step:6:1).
File checks passed at
[PR file step 5](https://github.com/kburson/aitm/actions/runs/42869601092/job/130016998616#step:5:1)
and [push file step 5](https://github.com/kburson/aitm/actions/runs/42871778928/job/130024571234#step:5:1).

The pinned observer collected **182 local advisory helper IDs** from the
shared tree, with exit 0, zero deselections and no phase reports or child
receipts. The [accepted plan](../plan/2026-11-10-138-pin-serial-baseline.md#3-reconcile-the-real-proof-and-record-delivery)
pins the command, four test targets, Python and lock. Original observer
SHA-256 is
`15a169e620c5b0a8e4180cfc7bf4b9b3597ba58d9788bb669312c3323e13111c`;
sorted compact node array SHA-256 is
`69cef362f4c87ba65846443eda6a2c8ae3dca3431f76905dcefc459c1e7200a4`.
The hosted helper jobs recorded coverage and overall success; their
per-node IDs and outcomes are unavailable.

## Timing and scope

Both exact Python lanes restored the same approved warm dependency cache.
The cache observation is recorded in
[PR Python step 3](https://github.com/kburson/aitm/actions/runs/42869601092/job/130016998564#step:3:1)
and [push Python step 3](https://github.com/kburson/aitm/actions/runs/42871778928/job/130024571344#step:3:1).
The shared observed key was
`setup-uv-2-aarch64-apple-darwin-macos-16-3.13.9-86ea6163e21c5eefe099281368d1bff32a6794dac7125c28e31557d8d0ca107d-macos-26-python-3.13.9`.
The independent PR base ran with its own uncached setup.

| Boundary, in seconds | PR candidate warm | Trunk push warm |
| --- | ---: | ---: |
| Run creation to Python job start | 305 | 3 |
| Python lane start to serial test bucket start | 5 | 3 |
| Serial product and helper test bucket, including coverage and helper setup | 181 | 111 |
| Python lane start through installed wheel smoke | 187 | 115 |
| Python job start to completion | 205 | 127 |
| Last required dependency completion to collector start | 2 | 3 |
| Collector start to completion | 8 | 8 |
| Run creation to last applicable job completion | 533 | 141 |
| Sum of non-skipped job elapsed time | 370 | 198 |

Raw Python timing SHA-256 is
`25dff39e830819dac2e2ff199bea8c08584bc29d10687b27b995a458fb783925`
for the candidate and
`aa26cc6f11692c93dc652fe33b8c6b88eb927102a57b4e4ecb289d2aa3b906d4`
for the push. Each role's comparable cold timing is **Unknown** because
that profile was unobserved. Finer test-only timing, unit/integration
splits and billed cost are **Unknown** for each role. The job duration
sum measures hosted job consumption; feedback uses elapsed wall time.

This is a historical comparison and input for #139 inventory
reconciliation. #103 remains the active PR gate. The advisory IDs carry
no hosted per-node outcomes or qualification, and these warm measurements
carry no cold, observer, scheduled health, FullProof, merge or Stop the
Line authority.
