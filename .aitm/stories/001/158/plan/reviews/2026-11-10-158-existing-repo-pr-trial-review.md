# #158 independent review of the GitHub PR merge trial

**Disposition.** Accepted for publication as bounded evidence. Full
#158 qualification remains held and #159 stays blocked.

| Reviewed artifact | SHA-256 |
| --- | --- |
| [Synchronous receipt](../../attachments/2026-11-10-158-existing-repo-pr-trial.json) | `b9e21f866a2d4ccc1eca1993cd74c257ad1e00ea3d01ca3040be8c27d49d954f` |
| [Asynchronous receipt](../../attachments/2026-11-10-158-existing-repo-async-merge-trial.json) | `a3b59d4206d2a11549d6d5ede7ba8d61b12770e4d352676b94807b2e2c46d0e3` |
| [Combined report](../2026-11-10-158-existing-repo-pr-trial.md) | `5dd67461f997036cc955d7013a8f210f24f8a6a85609bb8c3e3178061cfbc47d` |
| [Story record](../../story.md) | `548c981812351c6542a0cf33940aec9744fac1698f1175ec7d77b05e8bd33bf9` |

The reviewer verified the staged hashes, REST responses and request
IDs, candidate Git trees and parents, client journal, protection
snapshots, and terminal cleanup. The synchronous request sent before
the simulated stop has a terminal denial and no demonstrated server
admission time. The separate async request's acceptance body preceded
the stop marker. Its UUID still returned pending after activation,
then failed with an active-rule denial. The target ref and PR
readbacks reconciled both requests before cleanup.

The review identified GitHub's separate asynchronous route and
checked its measurements in a follow-up. The final report attributes
the Claude account settings and the web merge button to coordinator
observations, with Claude's internal event handling unobserved. The
prior spike and #159 artifacts are untouched. No publication
findings remain.

Reviewer: independent Codex agent `review158_pr_trial`.
