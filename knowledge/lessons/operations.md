# Lessons: running jobs without losing a night

Sources: `docs/evolution/HANDOFF.md` (gotchas), `docs/K1_KICK_LESSONS.md` §6,
session memory (kill-pattern-self-match, k1-striker-selfplay,
k1-dribble-speed, selfplay-code-in-stash, restructure-preserve-knowledge).

## Processes and GPU

**O1. Kill by PID, in a separate command.** `pgrep -f` / `pkill -f "<run
name>"` matches the shell's own command line when the same command launches or
edits something containing that name; the shell dies (exit 144) and the rest
never runs. Happened at least four times.

**O2. Run evals with `timeout -k 30 N .venv/bin/python ...`, not through
`uv run`.** A `timeout uv run` eval hung for 8 h holding the GPU and cut
training throughput 2.5×. Check `nvidia-smi --query-compute-apps` afterwards.

**O3. At most 2 trainings at a time** (3 ran out of GPU memory); benches
alongside training are fine but slow everything (two parallel benches took
training from 4.3 to 11.4 s per iteration). A forgotten stray run halved
training speed for two hours. Leftover viewers (viser) slow training too.

**O4. Background shell waits in the agent harness time out after ~2–3 h;**
use detached `nohup` watchers for long waits.

**O5. Checkpoints save every 50 iterations;** a run ending at 17649 has no
model_17650.

## Loops and watchers

**O6. Code changes to `fitness_v2.py` / `evolve_*.py` reach the running loop
only after a restart** (use `STOP_AFTER_FRAME`, then relaunch); env / reward /
rl_cfg changes reach the next child automatically.

**O7. Context `best` scores are relative to the champion at the time;**
rescore after a promotion.

**O8. The loop's `log.md` is not reliably append-only;** diff its tail rather
than line-count watching.

**O9. Dribble watchers need the run's `DRIBBLE_GENES`** or eval / export
crash on the discriminator size and the watch silently shows nothing. Confirm
the first eval runs longer than a minute.

## Repository and data

**O10. Don't strand work in a stash.** On 2026-10-16 local self-play work was
stashed before a pull and never re-applied; its runs were unreproducible for a
week. Commit or branch before pulling; check `git stash list`.

**O10b. A merge can carry hidden environment changes.** The self-play stash
also switched the shared kick ball to B-Human's (0.29 kg) in an Oct 16
experiment, so after the merge every kept model ran on a ball it never
trained on (champion goals 1.19 → 0.91, long kick 4.5 → 3.8 m/s). Only the
champion benchmark check caught it, by bisecting commits. Run the
safety net (`tests/golden/README.md`) after every merge.

**O11. Archive before deleting.** Tasks that look unused can back curated
checkpoints (BaseWalk, Kick-Approach, Kick-Near did). The 2026-10-23
restructure kept every run's latest + best + referenced checkpoints and all
configs, and recorded every decision in `restructure/KEEP_LIST.md`.
Re-run `restructure/best_ckpt.py` then `restructure/inventory.py` before any
future pruning.

**O11b. Run directories can be symlinks to runs in other experiments**
(three are: a wwcmu45 → wwcmu30 alias, a wwcmu50 → wwcmu45 alias and an
approach → stage-1 alias, made to resume across experiments). Any tool that
walks `logs/` must skip symlinked run dirs, or it sees the same files twice
and can delete through the alias. Match deployed ONNX to checkpoints by file
hash first; name heuristics picked the wrong run for the gold walk.

**O12. Large outputs don't belong in `docs/` or git.** Raw benchmark traces
(18 GB of `.npz`) were once staged into git by accident; keep JSON summaries,
put raw data outside the repo.

**O13. Verify file paths before acting on a note.** Notes and memory record
paths at the time; checkpoints may since have been pruned (latest, best and
referenced ones are kept) and some folders were deleted by the user
(`checkpoints/`, `nubots_models/`; both remain on the archive branch).

**O14. In this repo use `.venv/bin/python -m pytest`** (a moved venv once left
a stale `uv run pytest` shebang).
