"""Every registered task loads, and the set of tasks only changes on purpose."""

import io
import warnings
from contextlib import redirect_stderr, redirect_stdout

import pytest
import torch
from conftest import get_test_device

from mjlab.envs import ManagerBasedRlEnv
from mjlab.tasks.registry import list_tasks, load_env_cfg, load_rl_cfg, load_runner_cls

# The K1 tasks kept by the 2026-10-23 restructure (restructure/KEEP_LIST.md).
# Adding or removing a task should be a deliberate edit here.
EXPECTED_TASKS = {
  *(
    f"Mjlab-BHuman-Kick{stage}-Booster-K1"
    for stage in (
      "",
      "-Stage1",
      "-Stage2",
      "-Stage3a",
      "-Stage3b",
      "-Stage4",
      "-Stage5",
      "-Stage6",
      "-Stage6a",
    )
  ),
  "Mjlab-Getup-Flat-Booster-K1",
  "Mjlab-Kick-Approach-Booster-K1",
  "Mjlab-Kick-Near-Booster-K1",
  "Mjlab-Kick-WalkAmp-Amp-DA-Muon-Booster-K1",
  "Mjlab-Kick-WalkAmp-DA-Muon-Booster-K1",
  "Mjlab-Tracking-Flat-Booster-K1-Kick",
  "Mjlab-Tracking-Flat-Booster-K1-Kick-Box",
  "Mjlab-Tracking-Flat-Booster-K1-Kick-Stage2",
  "Mjlab-Velocity-Dribble-Amp-DA-Muon-Booster-K1",
  "Mjlab-Velocity-Flat-Amp-DA-Muon-Booster-K1",
  "Mjlab-Velocity-Flat-Booster-K1",
  "Mjlab-Velocity-Flat-Booster-K1-BaseWalk",
  "Mjlab-Velocity-HTWK-Booster-K1-Nubots",
  "Mjlab-Velocity-HTWK-Exact-Booster-K1-Nubots",
  "Mjlab-Velocity-HTWK-Robust-FT-Booster-K1-Nubots",
  "Mjlab-Velocity-HTWK-Unclipped-Booster-K1-Nubots",
  "Mjlab-Velocity-Kick-Approach-Amp-DA-Muon-Booster-K1",
  "Mjlab-Velocity-Kick-SelfPlay-Amp-DA-Muon-Booster-K1",
  "Mjlab-Velocity-Kick-Stage1-Amp-DA-Muon-Booster-K1",
  "Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1",
  "Mjlab-Velocity-Rough-Amp-DA-Muon-Booster-K1",
  "Mjlab-Velocity-Rough-Amp-DA-Muon-Booster-K1-KickHandoff",
  "Mjlab-Velocity-Rough-Booster-K1",
  "Mjlab-Velocity-Rough-Booster-K1-BaseWalk",
  "Mjlab-Velocity-Striker-Controller-Booster-K1",
}


def test_registered_tasks_are_the_expected_set() -> None:
  tasks = set(list_tasks())
  assert tasks - EXPECTED_TASKS == set(), "new tasks: add them to EXPECTED_TASKS"
  assert EXPECTED_TASKS - tasks == set(), "missing tasks"


@pytest.mark.parametrize("task_id", sorted(EXPECTED_TASKS))
def test_task_configs_load(task_id: str) -> None:
  for play in (False, True):
    cfg = load_env_cfg(task_id, play=play)
    assert cfg.observations and cfg.actions
  assert load_rl_cfg(task_id).experiment_name
  load_runner_cls(task_id)  # resolves (None means the default runner)


@pytest.mark.slow
@pytest.mark.parametrize("task_id", sorted(EXPECTED_TASKS))
def test_task_env_builds_and_steps(task_id: str) -> None:
  """Each task's training env builds with a few envs and takes one step."""
  cfg = load_env_cfg(task_id)
  cfg.scene.num_envs = 2
  with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
      env = ManagerBasedRlEnv(cfg, device=get_test_device())
  try:
    env.reset()
    action = torch.zeros(
      (env.num_envs, env.action_manager.total_action_dim), device=env.device
    )
    obs, reward, *_ = env.step(action)
    assert torch.isfinite(reward).all()
    for group, value in obs.items():
      if isinstance(value, torch.Tensor):
        assert torch.isfinite(value).all(), group
  finally:
    env.close()
