# TIA build optimizer independent deployment enhancement

Proposed follow-on after the optimizer's base selection, sharded
validation, and Stop the Line qualification are proven. The
[accepted base design](test-impact-analysis-design.md) governs #133.

Expose the TIA build optimizer as an independently versioned
distribution. A repository can use its selector, runner integration,
coverage evidence, and approved health and repair authority without
installing AITM-Core or the usage monitor. The standalone artifact owns
its runner contracts and evidence. Installing it does not activate a
required gate, grant merge credentials, change protection, or enroll
workspaces. Those actions retain separate authority.

AITM-Core can optionally load a separately installed adapter through
the `aitm.extensions` registry and enable it in committed
`[extensions].enabled` policy. The adapter uses the versioned test plan,
outcome and health receipts. It checks repository, candidate, policy,
scope and freshness before projecting evidence to Core. External reads
and hosted execution stay outside pure local Core guards. The product
retains control of selection and full fallback, merge authorization,
incident recovery and workspace acknowledgments.
[Core extension contract](../../../000/2/design/core-design.md#extension-api)

Standalone validation works with the adapter absent or disabled.
Required integrated evidence is unavailable when the configured
adapter is absent, stale or incompatible. A configuration edit cannot
turn an unavailable result into a pass, clear a stop, or discard
pending authority and receipts.

[Proposed follow-on plan](../plan/independent-deployment-enhancement.md)
