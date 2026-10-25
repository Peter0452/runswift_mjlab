---
description: Literature review from measured gaps; feeds the engine's approach designer
argument-hint: TOPIC [--task kick]
---

## Context

- Measured gaps and what the engine would try: !`.venv/bin/python -m k1.cli review gaps`
- Review format: knowledge/reviews/README.md; approach cards: knowledge/approaches/README.md; sources: knowledge/sources/README.md

## Your task

Run a literature review for: $ARGUMENTS

1. Start it: `.venv/bin/python -m k1.cli review new "<topic>" --task <family> --trigger "<why now>"`. This writes `knowledge/reviews/<date>_<topic>.md` with the gaps and what the knowledge base already holds.
2. **Search related tasks first**, then methods for the gap tags:
   - humanoid soccer, kicking, dribbling, falls with the ball behind, multi-skill
   - the local clones next to `runswift_mjlab/` (APEX, humanoid-soccer, RoboNaldo, GMR, DribbleMaster, htwk-gym, MachineLearning/IsaacGymRL, contact-uan)
   - the web

   Record your queries in the review's "Search" section.
3. For each relevant source:
   - add or update `knowledge/sources/<id>.md` (their task, robot, their approach as elements, `extraction`)
   - add or update approach cards in `knowledge/approaches/<element>/`
   - give a card a `trial` only when a recipe can apply it: parameters of a registered approach (`k1/approaches/registry.py`) or genes the task reads. Otherwise `trial: null`: it needs building, and the review says what.
4. Judge fit for every candidate: relevance to a measured gap, whether its assumptions hold for the K1 and the deploy contract, evidence transfer from their robot, cost and risk, our track record (`knowledge/uses/uses.yaml`). A rejected approach needs a new reason.
5. Write the ranked shortlist in the body and in the front matter `shortlist:` as `{approach: <card id>, gap: "<metric in situation>", hypothesis: "<what moves, how much>"}`.
6. Run `.venv/bin/python -m k1.cli knowledge check` until it is clean.
7. Stop and show the user the shortlist. Only after they agree: `.venv/bin/python -m k1.cli review approve <name> --agreed`. Never change an approach's status from a paper's claims; only our results (use records) do that.
