# #115 Grok pricing retrospective

I implemented the versioned Grok rate card and exact Decimal pricing for `grok-4.7` below the 200,000-token full-input threshold. The estimate stays Unknown for Build, missing quantities or rates, and positive cache creation. Provider ticks stay separate. I verified the public xAI source digest and froze the legacy Codex and Claude export bytes and rate basis.

My red run recorded three expected failures and two passing legacy controls. The focused green run passed 205 tests. The locked package run passed 597 tests with the native adapter tests still in progress and excluded. I verified delivery at merge `37a22922f072e39c35434ae645a1c20692b8da01`.

The legacy file check caught a packaging boundary I missed. Integration moved the same rate resource bytes into `rates/monitor/2026-11-10.json`. I learned to check the repository’s resource inventory rules alongside wheel contents when introducing a versioned namespace.

Active implementation time and spend are Unknown.

Signed by **Codex `/root/grok_pricing`**, delegated #115 pricing implementer.
