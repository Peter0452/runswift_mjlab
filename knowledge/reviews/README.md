# Literature reviews

A review answers one question for one task request or symptom: which
approaches from the literature (and from our own uses) are worth trying, and
why. Literature only decides what is worth trying; the benchmark decides what
stays.

`<date>_<topic>.md`, with these sections:

1. **Trigger:** new task request, stalled loop, a measured symptom, or a periodic scan.
2. **Question:** the symptom or requirement, with the measured numbers.
3. **Search:** where and for what: related *tasks* first (humanoid soccer,
   kicking, dribbling, multi-skill), then methods.
4. **Sources found:** each becomes or updates a record in `knowledge/sources/`,
   with its approach written as elements.
5. **Approaches extracted:** new or updated cards in `knowledge/approaches/`.
6. **Fit for our task:** for each candidate:
   - relevance (a measured symptom)
   - fit (its assumptions hold here: level, data, real-time, deploy contract)
   - evidence transfer (their robot and setting vs the K1)
   - cost and risk (effort, compute, runtime impact)
   - our track record (uses; a rejected approach needs a new reason)
7. **Shortlist:** ranked, each with a falsifiable hypothesis and the metric it
   should move; one change per trial.
8. **Outcome:** filled in later: links to the use records the trials produced.

| Review | Date | Question |
|---|---|---|
| [kick approach loop](2026-10-06_kick_approach_loop.md) | 2026-10-06 | Which external methods can close the kick gaps vs B-Human? |
| [ENPIRE and harbor for the loop](2026-10-25_enpire_harbor_loop.md) | 2026-10-25 | What should our engine and interfaces learn from ENPIRE and harbor? |
