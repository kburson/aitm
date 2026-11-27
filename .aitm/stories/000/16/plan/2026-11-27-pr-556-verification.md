# PR #556 local verification

Base `74cbd6a9686b630910cc0f6858bbd458014cc182`, head `a3590a59eeff89b8dc8253f13a9521f839a1edf5`, synthetic merge `5053f87d372962ce464147c1e5fc62ad9dffcb2d`, tree `ec60fa7ad0e295f576ce4297b2c923104d0e8f24`.

- RED: focused C15 suite could not collect because the required description producer was missing.
- GREEN: seven focused cases passed. The full Core product suite passed 810 tests. Locked non-editable unit and tooling verification passed 757 tests. Ruff check and format check passed.
- The installed `aitm describe` console was exercised in a disposable Git repository with an explicit C07 fixture policy, initialized story and store anchor. It returned typed local completion, staged one atomic description/event/receipt commit, and the new history validated through the public anchored validator.
- Local macOS full unique Core collection: 756 unit, 54 integration, 810 total. The Core limit remains 92%.
- Hosted Core CI run #46051144078 and repository CI run #46051144100 were triggered for this draft implementation candidate. Hosted conclusions, independent review and verifier are recorded separately.

## Current candidate

Head `f112ae86e526c67df40890745a0feb7edc61dae5` replaces the first candidate with a generated `story.md` view from folded state. The expanded golden tests first failed on the missing StoryState projection. The reinstalled, locked wheel passed all 757 unit and tooling tests and Ruff. The existing Core 92% floor remains 756 of 810. The aitm-usage macOS collection is 1,642 unit and 138 integration out of 1,780, at the same 92% floor. The successful older hosted runs cover only the prior candidate.

Base `74cbd6a9686b630910cc0f6858bbd458014cc182`, synthetic merge `ddbe6b85ed99c17e200eb8a2df65a5af96fde986`, tree `4f3d341967e701bcd1a2d9ca9ba88c0900e99c54`. Hosted repository CI run #46051591543 and Core CI run #46051591564 qualify this exact version separately.
