from __future__ import annotations

import copy
import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal

import numpy as np
import torch

from mjlab.managers import CommandTerm, CommandTermCfg
from mjlab.tasks.tracking.mdp.shot import reset_kick_shot
from mjlab.utils.lab_api.math import (
  matrix_from_quat,
  quat_apply,
  quat_error_magnitude,
  quat_from_euler_xyz,
  quat_inv,
  quat_mul,
  sample_uniform,
  yaw_quat,
)
from mjlab.viewer.debug_visualizer import DebugVisualizer

if TYPE_CHECKING:
  from collections.abc import Callable
  from typing import Any

  import viser

  from mjlab.entity import Entity
  from mjlab.envs import ManagerBasedRlEnv

_DESIRED_FRAME_COLORS = ((1.0, 0.5, 0.5), (0.5, 1.0, 0.5), (0.5, 0.5, 1.0))


class MotionLoader:
  def __init__(
    self, motion_file: str, body_indexes: torch.Tensor, device: str = "cpu"
  ) -> None:
    data = np.load(motion_file)
    self.joint_pos = torch.tensor(data["joint_pos"], dtype=torch.float32, device=device)
    self.joint_vel = torch.tensor(data["joint_vel"], dtype=torch.float32, device=device)
    self._body_pos_w = torch.tensor(
      data["body_pos_w"], dtype=torch.float32, device=device
    )
    self._body_quat_w = torch.tensor(
      data["body_quat_w"], dtype=torch.float32, device=device
    )
    self._body_lin_vel_w = torch.tensor(
      data["body_lin_vel_w"], dtype=torch.float32, device=device
    )
    self._body_ang_vel_w = torch.tensor(
      data["body_ang_vel_w"], dtype=torch.float32, device=device
    )
    self._body_indexes = body_indexes
    self.body_pos_w = self._body_pos_w[:, self._body_indexes]
    self.body_quat_w = self._body_quat_w[:, self._body_indexes]
    self.body_lin_vel_w = self._body_lin_vel_w[:, self._body_indexes]
    self.body_ang_vel_w = self._body_ang_vel_w[:, self._body_indexes]
    self.time_step_total = self.joint_pos.shape[0]
    if "clip_ends" in data.files:
      self.clip_ends = torch.tensor(data["clip_ends"], dtype=torch.long, device=device)
      self.clip_starts = torch.cat(
        [
          torch.zeros(1, dtype=torch.long, device=device),
          self.clip_ends[:-1],
        ]
      )
    else:
      self.clip_ends = None
      self.clip_starts = None
    if "clip_z" in data.files:
      self.clip_z = torch.tensor(data["clip_z"], dtype=torch.float32, device=device)
    else:
      self.clip_z = None
    if "clip_names" in data.files:
      self.clip_names = [str(name) for name in data["clip_names"]]
    else:
      self.clip_names = None
    if "clip_z_names" in data.files:
      self.clip_z_names = [str(name) for name in data["clip_z_names"]]
    else:
      self.clip_z_names = None
    # 0 = right foot, 1 = left foot. Missing means every clip is right-footed.
    if "clip_kick_foot" in data.files:
      self.clip_kick_foot = torch.tensor(
        data["clip_kick_foot"], dtype=torch.long, device=device
      )
    else:
      self.clip_kick_foot = None


def estimate_clip_strike_positions(
  foot_pos: torch.Tensor,
  clip_ends: torch.Tensor,
  ball_z: float,
) -> torch.Tensor:
  """Ball center for each clip, in the motion frame.

  The strike is the first frame after the foot's highest point where the foot
  descends through ``ball_z``. If it never crosses, the fastest horizontal
  step after the peak is used. Returned z is ``ball_z``.
  """
  strikes = []
  ends = [int(end) for end in clip_ends]
  starts = [0, *ends[:-1]]
  for start, end in zip(starts, ends, strict=True):
    foot = foot_pos[start:end]
    peak = int(torch.argmax(foot[:, 2]))
    z = foot[:, 2]
    crosses = (z[:-1] >= ball_z) & (z[1:] < ball_z)
    crosses[:peak] = False
    if bool(crosses.any()):
      frame = int(torch.argmax(crosses.int()))
    else:
      step = foot[1:, :2] - foot[:-1, :2]
      speed = torch.linalg.norm(step, dim=-1)
      speed[:peak] = -1.0
      frame = int(torch.argmax(speed)) + 1
    strikes.append(
      torch.stack(
        (
          foot[frame, 0],
          foot[frame, 1],
          foot.new_tensor(ball_z),
        )
      )
    )
  return torch.stack(strikes)


