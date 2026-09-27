"""Recipe C: frozen Walk enter/exit around Kick PPO (concurrent FSM).

Every train step muxes actions by phase:
  APPROACH / EXIT → Walk ``9950`` (rewards zeroed; Kick actions unused in buffer)
  KICK → student Kick policy (normal Near rewards)

Exit: after settle and ball≥``exit_ball_min_m``, hold Walk for T∈[0.5,1]s;
survive → bonus + done; fall → penalty + done. Attributed on that Kick transition
window (Walk steps stay low-advantage via zero reward until terminal).
"""

from __future__ import annotations

from dataclasses import dataclass

import torch
from tensordict import TensorDict

from mjlab.rl.vecenv_wrapper import RslRlVecEnvWrapper
from mjlab.tasks.kick.mdp.ball_phase import ensure_ball_phase_updated
from mjlab.tasks.kick.mdp.walk_handoff import (
  DEFAULT_WALK_CKPT,
  DEFAULT_WALK_TASK,
  KICK_LEG_JOINTS,
  PHASE_APPROACH,
  PHASE_EXIT,
  PHASE_KICK,
  WALK_JOINTS,
  WALK_UPPER_JOINTS,
  WalkHandoffKit,
  load_walk_inference_policy,
  resolve_scale_dict,
)
from mjlab.tasks.registry import load_env_cfg


@dataclass
class FrozenWalkHandoffCfg:
  walk_task: str = DEFAULT_WALK_TASK
  walk_checkpoint: str = str(DEFAULT_WALK_CKPT)
  kick_enter_m: float = 0.55
  """Distance band for enter hold (match play Setup B)."""
  enter_facing_rad: float = 0.40
  enter_tilt_max_rad: float = 0.35
  enter_speed_max: float = 0.55
  enter_stand_s: float = 0.30
  approach_speed: float = 0.9
  approach_yaw_gain: float = 2.0
  approach_turn_speed: float = 1.2
  settle_time_s: float = 1.0
  exit_ball_min_m: float = 0.5
  exit_hold_s_range: tuple[float, float] = (0.5, 1.0)
  exit_ok_bonus: float = 2.0
  exit_fall_penalty: float = -5.0
  exit_vx: float = 0.0
  fall_min_height: float = 0.40
  fall_tilt_max_rad: float = 0.85


