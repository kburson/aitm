# Grok second opinion on the Desktop qualification plan

Grok Build 1.0.92 with Grok 4.7 Build Fast reviewed the proposed Desktop qualification as a separate, read-only model turn. Its disposition was **revise before approval**.

## Findings and recommendation

1. A project hook can start for other chats that load the same project configuration. The current entry point constructs the private store before checking the thread. Other threads cannot enroll or read a rollout after the filter, but they can still start the process and open the store. A linked checkout also has project-layer inheritance to account for.
2. Qualify in a disposable Desktop chat backed by a separate scratch repository outside the normal project's worktrees. Bind the helper to that disposable thread. Capture the actual owner and child callback IDs before interpreting them. The scratch run must use the accepted capture and publication interfaces and the installed Desktop build.
3. Review exactly what will execute. Pin the helper and installed wheel hashes and tie verification to the reviewed configuration. File ownership and mode alone do not establish that the executed bytes are the ones reviewed. Grok flagged that the installed app's trust behavior for script replacement under an unchanged command remains unverified.
4. Record completion separately from callback exit. A pending callback must leave a durable exact reference that can be settled after native retention, without another hook delivery. Observe callback latency and show publication is a separate explicit operation.
5. Keep the selected story stable for the first live dispatch proof. After both receipts settle, switch story and restart the reader, then verify that the original receipts replay byte-identically. Use a separate controlled check if a live in-flight story switch is needed for acceptance. Remove the scratch configuration and verify the helper stops launching.

Grok proposed repeating the experiment once in the long-lived chat after the scratch proof. The coordinator recommends qualifying first with a real owner and supervised subagent in the isolated Desktop chat, then checking whether the accepted route actually requires a second live trial in the normal checkout. This avoids expanding project hook trust before there is evidence it is needed. The original approval request is on hold pending the owner's decision. #457 remains in Test and PR #460 remains draft.

The exact Grok usage replay verified 8,832 cached input tokens, 10,571 new input tokens, 5,350 output tokens, and $0.03920744 provider-reported. The wrapper elapsed 76.049 seconds. The native start boundary is unavailable, so the wrapper duration is listed separately from agent engagement. [Codex hook discovery and trust](https://learn.chatgpt.com/docs/hooks#review-and-trust-hooks)
