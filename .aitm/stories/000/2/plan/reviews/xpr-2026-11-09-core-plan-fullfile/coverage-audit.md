# Full-file retrieval verification

This separately authorized validation required fresh retrieval of the complete current FUR every round. Before each revision/finalization, the author compared actual numbered Read result text against every physical line of that round's exact Git blob. Requests alone were not counted.

| Round | Input commit | Physical lines verified | Read results | Audit |
| --- | --- | --- | --- | --- |
| 1 | ab631c02f2eef28517f8a864e54679fdd548f467 | 1487/1487 | 50 | [complete](read-audit-round-1.json) |
| 2 | b80d0fb9bd63cecbc9665a295c98119a24ec2440 | 1559/1559 | 52 | [complete](read-audit-round-2.json) |
| 3 | 967393ff2724084e19595dcc225a730a9f5cf998 | 1579/1579 | 53 | [complete](read-audit-round-3.json) |

No returned authored line was missing or truncated; all matched the source. Long physical paragraphs were wrapped before sealing the initial candidate so native Read's per-line limit could not hide their endings. Terminal newline split accounting is separate from authored physical lines. Sanitized JSON retains ranges/timestamps, exact input digests, observed model and private transcript-prefix hashes, not raw provider handles/transcript. The reviewer could not run its own shell hash; the author checked each raw digest and actual returned content.

The immutable [pre-start instructions](review-instructions.md) have raw SHA-256 `1bdf34c038fa1395a6660554c0401337af65a54990e0fbb7759caecce062b121`. Observed response model was `claude-opus-5-5` in every round; native launch/resume retained requested `high`. Author observed turn context was `gpt-6-astra/xhigh`. These are declared/runtime provenance, not independent per-token effort attestation. Full retrieval is not proof of attention or absence of defects.

The [historical procedure audit](../../review-procedure-audit.md) remains true about the earlier accepted reviews. This new independent record fulfills the owner's later validation instruction; it neither adds a sixth historical round nor backdates retrieval. The design had its own separately published full-file validation before this plan review.
