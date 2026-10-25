# Step 8 log: a designer that reads gaps and the knowledge base; reviews from gaps

2026-10-25. The user asked for designers that read the measured gaps and pick
approaches from the knowledge base, fed by the review command (option A). Then
for the designer to look at its options in the knowledge, then combine and
tune them ("amp with reward shaping, etc."). The designer is deterministic
code, not an LLM: the LLM part is the review step, which writes the knowledge
and the shortlist the designer reads.

## Built

| What | Checked by |
|---|---|
| `k1/engine/gaps.py`: the champion's gaps from its full benchmark v2. Covers kick-league metrics behind B-Human and fall metrics above the 0-falls target, sized in fitness tolerances and weighted by requirement priority. Tags come from `knowledge/approaches/symptoms.yaml` (metric → tags + requirement; situation words → tags; primary gaps add half-weight `exploration`, `multi-objective`). | run on h022: 25 gaps; top are falls with the ball behind 24.6 % and goal-grid world falls 14 %, then long kick 4.0 vs B-Human 4.31 m/s |
| Approach cards gain `trial` (how a recipe switches the approach on) and `tune` (parameter ranges, tags, step direction). Trials exist for caps, DecAP, multi-critic and the three scenario approaches. Tunes exist for the AMP style weight, CAPS temporal, scenario probabilities and a new card `task_reward_shaping` (8 reward weights by tag). | `rsw knowledge check` validates fields, paths, ranges and tags |
| `k1/engine/designers/approach.py` (`ApproachDesigner`): **add** and **tune** moves per gap. Ranking: tag match × status, plus the track record from uses, × gap weight. Each earlier try of the same approach halves its score, so tries spread out. Approved review shortlists come first. Rejected and parked approaches are skipped; the ones it can't apply go to `blocked`. One change per child by default; `combine=N` bundles moves on different approaches. | `tests/test_k1_approach_designer.py` (9 tests) |
| The engine (`rsw engine`) now runs the approach designer plus one-gene steps (the hard-coded MethodDesigner list is gone from the CLI). Escalation packets list the blocked approaches and point to `rsw review new`. | `tests/test_k1_engine.py` |
| `k1/approaches/review.py` + `rsw review gaps` (gaps, what the designer would try, what it can't apply), `rsw review new TOPIC --task kick` (skeleton prefilled with gaps and matching knowledge, front matter with `approved: false` and `shortlist`), `rsw review approve NAME --agreed`; `/review` command (`.claude/commands/review.md`) for the research step | tests (skeleton, approval, shortlist ranks first) |

## What the designer would try now (kick, from h022)

1. add `ball_behind_starts`: `s.far_spawn_prob` 0.2 → 0.3 (falls with the ball behind)
2. tune `task_reward_shaping`: `w.hop_kick_fall` −1000 → −1250
3. add `decap` (kick clips)
4. add `world_model_ball`: `s.world_ball_prob` → 0.2
5. tune `ball_behind_starts`: `s.spawn_any_prob` 0.3 → 0.375
6. tune `task_reward_shaping`: `w.long_kick_power` 4000 → 5000 (long kick vs B-Human)
7. add `multi_critic` (0.5, 0.5)

Blocked for the engine, waiting on a person or a review:
- continuous kick range
- fall constraint
- kick teacher
- motion-guided curriculum
- N-P3O
- privileged teacher + DAgger
- retargeted human kicks
- reward grammar

## Best guesses (review these)

1. **Combination by stacking, one change per child.** This keeps the standing
   decision of 2026-10-21. `combine` > 1 exists but is off: switching it on
   would change that decision, so it's yours to make.
2. **Trial and tune values come from earlier settings, not new ones:**
   - catalogue frames (scenario probabilities)
   - Step 5 loop defaults (caps temporal 1.5, DecAP kick source, gene ranges)
   - the task default (multi-critic 0.5 / 0.5)
   - uses (CAPS 2.0 was sluggish, so CAPS is tuned up to 1.5 only; the AMP
     style weight is tuned between 0.1 and 0.4, since 0.5 saturates)

   The reward-shaping ranges are Step 5's `EVOLVE_GENES` widened to cover the
   champion's values, plus `touchdown_speed` and `hop_kick_fall` around the
   champion's.
3. **Tune directions** (`step`): more of a scenario helps its tags; a stronger
   reward weight or penalty (in magnitude) helps its tag; AMP style is "both".
4. **Gaps are kick-only** (the only wrapped judge), measured on the champion's
   seed-1 full benchmark against B-Human and the 0-falls target. Requirements
   without a B-Human or zero reference (posture, styles) aren't gaps yet.
5. **The decap match is weak:** it matches the behind-falls gap only through
   the `exploration` tag that the "behind" situation adds. It is a hypothesis
   for the benchmark to test, not a claim.

## Not built yet

- Verdicts per requirement and an automatic use record after each verdict
  (the designer's track record then updates itself).
- Recipe support for `kl_anchor` (it needs `with_anchor` wrapping), so it can
  get a `trial`.
- Gaps for dribble, self-play and striker (their judges aren't wrapped).
- The engine starting a review by itself on escalation (option B).
