# symmetry_aug

**What.** Left-right mirrored copies of each batch (observations and actions) in the PPO update.

**Source.** rsl_rl symmetry hook; mirror functions `k1/tasks/velocity/mdp/amp_symmetry.py` (`augment_symmetries_kick_loop`), `dribble/mdp/dribble.py`, `selfplay/mdp/self_play.py`.

**Where it plugs in.** `algorithm.symmetry_cfg` (`use_data_augmentation`, `use_mirror_loss`, `data_augmentation_func`).

**Deployment impact.** Training-only, but the mirror function must know every observation slot: a new slot without a mirror rule silently trains on wrong mirrored data.

**Status.** adopted: walk and kick-loop tasks (`-DA-` in task names).

**Evidence.** Robot L/R asymmetry (left hip pitch p99 ~30 % above right; sim2real S9) is not fixed by shared weights; adopt asymmetric corrections only through the benchmark gate (skills/walk.md, kick.md).

**Pitfalls.** When adding observation slots, extend the mirror function in the same commit; the memory-age slot needed its own test (`test_kick_loop_mirror_keeps_the_memory_age`).

Registry entry: `k1/methods/registry.py` (extension points, parameter fields, `detect`).
Promotion rule and statuses: `knowledge/architecture.md`.
