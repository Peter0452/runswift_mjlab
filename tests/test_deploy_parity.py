"""The ONNX models deployed on the robot satisfy the contract (metadata check of
the deploy gate). Reads ../k1_policy_runner; skipped when it is not present."""

import pytest

from k1.deploy.obs_layout import LAYOUTS
from k1.deploy.parity import ROOT, check_onnx_metadata

RUNNER = ROOT.parent / "k1_policy_runner"
DEPLOYED = {
  # Runner branch dev (2026-10-25): the models its launch scripts use.
  "kick_loop_models/iter23.onnx": "kick_loop_v1",
  "amp_models/2026-10-17_21-58-53_softland_v1.onnx": "walk_amp",
  # Earlier deployments (present on the dribble branch; skipped when absent).
  "kick_loop_models/k1_kick_loop_h022_c2_18450.onnx": "kick_loop_v1",
  "kick_loop_models/k1_kick_loop_swa_v15v16_9100.onnx": "selfplay_v1",
  "dribble_models/k1_dribble_swaA_v15b_12400.onnx": "dribble_v1",
  "amp_models/model_9950.onnx": "walk_amp",
}


# The gold walk was exported before the 6-decimal fix (lesson S5): its hip and
# ankle action scales are rounded (0.213 for 0.2125, 0.12 for 0.119687). Strict:
# this starts failing once a re-exported walk is deployed; then drop the mark.
KNOWN = {
  "amp_models/model_9950.onnx": pytest.mark.xfail(
    strict=True, reason="pre-S5 export: action scales rounded to 3 decimals"
  )
}


@pytest.mark.parametrize(
  "rel", [pytest.param(r, marks=KNOWN.get(r, ())) for r in sorted(DEPLOYED)]
)
def test_deployed_onnx_meets_the_contract(rel: str) -> None:
  path = RUNNER / rel
  if not path.is_file():
    pytest.skip(f"{path} not present")
  assert check_onnx_metadata(path, LAYOUTS[DEPLOYED[rel]]) == []


CHAMPION = (
  ROOT
  / "logs/rsl_rl/k1_kick_stage3_amp/2026-10-09_10-22-47_champ_h022_c2_18450/model_18450.pt"
)


@pytest.mark.slow
@pytest.mark.skipif(not CHAMPION.is_file(), reason="champion checkpoint not on disk")
def test_deploy_gate_passes_the_deployed_champion(tmp_path) -> None:
  from k1.deploy.parity import RUNNER_PY, gate

  if RUNNER_PY is None:
    pytest.skip("runner not present")
  result = gate(
    "Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1", str(CHAMPION), tmp_path
  )
  assert result["metadata_problems"] == []
  assert result["onnx_max_diff"] < 1e-4
  assert result["lost_rule"]["passed"], result["lost_rule"]["detail"]
  assert result["intake"]["verdict"] == "TAKE", result["intake"]
  assert result["passed"]
