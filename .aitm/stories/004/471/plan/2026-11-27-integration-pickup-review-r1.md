# #471 initial pickup review

Grok 4.7 Build Fast requested changes. The actual ledger uses an ordinal and a separate verified board rank. The project readback and published ranks both put #471 at rank 20 as the second epic. The amended plan makes the distinction, clarifies child dependencies, and enumerates the decision sets and consumer gates.

CHANGES REQUIRED

The #471 pickup mislabels this epic as rank 20. On the accepted ledger, Legacy rule and policy qualification is epic 2: 4 children, 15 hours (4 + 3.5 + 4 + 3.5), prerequisite none, integration owner C110, children C107–C109. Figure 20 sits on Core records and reducers. Inside this slice, rank 20 is child #495 / C108, and trunk admission is rank 40 #497 / C110.

The source pin must be stated as one pair everywhere it is used. Commit `c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905` has Git tree `844ae26bb169e8618e45fc3b1aedb57f44896fe0`. The accepted crosswalk’s “tree” label on the commit stays a retained crosswalk error. Child work cites that commit and that tree, and the later “pinned legacy tree” line uses those two identifiers.

Child order follows the ledger prerequisites. C107, C108, and C109 stay unblocked relative to each other. Only C110 / #497 waits on all three. The shared decision rows (C107 with C108, C108 with C109) meet in C110; they do not become a 10→20→30 sequence.

The decision inventory is eight sets, and the pickup still says six undecided registrations. Scope covers all eight rows: discussion and field meanings, parent eligibility and caps, deep-dive and plan metadata, ownership and overrides, dependency and blocker checks plus the code-complete marker, reviewed scope and closeout, resident action and evidence semantics, and verbs, directives, hooks, and provider policy.

Trunk and pickup gates match the ledger sentence that actually binds implementation. #12, #37, #80, and #241 wait on the C110 trunk decision fixture. #53 / C46, #21 / C16, #49 / C42, #42 / C35, #50 / C43, and C93 / C94 cite the matching disposition at their own JIT. A pending choice assigned to project policy holds Core only when the accepted profile lacks a defined behavior. Where the profile already defines behavior, the legacy exception stays visible and project equivalence carries the chosen rule plus a bounded proof.

Owner boundary stays: C107–C109 record observed behavior and a recommendation; an authorized policy owner approves only a real residual choice; C110 records source or explicit uncertainty, the named owner, the earliest gate, representative Core vectors, and separate provider handoffs, then lands on trunk. The slice branch is the integration branch from verified trunk `8aa608cc1e64ed5986c5b6a8371df5a4c5b3f3e6` after #470. Local verification, both hosted workflows, and a fresh Grok 4.7 source SAR apply to each non-draft story PR and to the final trunk PR. The configured-workflow amendment, its state flow, JIT review threshold, and host authority stay in force.
