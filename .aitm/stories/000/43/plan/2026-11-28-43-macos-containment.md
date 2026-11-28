# #43 macOS contained verification

[C36 scope](../story.md) · [Verified EP12 Dev admission](../../../004/481/plan/2026-11-28-manual-admission.md) · [C35 delivery](../../42/retro/2026-11-28-42-delivery.md).

The parent read Dev at planning publication `8a8619c78c0059fd6681d33956f7619ee97b8b5b`. Rank 20 follows #42, which is Closed/Completed and Done with native Linked PR #601. Base `cf814522221adf8f7782778feccb11e9cca155f9` has the exact reviewed C35 tree `76691f100bcfeb3b19a47032b6d54cc2bf4a0331`.

1. Build a macOS-only adapter for C35's fixed lane selector. Use a bounded probe that requires actual allowed output and denied operations in a descendant. Missing, failing or unsupported `sandbox-exec` gives unavailable assurance.
2. Require canonical, disjoint read and write roots. Allow the sealed export and prepared runtime as read-only inputs. Allow writes in the isolated scratch root. Deny networking and test inheritance with an actual managed descendant. Keep captured-export as its separate committed choice.
3. Use deterministic tests for profile path rules and capability outcomes. Use one integration node for actual macOS and the installed init, doctor and test routes. Collect that node under the established Core integration path and record its actual macOS run separately from hosted Linux collection and gates.

This manual Planning pickup records applicability to the accepted parent plan. Runtime transition and implementation clock are both false.

Project 24 read Dev for both #481 and #43 at `2026-11-28T19:58:28.121551+00:00`, after the separate child Planning checkpoint. This is manual admission. Runtime transition and implementation clock are both false.
