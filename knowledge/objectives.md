# Objectives and standing decisions

What the user has asked for, with dates. Agents: judge every run against the
relevant section, and do not change a standing decision without asking.
Sources: `docs/evolution/HANDOFF.md`, `docs/experience/README.md`, session
memory (k1-kick-objectives, benchmark-gated-adoption, dribble-kick-objectives,
dribble-speed-over-slow, gait-penalty-weighting, kick-dr-from-amp-walk,
selfplay-run-authority).

## Everywhere

- **Goal:** real-match deployment on the K1 (RoboCup), through
  `k1_policy_runner`.
- **Benchmark-gated adoption (2026-10-05):** learn from B-Human and others,
  but aim to transcend them. Adopt a technique or a mix of ours and theirs
  only when a fixed benchmark shows it beating the reference on the targeted
  metrics with no regression elsewhere — never because it resembles the
  reference.
- **No regression:** never trade away an objective already built up.
- **One change per run**, with a regression check against a same-length
  no-change control (2026-10-21).
- **Truthful reporting:** report results as measured, including failures.
- **Domain randomization, latency and limits** are inherited from the AMP walk
  on purpose, because it transfers to the robot. Don't change them because
  another config differs; propose changes only with robot evidence and the
  user's go-ahead (2026-10-02).
  - **Exception (2026-10-07):** leg torque is hard-clipped at B-Human's kick
    clip (hip pitch / roll 50, hip yaw 30, knee 60, ankle pitch / roll 30 Nm),
    because the motor ratings are believed to be no-load values. Keep the
    numbers in one table (`env_cfgs.LEG_TORQUE_CLIP`) so measured values can
    replace them.
- **Gait penalties stay light (2026-10-20):** target the deployed AMP walk's
  numbers (flat stance ~73 %, first loaded step ~0.8 × body weight); strong
  pose penalties make the robot slap its feet.
- **Run authority (2026-10-13):** stop plateaued runs and launch the next
  variant without asking, but don't waste GPU. Reversing a reward design the
  user asked for still needs their OK.

## Kick (stage-3 kick loop)

- **Headline (2026-10-08):** kick faster, more accurately and more powerfully
  than B-Human across diverse ball sizes, without losing stability, with no
  falls and smooth actions. Steps should be quiet (loud on the robot).
- **Power by range:** short 1–4 m soft and accurate, medium 4–8 m matched to
  the distance, long ≥ 8 m as hard as possible (at least B-Human's power;
  7–8 m/s goal; air balls are fine, 2026-10-07).
- **Kick quickly** once at the ball.
- **Run at the speed caps:** the caps are limits for ball play, and the policy
  should actually reach them. Since 2026-10-23 the kick-loop caps are the
  chase caps: |vx| ≤ 2.0 (1.75 back), |vy| ≤ 2.0, |wz| ≤ 3.0.
- **Posture:** upright, no lean even at speed, height ~0.52 m, no crouch,
  knock-knee, wide arms or head up, flat feet; as smooth as the gold walk
  (model_9950).
- **Action rate must stay stable and smooth (2026-10-08).**
- **One end-to-end kick policy (2026-10-06):** no policy switching or
  walk/kick hybrids for now. External methods enter only through data,
  scenarios, rewards, constraints, the training algorithm or distillation.
- **Kick styles (2026-10-05/07):** keep several styles (front, inside foot,
  hop) and let the policy choose per situation from outcomes; no style forced
  by range.
- **83 inputs fixed** for the kick loop (86 with opponent inputs in self-play).
- **Ball (2026-10-08, 2026-10-23):** the default stays our ball, radius
  0.07–0.13 m and mass 0.05–0.45 kg around 0.08 m / 0.1 kg, because every
  kept model was trained on it. **Future training should move to B-Human's
  ball** (0.095 m ± 0.01, 0.29 kg ± 0.01, solid): opt in per run with
  `K1_BALL=bhuman` (read at import, `mdp/approach.py`); switch the default
  when a lineage has been retrained on it, then re-record the golden
  references.
- runswift's fixture is a proxy soft gate: we may be slightly worse where its
  ideal assumptions matter, but not on falls, accuracy or kick speed (kick
  speed gated on 6/9 m tasks only).

## Dribble

- **Speed (2026-10-19):** dribble at ~1.5 m/s in all directions with good
  ball control. Speed beats slow precision a bit (2026-10-21): slow-dribble
  gates (0.3 / 0.5 m/s) relaxed to −0.08 vs v17; 0.8 m/s, falls and posture
  gates stay strict.
- **Kick mode (2026-10-21, obs slot 82):**
  - style by geometry first (kick direction vs approach line under ~30° =
    power kick, over = side-foot kick), then outcome-based style choice;
  - power at least B-Human's (~4.3 m/s 3D in our bench); air balls fine;
  - time to kick as short as possible;
  - re-kick until the ball is more than 0.5 m away, then stand;
  - do not compromise the dribble;
  - later: smooth, fast dribble → kick transitions.
- The user allowed changing the inputs if needed (2026-10-23), as a separate
  model version with runner and parity updated.
- B-Human may be used as a teacher (2026-10-22).

## Self-play striker

- Go beyond the stage-3 kick loop to continuous dribble, kick and outmanoeuvre
  play inside the runswift behaviour (`docs/STRIKER_SELF_PLAY_PLAN.md`).
- The kick skill is still held to the kick objectives and benchmark gate.
- The user asked for Bansal-style annealing of task shaping (anneal to 0.2);
  freezing α (v13–v16) deviated from that and was reported.
- Even the sides by giving the opponent the learner's DR, never by removing it
  from the learner.

## B-Human port

- A faithful reproduction (inputs, outputs, rewards, randomisation, PPO) on
  our simulator, to compare with and mix into our kick. Separate from the
  one-policy kick objective.

## Open questions waiting on the user

- Runner: switch `start_kick.sh` to the champion with caps that match
  training; `DEFAULT_MODEL_PATH`; `--record-obs` (HANDOFF "Pending").
- Ball tracker (Kalman + odometry), then a learned ball predictor; RMA-style
  adaptation as an L5 atom.
- Whether the official runswift fixture should adopt mesh feet / soles origin /
  caps / vision for our policy (2026-10-09).
- Dribble: kick power has stayed ~3.0 m/s across every reward lever (v33–v52);
  the remaining options change deployment (observation history, phase input,
  B-Human handover).
