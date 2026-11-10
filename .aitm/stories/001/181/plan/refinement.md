# #181 refinement for capture and local dashboard

The accepted design places evidence capture and a pinned snapshot in A, an offline local dashboard in B, and product integration in C. The owner requested A and B first while Core #2 and monitor #100 are underway.

The scoped planning estimate is **26.0 implementation agent-hours**. A accounts for 20.0 across six leaves and B accounts for 6.0 across two. Estimates are bottom-up allowances for implementation, local verification and source-review engagement, with a four-hour cap per leaf. They are provisional until each leaf's applicable refinement and JIT. P1 expresses the requested delivery priority. The feature estimate describes A/B only.

The first leaf delivers a receipt validator and operator instructions. The local reader and dashboard can work from the existing planning store and the preserved historical seed. C remains part of the accepted product design and requires separate refinement against the eventual owning interfaces. Its work is outside the A/B estimate and A/B's dependency graph.

Use the reviewed plan's leaf catalog to verify dependencies and pickup order. Parent Planning acceptance does not supply a leaf's design, plan, JIT or implementation authority.
