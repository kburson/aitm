# Grok advisory on the Desktop callback failure

Grok 4.7 Build Fast reviewed a sanitized description of the post-restart failure and the callback control flow in one read-only advisory turn. [Observed failure](457-disposable-desktop-post-restart.md).

1. The missing prompt callback in the trace does not distinguish missing delivery from an early wrapper rejection. The wrapper traces only after checking the exact disposable thread. Capture an event name and the allowlist outcome at wrapper entry in the standalone scratch repo. Keep raw IDs and prompt content out of diagnostics.
2. Compare one prompt typed into the disposable Desktop composer with one app-tool-forwarded prompt. Make both terminal hooks nonblocking before either prompt so the experiment cannot reproduce the retry loop. A composer pass alone qualifies only that route.
3. Retain the minimal exact terminal callback before looking up the enrollment. When the owner enrollment is missing, return a nonblocking pending result. Settle only against an authoritative start-time story binding. If none exists, leave the callback unassigned so switching stories cannot move the charge. The coordinator would apply the same rule to the child through its verified owner lineage.

The next experiment is still pending. This advisory did not change hooks, product code, or delivery gates.

Grok reported 8,832 cached input tokens, 10,206 new input tokens, 3,230 output tokens and $0.03006144. Exact usage replay matched. Wrapper elapsed time was 36.230 s. Native agent engagement was unavailable.
