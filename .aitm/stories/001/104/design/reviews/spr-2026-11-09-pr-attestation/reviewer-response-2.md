# #104 ordinary-PR tested-merge attestation replan · independent manual SPR, round 2

Submitted UTC `2026-11-10T04:25:05Z`.

**Verdict: accepted. No required findings remain.**

## Identity and exact coverage

- Declared independent same-provider manual SPR, continuing the distinct Codex reviewer session. Recorded context is Codex Desktop, `openai`, `gpt-6.1-sol`, high effort. I rederived fingerprint `sha256:a3bb437a4264b6ad468ee66ea2fa72d26913b9712e2db7f6ecbf105ed0bbd287` from the exact UTF-8 prefix `ai-peer-review.session/v1\nopenai\n` followed by this session's handle without an added newline. This is manual review evidence.
- Artifact `.aitm/stories/001/104/design/github-tested-merge-binding-replan.md`, exact source `eb8ab8f471f33cdc52c1e67e01283ab8bc50cdd2`, raw SHA-256 `c5771f307d55aafe79d8dcb6fed4940f5d1dbdda2ee9e2eb616f208215abedf0`. The file and named source match. I reread contiguous lines 1–20, 21–40 and 41–42 to EOF without omissions. I compared round-one findings and the accepted ordinary-PR design and plan context.

## Finding dispositions

1. **SPR-ATT01 resolved.** Lines 11 and 33 distinguish the attempt archive, GitHub repository attestation and permanent public transparency publication. Separate future authority is required for the diagnostic and recurring PR signing, covering the exact narrow permissions, sanitized subject digest and public metadata. Eligibility requires a current visibility and entitlement preflight. Missing authority or a changed provider route holds the work. Disabling registry and linked-artifact storage does not remove attestation or transparency publication.
2. **SPR-ATT02 resolved.** Lines 32 and 37 use the same two-job collector and isolated signer for both the diagnostic and production path. The signer accepts only the pinned upload's positive ID and digest, checks exact authenticated same-run metadata with scoped `actions: read`, then downloads the raw current-run archive without an injected downloader token and refuses digest errors, unsafe members, wrong identity or prior attempts before signing. Candidate JSON cannot select executable inputs. The full signer permissions are listed and all other job permissions stay disabled. The diagnostic requires independent final archive, signed claims and wrong-SHA or wrong-attempt refusal before the production work can start.

## Exact attempt and scope assessment

Lines 23 and 26 combine the selected attempt-specific endpoint with required job ID uniqueness, native run and attempt fields, and job start timestamps bounded by the authenticated attempt start. Read-only checks confirmed that the official action's PR example exposes those fields. In an independent public Actions runner example, the attempt-2 endpoint labeled all ten job records with `run_attempt=2` but included jobs started before that attempt's recorded start. The time boundary closes a concrete hole in relying on the endpoint and labels alone. The live #104 probe and negative fixtures remain necessary. [Official PR example](https://github.com/actions/attest/actions/runs/42272300446/attempts/1) · [Public attempt with carried-over jobs](https://github.com/actions/runner/actions/runs/40339492476/attempts/2) · [GitHub rerun semantics](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs)

Lines 7–11, 23–27 and 37–42 preserve the normal story branch and ordinary PR into its declared target. They exclude alternate candidate branches and distinguish signed certificate identity, the signed subject digest, and reported evidence. Exact current merge and ordered parents remain mandatory. A stale attempt needs a fresh ordinary PR event. A qualified diagnostic still requires fresh JIT and explicit future authority. The unrounded 90% product and helper floors, meaningful behavioral tests, serial Darwin and independent closure remain. The 0.35 prior debit, 3.45 remaining active forecast and 0.20 maximum reserve total 4.00 hours. No live probe, repository mutation, implementation, Epic #2 or C01 work was performed.
