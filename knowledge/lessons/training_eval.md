# Lessons: training, evaluation and checkpoint choice

Sources: `docs/K1_KICK_LESSONS.md` (§5, §6), `docs/K1_KICK_APPROACH_NOTES.md`,
`docs/experience/README.md`, `docs/evolution/HANDOFF.md`,
`docs/evolution/monitor.md`, session memory (k1-kick-staged-training,
k1-striker-selfplay, k1-dribble-speed).

## Judging runs

**E1. Training reward curves lie; judge only by evaluation.** They swing
±15 % over a few hundred iterations (v50d's aim reward 0.35 → 0.30 → 0.34
while it was the best model); self-play curves rose while play vs h022 fell.

**E2. The best checkpoint comes 250–500 iterations after a resume or fix,
then the policy drifts** (fewer, slower, more cautious kicks; dribble and
self-play show the same peak-then-slide). Evaluate every 250 iterations, keep
the peak, don't train long. Continuing from a plateau trades safety for
productivity regardless of step size or fall penalty.

**E3. Judge a resumed run against a same-length no-change continuation, not
against its parent checkpoint.** Continuations drift on their own (dribble
v39: side kicks 24 → 8.5 % with no change).

**E4. Know the noise before calling a winner.** Use two seeds at least; one
seed varies a few percent. Dribble: kick deltas count above ~0.1 m/s / 0.7°,
slow dribble above ~0.08, search above ~8 points, and search swings ±10 points
between checkpoints of one run. Self-play: 384-env evals vary ±0.02–0.05; use
≥ 1536 envs × 2 seeds with a CI.

**E5. Measure on the right conditions.** Kick speed with the nominal 0.1 kg
ball on flat ground (ball DR up to 0.25 kg hid a +36 % long-kick gain).
Compare models on the same config: enabling a feature in the base config
changes every eval mode.

**E6. Split aggregate metrics before concluding** — per range, per speed bin,
walking vs near-ball. Lean and heel-up appear only above 1 m/s; aggregates rise
just because the robot walks faster; v53's "tilt p90 7.7°" was the kick swing.

**E7. A "smooth" policy can be standing still.** Track idle time at a far
ball alongside jitter; judge gait with speed-matched walking-only benches.

**E8. Test the scenario a feature targets, and the old checks too**
(bumps, flat, push, moving ball, side drills, nominal-ball power, lean per
speed, cap tracking, per-range passes, runner-sim bench).

**E9. Benchmark the deployed action path.** See
[sim2real S1](sim2real.md#s1-benchmark-and-train-the-deployed-action-path).

**E10. A benchmark against a reference must give both sides the same inputs.**
B-Human was compared with a true ball while ours had the camera; under equal
camera perception ours won most metrics, under equal perfect perception
B-Human's technique still won.

**E11. The benchmark predicted the robot.** The benchmark-promoted x4_g004_70
kicked accurately on the K1; the rejected evo_g014/14550 kept missing. Trust
the gates.

## Run hygiene

**E12. One change per run.** When two changes ship together and results drop,
split them (v50 → v50d found that pushes, not the strike term, cost
accuracy; dribble v28 bundled four changes and couldn't be diagnosed).

**E13. Stop broken runs early** (v51 at ~400 iterations saved hours).

**E14. After any loader or warm-start change, check the first iterations'
episode length against the parent run.** Dribble v27 silently trained from
random weights (episode length ~48) after a load-config change.

**E15. Stage handoffs need `prepare_warmstart.py`.** Slots held constant in
the previous stage have normaliser std 0 (×100 amplification) and untrained
weights; reset them. Better: feed realistic dummy values in the earlier stage.

**E16. Curricula must count their own steps.** On resume the runner sets the
global step counter to the checkpoint's value, so step-keyed ramps jump to
their end (also on warm starts: h022 ≈ 400k steps).

**E17. Cap the action std** (std_range max 0.6 in stage 3; 0.4 / 0.25 in
self-play). It grew in every run otherwise, and with std pinned at the cap the
deterministic policy random-walks between checkpoints.

**E18. Fine-tunes need small steps.** Muon at the adaptive LR (~1e-3) with
desired_kl 0.01 random-walks a fine-tune; desired_kl 0.002 pinned the LR at
the 1e-5 floor (KL has an ~0.003 floor). A fixed LR 1e-4 (and, in self-play,
the KL anchor) worked. Under a fixed schedule `Loss/kl_divergence` logs 0.

**E19. Guard against one diverged simulation.** One env blowing up (finite
but huge velocities) produced a −1.17 M step reward and destroyed a healthy
run (approach_v2 at 5121). The k1_amp tasks now terminate on `physics_blowup`
(NaN/Inf or |qvel| > 200) with `invalid_state=True`, which zeros all rewards
for that env-step. Signature: value-loss spike with `nan_state` > 0.

## Blending and the evolution loop

**E20. Weight blends with the champion were the main promotion route.** In the
flat and hierarchical loops, single gene changes rarely survived the
no-regression gate; 70/30 or 50/50 blends of a near-miss child with the
champion kept gains and dropped regressions (x4, h007, h010). Blends do not
fine-tune well afterwards (ft_x50a/b fell from 170 to 80–98 goals).

**E21. Averaging nearby checkpoints (SWA) is a cheap, reliable gain** (dribble
swaA_v15b, swa_v16/v17; self-play swa_v15v16 was the best flat striker).

**E22. Make every default a switchable gene and record the parent's exact
recipe;** a default change confounds every child that inherits it (the K4
bundle cost goals and power in v59 and the style runs).

**E23. Scenario mixes have real costs.** Ball-behind training cost 0.5–2 s of
low-cap time to kick; more low-cap episodes made low caps slower, not faster.

**E24. The early-stop gate compares the best of 5 child screens with one
parent screen** — it favours children; frames that fail it are genuinely
worse. *Source:* monitor.md 2026-10-09.

## Diagnosis habits

**E25. Write insights down every run, with numbers.** The notes are why these
lessons are recoverable.

**E26. Keep evaluation tools in the repo, not a temp directory** (scratch
probes were wiped between sessions).
