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
