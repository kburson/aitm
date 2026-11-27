# PR #558 verification

Base `30552dd22c88167887da6b89f0d4b453aba77a37`, head `147727bf8a2e89203a53532c4b375dae7379019d`, synthetic merge `99793e2875329f83b00b47e5755b3857fa7a7f16`, tree `03b226bacc7f1ea9a05c8f4192ce128fa592e8ba`.

The initial installed repair test failed with the capability unavailable. After wiring repair, a second failing assertion reproduced a changed repair commit identity when retrying an incomplete remote push. The final focused test passed on real disposable Git clones. It verifies the same repair commit on retry, the maximal valid prefix, the retained unpublished ref, fresh installed validation, and refusal of stale or older state, forged receipt, and code-shared ancestry. C06 and the full unit suite passed with the explicit unregistered verifier behavior unchanged. Ruff check and format passed. The full unique Core collection is 756 unit and 62 integration out of 818. Hosted repository run #46056757256 and Core run #46056757092 qualify this exact draft candidate separately.

## Revised candidate

Head `ccbe80a8e56af496439d3420cf8aa0f06a0e8358`, synthetic merge `b224d54ce787148668abda94f94cb3f52fccf93c`, tree `5fb1586bfe0fe19f5fbb255a3221354a8466873e`. The focused regression first showed that stopping immediately at a forged receipt prevented validation of a later legitimate repair. Validation now retains the refused evidence, still rejects a chain that ends without a valid repair, and accepts a subsequent exact maximal-prefix proof. New repository run #46057090109 and Core run #46057090113 were started from draft.
