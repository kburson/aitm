# #282 Claude Agent telemetry and story coverage

## Bounded sample

Read the existing #83 project ledger without a writer and verify the project identity against the accepted activation receipt, then load the current ledger-authenticated registration. Use the ledger's admitted Claude request references to select at most 12 retained sessions from exact approved AITM checkout folders. Extract only identity, scope, time and counters needed for this analysis. Native JSON rows are parsed transiently. No raw paths, provider IDs, prompt text or story labels from the source are exported.

The post-activation sample from Nov 10 through Nov 12 UTC has zero eligible registered Claude request rows. This could reflect missing admission or ingestion. The result gives no production prevalence or per-story usage denominator. As a positive control, the #83 activation window from Nov 9 23:06:05.589056 through 23:16:20 UTC has two admitted Claude sessions, five retained prompt IDs and five ledger requests matched by native identity. One matched request belongs to one verified issue scope. The completed foreground Agent detector found zero overlap in those five prompts. Interrupted, orphaned and background children fall outside this detector. The control was a planned qualification workload and the ledger conditions the selection on already admitted usage. The zero in this control cannot bound the effect across everyday AITM stories. Project active time and story progress were not derived from request coverage.

## Controlled experiment

One pinned Claude Code 2.1.318 macOS trial captured native local OpenTelemetry with prompt and tool content disabled. Match all five unique provider requests to native counters and their exact parent or child. The foreground Agent prompt accounted for four requests, two from the child. The child was 50% of request count, 50% of input tokens, 39.5% of output tokens, 10.4% of cache-read tokens, 77.0% of cache-creation tokens and 47.2% of estimated API cost in that synthetic Agent prompt. The parent result included the final child request's counters. The earlier child represented 40.1% of estimated API cost in that same prompt and was outside that aggregate. These figures describe the controlled prompt.

Replay the recorded loopback OTLP POST bodies, hashed independently of the native CLI stream through a disposable durable join. Eight deliveries of four distinct requests yielded four durable records. Dropping one child event left one detectable gap after a separate process reopened the store. Late replay restored exactly five distinct requests, repeated delivery did not alter counters, and a contradictory duplicate was rejected. This verifies the offline reference join. Provider-side live retransmission is unproven.

## Disposition

Keep telemetry as a corroboration option for a later pinned carrier qualification. The join can establish membership and counters in the controlled shape. It supplies neither original project ownership nor a pre-request opportunity to arm the original child file. Defer a separate qualification design until there is a credible eligible carrier or an agreed prospective project-scoped study with an independent denominator. Keep production prevalence, per-story exposure, and correction factor unknown. No dependency, ledger, report or production change follows from the spike. #204 remains separate.
