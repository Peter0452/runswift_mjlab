# ENPIRE and harbor for the loop (2026-10-25)

- **Trigger:** designing the task-request / task-implementation structure and
  the engine (Step 6).
- **Question:** what should our engine and interfaces take from ENPIRE
  (agentic real-world policy improvement) and harbor (agentic task and reward
  authoring), and what not?
- **Sources:** `enpire2026` (paper arXiv 2606.19980 and the clone `../ENPIRE`),
  `harbor_rl` (`../harbor-rl` and the harbor plugin).

## What they are

- **ENPIRE.** Two stages:
  - **Stage one (human-guided):** builds reset, verification and safety. These
    then freeze as an API agents can't change.
  - **Stage two (autonomous):** one coding agent per robot station forms
    hypotheses, edits training code, runs real trials and keeps changes that
    raise the success rate.
  - **Across stations:** git branches, with merges and cherry-picks by average
    success rate.
  - **Code-as-policy path:** skill author (refine / replace / new),
    cross-seed reflection with a failure histogram, escalation after 3 discards.
  - **Learned path (PLD):** SAC, plus BC and contrastive BC modes switched on
    by hand. BC regularisation was their largest single gain (+10.8 pp).
  - **Who chooses BC vs RL vs heuristics:** the agents, from a menu in the
    prompt. No code selects a paradigm.
- **harbor.**
  - **A task is a sectioned spec:** scene, actions, reset, goal and
    termination, observations, reward, DR. Each section has its own smoke test.
  - **Probe:** extracts a portable spec from an existing task.
  - **Reward tuning:** a designer agent and a candidate agent that only
    implements. Candidates run in a fixed-size pool, each in an isolated clone.
    The winner is promoted and its checks re-run. Reward edits follow
    adapt-first with a magnitude budget.
  - **Supporting rules:** per-term reward logging, smoke loops bounded by
    progress, experience ledgers.

## Taken (into the Step 6 structure)

| From | Lesson | Where |
|---|---|---|
| ENPIRE | the verifier and safety are frozen; agents can't move the goalposts | task request: `verification` frozen by hash (`rsw request freeze`) |
| ENPIRE | one falsifiable hypothesis per change; failures kept | recipe `hypothesis` field, engine history, use records |
| ENPIRE | diagnose from evidence before proposing; tiered escalation | engine designers (planned) |
| ENPIRE | reflection carried to new tasks | reviews, uses |
| harbor | sectioned implementation with per-section smoke tests | task implementation (planned: smoke per section) |
| harbor | designer separate from implementer; isolated candidates; re-check on promote | engine |
| harbor | probe an existing task into a spec | first task requests written from existing tasks |
| both | open method menu → our structured approach knowledge with evidence | `knowledge/approaches/` by element |

## Not taken

- **ENPIRE's code-as-policy machinery:** our policies are networks, not
  programs.
- **Training on the robot (PLD):** the K1 validates, it doesn't train.
- **Free git merges judged by average success rate:** too noisy for sim-to-real.
  Seed-2 confirmation and the deploy gate stay.
- **Calling harbor from the outer loop:** standing rule; its ideas are
  re-implemented in our own code.

## Evidence for approaches

ENPIRE's BC-regularisation result supports `kl_anchor` and `kick_teacher`
(regularising toward a known-good policy). A candidate worth a card later is
outcome-filtered teacher imitation: imitate the teacher only on near-ball steps
that led to a good kick, as a cheap form of their contrastive BC.

## Outcome

Structure built in Step 6 (`restructure/STEP6_LOG.md`).
