# Kick benchmark (runswift spec v2) results

Produced by `scripts/tools/rs_kick_bench.py` (our kick loop) with the trials,
kick rule and score of `k1/eval/rs_kick.py`, shared with
`scripts/tools/bench_bhuman_kick_v2.py` (B-Human's kick, results in
`docs/benchmarks_bhuman_kick/`).

| Run | Policy | Setup | Score |
|---|---|---|---|
| `kick_rs_v2_seed0` | h022 (champion) | spec defaults: Booster Gym kick rule, B-Human ball contact + damping, camera, typical delay, caps 2.0 / 1.5 / 1.5 | 0.836 |
| `pow_b_check` | pow_b 19249 | spec defaults | 0.848 |
| `pow_b_rule_ours` | pow_b 19249 | kick loop's kick event | 0.845 |
| `pow_b_ball_ours` | pow_b 19249 | training ball contact | 0.848 |
| `pow_b_both_ours` | pow_b 19249 | kick event + training ball | 0.879 |

The 2026-10-14 report (pow_b 0.898, iter 12 0.902) came from another copy of
this benchmark that is not in this repo; none of the setups above reproduces it
exactly (closest: kick event + training ball, 0.879, same medians, longer
rolls). Its exact ball, caps, perception and kick detection are needed to match.
