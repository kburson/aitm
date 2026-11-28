# #569 draft candidate

- Base `4fdf3b1f34b77fe387d2580b49951d1a73471389`
- Head `769485499a1094a7ece2c757f13030b76663070f`
- Synthetic merge `aef78a68c7a412489fd54862d94c2f28fff8a976`
- Tree `aa0d95658da710e310bb9fb623ca799ead436e67`

The installed real-Git test first failed because the idea open route was unavailable. The draft candidate adds entity open, entity sync and unbind, canonical entity scope pins, and an in-transaction binding disposition for discard. #569 is draft while [repository CI](https://github.com/kburson/aitm/actions/runs/46094392859) and [Core CI](https://github.com/kburson/aitm/actions/runs/46094393058) qualify the exact candidate. #567 stays draft.

## Revised draft

The initial hosted Core run passed 937 tests and failed one C17 test that explicitly expected the unimplemented entity sync stub to return unavailable. The installed route now validates the binding coordinates. The revised assertion verifies the integrity error and message for missing coordinates, and preserves the rest of the C17 behavior and tests. No check was removed.

- Base `4fdf3b1f34b77fe387d2580b49951d1a73471389`
- Head `c7f2a9a207d4f7069fad9ed9cc18f323f46667b5`
- Synthetic merge `d56354dc979b51b08993efed0adac334721aa045`
- Tree `bdb2c55b5fc6e7484c990eb82c1e6e77567a1c47`

The revised candidate passed all eight affected local cases, local tooling and Ruff. The macOS full collection counted 863 unit of 938 Core cases and 1,642 unit of 1,780 aitm-usage cases. [Hosted Core CI](https://github.com/kburson/aitm/actions/runs/46094616961/attempts/1) passed 938 product and one tooling test with the unchanged 92% floor. [Hosted repository CI](https://github.com/kburson/aitm/actions/runs/46094616963/attempts/1) and the [trusted verifier](2026-11-27-pr-569-c7f2a9a2-verifier.json) passed on the same base, head, synthetic merge and tree. #569 was marked ready only after those gates passed. The independent Grok 4.7 source review was then requested.
