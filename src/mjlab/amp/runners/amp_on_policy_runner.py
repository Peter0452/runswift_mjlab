from __future__ import annotations

import os
import time
from dataclasses import dataclass, field

import torch
from rsl_rl.utils import check_nan

from mjlab.amp.config import DEFAULT_AMP_DATASET, AmpDiscriminatorCfg
from mjlab.amp.runners.amp_support import AmpRunner
from mjlab.rl import (
  MjlabOnPolicyRunner,
  RslRlOnPolicyRunnerCfg,
  RslRlPpoAlgorithmCfg,
  RslRlVecEnvWrapper,
)


@dataclass
class AmpRslRlPpoAlgorithmCfg(RslRlPpoAlgorithmCfg):
  """Configuration for AMP PPO algorithm."""

  class_name: str = "mjlab.amp.algorithms.amp_ppo:AmpPPO"
  """Fully qualified class name for the AMP PPO implementation."""
  caps_temporal_coef: float = 0.0
  """CAPS temporal smoothness of the deterministic action (0 = off)."""
  caps_spatial_coef: float = 0.0
  """CAPS spatial smoothness: action change under input noise (0 = off)."""
  caps_spatial_sigma: float = 0.05
  """Input noise for the spatial term, in normalized-observation units."""
  caps_near_ball_scale: float = 1.0
  """CAPS weight on samples whose actor ball estimate is near (kick tasks)."""
  caps_near_ball_dist: float = 0.8
  """Distance (m) under which a sample counts as near the ball."""
  caps_ball_slot: int = 72
  """Actor observation index of the ball x (y follows)."""
  imitation_coef: float = 0.0
  """Teacher imitation (kick tasks): MSE weight on near-ball teacher actions (0 = off)."""
  imitation_decay_updates: int = 1000
  """Updates over which the imitation weight decays linearly to 0."""
  multi_critic_alphas: tuple[float, ...] | None = None
  """APEX multi-critic mix. ``None`` keeps one critic. ``(0.5, 0.5)`` is motion style, then task."""


@dataclass
class AmpRslRlMuonPpoAlgorithmCfg(AmpRslRlPpoAlgorithmCfg):
  """AMP PPO with Muon actor/critic updates and Adam discriminator updates."""

  class_name: str = "mjlab.amp.algorithms.amp_ppo:AmpPPO"
  use_muon: bool = True
  muon_weight_decay: float = 0.0
  muon_momentum: float = 0.95
  muon_ns_steps: int = 5


