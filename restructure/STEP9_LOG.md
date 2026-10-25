# Step 9 log: the LLM agent is the designer

2026-10-26. The user: "I want the designer to be the llm agent that receives
the context prompts, and skills, tools to integrate everything and propose
candidates of correct format to be implemented by later layers."

## How it works

```
 /design (LLM agent, Claude Code)
   reads   rsw design context: request, champion recipe, measured gaps,
           engine history, approaches (status, tags, trial/tune, uses),
           approved shortlists, baseline suggestions, rules, proposal schema
   uses    knowledge files, rsw approaches, rsw review gaps, /review,
           the champion's benchmark JSON, the task code
   writes  experiments/evolution/proposals/inbox/<date>_<name>.yaml (schema)
   checks  rsw design check
        │
        ▼
 engine (rsw engine step|run --go)
   InboxDesigner (priority: asked first every step) → design.check again
     valid      → child recipe → rsw recipe check → train → judge → promote
     invalid    → proposals/rejected/<name>.yaml + .why.txt
     kind: new  → proposals/build/ (needs code; for a person)
   inbox empty → ApproachDesigner (deterministic, tag matching) → GeneDesigner
```

## Built

| What | Checked by |
|---|---|
| `k1/engine/design.py`: the context pack, proposal schema, `check` (fields; known, non-rejected/parked, training-only approaches; edits only on the recipe surface: registered approach parameters, genes, reward weights; tune ranges unless `out_of_range_reason`; one approach per proposal unless bundles are allowed; no repeats; the edit must change the recipe), `to_proposal`, the inbox folders | `tests/test_k1_llm_designer.py` (14 tests) |
| `k1/engine/designers/llm.py` (`InboxDesigner`) and engine priority designers (asked first every step, others take turns) | test: the engine starts the inbox proposal before a gene step |
| `rsw design context|check|inbox`; `/design` (`.claude/commands/design.md`): the designer's role, tools, how to integrate combinations (as stacked sequences under the one-change rule), schema, check, report | used to write and check a first proposal |

## State left in place

`experiments/evolution/proposals/inbox/2026-10-25_behind_spawns.yaml`: a first
proposal written as the designer (add `ball_behind_starts`:
`s.far_spawn_prob` 0.2 → 0.3, for the 24.6 % behind falls). It checks clean.
Nothing trains until someone runs `rsw engine step --go`. Delete it if
unwanted (the folder is gitignored state).

## Best guesses (review these)

1. **The LLM writes proposals in a session; the engine doesn't call the LLM.**
   The engine consumes the inbox. Letting the engine run an LLM unattended
   (`claude -p` on escalation or on an empty inbox) is the open Step 5 question
   ("whether an LLM front-end may write recipes unattended"). It's a small
   addition once you say yes.
2. **The checker is the contract.** An LLM proposal gets exactly the same
   gates as the deterministic designers' (recipe check, benchmark, seed-2
   confirmation), plus the schema check.
3. **Combinations are sequences** under the one-change rule (`why` names the
   next steps); bundles stay off until you allow multi-change runs.
4. Only the kick has measured gaps and a wrapped judge, so `task` is kick-only
   for now.
