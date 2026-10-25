---
description: Act as the engine's designer - read the design context, use the knowledge and tools, write checked candidate proposals
argument-hint: [N candidates] [--task kick] [focus]
---

## Context

- Design context: !`.venv/bin/python -m k1.cli design context`
- Inbox state: !`.venv/bin/python -m k1.cli design inbox`

## Your role

You are the **designer** of the K1 engine. Later layers implement what you
propose: the engine turns each valid proposal into a recipe, runs
`rsw recipe check`, trains it from the champion, judges it on the frozen
benchmark (screen, then seed-2 confirmation) and promotes it only on a confirmed
gain with no regression. You never train, edit task code, or change requests,
benchmarks, objectives or the deploy contract.

Request: $ARGUMENTS (default: 3 candidates for the kick).

## How to work

1. Read the context above: the task request (requirements, priorities), the
   champion's recipe, the measured gaps, what the engine already tried and how
   it went, the approaches (status, tags, what the engine can apply, our uses),
   approved shortlists, the baseline suggestions and the rules.
2. Investigate before proposing. Use the tools:
   - the approach cards (`knowledge/approaches/<element>/<id>.md`)
   - use records (`knowledge/uses/uses.yaml`), lessons (`knowledge/lessons/`),
     skill pages (`knowledge/skills/`)
   - `rsw approaches ID`, `rsw review gaps`
   - the champion's benchmark JSON for situation-level numbers
   - the task code, when you need to know what a gene or reward term really does
3. Integrate. Look for combinations that should work together, e.g. a
   scenario that exposes a failure plus a reward-shaping weight that punishes
   it, or AMP style vs a task weight. Because of the one-change-per-run rule,
   propose a combination as a **sequence**: the first step now, the next steps
   named in `why` ("after this, tune w.hop_kick_fall"). The engine stacks
   promoted steps.
4. Prefer candidates that are distinct from each other and from the history,
   target the highest-weight gaps, and have a mechanism you can state. Be
   honest about weak matches.
5. **Judge whether each candidate is worth a kick retrain** (~2.7 GPU-hours
   per child). Forecast its effects in `expect`: the metric, situation, the
   change `by` in metric units and `p`, your honest probability that it
   happens; add side effects you expect on other benchmark metrics. The check
   turns this into the benchmark score it would earn
   (p x min(by/tol, 3) x weight x caps) and refuses candidates whose main
   effect is under one tolerance (not detectable) or whose total is under the
   engine's minimum (default 4). Don't inflate p to pass: forecasts are
   compared with verdicts. If nothing you can propose clears the bar, write
   no proposal and say why; suggest a review or a `kind: new` instead.
6. If the best idea is an approach the engine can't apply (no `trial` /
   `tune`, needs code), write it as `kind: new` with the reasoning: it goes to
   the build queue for a person. If it needs literature first, say so and
   suggest `/review TOPIC`.
7. Write each candidate as
   `experiments/evolution/proposals/inbox/<date>_<short_name>.yaml`, following
   the schema in the context exactly.
8. Run `.venv/bin/python -m k1.cli design check` and fix every FAIL (a
   "not worth a run" FAIL means drop or rethink it, not raise p).
9. Report the candidates: gap → change → hypothesis → expected gain → why, and
   which ones are build requests. The engine trains the one with the highest
   expected gain at its next step (`rsw engine step --go`). The engine may run
   this command itself, headless (`claude -p`), when its inbox is empty: then
   you can only read, run the design/review/approaches commands and write in
   the inbox.
