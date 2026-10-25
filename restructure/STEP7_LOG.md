# Step 7 log: the runner's RL development interface as our output contract

2026-10-25, after the user named `k1_policy_runner` branch `dev` as the runner
to structure around ("RL development interface is our outputs coming in to
k1_policy_runner"). Nothing in the runner was edited; it is read only.

## Built

| What | Checked by |
|---|---|
| `k1/deploy/runner_spec.py`: reads the runner's docs and constants without importing it. Covers the required-metadata table, the joint table, each policy spec's `obs_layout` and `spec_version`, `ast` reads of `kick_loop_policy.py` constants, and the runner package dir on `dev` (`policy_runner/`) or older branches (`python-implementation/`). | `tests/test_runner_spec.py` |
| Layouts bound to runner specs: `walk_amp` → `walk_amp_v1@1`, `kick_loop_v1` → `kick_loop_v1@1`, each with the spec's `obs_layout` string verbatim. Dribble, self-play and striker stay unbound. | `test_layout_matches_its_policy_spec` (strings, versions, sizes, block boundaries) |
| Export writes `policy_id`, `spec_version`, `obs_dim`, `obs_layout` for bound layouts (`scripts/tools/export_onnx.py`, used by the gate). Only explicit exports do this: the ONNX that runners save into run directories stay as before. | the slow gate test (intake verdict TAKE on the h022 export) |
| `k1/deploy/intake.py`: the runner's `model-intake.md` as code. Runs its `tools/onnx_dump.py`, classifies each difference, and writes the runner's report template. | iter23 and softland_v1 → TAKE AS LEGACY (the runner's own worked example) |
| Deploy gate: 4th check = intake verdict TAKE; lost-rule parity runs against `dev`'s package; the intake report is saved next to the ONNX. `rsw deploy intake ONNX`. | `tests/test_deploy_parity.py` (now includes dev's deployed models) |
| Conformance tests: the joint table vs `contract.py`; the required-metadata table vs what we write; actor-input order of the training env vs the layout; the kick's lost rule, memory, camera FOV and head tracker vs the runner's constants. A layout without a spec is flagged once the runner gains a spec for it. | 11 pass, 1 xfail (speed ranges, below) |
| Task requests: `kick` names `interface.policy: kick_loop_v1@1` (checked against the bound layouts). `dribble` and `striker` note that they have no runner spec yet. | `tests/test_k1_requests.py` |
| `deliveries/README.md` (the delivery package; the tier-2 route: draft spec in `deliveries/specs/`, bind the layout, test fails until the runner adopts the spec); `knowledge/deployment.md` §0; architecture and INDEX updated | read through |

## Findings

- **Everything in tier 1 and tier 2 matches** between training and runner
  `dev`:
  - joint order, default pose, action scales, PD gains, joint limits
  - the `kick_loop_v1` and `walk_amp_v1` layouts
  - the kick's lost rule (0.5 s in view within 3 m, 1.5 s timeout, virtual
    ball 2.0 m at ±1.6 rad), memory tau 2 s, camera half FOV
  - the head tracker's pivot, look-down 0.18 and lost-after 0.2
- **One mismatch: trained speed ranges.** The registered Stage 3 samples caps
  up to (0.3–2.0, 0.2–2.0, 0.4–3.0) (chase caps since 2026-10-23). The runner's
  `SPEED_LIMIT_RANGES` and the spec say (0.3–2.0, 0.2–1.5, 0.4–1.5), the h022
  champion's caps. The test is marked xfail (strict) until you and the runner
  owner decide.
- `knowledge/deployment.md` said the kick's virtual ball is "close". Training
  and the runner both use 2.0 m at ±1.6 rad; the page is corrected.
- Runner `dev` deploys walk `softland_v1` and kick `iter23`; both pass our
  contract metadata check and the intake as legacy v1. Our records (models.md,
  session hook) still name gold walk 9950 and h022: **not changed**, waiting
  for the user to confirm what runs on the robot.

## Best guesses (review these)

1. **Spec metadata only in explicit exports** (`export_onnx.py`, the gate),
   not in the ONNX the trainers write into run directories. Those trainers
   don't know which layout they serve, and the dribble and kick layouts look
   identical by term names. Deliverables come from the gate anyway.
2. **A layout without a runner spec fails the gate** (intake can't TAKE it).
   So dribble can't pass `rsw deploy check` until the `dribble` branch brings
   its spec into `dev`. This matches "dev is the target"; say if dribble should
   be exempt meanwhile.
3. **The runner's docs are parsed, not copied.** If the runner changes its
   table or spec format, `runner_spec.py` needs a matching tweak. The test
   then fails loudly rather than passing silently.
4. The ball frame (training: feet midpoint; runner spec: "trunk frame",
   meaning runswift `base_link` from vision) can't be compared as numbers. It
   stays a documented item, not a test.

## Safety net

153 passed, 4 skipped, 1 xfailed (the speed ranges); golden snapshots 6/6 ok.
The slow deploy-gate test passes again on runner `dev`: h022 exports with the
spec keys, intake verdict **TAKE**, lost-rule parity runs against
`policy_runner/policy_runner/`, ONNX vs actor < 1e-4. This fixes the Step 6
failure. No training code or config changed.
