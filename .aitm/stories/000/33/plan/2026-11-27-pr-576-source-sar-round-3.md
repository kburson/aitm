# Second exact sar for #576

The coordinator retained the supported historic formats, addressed the clock and finalization findings, and requalified the revision. Packet SHA-256 `caaba723e926b7d8094e92b76c2d902126b61ba88a64d5ef41c98b41003306d7`.

CHANGES REQUIRED
c49b535d522f7fca1b8e5c6038b1783993e1c012 ebef35e0cf6d0cba02d92827e1f80ccd27aebe1f 481e018d7472d386f1045d2cfa87aad45711a415 eeb42add68dc5d2dc4de3f2de0f2cb2bc84c9d70

Accepted manifests still require status `accepted`, one public JSON block, ordered consensus, raw response digests, and incoming blob/digest lineage. Numbered claims may precede the other role’s submit, ambiguous matches stay `unknown`, and a later round does not reuse an unnumbered round-1 claim. Those parts match the prior failures. Four gaps remain.

Legacy prior-submit aliases still qualify when `start_source_digest` is omitted. `_bind_turn` treats `stated_hash in (None, anchor.source.digest)` as a match, so only a conflicting hash fails. The same omission is allowed for claim anchors (`stated_hash in (None, anchor.source.digest)` against the manifest digest). A retained alias or `#claim-<id>` fragment can therefore pass with no digest on the timing record.

`native_finalization_commit` is not native evidence. `map_native` always leaves `finalization_commit` unset. `_bind_bundle` copies the portable header, and `finalization == facts.revision_commit` does not fail when the header omits it. A present value is not checked against the manifest, history, or a blob digest. Revision tip and finalization stay unproven as distinct public commits.

`derive_anchor` returns `unknown` with no source when the predecessor timestamp is after the response, before exact-turn claims are considered. A valid numbered claim is dropped, and the proxy bound is not kept. Separately, `turn is None` still becomes a round-1 `claim` start. That is a registration-style timestamp, not an exact-turn claim. `start_basis is None` also skips anchor comparison after provenance checks, so portable responses can omit the basis the facts still report.

Local `test_c58` coverage and the hosted core/repository pass do not exercise omitted digests, omitted finalization, the predecessor short-circuit, or unnumbered round-1 claims. Custody of referenced response bytes and the C24 replay path is otherwise intact. This stop is before live capsules and timing aggregation.

REVIEW COMPLETE
