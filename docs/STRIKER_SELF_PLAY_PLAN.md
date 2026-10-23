# Learned striker by self-play — plan

Living plan for training a K1 striker with self-play / multi-agent RL and
plugging it into the runswift behaviour. Branch: `claude/inspiring-thompson-i5igqs`.

## 1. Goal

Demonstrate a learned **striker**: continuous ball handling, dribbling, kicking
and outmanoeuvring the opposing striker to score, within the system's
constraints (deploy joint / torque limits, the robot's real perception, the
runswift behaviour's rules and roles).

Everything else is abstracted and given: referee states, roles, restarts,
localisation, getting up, teammates. The striker runs only when the behaviour
says *open play, you are the striker*.

## 2. Problem as trained

- **Game**: 1v1, striker against striker (runswift's `RoleCoordinator` makes
  the robot closest to the ball each team's striker, so the robot our striker
  meets at the ball is the other team's striker).
- **Field**: per episode 9 x 6 m up to 14 x 9 m (width scales with length),
  random heading, placed around the spawned ball and robot. Goals 2.4 m wide,
  crossbar 1.6 m (small) / 1.8 m (medium, length >= 11.5 m).
- **Goal**: whole ball over the goal line between the posts, under the bar.
  Over any other line: out. Either ends the point and the side that did not
  cause it restarts on the same field: after a goal the side that conceded,
  after an out the side that did not touch the ball last (contact sensors;
  ties and untouched balls count against the learner). Learner restart: ball
  ahead of the learner, opponent at the learner's spot mirrored through the
  ball. Opponent restart: ball near where it went out (centre after a goal),
  ≥ 2 m from the learner (never teleported), opponent 0.4–0.9 m behind it
  facing its attack. Episodes end on falls or time out (30 s).
- **Opponent**: frozen copies of the learner (mirror) or members of a pool of
  past selves and seeds. It is not trained on its own.

## 3. Inputs and outputs

### Flat striker (one policy, joints)

86 inputs at 50 Hz, 22 joint targets out.

| Slots | Input | Robot source |
|---|---|---|
| 0–2 | Trunk angular velocity | IMU |
| 3–5 | Gravity in trunk frame | IMU |
| 6–27 | Joint positions − default | Joint states |
| 28–49 | Joint velocities | Joint states |
| 50–71 | Previous raw action | Runner |
| 72–73 | Ball x, y (level frame, origin between feet) | Vision `position_projection` |
| 74 | Ball memory age exp(−t/2 s) | Runner (IMU-yaw memory, no odometry) |
| 75–77 | Speed caps \|vx\|, \|vy\|, \|wz\| | Constants |
| 78–79 | Aim direction (cos, sin), robot heading frame | Target source (§7) |
| 80–82 | Range one-hot (< 4 / 4–8 / ≥ 8 m) | Target source |
| 83–84 | Opponent x, y | Vision robot detection `position_projection` |
| 85 | Opponent seen (1 / 0; zeros when unseen) | Runner |

Slots 0–82 are the stage-3 kick loop (`docs/K1_KICK_LOOP_POLICY_IO.md`).
Opponent detection: trunk in the head camera's view, within 6 m, 5 % dropout,
noise 5 cm + 5 % of distance. Critic: 101 (stage-3 98 + true opponent).

### Two-level striker (controller over skills)

Controller every 0.2 s (10 env steps), 4 outputs in [−1, 1]:
`a0` kick (> 0) or walk, `a1:3` direction (cos, sin) in the robot frame,
`a3` kick range (thirds) or walk speed (0–1.2 m/s). Inputs: the 86 above +
current skill + time since switch (88). Actor: GRU (128) → MLP (128) → 4;
its memory (opponent motion, play history the single-frame detections drop)
lasts an episode, across kickoffs, and steps once per decision. Deploy as
ONNX `obs` [1, 88] + `h_in` [1, 1, 128] → `actions` + `h_out`; the runner
holds the state and zeroes it when the striker takes over. Skills (frozen):

- **Kick**: stage-3 kick loop (`h022_c2_x50`); aim / range slots overwritten
  with the controller's choice.
- **Walk**: AMP walk `model_9950` (wwcmu50 stageA); velocity command from
  direction and speed (turns towards the direction). Dribble = walk through
  the ball.

Both skills drive the same 22 joints, so switching only changes which network
runs.

## 4. Algorithms

| Piece | Flat striker | Controller |
|---|---|---|
| RL | PPO (rsl_rl) | PPO at 5 Hz, GRU actor (BPTT over a 24-decision rollout), MLP critic |
| Style prior | AMP discriminator (weight 0.3, off around kicks) | — (skills own style) |
| Optimiser | Muon (actor / critic), Adam (discriminator) | Adam |
| Extras | Mirror augmentation, CAPS smoothness, privileged critic | Privileged critic |
| Horizon | γ 0.995 (~4 s), λ 0.95 | γ 0.99 (~20 s), λ 0.95 |
| Opponents | 50 % mirror, 50 % pool | 50 % controller mirror, 50 % pool |
| Warm start | `h022` with zero weights on the 3 opponent inputs | Random (mirror starts as zeros) |

Pool: seeds (`h022` flat striker, walk 9950 dribbling under a scripted
command), plus snapshots every 200 iterations (newest 8, saved to
`<run>/opponents/`). A fallen opponent is stood up after 1 s.

## 5. Rewards

| Term | Flat | Controller |
|---|---|---|
| Goal scored / conceded | ±30 per goal | ±30 |
| Dribble progress (ball towards goal while within 0.6 m and closer than the opponent) | 4/s per m/s | yes |
| Stage-3 kick quality, aim, power | yes | kick_vel, kick_direction, kick_vel_accurate |
| Fall / kick fall / alive | yes | yes |
| Posture, smoothness, torque, feet | yes | — (skills own them) |
| Stage-3 second-touch penalty (−200), point-target goal | off | off |
| Kick / walk switch | — | −0.05 per switch |

## 6. Training recipe (option 2: alternate controller and skills)

```
Phase 1  controller learns, skills frozen       Mjlab-Velocity-Striker-Controller-Booster-K1
Phase 2  kick skill learns inside the game       Mjlab-Velocity-Kick-SelfPlay-Amp-DA-Muon-Booster-K1
Phase 3  controller re-learns with the new kick  phase-1 task, new kick checkpoint
... repeat; optional final: distil into one flat policy and self-play it end-to-end
```

```sh
# Phase 1
uv run train Mjlab-Velocity-Striker-Controller-Booster-K1 --env.scene.num-envs 4096
# Phase 2: kick fine-tunes against the phase-1 striker; aims are lanes across
# the goal mouth (up to 40 % of its width) so the kick obeys commanded aims.
uv run train Mjlab-Velocity-Kick-SelfPlay-Amp-DA-Muon-Booster-K1 \
  --env.actions.opponent.controller-checkpoint <phase1>/model_N.pt
# Phase 3
uv run train Mjlab-Velocity-Striker-Controller-Booster-K1 \
  --env.actions.opponent.kick-skill-checkpoint <phase2>/model_M.pt
```

Guardrails each round: deploy-safety terms stay on; gate on the runswift kick
grid and the 90-case score grid (`runswift_code/behaviour/examples/booster_match/score-benchmark.md`)
before accepting a skill round.

## 7. Integration with the runswift behaviour

```
MatchRunner (unchanged gates: playing, striker, no active restart, upright, localised)
  _play_ball  →  learned striker branch
     target = select_target(field, ball, scene, tactics)      # unchanged lane choice
     d = target − ball_field;  aim = rotate(d, −θ)/|d|;  range = bucket(|d|)
     StrikerIntent{active, aim, range, speed caps, stamp, deadline}
policy_runner (50 Hz) StrikerPolicy
  vision → ball (72–74), opponent (83–85);  IMU / joints → body (0–71)
  aim held between intents, turned by IMU yaw change since its stamp
  lease expired / whistle / role change / fall / lost localisation → hand back
```

Ownership while the striker runs: behaviour decides *whether* and *where to
attack*; the policy decides *how*; the runner's head tracker owns the head; the
existing get-up routine handles falls.

No new odometry or localisation: the ball memory uses IMU yaw only (as
trained), the opponent is single-frame detections, and the aim uses the
behaviour's existing field pose. Standalone (no behaviour): aim from a fixed
IMU heading (`--kick-dir-mode field`) or through the ball, operator-supervised.

## 8. Built so far

| Commit | What |
|---|---|
| `55ff24d` | 1v1 self-play task, frozen opponent action term, mirror + pool runner |
| `8c8467f` | Opponent detection inputs (83–85), widening warm start, mirror augmentation |
| `aca1b8c` | Real field, goal mouths, out lines, mirrored kickoffs, dribble reward |
| `afa6f1d` | Two-level striker (controller task, wrapper, runner), controller opponents, aim lanes |

Verified on CPU: unit / env tests (`tests/test_self_play.py`,
`tests/test_striker_controller.py`), 2-iteration training runs of both tasks,
ONNX export 86 → 22, balanced 3–3 frozen-vs-frozen rollout, handoff check (no
falls from random kick / walk switching, 2.7 robot-minutes). GRU controller
(2026-10-11): frozen GRU opponents match rsl_rl's `RNNModel` step by step,
3-iteration GPU smoke run (256 envs, GRU snapshots in the pool), ONNX export
with `h_in` / `h_out`. **No full GPU training run yet.**

## 9. Next (in order)

1. ~~Ball-out restart fix~~ done 2026-10-11 (see §2): outs and the
   learner's goals hand the restart to the opponent. No extra penalty: losing
   the ball is the cost. Watch `ball_out_by_learner`, `opponent_restarts`.
2. **Aim realism**: noise on slots 78–80 (per-episode heading bias, jitter,
   occasional jumps) for localisation error; occasional aim-lane switches
   mid-point (as `select_target` does when a lane closes).
3. **Opponent sampling** (OpenAI lessons): longer snapshot history (e.g. 32
   every 100 iterations, uniform over the recent half), mirror share ~0.2.
4. **Anneal task shaping** (OpenAI lessons): kick shaping towards ~20 % over
   the first 3–5k iterations; deploy-safety terms fixed.
5. **Pushing constraint**: cap robot–robot contact force (`c.<term>` adaptive
   constraints), so play is legal standalone.
6. First GPU runs: phase 1, then phase 2; fixed-opponent evaluations (`h022`,
   walker, runswift scripted striker) logged alongside self-play win rates.
7. Opponent motion: GRU controller done; the flat striker still sees single
   frames (frame stacking or a GRU there if it needs them).
8. Integration: `StrikerIntent` in the behaviour, `StrikerPolicy` in the
   runner, SDK ↔ low-level mode handoff timing on the K1.
9. Later: scripted runswift goalie (`blocking_target`) on the pitch; physical
   goal posts; learned defender / 2v1.

## 10. What to watch

| Signal | Healthy |
|---|---|
| `SelfPlay/win_rate_latest` | ≈ 0.5 (even against itself) |
| `SelfPlay/win_rate_pool` | rising (beats past selves) |
| `Metrics/twist/contest_scored` | rising per episode |
| `Metrics/twist/ball_out` | falling |
| `Metrics/twist/ball_out_by_learner` | falling (not used as a free reset) |
| `Episode_Reward/dribble_progress` | rising without goals falling (carrying, not stalling) |
| Falls, kick speed | stay at stage-3 levels |

## 11. Risks

- Non-stationary opponents: the critic does not know which opponent it faces.
- Shooting earlier instead of outmanoeuvring (stage-3 kick shaping still pays).
- Phase 2 trains the kick on its own decisions plus random aims, not inside
  the controller's decisions (an approximation).
- Localisation may degrade while the head tracks the ball during long plays.
- Controller-mode switching on the real K1 (SDK walking / soccer vs low-level)
  is unmeasured.

## 12. References

- Bansal et al., *Emergent Complexity via Multi-Agent Competition*, ICLR 2018
  (arXiv 1710.03748); code `openai/multiagent-competition` — PPO, dense-shaping
  curriculum annealed to win / lose, opponents sampled from past snapshots.
- Su et al., *Toward Real-World Cooperative and Competitive Soccer with
  Quadrupedal Robot Teams*, CoRL 2025 (arXiv 2505.13834) — frozen skills +
  learned high-level policy (MAPPO, fictitious self-play), real Go1 robots.
- runswift behaviour: `runswift_code/behaviour/scripts/match_runner.py`,
  `match_tactics.py`.