@dataclass
class AmpOnPolicyRunnerCfg(RslRlOnPolicyRunnerCfg):
  """Configuration for the AMP on-policy runner."""

  dataset_root: str = DEFAULT_AMP_DATASET
  """Local motion path or Hugging Face dataset ID (``namespace/repo``)."""
  warm_start: bool = False
  """With ``resume``, load only the actor, critic and discriminator weights from the checkpoint.

    Optimizer state and the iteration counter start fresh, so a checkpoint can seed a run with a
    different optimizer (e.g. Adam -> Muon) or a different training setup. Without this flag,
    ``resume`` restores everything and the run continues where it left off.
    """
  class_name: str = "AmpOnPolicyRunner"
  """The runner class name. Default is AmpOnPolicyRunner."""
  discriminator: AmpDiscriminatorCfg = field(default_factory=AmpDiscriminatorCfg)
  """The configuration for the AMP discriminator."""
  style_reward_weight: float = 0.5
  """The weight of the style reward."""
  decap: bool = False
  """Blend policy joint targets toward the AMP clips with an exponential decay."""
  decap_source: str = "kick"
  """``kick`` plays the kick takes. ``loader`` plays this task's AMP clips (walk)."""
  decap_gamma: float = 0.99
  """Base of the exponential DecAP schedule (APEX ``gamma``)."""
  decap_k: float = 100.0
  """Time constant of the exponential DecAP schedule (APEX ``k``)."""
  amp_replay_buffer_size: int = 200_000
  """The size of the AMP replay buffer."""
  amp_replay_insert_size: int = 1_000
  """Samples inserted per rollout once the AMP replay buffer is full."""
  num_amp_obs_steps: int = 10
  """Number of sequential observation frames in each discriminator sample."""
  kick_teacher_checkpoint: str | None = None
  """Dribble kick mode (v23): a kick-loop checkpoint whose actor is imitated in
  kick windows near the ball (with ``algorithm.imitation_coef`` > 0)."""
  kick_teacher_dist: float | None = None
  """Imitate the kick teacher within this ball distance (m) before the kick;
  None = KICK_TEACHER_DIST (1.5 m). v24 uses the whole window (approach too)."""
  kick_teacher_max_offset_deg: float | None = None
  """v36: imitate the kick teacher only in kick windows whose direction is at
  most this far (deg) off the robot-to-ball line (straight power kicks)."""
  kick_teacher_arms: bool = False
  """Also imitate the teacher's arms (its balance through the kick), not only
  the legs (v24)."""
  kick_takeover_prob: float | None = None
  """v43: with kick_teacher_bhuman_dist, B-Human *executes* the legs (instead of
  only labelling them) in this share of angled kick windows near the ball; the
  executed steps feed imitation only (zero advantage). Decays to 0 over
  kick_takeover_decay updates."""
  kick_takeover_decay: int = 3000
  kick_teacher_bhuman_dist: float | None = None
  """v41: B-Human's kick policy (K1_kick_inner, via the play_bhuman_kick adapter)
  is the teacher in the angled kick windows (beyond kick_teacher_max_offset_deg)
  within this ball distance (m); its legs only (arms stay the kick-loop's)."""
  extra_reward_group: tuple[str, ...] | None = None
  """v27: env reward terms that form a third reward group (own critic head and
  ``multi_critic_alphas`` entry), taken out of the task group; e.g. the
  dribble's kick terms."""
  amp_cond_free_prob: float = 0.25
  """With an ``amp_cond`` observation group: share of expert samples given the
  all-zero ("free") condition, as policy samples get before ball control."""
  amp_speed_mass: tuple[tuple[float, float], ...] | None = None
  """With ``amp_cond``: expert sampling mass per travel-speed bin, as
  (upper speed m/s, mass) pairs in ascending order; the clip weights only
  share mass within a bin. None keeps the clip weights."""
  algorithm: AmpRslRlPpoAlgorithmCfg | AmpRslRlMuonPpoAlgorithmCfg = field(
    default_factory=AmpRslRlPpoAlgorithmCfg
  )
  """The algorithm configuration. Defaults to the AMP PPO implementation."""
  speed_factor: float = 1.0
  """Playback speed multiplier for motion data (`>1` faster, `<1` slower)."""
  dataset_weights: list[float] | None = None
  """The weights for each dataset in the motion dataset. If None, all datasets are weighted equally."""
  dataset_augmentations: list[dict[str, object]] | None = None
  """Additional AMP motion augmentations applied per clip (for example: mirror, speed modifiers)."""
  dataset_transform: str | None = None
  """Optional ``module.path:function`` remapping each clip onto the robot's joint layout."""
  obs_groups: dict[str, tuple[str, ...]] = field(
    default_factory=lambda: {
      "actor": ("actor",),
      "critic": ("critic",),
      "amp": ("amp",),
    }
  )
  """The observation groups for the runner. Include AMP obs group so resolve_obs_groups picks it up when present."""