class MotionCommand(CommandTerm):
  cfg: MotionCommandCfg
  _env: ManagerBasedRlEnv

  def __init__(self, cfg: MotionCommandCfg, env: ManagerBasedRlEnv):
    super().__init__(cfg, env)

    self.robot: Entity = env.scene[cfg.entity_name]
    self.robot_anchor_body_index = self.robot.body_names.index(
      self.cfg.anchor_body_name
    )
    self.motion_anchor_body_index = self.cfg.body_names.index(self.cfg.anchor_body_name)
    self.body_indexes = torch.tensor(
      self.robot.find_bodies(self.cfg.body_names, preserve_order=True)[0],
      dtype=torch.long,
      device=self.device,
    )

    self.motion = MotionLoader(
      self.cfg.motion_file, self.body_indexes, device=self.device
    )
    self.time_steps = torch.zeros(self.num_envs, dtype=torch.long, device=self.device)
    self.body_pos_relative_w = torch.zeros(
      self.num_envs, len(cfg.body_names), 3, device=self.device
    )
    self.body_quat_relative_w = torch.zeros(
      self.num_envs, len(cfg.body_names), 4, device=self.device
    )
    self.body_quat_relative_w[:, :, 0] = 1.0

    self.bin_count = int(self.motion.time_step_total // (1 / env.step_dt)) + 1
    self.bin_failed_count = torch.zeros(
      self.bin_count, dtype=torch.float, device=self.device
    )
    self._current_bin_failed = torch.zeros(
      self.bin_count, dtype=torch.float, device=self.device
    )
    self.kernel = torch.tensor(
      [self.cfg.adaptive_lambda**i for i in range(self.cfg.adaptive_kernel_size)],
      device=self.device,
    )
    self.kernel = self.kernel / self.kernel.sum()

    self.metrics["error_anchor_pos"] = torch.zeros(self.num_envs, device=self.device)
    self.metrics["error_anchor_rot"] = torch.zeros(self.num_envs, device=self.device)
    self.metrics["error_anchor_lin_vel"] = torch.zeros(
      self.num_envs, device=self.device
    )
    self.metrics["error_anchor_ang_vel"] = torch.zeros(
      self.num_envs, device=self.device
    )
    self.metrics["error_body_pos"] = torch.zeros(self.num_envs, device=self.device)
    self.metrics["error_body_rot"] = torch.zeros(self.num_envs, device=self.device)
    self.metrics["error_joint_pos"] = torch.zeros(self.num_envs, device=self.device)
    self.metrics["error_joint_vel"] = torch.zeros(self.num_envs, device=self.device)
    self.metrics["sampling_entropy"] = torch.zeros(self.num_envs, device=self.device)
    self.metrics["sampling_top1_prob"] = torch.zeros(self.num_envs, device=self.device)
    self.metrics["sampling_top1_bin"] = torch.zeros(self.num_envs, device=self.device)

    self._ghost_model = None
    self._ghost_color = np.array(cfg.viz.ghost_color, dtype=np.float32)
    self._clip_strike = self._build_clip_strikes()
    self._ignore_scrubber = False
    self._ignore_clip_menu = False

  def _clip_index(self, time_steps: torch.Tensor) -> torch.Tensor:
    """Clip id for each frame. ``clip_ends`` are exclusive."""
    ends = self.motion.clip_ends
    assert ends is not None
    return torch.bucketize(time_steps, ends, right=True).clamp(max=ends.numel() - 1)

  @property
  def style_z(self) -> torch.Tensor:
    """One-hot style of the clip each env is tracking. Zeros if the file has none."""
    styles = self.motion.clip_z
    if styles is None:
      return torch.zeros(self.num_envs, 3, device=self.device)
    return styles[self._clip_index(self.time_steps)]

  def kick_foot_is_left(self) -> torch.Tensor:
    """True when the clip being tracked swings the left foot."""
    feet = self.motion.clip_kick_foot
    if feet is None:
      return torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)
    return feet[self._clip_index(self.time_steps)].bool()

  @property
  def command(self) -> torch.Tensor:
    return torch.cat([self.joint_pos, self.joint_vel], dim=1)

  @property
  def joint_pos(self) -> torch.Tensor:
    return self.motion.joint_pos[self.time_steps]

  @property
  def joint_vel(self) -> torch.Tensor:
    return self.motion.joint_vel[self.time_steps]

  @property
  def body_pos_w(self) -> torch.Tensor:
    return (
      self.motion.body_pos_w[self.time_steps] + self._env.scene.env_origins[:, None, :]
    )

  @property
  def body_quat_w(self) -> torch.Tensor:
    return self.motion.body_quat_w[self.time_steps]

  @property
  def body_lin_vel_w(self) -> torch.Tensor:
    return self.motion.body_lin_vel_w[self.time_steps]

  @property
  def body_ang_vel_w(self) -> torch.Tensor:
    return self.motion.body_ang_vel_w[self.time_steps]

  @property
  def anchor_pos_w(self) -> torch.Tensor:
    return (
      self.motion.body_pos_w[self.time_steps, self.motion_anchor_body_index]
      + self._env.scene.env_origins
    )

  @property
  def anchor_quat_w(self) -> torch.Tensor:
    return self.motion.body_quat_w[self.time_steps, self.motion_anchor_body_index]

  @property
  def anchor_lin_vel_w(self) -> torch.Tensor:
    return self.motion.body_lin_vel_w[self.time_steps, self.motion_anchor_body_index]

  @property
  def anchor_ang_vel_w(self) -> torch.Tensor:
    return self.motion.body_ang_vel_w[self.time_steps, self.motion_anchor_body_index]

  @property
  def robot_joint_pos(self) -> torch.Tensor:
    return self.robot.data.joint_pos

  @property
  def robot_joint_vel(self) -> torch.Tensor:
    return self.robot.data.joint_vel

  @property
  def robot_body_pos_w(self) -> torch.Tensor:
    return self.robot.data.body_link_pos_w[:, self.body_indexes]

  @property
  def robot_body_quat_w(self) -> torch.Tensor:
    return self.robot.data.body_link_quat_w[:, self.body_indexes]

  @property
  def robot_body_lin_vel_w(self) -> torch.Tensor:
    return self.robot.data.body_link_lin_vel_w[:, self.body_indexes]

  @property
  def robot_body_ang_vel_w(self) -> torch.Tensor:
    return self.robot.data.body_link_ang_vel_w[:, self.body_indexes]

  @property
  def robot_anchor_pos_w(self) -> torch.Tensor:
    return self.robot.data.body_link_pos_w[:, self.robot_anchor_body_index]

  @property
  def robot_anchor_quat_w(self) -> torch.Tensor:
    return self.robot.data.body_link_quat_w[:, self.robot_anchor_body_index]

  @property
  def robot_anchor_lin_vel_w(self) -> torch.Tensor:
    return self.robot.data.body_link_lin_vel_w[:, self.robot_anchor_body_index]

  @property
  def robot_anchor_ang_vel_w(self) -> torch.Tensor:
    return self.robot.data.body_link_ang_vel_w[:, self.robot_anchor_body_index]

  def _update_metrics(self):
    self.metrics["error_anchor_pos"] = torch.norm(
      self.anchor_pos_w - self.robot_anchor_pos_w, dim=-1
    )
    self.metrics["error_anchor_rot"] = quat_error_magnitude(
      self.anchor_quat_w, self.robot_anchor_quat_w
    )
    self.metrics["error_anchor_lin_vel"] = torch.norm(
      self.anchor_lin_vel_w - self.robot_anchor_lin_vel_w, dim=-1
    )
    self.metrics["error_anchor_ang_vel"] = torch.norm(
      self.anchor_ang_vel_w - self.robot_anchor_ang_vel_w, dim=-1
    )

    self.metrics["error_body_pos"] = torch.norm(
      self.body_pos_relative_w - self.robot_body_pos_w, dim=-1
    ).mean(dim=-1)
    self.metrics["error_body_rot"] = quat_error_magnitude(
      self.body_quat_relative_w, self.robot_body_quat_w
    ).mean(dim=-1)

    self.metrics["error_body_lin_vel"] = torch.norm(
      self.body_lin_vel_w - self.robot_body_lin_vel_w, dim=-1
    ).mean(dim=-1)
    self.metrics["error_body_ang_vel"] = torch.norm(
      self.body_ang_vel_w - self.robot_body_ang_vel_w, dim=-1
    ).mean(dim=-1)

    self.metrics["error_joint_pos"] = torch.norm(
      self.joint_pos - self.robot_joint_pos, dim=-1
    )
    self.metrics["error_joint_vel"] = torch.norm(
      self.joint_vel - self.robot_joint_vel, dim=-1
    )

  def _adaptive_sampling(self, env_ids: torch.Tensor):
    episode_failed = self._env.termination_manager.terminated[env_ids]
    if torch.any(episode_failed):
      current_bin_index = torch.clamp(
        (self.time_steps * self.bin_count) // max(self.motion.time_step_total, 1),
        0,
        self.bin_count - 1,
      )
      fail_bins = current_bin_index[env_ids][episode_failed]
      self._current_bin_failed[:] = torch.bincount(fail_bins, minlength=self.bin_count)

    # Sample.
    sampling_probabilities = (
      self.bin_failed_count + self.cfg.adaptive_uniform_ratio / float(self.bin_count)
    )
    sampling_probabilities = self._smooth_bin_probs(sampling_probabilities)
    sampling_probabilities = sampling_probabilities / sampling_probabilities.sum()

    if self.motion.clip_ends is None:
      sampled_bins = torch.multinomial(
        sampling_probabilities, len(env_ids), replacement=True
      )
      self.time_steps[env_ids] = (
        (sampled_bins + sample_uniform(0.0, 1.0, (len(env_ids),), device=self.device))
        / self.bin_count
        * (self.motion.time_step_total - 1)
      ).long()
    else:
      self.time_steps[env_ids] = self._sample_frames_in_clips(
        len(env_ids), sampling_probabilities
      )

    # Update metrics.
    H = -(sampling_probabilities * (sampling_probabilities + 1e-12).log()).sum()
    H_norm = H / math.log(self.bin_count) if self.bin_count > 1 else 1.0
    pmax, imax = sampling_probabilities.max(dim=0)
    self.metrics["sampling_entropy"][:] = H_norm
    self.metrics["sampling_top1_prob"][:] = pmax
    self.metrics["sampling_top1_bin"][:] = imax.float() / self.bin_count

  def _smooth_bin_probs(self, probs: torch.Tensor) -> torch.Tensor:
    """Failure-bin smoothing. Multi-clip files are smoothed inside each clip."""
    ends = self.motion.clip_ends
    if ends is None:
      return self._conv_bins(probs)
    smoothed = torch.zeros_like(probs)
    starts = self.motion.clip_starts
    assert starts is not None
    for start, end in zip(starts.tolist(), ends.tolist(), strict=True):
      bin_lo, bin_hi = self._clip_bin_range(start, end)
      smoothed[bin_lo:bin_hi] = self._conv_bins(probs[bin_lo:bin_hi])
    return smoothed

  def _clip_bin_range(self, start: int, end: int) -> tuple[int, int]:
    """Bins covering frames ``[start, end)``, without sharing a bin across clips."""
    total = max(self.motion.time_step_total, 1)
    bin_lo = (start * self.bin_count) // total
    if end >= self.motion.time_step_total:
      bin_hi = self.bin_count
    else:
      bin_hi = (end * self.bin_count) // total
    return bin_lo, max(bin_hi, bin_lo + 1)

  def _conv_bins(self, probs: torch.Tensor) -> torch.Tensor:
    padded = torch.nn.functional.pad(
      probs.view(1, 1, -1),
      (0, self.cfg.adaptive_kernel_size - 1),  # Non-causal kernel
      mode="replicate",
    )
    return torch.nn.functional.conv1d(padded, self.kernel.view(1, 1, -1)).view(-1)

  def _sample_frames_in_clips(
    self, count: int, sampling_probabilities: torch.Tensor
  ) -> torch.Tensor:
    """Pick a kick, then a failure-biased frame inside that kick."""
    ends = self.motion.clip_ends
    starts = self.motion.clip_starts
    assert ends is not None and starts is not None
    clip_ids = self._sample_clip_ids(count)
    frames = torch.empty(count, dtype=torch.long, device=self.device)
    total = max(self.motion.time_step_total, 1)
    for clip_id in range(ends.numel()):
      selected = (clip_ids == clip_id).nonzero(as_tuple=False).view(-1)
      if selected.numel() == 0:
        continue
      start = int(starts[clip_id])
      end = int(ends[clip_id])
      bin_lo, bin_hi = self._clip_bin_range(start, end)
      clip_probs = sampling_probabilities[bin_lo:bin_hi]
      clip_probs = clip_probs / clip_probs.sum().clamp_min(1e-8)
      local_bins = torch.multinomial(clip_probs, selected.numel(), replacement=True)
      draw = sample_uniform(0.0, 1.0, (selected.numel(),), device=self.device)
      sampled = ((local_bins + bin_lo).float() + draw) / self.bin_count * (total - 1)
      frames[selected] = sampled.long().clamp(start, end - 1)
    return frames

  def _start_mode_frames(self, env_ids: torch.Tensor) -> torch.Tensor:
    """Play each kick from its own first frame, then the next kick."""
    ends = self.motion.clip_ends
    if ends is None:
      return torch.zeros(len(env_ids), dtype=torch.long, device=self.device)
    time_steps = self.time_steps[env_ids]
    at_end = torch.isin(time_steps, ends) | (time_steps >= self.motion.time_step_total)
    finished = (torch.bucketize(time_steps, ends, right=True) - 1).clamp(
      min=0, max=ends.numel() - 1
    )
    next_clip = (finished + 1) % ends.numel()
    starts = self.motion.clip_starts
    assert starts is not None
    restart = torch.zeros_like(time_steps)
    return torch.where(at_end, starts[next_clip], restart)

  def _prefix_sampling(self, env_ids: torch.Tensor) -> None:
    """Uniform clip, then a frame in the first ``start_fraction`` of that clip."""
    ends = self.motion.clip_ends
    starts = self.motion.clip_starts
    fraction = float(self.cfg.start_fraction)
    device = self.time_steps.device
    if ends is None or starts is None:
      window = max(int(self.motion.time_step_total * fraction), 1)
      self.time_steps[env_ids] = torch.randint(
        0, window, (len(env_ids),), device=device
      )
      return
    clip_ids = self._sample_clip_ids(len(env_ids))
    span = (ends - starts).clamp(min=1)
    window = (span.float() * fraction).long().clamp(min=1)
    draw = torch.rand(len(env_ids), device=device)
    self.time_steps[env_ids] = starts[clip_ids] + (draw * window[clip_ids].float()).long()

  def _uniform_sampling(self, env_ids: torch.Tensor):
    ends = self.motion.clip_ends
    starts = self.motion.clip_starts
    if ends is None or starts is None:
      self.time_steps[env_ids] = torch.randint(
        0, self.motion.time_step_total, (len(env_ids),), device=self.device
      )
    else:
      clip_ids = self._sample_clip_ids(len(env_ids))
      span = (ends - starts).clamp(min=1)
      draw = torch.rand(len(env_ids), device=self.device)
      self.time_steps[env_ids] = starts[clip_ids] + (draw * span[clip_ids]).long()
    self.metrics["sampling_entropy"][:] = 1.0  # Maximum entropy for uniform.
    self.metrics["sampling_top1_prob"][:] = 1.0 / self.bin_count
    self.metrics["sampling_top1_bin"][:] = 0.5  # No specific bin preference.

  def _sample_clip_ids(self, count: int) -> torch.Tensor:
    """Draw clip ids. ``left_clip_prob`` is the chance of a left-foot kick."""
    ends = self.motion.clip_ends
    assert ends is not None
    device = self.time_steps.device
    n_clips = int(ends.numel())
    prob = float(getattr(self.cfg, "left_clip_prob", 0.5))
    feet = getattr(self.motion, "clip_kick_foot", None)
    if feet is None or prob == 0.5:
      return torch.randint(0, n_clips, (count,), device=device)
    left = (feet == 1).nonzero(as_tuple=False).view(-1)
    right = (feet == 0).nonzero(as_tuple=False).view(-1)
    if left.numel() == 0 or right.numel() == 0:
      return torch.randint(0, n_clips, (count,), device=device)
    choose_left = torch.rand(count, device=device) < prob
    left_pick = left[torch.randint(0, int(left.numel()), (count,), device=device)]
    right_pick = right[torch.randint(0, int(right.numel()), (count,), device=device)]
    return torch.where(choose_left, left_pick, right_pick)

  def _write_reference_state_to_sim(
    self,
    env_ids: torch.Tensor,
    root_pos: torch.Tensor,
    root_ori: torch.Tensor,
    root_lin_vel: torch.Tensor,
    root_ang_vel: torch.Tensor,
    joint_pos: torch.Tensor,
    joint_vel: torch.Tensor,
  ) -> None:
    """Clip joint positions and write root + joint state to sim."""
    soft_limits = self.robot.data.soft_joint_pos_limits[env_ids]
    joint_pos = torch.clip(joint_pos, soft_limits[:, :, 0], soft_limits[:, :, 1])
    self.robot.write_joint_state_to_sim(joint_pos, joint_vel, env_ids=env_ids)

    root_state = torch.cat([root_pos, root_ori, root_lin_vel, root_ang_vel], dim=-1)
    self.robot.write_root_state_to_sim(root_state, env_ids=env_ids)
    self.robot.reset(env_ids=env_ids)

  def _resample_command(self, env_ids: torch.Tensor):
    if self.cfg.sampling_mode == "start":
      self.time_steps[env_ids] = self._start_mode_frames(env_ids)
    elif self.cfg.sampling_mode == "uniform":
      self._uniform_sampling(env_ids)
    elif self.cfg.sampling_mode == "prefix":
      self._prefix_sampling(env_ids)
    else:
      assert self.cfg.sampling_mode == "adaptive"
      self._adaptive_sampling(env_ids)

    root_pos = self.body_pos_w[env_ids, 0].clone()
    root_ori = self.body_quat_w[env_ids, 0].clone()
    root_lin_vel = self.body_lin_vel_w[env_ids, 0].clone()
    root_ang_vel = self.body_ang_vel_w[env_ids, 0].clone()

    range_list = [
      self.cfg.pose_range.get(key, (0.0, 0.0))
      for key in ["x", "y", "z", "roll", "pitch", "yaw"]
    ]
    ranges = torch.tensor(range_list, device=self.device)
    rand_samples = sample_uniform(
      ranges[:, 0], ranges[:, 1], (len(env_ids), 6), device=self.device
    )
    root_pos += rand_samples[:, 0:3]
    orientations_delta = quat_from_euler_xyz(
      rand_samples[:, 3], rand_samples[:, 4], rand_samples[:, 5]
    )
    root_ori = quat_mul(orientations_delta, root_ori)
    range_list = [
      self.cfg.velocity_range.get(key, (0.0, 0.0))
      for key in ["x", "y", "z", "roll", "pitch", "yaw"]
    ]
    ranges = torch.tensor(range_list, device=self.device)
    rand_samples = sample_uniform(
      ranges[:, 0], ranges[:, 1], (len(env_ids), 6), device=self.device
    )
    root_lin_vel += rand_samples[:, :3]
    root_ang_vel += rand_samples[:, 3:]

    joint_pos = self.joint_pos[env_ids].clone()
    joint_vel = self.joint_vel[env_ids]

    joint_pos += sample_uniform(
      lower=self.cfg.joint_position_range[0],
      upper=self.cfg.joint_position_range[1],
      size=joint_pos.shape,
      device=joint_pos.device,  # type: ignore
    )

    self._write_reference_state_to_sim(
      env_ids,
      root_pos,
      root_ori,
      root_lin_vel,
      root_ang_vel,
      joint_pos,
      joint_vel,
    )
    self._place_ball_at_clip_strike(env_ids)

  def _build_clip_strikes(self) -> torch.Tensor | None:
    """Estimated ball position of each clip, or None when placement is off."""
    if not self.cfg.place_ball_at_strike:
      return None
    ends = self.motion.clip_ends
    if ends is None:
      raise ValueError("place_ball_at_strike requires a motion file with clip_ends")
    height = self.cfg.strike_height
    if height is None:
      height = 0.11
    starts = torch.cat(
      [torch.zeros(1, dtype=torch.long, device=ends.device), ends[:-1]]
    )
    strikes = []
    for clip_id, (start, end) in enumerate(zip(starts.tolist(), ends.tolist(), strict=True)):
      left = (
        self.motion.clip_kick_foot is not None
        and int(self.motion.clip_kick_foot[clip_id]) == 1
      )
      foot_name = "left_foot_link" if left else self.cfg.strike_body_name
      foot_index = self.cfg.body_names.index(foot_name)
      foot = self.motion.body_pos_w[start:end, foot_index]
      strikes.append(
        estimate_clip_strike_positions(foot, torch.tensor([end - start]), height)[0]
      )
    strikes = torch.stack(strikes)
    names = self.motion.clip_names or [str(i) for i in range(strikes.shape[0])]
    for name, strike in zip(names, strikes, strict=True):
      print(
        f"[INFO] {name} ball "
        f"({strike[0]:.2f}, {strike[1]:.2f}, {strike[2]:.2f})"
      )
    return strikes

  def _place_ball_at_clip_strike(self, env_ids: torch.Tensor) -> None:
    """Put the ball on the estimated strike of the clip each env is playing."""
    if self._clip_strike is None or env_ids.numel() == 0:
      return
    name = self.cfg.ball_entity_name
    if name not in self._env.scene.entities:
      return
    ball: Entity = self._env.scene[name]
    clip_ids = self._clip_index(self.time_steps[env_ids])
    pose = ball.data.default_root_state[env_ids].clone()
    pose[:, 0:3] = self._clip_strike[clip_ids] + self._env.scene.env_origins[env_ids]
    pose[:, 7:13] = 0.0
    x_half, y_half = self.cfg.strike_pos_noise
    if x_half or y_half:
      pose[:, 0] += sample_uniform(-x_half, x_half, (len(env_ids),), device=self.device)
      pose[:, 1] += sample_uniform(-y_half, y_half, (len(env_ids),), device=self.device)
    vx_half, vy_half = self.cfg.strike_vel_noise
    if vx_half or vy_half:
      pose[:, 7] += sample_uniform(-vx_half, vx_half, (len(env_ids),), device=self.device)
      pose[:, 8] += sample_uniform(-vy_half, vy_half, (len(env_ids),), device=self.device)
    ball.write_root_state_to_sim(pose, env_ids=env_ids)
    reset_kick_shot(self._env, env_ids)

  def _clip_menu_labels(self) -> list[str]:
    assert self.motion.clip_ends is not None
    names = self.motion.clip_names or [
      f"clip {i}" for i in range(int(self.motion.clip_ends.numel()))
    ]
    labels = []
    for i, name in enumerate(names):
      short = name.removesuffix("_left").removesuffix("_stageii")
      styles = self.motion.clip_z
      style_names = self.motion.clip_z_names
      feet = self.motion.clip_kick_foot
      foot = ""
      if feet is not None:
        foot = " left" if int(feet[i]) == 1 else " right"
      if styles is not None and style_names is not None:
        style = style_names[int(torch.argmax(styles[i]))]
        short = f"{short}{foot} ({style})"
      labels.append(short)
    return labels

  def _strike_note(self, clip_id: int) -> str:
    assert self._clip_strike is not None
    strike = self._clip_strike[clip_id]
    return f"Ball ({strike[0]:.2f}, {strike[1]:.2f}, {strike[2]:.2f})"

  def update_relative_body_poses(self) -> None:
    """Recompute ``body_pos_relative_w`` and ``body_quat_relative_w``.

    Called after ``reset_to_frame`` so that termination checks that
    compare relative body positions see the correct state.
    """
    anchor_pos_w_repeat = self.anchor_pos_w[:, None, :].repeat(
      1, len(self.cfg.body_names), 1
    )
    anchor_quat_w_repeat = self.anchor_quat_w[:, None, :].repeat(
      1, len(self.cfg.body_names), 1
    )
    robot_anchor_pos_w_repeat = self.robot_anchor_pos_w[:, None, :].repeat(
      1, len(self.cfg.body_names), 1
    )
    robot_anchor_quat_w_repeat = self.robot_anchor_quat_w[:, None, :].repeat(
      1, len(self.cfg.body_names), 1
    )

    delta_pos_w = robot_anchor_pos_w_repeat
    delta_pos_w[..., 2] = anchor_pos_w_repeat[..., 2]
    delta_ori_w = yaw_quat(
      quat_mul(robot_anchor_quat_w_repeat, quat_inv(anchor_quat_w_repeat))
    )

    self.body_quat_relative_w = quat_mul(delta_ori_w, self.body_quat_w)
    self.body_pos_relative_w = delta_pos_w + quat_apply(
      delta_ori_w, self.body_pos_w - anchor_pos_w_repeat
    )

  def _envs_leaving_motion(self) -> torch.Tensor:
    """Envs whose clock just stepped off the current clip.

    A single clip resamples only past the last frame. A multi-clip file also
    resamples on the first frame of the next clip, so playback does not walk
    from one kick into an unrelated one.
    """
    past_end = self.time_steps >= self.motion.time_step_total
    clip_ends = self.motion.clip_ends
    if clip_ends is None:
      return torch.where(past_end)[0]
    at_clip_end = torch.isin(self.time_steps, clip_ends)
    return torch.where(past_end | at_clip_end)[0]

  def _update_command(self):
    self.time_steps += 1
    env_ids = self._envs_leaving_motion()
    if env_ids.numel() > 0:
      self._resample_command(env_ids)
      # _resample_command writes qpos/qvel but does not refresh derived
      # quantities; forward() so update_relative_body_poses reads the
      # post-teleport robot anchor instead of the stale pre-resample pose.
      self._env.sim.forward()

    self.update_relative_body_poses()

    if self.cfg.sampling_mode == "adaptive":
      self.bin_failed_count = (
        self.cfg.adaptive_alpha * self._current_bin_failed
        + (1 - self.cfg.adaptive_alpha) * self.bin_failed_count
      )
      self._current_bin_failed.zero_()

  def _debug_vis_impl(self, visualizer: DebugVisualizer) -> None:
    """Draw ghost robot or frames based on visualization mode."""
    env_indices = visualizer.get_env_indices(self.num_envs)
    if not env_indices:
      return

    if self.cfg.viz.mode == "ghost":
      if self._ghost_model is None:
        # Build a ghost model with only visual geoms visible. Collision geoms (nonzero
        # contype/conaffinity) get alpha=0 so the viewer's alpha filter excludes them.
        self._ghost_model = copy.deepcopy(self._env.sim.mj_model)
        for gi in range(self._ghost_model.ngeom):
          if (
            self._ghost_model.geom_contype[gi] != 0
            or self._ghost_model.geom_conaffinity[gi] != 0
          ):
            self._ghost_model.geom_rgba[gi, 3] = 0
          else:
            self._ghost_model.geom_rgba[gi] = self._ghost_color

      entity: Entity = self._env.scene[self.cfg.entity_name]
      indexing = entity.indexing
      free_joint_q_adr = indexing.free_joint_q_adr.cpu().numpy()
      joint_q_adr = indexing.joint_q_adr.cpu().numpy()

      for batch in env_indices:
        qpos = np.zeros(self._env.sim.mj_model.nq)
        qpos[free_joint_q_adr[0:3]] = self.body_pos_w[batch, 0].cpu().numpy()
        qpos[free_joint_q_adr[3:7]] = self.body_quat_w[batch, 0].cpu().numpy()
        qpos[joint_q_adr] = self.joint_pos[batch].cpu().numpy()

        visualizer.add_ghost_mesh(
          qpos,
          model=self._ghost_model,
          label=f"ghost_{batch}",
        )

    elif self.cfg.viz.mode == "frames":
      for batch in env_indices:
        desired_body_pos = self.body_pos_w[batch].cpu().numpy()
        desired_body_quat = self.body_quat_w[batch]
        desired_body_rotm = matrix_from_quat(desired_body_quat).cpu().numpy()

        current_body_pos = self.robot_body_pos_w[batch].cpu().numpy()
        current_body_quat = self.robot_body_quat_w[batch]
        current_body_rotm = matrix_from_quat(current_body_quat).cpu().numpy()

        for i, body_name in enumerate(self.cfg.body_names):
          visualizer.add_frame(
            position=desired_body_pos[i],
            rotation_matrix=desired_body_rotm[i],
            scale=0.08,
            label=f"desired_{body_name}_{batch}",
            axis_colors=_DESIRED_FRAME_COLORS,
          )
          visualizer.add_frame(
            position=current_body_pos[i],
            rotation_matrix=current_body_rotm[i],
            scale=0.12,
            label=f"current_{body_name}_{batch}",
          )

        desired_anchor_pos = self.anchor_pos_w[batch].cpu().numpy()
        desired_anchor_quat = self.anchor_quat_w[batch]
        desired_rotation_matrix = matrix_from_quat(desired_anchor_quat).cpu().numpy()
        visualizer.add_frame(
          position=desired_anchor_pos,
          rotation_matrix=desired_rotation_matrix,
          scale=0.1,
          label=f"desired_anchor_{batch}",
          axis_colors=_DESIRED_FRAME_COLORS,
        )

        current_anchor_pos = self.robot_anchor_pos_w[batch].cpu().numpy()
        current_anchor_quat = self.robot_anchor_quat_w[batch]
        current_rotation_matrix = matrix_from_quat(current_anchor_quat).cpu().numpy()
        visualizer.add_frame(
          position=current_anchor_pos,
          rotation_matrix=current_rotation_matrix,
          scale=0.15,
          label=f"current_anchor_{batch}",
        )

  def create_gui(
    self,
    name: str,
    server: viser.ViserServer,
    get_env_idx: Callable[[], int],
    on_change: Callable[[], None] | None = None,
    request_action: Callable[[str, Any], None] | None = None,
  ) -> None:
    """Create motion scrubber controls in the Viser viewer."""
    max_frame = int(self.motion.time_step_total) - 1

    with server.gui.add_folder(name.capitalize()):
      scrubber = server.gui.add_slider(
        "Frame",
        min=0,
        max=max_frame,
        step=1,
        initial_value=0,
      )

      @scrubber.on_update
      def _(_) -> None:
        if self._ignore_scrubber:
          return
        idx = get_env_idx()
        self.time_steps[idx] = int(scrubber.value)
        if on_change is not None:
          on_change()

      all_envs_cb = server.gui.add_checkbox("All envs", initial_value=True)
      start_btn = server.gui.add_button("Start Here")

      @start_btn.on_click
      def _(_) -> None:
        if request_action is not None:
          request_action(
            "CUSTOM",
            {"type": "gui_reset", "all_envs": all_envs_cb.value},
          )

      if self._clip_strike is not None and self.motion.clip_starts is not None:
        labels = self._clip_menu_labels()
        clip_menu = server.gui.add_dropdown(
          "Clip",
          options=labels,
          initial_value=labels[0],
        )
        strike_note = server.gui.add_markdown(self._strike_note(0))
        clip_buttons = server.gui.add_button_group(
          "",
          options=["Previous", "Next"],
        )

        def _select_clip(clip_id: int) -> None:
          assert self.motion.clip_starts is not None
          count = len(labels)
          clip_id = clip_id % count
          frame = int(self.motion.clip_starts[clip_id])
          self._ignore_scrubber = True
          self._ignore_clip_menu = True
          scrubber.value = frame
          clip_menu.value = labels[clip_id]
          strike_note.content = self._strike_note(clip_id)
          self._ignore_scrubber = False
          self._ignore_clip_menu = False
          if request_action is not None:
            request_action(
              "CUSTOM",
              {"type": "gui_reset", "all_envs": all_envs_cb.value},
            )

        @clip_menu.on_update
        def _(_) -> None:
          if self._ignore_clip_menu:
            return
          _select_clip(labels.index(clip_menu.value))

        @clip_buttons.on_click
        def _(event) -> None:
          current = labels.index(clip_menu.value)
          step = -1 if event.target.value == "Previous" else 1
          _select_clip(current + step)

        @scrubber.on_update
        def _sync_clip_note(_) -> None:
          if self._ignore_scrubber or self.motion.clip_ends is None:
            return
          clip_id = int(self._clip_index(torch.tensor([int(scrubber.value)])))
          self._ignore_clip_menu = True
          clip_menu.value = labels[clip_id]
          strike_note.content = self._strike_note(clip_id)
          self._ignore_clip_menu = False

    self._scrubber_handles = (scrubber, all_envs_cb, start_btn)
    self._set_scrubber_disabled(True)

  def _set_scrubber_disabled(self, disabled: bool) -> None:
    """Enable or disable the motion scrubber GUI controls."""
    for handle in self._scrubber_handles:
      handle.disabled = disabled

  def on_viewer_pause(self, paused: bool) -> None:
    if hasattr(self, "_scrubber_handles"):
      self._set_scrubber_disabled(not paused)

  def apply_gui_reset(self, env_ids: torch.Tensor) -> bool:
    if not hasattr(self, "_scrubber_handles"):
      return False
    frame = int(self._scrubber_handles[0].value)
    self.reset_to_frame(env_ids, frame)
    self.update_relative_body_poses()
    return True

  def reset_to_frame(self, env_ids: torch.Tensor, frame: int) -> None:
    """Reset to exact reference state at a specific frame.

    Like ``_resample_command`` but deterministic: no random
    perturbations to pose, velocity, or joint positions.
    """
    self.time_steps[env_ids] = frame
    self._write_reference_state_to_sim(
      env_ids,
      self.body_pos_w[env_ids, 0],
      self.body_quat_w[env_ids, 0],
      self.body_lin_vel_w[env_ids, 0],
      self.body_ang_vel_w[env_ids, 0],
      self.joint_pos[env_ids],
      self.joint_vel[env_ids],
    )
    self._place_ball_at_clip_strike(env_ids)


