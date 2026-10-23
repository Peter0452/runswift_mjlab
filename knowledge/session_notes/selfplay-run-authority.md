---
name: selfplay-run-authority
description: User authorises stopping/relaunching self-play training runs on my own judgement of progress
metadata:
  type: feedback
---
The user (2026-10-13) said: "you should be able to stop and run different trainings according to the progress" — stop plateaued/declining runs and launch the next experiment without asking, but don't waste GPU.

**Why:** a plateaued v14 kept the GPU for hours while I waited on permission; the auto-mode classifier blocks kills that lack an explicit instruction.
**How to apply:** when a run plateaus on the fixed benchmark, stop it by PID and launch the next variant; cite this instruction. Reward-design reversals the user asked for (e.g. undoing the α anneal) still need their OK. See [[k1-striker-selfplay]], [[kill-pattern-self-match]].
