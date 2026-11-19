# #370 import-chain list

**#402 is replaced before work started. #403 is next. #370 stays open.**

#393 and #398 showed that a reviewed boundary of `test_grok.py` can run 33 tests in about 4 seconds while the full lane runs 1,776. That saving belongs to one hash-pinned decoder body on one base. It does not list the tests for an arbitrary change. Another declaration of that suite would repeat the same measurement.

#383 already walks imports for the staged index, HEAD, and a pull request against the parent-branch divergence commit. #385 showed that walk returning full on real product trees. An unresolved record with no `possible_inputs` is applied to every changed path. The product tree carries `dynamic-import`, `unresolved-import`, and `relative-import-context` records. The fixture narrowed because it had none of those records.

#403 changes that applicability rule and proves the walk on one real product change. A record applies only when it can hide a reverse edge to the changed path, or when the walk already goes through the uncertain file. A non-literal dynamic import still forces full. A shared `conftest.py` in the walk still forces full. A missing snapshot or inventory stays unavailable.

The required workflow, path map, evaluator, verifier, branch rules, and the pinned #355 command stay unchanged. The #403 receipt is the evidence for a later close of #370. Promotion of the list into the required gate remains a separate decision.

[#403](../../403/story.md) · [#385 findings](2026-11-19-370-hosted-shadow-findings.md) · [Superseded integration decision](2026-11-19-370-suite-hosted-integration-decision.md)