@dataclass(kw_only=True)
class MotionCommandCfg(CommandTermCfg):
  motion_file: str
  anchor_body_name: str
  body_names: tuple[str, ...]
  entity_name: str
  pose_range: dict[str, tuple[float, float]] = field(default_factory=dict)
  velocity_range: dict[str, tuple[float, float]] = field(default_factory=dict)
  joint_position_range: tuple[float, float] = (-0.52, 0.52)
  adaptive_kernel_size: int = 1
  adaptive_lambda: float = 0.8
  adaptive_uniform_ratio: float = 0.1
  adaptive_alpha: float = 0.001
  sampling_mode: Literal["adaptive", "uniform", "start", "prefix"] = "adaptive"
  # Fraction of each clip used by ``sampling_mode="prefix"``.
  start_fraction: float = 0.05
  # Chance a sampled clip swings the left foot. 0.5 keeps the two feet equal.
  left_clip_prob: float = 0.5
  # Reset the ball onto each clip's estimated right-foot strike.
  place_ball_at_strike: bool = False
  strike_body_name: str = "right_foot_link"
  ball_entity_name: str = "ball"
  strike_height: float | None = None
  # Half-width of the uniform jitter added on top of the strike. Zero is exact.
  strike_pos_noise: tuple[float, float] = (0.0, 0.0)
  strike_vel_noise: tuple[float, float] = (0.0, 0.0)

  @dataclass
  class VizCfg:
    mode: Literal["ghost", "frames"] = "ghost"
    ghost_color: tuple[float, float, float, float] = (0.5, 0.7, 0.5, 0.5)

  viz: VizCfg = field(default_factory=VizCfg)

  def build(self, env: ManagerBasedRlEnv) -> MotionCommand:
    return MotionCommand(self, env)
