Both sample windows use the identical sample.py script and the installed #83 release's Python runtime. ROOT is the existing registered #83 project state directory and ACTIVATION is its accepted activation receipt. The private local state remains read-only.

```sh
"$PY" sample.py "$ROOT" "$ACTIVATION" sample.json 2026-11-10T00:00:00+00:00 2026-11-13T00:00:00+00:00
"$PY" sample.py "$ROOT" "$ACTIVATION" control-sample.json 2026-11-09T23:06:05.589056+00:00 2026-11-09T23:16:20+00:00
cmp "$TRIAL/feasibility.json" "$TRIAL/verified-replay.json"
python3 replay.py "$TRIAL" "$SCRATCH"
```

The two trial receipts are byte-identical. SHA-256 03707eb5926d2bde487ee2dbee141fda03a4578fb031c6659cb01f320421d558. Probe.py captures telemetry.json from loopback POST bodies and wire.jsonl independently from the native CLI stdout. Neither is derived from the other. The replay verifies both hashes and the parent and child source hashes. The replay store is private, uses an ephemeral keyed request reference and is deleted after a separate process verifies its persisted state. The offline test supplies no evidence of provider-side retry behavior.
