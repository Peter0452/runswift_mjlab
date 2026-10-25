# Deliveries to k1_policy_runner

What leaves this repo for the robot, and how a change to the runner's RL
development interface is proposed. The runner (branch `dev`) owns that
interface: `../k1_policy_runner/docs/rl-development/interface.md`, the joint
table and one spec per policy in `docs/policies/`. We mirror it in
`src/k1/deploy/` and never edit the runner from here.

## A delivery

A model is delivered when `rsw deploy check CKPT --run RUN_DIR` passes all
four checks:

1. ONNX metadata against our contract.
2. ONNX against the trained actor.
3. Lost-ball parity (kick family).
4. **The runner's model intake with verdict `TAKE`.** The export writes
   `policy_id`, `spec_version`, `obs_dim` and `obs_layout`, so our models are
   never "legacy".

The package handed to the runner side:

- the ONNX (from the gate's output directory)
- the intake report (`<model>_intake.txt`, the runner's template)
- the run's `run.json` (recipe, verdicts, label `deployable`)
- the verdict per requirement of the task request (`tasks/<name>/`)
- the training randomisation the policy relies on at run time (delay, noise),
  if the policy spec doesn't list it yet

Copying the ONNX into the runner and switching its launch scripts is the
runner owner's step.

## Tier-2 changes: a new policy version

Anything pinned per policy is a tier-2 change:

- the observation layout or a slot's meaning
- the default pose
- action scales
- PD gains
- which joints the policy controls

A tier-2 change is never made in place. It ships as a new policy version
(`kick_loop_v2`, ...):

1. The recipe says `touches: runtime`; `rsw recipe check` enforces this for
   actor-input changes.
2. Write the proposed spec in `deliveries/specs/<policy_id>.md`, in the
   runner's spec format: observation table, `obs_layout` string, output,
   training randomisation, version history.
3. Bind the layout in `src/k1/deploy/obs_layout.py` (`policy_id`,
   `spec_version`, `spec_layout`). `tests/test_runner_spec.py` fails until the
   runner has the matching spec, which is the signal that the runner side
   adopted it.
4. Hand over the draft spec with the first model. The runner owner adds the
   spec, the policy class and any behaviour-interface change.

Tier-3 changes (weights, rewards, DR, curriculum, network size) need nothing
from the runner.

## Open items (2026-10-25)

- **Kick speed caps.** Training samples caps up to vy 2.0, wz 3.0 (chase caps
  since 2026-10-23). The `kick_loop_v1` spec and the runner's
  `SPEED_LIMIT_RANGES` say vy ≤ 1.5, wz ≤ 1.5, and the launch scripts use
  1.5 / 1.5 / 2.0. Decide whether to update the spec's trained ranges at the
  next kick delivery, or to train at the runner's ranges. The test is marked
  xfail until then.
- **No runner spec yet** for dribble (the `dribble` branch merges later),
  flat self-play (86 inputs) or the striker controller.
