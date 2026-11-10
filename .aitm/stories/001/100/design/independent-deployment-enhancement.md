# Cross-agent usage monitor independent deployment enhancement

Proposed follow-on after the base monitor is delivered and its supported
host, provider, and upgrade paths are proven. The
[accepted base design](multi-project-usage-monitor-design.md) governs
the monitor currently in delivery.

Expose the cross-agent usage monitor as an independently versioned
distribution and service. An operator can install, configure, run,
upgrade, and remove it without installing AITM-Core or the TIA build
optimizer. It owns its service state, provider enrollment, access to
local sources, retention, and report/export receipts. Preserve the
existing `aitm-usage` command, ledger identity, and compatible export
until a separately reviewed migration addresses any change.

AITM-Core can optionally load a separately installed adapter through
its `aitm.extensions` registry and enable it from committed
`[extensions].enabled` policy. Use the product's versioned sanitized
export and the existing compatible receiver boundary. The adapter
validates product, schema and receipt identity. It can project verified
usage, coverage and Unknown without accessing provider transcripts or
taking ownership of the monitor's local service. The existing [C44
consumer](../../../000/51/story.md) retains its own scope and review.
[Core extension contract](../../../000/2/design/core-design.md#extension-api)

Absent or disabled integration leaves the standalone service usable.
An enabled incompatible adapter reports unavailable. A missing result
never means zero usage or confirmed engagement. Opt-in does not enroll
providers, start a service, grant access to transcript roots, or
authorize release and cutover.

[Proposed follow-on plan](../plan/independent-deployment-enhancement.md)
