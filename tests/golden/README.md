# Golden references

Recorded 2026-10-23 on branch `restructure`, before any code moves, with the
default ball (`K1_BALL` unset = ours). Recording first caught a regression: the
self-play stash merge had switched the kick ball to B-Human's; the default was
restored and the references re-recorded. Re-record only when a change is *meant* to alter behaviour,
and say so in the commit.

| Check | Command | What must hold | Time |
|---|---|---|---|
| Task set and configs | `.venv/bin/python -m pytest tests/test_task_registry.py -m "not slow"` | exactly the 34 expected tasks; every train/play/RL config loads | ~1 s |
| Every env builds | `.venv/bin/python -m pytest tests/test_task_registry.py -m slow` | each task builds with 2 envs and steps once with finite rewards and observations | ~3.5 min |
| Model snapshots | `.venv/bin/python scripts/tools/golden.py check` (or `pytest tests/test_golden_policies.py -m slow`) | for 6 key models: same observation layout, same actions on the stored observations (≤ 1e-5), same actor observations after a seeded reset (≤ 1e-4) | ~3 min |
| Champion benchmark | `.venv/bin/python scripts/tools/golden_bench.py check` | benchmark v2 quick on the kick champion: at most 3 metric CIs separate from the reference (equivalent code: 0–2; the ball regression: 29); style statistics reported, not gated | ~10 min, GPU alone |

Files:

- `policies/<name>.pt`: layout, reset observations (16 envs, seed 7) and
  actions for each model in `scripts/tools/golden.py` `MODELS` (gold walk,
  kick champion h022, kick teacher h011, self-play SWA, striker controller v2,
  dribble v51_11750).
- `bench/kick_champion_h022_quick.json`: benchmark v2 quick, seed 1, for the
  champion checkpoint.

The model checks need the checkpoints under `logs/` (not in git); on a
machine without them the tests skip.

Re-record: `scripts/tools/golden.py record [NAME ...]`,
`scripts/tools/golden_bench.py record`.