class FrozenWalkHandoffWrapper(RslRlVecEnvWrapper):
  """Wrap Kick Near env with frozen Walk approach/exit FSM."""

  def __init__(
    self,
    env,
    *,
    clip_actions: float | None = None,
    cfg: FrozenWalkHandoffCfg | None = None,
    kick_action_scale: float | dict[str, float] | None = None,
  ) -> None:
    # Parent resets once; defer FSM until Walk policy is loaded.
    self._handoff_cfg = cfg or FrozenWalkHandoffCfg()
    self._kick_action_scale = kick_action_scale
    self._walk_shell: RslRlVecEnvWrapper | None = None
    self._handoff_ready = False
    super().__init__(env, clip_actions=clip_actions)
    self._init_handoff()
    self._handoff_ready = True
    self._on_env_reset(
      torch.ones(self.num_envs, dtype=torch.bool, device=self.device)
    )

  def reset(self) -> tuple[TensorDict, dict]:
    obs, extras = super().reset()
    if self._handoff_ready:
      self._on_env_reset(
        torch.ones(self.num_envs, dtype=torch.bool, device=self.device)
      )
      self._prev_ep_len = self.unwrapped.episode_length_buf.clone()
    return obs, extras

  def step(
    self, actions: torch.Tensor
  ) -> tuple[TensorDict, torch.Tensor, torch.Tensor, dict]:
    if not self._handoff_ready:
      return super().step(actions)
    self._update_phase_pre_step()
    mixed = self._mux_actions(actions)
    obs, rew, dones, extras = super().step(mixed)
    rew, dones, force_reset = self._finish_exit_and_zero_walk_rew(rew, dones)

    if bool(force_reset.any()):
      ids = force_reset.nonzero(as_tuple=False).flatten()
      self.unwrapped.reset(env_ids=ids)
      obs = self.get_observations()
      self._on_env_reset(force_reset)

    # Sync phase after auto-reset inside parent step.
    if bool((dones > 0).any()):
      self._on_env_reset(dones > 0)
    self._prev_ep_len = self.unwrapped.episode_length_buf.clone()

    self._log_metrics(extras)
    return obs, rew, dones, extras
  def _init_handoff(self) -> None:
    cfg = self._handoff_cfg
    raw = self.unwrapped
    device = str(raw.device)
    print(
      f"[INFO] Recipe C frozen Walk handoff: ckpt={cfg.walk_checkpoint}  "
      f"enter≤{cfg.kick_enter_m}m  exit_ball≥{cfg.exit_ball_min_m}m  "
      f"exit_hold={cfg.exit_hold_s_range}"
    )
    walk_policy, walk_shell = load_walk_inference_policy(
      walk_task=cfg.walk_task,
      walk_checkpoint=cfg.walk_checkpoint,
      device=device,
    )
    self._walk_shell = walk_shell
    self.walk_policy = walk_policy

    walk_env_cfg = load_env_cfg(cfg.walk_task, play=True)
    walk_scale_full = resolve_scale_dict(
      walk_env_cfg.actions["joint_pos"].scale, WALK_JOINTS
    )
    if self._kick_action_scale is None:
      kick_scale_cfg = raw.cfg.actions["joint_pos"].scale
    else:
      kick_scale_cfg = self._kick_action_scale
    kick_scale = resolve_scale_dict(kick_scale_cfg, KICK_LEG_JOINTS)
    walk_leg_indices = torch.tensor(
      [WALK_JOINTS.index(n) for n in KICK_LEG_JOINTS], dtype=torch.long
    )
    walk_upper_indices = torch.tensor(
      [WALK_JOINTS.index(n) for n in WALK_UPPER_JOINTS],
      dtype=torch.long,
      device=raw.device,
    )
    self.kit = WalkHandoffKit(
      raw_env=raw,
      walk_scale_full=walk_scale_full,
      kick_scale=kick_scale,
      walk_leg_indices=walk_leg_indices,
      walk_upper_indices=walk_upper_indices,
      enter_facing_rad=cfg.enter_facing_rad,
      enter_tilt_max_rad=cfg.enter_tilt_max_rad,
      enter_speed_max=cfg.enter_speed_max,
      approach_speed=cfg.approach_speed,
      approach_yaw_gain=cfg.approach_yaw_gain,
      approach_turn_speed=cfg.approach_turn_speed,
      fall_min_height=cfg.fall_min_height,
      fall_tilt_max_rad=cfg.fall_tilt_max_rad,
    )
    n = raw.num_envs
    device_t = raw.device
    self._phase = torch.full(
      (n,), PHASE_APPROACH, dtype=torch.long, device=device_t
    )
    self._enter_hold_s = torch.zeros(n, device=device_t)
    self._exit_hold_s = torch.zeros(n, device=device_t)
    self._exit_hold_target_s = torch.zeros(n, device=device_t)
    self._prev_ep_len = raw.episode_length_buf.clone()
    # Metrics (EMA-ish counters for logging).
    self._metric_enter = 0.0
    self._metric_exit_ok = 0.0
    self._metric_exit_fall = 0.0
    self._metric_n = 0.0

  def close(self) -> None:
    if self._walk_shell is not None:
      self._walk_shell.close()
      self._walk_shell = None
    return super().close()

  def _sample_exit_hold(self, env_ids: torch.Tensor) -> None:
    lo, hi = self._handoff_cfg.exit_hold_s_range
    n = env_ids.numel()
    if n == 0:
      return
    u = torch.rand(n, device=self.unwrapped.device)
    self._exit_hold_target_s[env_ids] = lo + (hi - lo) * u
    self._exit_hold_s[env_ids] = 0.0

  def _on_env_reset(self, reset: torch.Tensor) -> None:
    if not bool(reset.any()):
      return
    self._phase[reset] = PHASE_APPROACH
    self.kit.last_walk_action[reset] = 0.0
    self._enter_hold_s[reset] = 0.0
    self._exit_hold_s[reset] = 0.0
    self._exit_hold_target_s[reset] = 0.0

  def _update_phase_pre_step(self) -> None:
    """Advance FSM using current state; set twist / walk-mode for this step."""
    raw = self.unwrapped
    cfg = self._handoff_cfg
    dt = float(raw.step_dt)
    ep = raw.episode_length_buf
    reset = ep < self._prev_ep_len
    self._prev_ep_len = ep.clone()
    self._on_env_reset(reset)

    state = ensure_ball_phase_updated(raw, ball_cfg_name="ball")
    assert state.kick_detected is not None
    assert state.time_since_kick_s is not None
    dist = self.kit.ball_dist()
    gates_ok, _ = self.kit.enter_gates()
    in_band = dist <= cfg.kick_enter_m

    approaching = self._phase == PHASE_APPROACH
    holding = approaching & in_band
    ready = holding & gates_ok
    self._enter_hold_s = torch.where(
      ready, self._enter_hold_s + dt, torch.zeros_like(self._enter_hold_s)
    )
    to_kick = ready & (self._enter_hold_s >= cfg.enter_stand_s)
    if bool(to_kick.any()):
      self._phase[to_kick] = PHASE_KICK
      self._enter_hold_s[to_kick] = 0.0
      # Kick horizon starts at handoff.
      raw.episode_length_buf[to_kick] = 0
      self._prev_ep_len[to_kick] = 0
      self._metric_enter += float(to_kick.sum().item())
      self.kit.free_arms(to_kick.nonzero(as_tuple=False).flatten())

    settled = state.kick_detected & (
      state.time_since_kick_s >= cfg.settle_time_s
    )
    ball_away = dist >= cfg.exit_ball_min_m
    to_exit = (self._phase == PHASE_KICK) & settled & ball_away
    if bool(to_exit.any()):
      ids = to_exit.nonzero(as_tuple=False).flatten()
      self._phase[to_exit] = PHASE_EXIT
      self._sample_exit_hold(ids)
      self.kit.set_twist(
        ids,
        cfg.exit_vx,
        0.0,
        0.0,
        standing=abs(cfg.exit_vx) < 1e-3,
      )
      self.kit.last_walk_action[to_exit] = 0.0

    # Teacher off whenever Walk owns the body.
    walk_own = self._phase != PHASE_KICK
    raw._setup_b_walk_mode = walk_own

    kick_ids = (self._phase == PHASE_KICK).nonzero(as_tuple=False).flatten()
    self.kit.free_arms(kick_ids)

    approach_ids = (self._phase == PHASE_APPROACH).nonzero(
      as_tuple=False
    ).flatten()
    self.kit.drive_approach(approach_ids, stand_hold=holding)

  def _mux_actions(self, kick_actions: torch.Tensor) -> torch.Tensor:
    use_walk = self._phase != PHASE_KICK
    if not bool(use_walk.any()):
      return kick_actions
    walk_obs = self.kit.build_walk_obs()
    with torch.no_grad():
      a_walk = self.walk_policy(walk_obs)
    self.kit.last_walk_action = torch.where(
      use_walk.unsqueeze(-1), a_walk, self.kit.last_walk_action
    )
    walk_ids = use_walk.nonzero(as_tuple=False).flatten()
    self.kit.apply_walk_upper_body(a_walk, walk_ids)
    a_from_walk = self.kit.walk_actions_to_kick(a_walk)
    return torch.where(use_walk.unsqueeze(-1), a_from_walk, kick_actions)

  def _finish_exit_and_zero_walk_rew(
    self, rew: torch.Tensor, dones: torch.Tensor
  ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Returns ``(rew, dones, force_reset)`` — force_reset needs env.reset."""
    cfg = self._handoff_cfg
    dt = float(self.unwrapped.step_dt)
    force_reset = torch.zeros(
      self.num_envs, dtype=torch.bool, device=self.device
    )
    exiting = self._phase == PHASE_EXIT
    if bool(exiting.any()):
      self._exit_hold_s = torch.where(
        exiting, self._exit_hold_s + dt, self._exit_hold_s
      )
      env_done = exiting & (dones > 0)
      fell = (exiting & self.kit.is_fallen()) | env_done
      held = (
        exiting
        & (self._exit_hold_s >= self._exit_hold_target_s)
        & ~fell
      )
      if bool(fell.any()):
        rew = rew.clone()
        rew[fell] = rew[fell] + cfg.exit_fall_penalty
        dones = dones.clone()
        dones[fell] = 1
        self._metric_exit_fall += float(fell.sum().item())
        # Env-done falls already auto-reset; others need an explicit reset.
        force_reset = force_reset | (fell & ~env_done)
        self._phase[fell] = PHASE_APPROACH
      if bool(held.any()):
        rew = rew.clone()
        rew[held] = rew[held] + cfg.exit_ok_bonus
        dones = dones.clone()
        dones[held] = 1
        self._metric_exit_ok += float(held.sum().item())
        force_reset = force_reset | held
        self._phase[held] = PHASE_APPROACH

    # Zero shaping during Walk phases (keep exit bonus/penalty on done steps).
    still_walk = self._phase != PHASE_KICK
    zero_mask = still_walk & (dones == 0)
    if bool(zero_mask.any()):
      rew = rew.clone()
      rew[zero_mask] = 0.0

    approaching = self._phase == PHASE_APPROACH
    if bool(approaching.any()):
      self.unwrapped.episode_length_buf[approaching] = 0
      self._prev_ep_len[approaching] = 0

    return rew, dones, force_reset

  def _log_metrics(self, extras: dict) -> None:
    self._metric_n += 1.0
    log = extras.setdefault("log", {})
    n = max(self._metric_n, 1.0)
    log["Metrics/walk_enter_count"] = self._metric_enter / n
    log["Metrics/walk_exit_ok"] = self._metric_exit_ok / n
    log["Metrics/walk_exit_fall"] = self._metric_exit_fall / n
    log["Metrics/walk_phase_approach"] = (
      self._phase == PHASE_APPROACH
    ).float().mean()
    log["Metrics/walk_phase_kick"] = (self._phase == PHASE_KICK).float().mean()
    log["Metrics/walk_phase_exit"] = (self._phase == PHASE_EXIT).float().mean()
