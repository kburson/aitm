# #570 exact draft qualification

Base `fb23ebeb2b36f61e6c6bdfbc67ccc18df3d81359`, head `fff1d41e7a9445b6f807e988ad58f8e9a1197fe6`, synthetic merge `58c9ba4f07135dc283cadc27c5e56f5649fa97c0`, tree `624eb9c9b8c1f204d03db00039548f2912e753fb`.

The focused test initially failed because the source and identity authority contracts were absent. The exact draft passed 37 focused and affected tests. Disposable shared Git repositories and provider doubles exercise distinct operation IDs joining one semantic reservation, reentrant sender contention, lost acknowledgement, positive absence without a fence, supported retry with bound fencing proof, uncertain cancellation, and a frozen draft that changes after reserve. The provider contract tests preserve C13 compatibility.

The PR remains draft while [repository CI](https://github.com/kburson/aitm/actions/runs/46096942277) and [Core CI](https://github.com/kburson/aitm/actions/runs/46096942271) run against the exact candidate.