class AmpOnPolicyRunner(AmpRunner, MjlabOnPolicyRunner):
  env: RslRlVecEnvWrapper

  def __init__(
    self,
    env: RslRlVecEnvWrapper,
    train_cfg: dict,
    log_dir: str | None = None,
    device: str = "cpu",
  ) -> None:
    if "amp" not in train_cfg["obs_groups"]:
      raise ValueError("AMP runner requires an 'amp' observation group.")
    train_cfg.setdefault("algorithm", {})
    # RSL-RL's logger expects this key to exist.
    train_cfg["algorithm"].setdefault("rnd_cfg", None)

    super().__init__(env, train_cfg=train_cfg, log_dir=log_dir, device=device)
    self._setup_amp_support(train_cfg, require_amp_group=True)

  def load(
    self,
    path: str,
    load_cfg: dict | None = None,
    strict: bool = True,
    map_location: str | None = None,
  ) -> dict:
    if load_cfg is None and self.cfg.get("warm_start", False):
      print(
        "[INFO] Warm start: loading actor, critic and discriminator weights only; "
        "optimizer state and iteration counter start fresh."
      )
      load_cfg = {"actor": True, "critic": True}
    infos = super().load(
      path, load_cfg=load_cfg, strict=strict, map_location=map_location
    )
    # Play only loads weights. The clip spring, root playback, and strike-ball
    # snap are training aids; ``learn`` attaches them. A deployed policy does
    # not have them, so play must not either.
    return infos

  def _attach_decap(self) -> None:
    """Point the kick action at AMP-clip joint targets, if DecAP is enabled."""
    if not self.cfg.get("decap", False):
      return
    from k1.tasks.velocity.mdp.decap import DecapReference, from_kick_clips

    action = self.env.unwrapped.action_manager.get_term("joint_pos")
    gamma = float(self.cfg.get("decap_gamma", 0.99))
    k = float(self.cfg.get("decap_k", 100.0))
    names = list(action.target_names)
    if self.cfg.get("decap_source", "kick") == "loader":
      reference = DecapReference.from_loader(
        self.alg.amp.amp_loader, names, self.env.num_envs, gamma=gamma, k=k
      )
    else:
      try:
        reference = from_kick_clips(
          names, self.env.num_envs, gamma=gamma, k=k, device=self.device
        )
      except FileNotFoundError:
        reference = DecapReference.from_loader(
          self.alg.amp.amp_loader, names, self.env.num_envs, gamma=gamma, k=k
        )
    reference.set_decay_steps(
      self.current_learning_iteration * int(self.cfg["num_steps_per_env"])
    )
    env = self.env.unwrapped
    env.decap = reference
    if reference.ball_pos is not None and hasattr(
      env.command_manager.get_term("twist"), "_apply_decap_spawn"
    ):
      import torch

      cmd = env.command_manager.get_term("twist")
      cmd._apply_decap_spawn(
        torch.arange(env.num_envs, device=self.device), move_robot=True
      )
      env.scene.write_data_to_sim()
      env.sim.forward()
    if reference.body_vel is not None:
      import torch

      all_ids = torch.arange(env.num_envs, device=self.device)
      env.event_manager.apply(
        mode="reset",
        env_ids=all_ids,
        global_env_step_count=env.common_step_counter,
      )
      reference.synced.zero_()
      env.scene.write_data_to_sim()
      env.sim.forward()
      cmd = env.command_manager.get_term("twist")
      if hasattr(cmd, "_resample_command"):
        cmd._resample_command(all_ids)
        cmd._update_command()
    mixed = ""
    if reference.clip_mixed is not None:
      mixed = f", mixed {int(reference.clip_mixed.sum())}"
    print(
      f"[INFO] DecAP: {reference.joint_pos.shape[0]} frames, "
      f"{int(reference.clip_lengths.shape[0])} clips{mixed}, "
      f"factor {reference.factor:.4f} at step {reference.decay_steps}"
    )

  def _on_learn_start(self) -> None:
    """Attach DecAP playback before the first rollout, when it is enabled."""
    self._attach_decap()

  def _on_policy_update(self, it: int) -> None:
    """Hook for subclasses: after each policy update."""

  # override the learn method to include AMP loop, most of the code is same as parent
  def learn(
    self, num_learning_iterations: int, init_at_random_ep_len: bool = False
  ) -> None:
    self._on_learn_start()
    # Randomize initial episode lengths (for exploration)
    if init_at_random_ep_len:
      self.env.episode_length_buf = torch.randint_like(
        self.env.episode_length_buf, high=int(self.env.max_episode_length)
      )

    # Start learning
    obs = self.env.get_observations().to(self.device)
    amp_obs = self._get_amp_obs(obs)
    self.alg.reset_amp_history(amp_obs)
    self.alg.train_mode()  # switch to train mode (for dropout for example)

    # Ensure all parameters are in-synced
    if self.is_distributed:
      print(f"Synchronizing parameters for rank {self.gpu_global_rank}...")
      self.alg.broadcast_parameters()

    # Initialize the logging writer
    self.logger.init_logging_writer()
    self._reset_amp_metrics()

    # Start training
    start_it = self.current_learning_iteration
    total_it = start_it + num_learning_iterations
    for it in range(start_it, total_it):
      start = time.time()
      # Rollout
      with torch.inference_mode():
        for _ in range(self.cfg["num_steps_per_env"]):
          obs, amp_obs, rewards, dones, extras = self._amp_collect_step(obs, amp_obs)
          if self.cfg.get("check_for_nan", True):
            check_nan(obs, rewards, dones)

          # Extract intrinsic rewards (only for logging)
          intrinsic_rewards = (
            self.alg.intrinsic_rewards if self.cfg["algorithm"].get("rnd_cfg") else None
          )

          # Book keeping via logger
          self.logger.process_env_step(rewards, dones, extras, intrinsic_rewards)

        stop = time.time()
        collect_time = stop - start
        start = stop

        # Compute returns
        self.alg.compute_returns(obs)

      # Update policy
      update_dict = self.alg.update()
      self._on_policy_update(it)

      stop = time.time()
      learn_time = stop - start
      self.current_learning_iteration = it

      loss_dict = dict(update_dict["loss"])

      # Log information
      self.logger.log(
        it=it,
        start_it=start_it,
        total_it=total_it,
        collect_time=collect_time,
        learn_time=learn_time,
        loss_dict=loss_dict,
        learning_rate=self.alg.learning_rate,
        action_std=self.alg.get_policy().output_std,
        rnd_weight=self.alg.rnd.weight
        if self.cfg["algorithm"].get("rnd_cfg")
        else None,
      )
      if self.logger.writer is not None:
        for metric_name, metric_value in update_dict.get("extra", {}).items():
          self.logger.writer.add_scalar(
            f"Discriminator/{metric_name}", metric_value, it
          )

      # Save model
      if self.logger.writer is not None and it % self.cfg["save_interval"] == 0:
        self.save(os.path.join(self.logger.log_dir, f"model_{it}.pt"))

    # Save the final model after training and stop the logging writer
    if self.logger.writer is not None:
      self.save(
        os.path.join(
          self.logger.log_dir, f"model_{self.current_learning_iteration}.pt"
        ),
      )
      self.logger.stop_logging_writer()
