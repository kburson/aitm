# Author response to SPR round 2

The revised spec SHA-256 is `d0d7a67acc4724185a82d66692182bb42b0065cc0230535f9286d7a7e7947c43`.

1. **Late competing handoffs.** Verify the scope generation immediately before the target boundary. Hold a late conflict after ACK and preserve old snapshots. The proof now exercises both arrival orders and reconciliation.
2. **Restore fence.** A private monotonic recovery fence must be durable before report publication or export send. Restore requires the independently retained current tail. An interruption ahead of proven common evidence becomes a replay hold. An uncertain receiver delivery must be reconciled.
3. **Grok late folded usage and forks.** Add release cases for late parent coverage after child publication, and inherited versus genuinely new turns on a forked session.
4. **Accepted immutable export correction.** Pin the original receipt and payload. Hold the changed revision from compatible export with a reconciliation record. The current local report uses the corrected revision once, and historical snapshots remain fixed.
