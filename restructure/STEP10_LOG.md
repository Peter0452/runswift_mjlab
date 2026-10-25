# Step 10 log: the engine calls the LLM designer itself; only runs worth a retrain

2026-10-26. The user: "May the engine call the LLM by itself: yes. Keep one
change per run, but it needs to evaluate if it is worth it, coz we don't want
to waste time and resources to check small trivial gains, so is it enough to
redo a kick?"

## Built

| What | Checked by |
|---|---|
| `k1/engine/worth.py`: a proposal's forecast (`expect`: effects with metric, situation, `by` in metric units, `p`) becomes the benchmark score it would earn with the fitness formula. The score is `p x min(by/tol, 3) x weight x caps`, summed over the effects. Two gates: the main effect must move its metric by >= 1 tolerance (detectable); the total must reach `min_gain` (default 4). Cost per child: `run_hours(500)` ~2.8 GPU-h. | `tests/test_k1_llm_designer.py` (formula, not detectable, not worth) |
| `design.check` applies the gate, and `rsw design check` prints the expected gain and each effect. Schema and rules ask for honest forecasts, side effects included. | tests |
| `InboxDesigner` trains the valid proposal with the **highest expected gain**; the others wait in the inbox. When the inbox has nothing worth a run, it calls the LLM designer itself (`ask`), at most once an hour and 6 times per engine run. | tests (ranking, ask + rate limit) |
| `design.ask_llm` / `rsw design ask`: `claude -p "/design N"` headless. The allowed tools are: read, the design/review/approaches commands, write in the inbox. The binary comes from `$K1_CLAUDE`, PATH, or the newest editor-extension build (`~/.local/bin/claude` points at a removed extension version). An optional `$K1_DESIGN_BUDGET_USD` caps spend. Transcripts go to `experiments/evolution/proposals/llm_logs/`. | real run (below) |
| `rsw engine step/run`: the LLM designer alone by default (`--min-gain`, `--no-llm`); the deterministic designers only with `--fallback`, since they have no forecast and can't be gated. Children and history store `expected_gain` for later calibration. | tests |
| `/design` gains a step "judge whether each candidate is worth a kick retrain". | read |

## Is far_spawn 0.2 -> 0.3 enough to redo a kick? No

The demo proposal in the inbox, forecast honestly:

- main effect: approach/behind/world falls 24.6 % cut by 6 points (2 tol), p 0.4, both caps → +3.2
- side effect: behind falls in the approach cut by 2 points (0.4 tol), p 0.3 → +0.5

That totals **+3.7 < 4**, so the engine won't train it. h022 already raised these
starts and the gap stayed, so a 50 % step is a weak bet. A worthwhile
candidate needs a mechanism that moves the big gaps by several tolerances
(for example, both the behind/world falls and the goal-grid world falls).

## Best guesses (review these)

1. **min_gain 4** is one safety metric better by one tolerance at both caps,
   for sure. Fully closing one safety gap at one cap is worth at most 6. The
   aggregate score's one-seed noise (+30) isn't the yardstick, because it sums
   ~80 metric-caps; detection is per metric (tolerances = seed noise).
   Calibrate it from forecasts vs verdicts.
2. **~2.8 GPU-h per child** uses 7.7 s/it beside another run (log 2026-10-05),
   plus the screen and two full benchmarks (~40 min each, alone).
3. **The LLM's forecasts are self-reported.** The gate is only as honest as p
   and `by`, so `expected_gain` is recorded with each verdict to check them.

## Not built yet

- Calibration report: expected vs measured gain per designer, and a forecast
  correction from it.
- The engine starting `/review` when the LLM designer finds nothing worth a run.
