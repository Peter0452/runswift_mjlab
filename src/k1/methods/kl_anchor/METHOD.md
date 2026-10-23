# kl_anchor

**What.** Adds β·KL(policy ‖ frozen reference) to the PPO loss, with β decaying, so a fine-tune can't random-walk away from a good checkpoint.

**Source.** `AnchoredAmpPPO`, `k1/tasks/velocity/rl/anchor.py` (`with_anchor`).

**Where it plugs in.** Algorithm config `anchor_checkpoint`, `anchor_coef`, `anchor_coef_final`, `anchor_decay_updates`, `anchor_loss`.

**Deployment impact.** Training-only.

**Status.** experimental: self-play fine-tunes.

**Evidence.** Self-play fine-tunes drifted 22–36 % in actor weights and got worse against h022; fixed LR 1e-4 plus the KL anchor (β 0.5 → 0.1) fixed it (skills/selfplay_striker.md, E18).

**Pitfalls.** Anchor to the best checkpoint after a reward fix, not to the old baseline (anchoring to h022 dragged a better approach back).

Registry entry: `k1/methods/registry.py` (extension points, parameter fields, `detect`).
Promotion rule and statuses: `knowledge/architecture.md`.
