---
id: muon
title: Muon optimizer for actor and critic
element: optimisation
also: []
tags:
- stability
status: adopted
impact: training-only
sources:
- jordan2024_muon
registry: muon
trial: null
tune: null
---

# Muon optimizer for actor and critic

**What.** Muon updates for the actor and critic weight matrices, Adam for the rest and for the discriminator, sharing one learning rate (`match_rms_adamw`).

**Source.** Muon optimizer; `AmpRslRlMuonPpoAlgorithmCfg`, `rl/muon.py`. Task names carry `-Muon-`.

**Where it plugs in.** `algorithm.use_muon`, `muon_momentum`, `muon_weight_decay`, `muon_ns_steps`.

**Deployment impact.** Training-only.

**Status.** adopted: all AMP K1 tasks and deployed models.

**Evidence.** E18: fine-tunes need small steps; Muon at the adaptive LR (~1e-3, desired_kl 0.01) random-walks a fine-tune; fixed LR 1e-4 worked.

**Pitfalls.** With an adaptive schedule the KL has a ~0.003 floor (desired_kl 0.002 pins the LR at 1e-5). Under a fixed schedule `Loss/kl_divergence` logs 0. Warm-starting Adam → Muon needs `warm_start` (fresh optimizer state).

Registry entry: `k1/approaches/registry.py` (extension points, parameter fields, `detect`).
Uses: `knowledge/uses/uses.yaml`. Promotion rule and statuses: `knowledge/architecture.md`.
