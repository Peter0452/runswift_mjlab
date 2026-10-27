"""Registry of the approaches K1 tasks can turn on in code.

An approach is one technique (AMP, DecAP, Muon, ...), filed by the element of
the learning system it changes (``element``: agent, reward, value, model, or
the context axes environment and optimisation; knowledge/approaches/README.md).
Each entry says where it plugs in (extension points), whether it changes what
runs on the robot (``impact``), how far it has been trusted (``status``, see the
promotion rule in knowledge/architecture.md) and which config fields carry its
parameters. Its card, ``knowledge/approaches/<element>/<name>.md``, holds the
sources, evidence and pitfalls; approaches without code (candidates from the
literature) have a card only.

``detect`` reads a task's env and runner configs and reports the approach's
parameters when it is on (``None`` when off). Recipes declare the approaches
they expect (their ``methods:`` field) and ``k1.recipes.check`` compares the
declaration with ``detect``; this is how recipes stay true to the code instead
of drifting from it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

Detect = Callable[[Any, Any], "dict[str, Any] | None"]

STATUSES = ("candidate", "experimental", "trial", "adopted", "rejected", "parked")
IMPACTS = ("training-only", "runtime")
ELEMENTS = ("agent", "reward", "value", "model", "environment", "optimisation")
POINTS = (
  "algorithm",
  "optimizer",
  "critic",
  "action prior",
  "smoothness",
  "data",
  "observation",
  "reward",
  "scenario/DR",
  "curriculum",
  "post-training",
  "evaluation",
)
CARDS = Path(__file__).resolve().parents[3] / "knowledge" / "approaches"


@dataclass(frozen=True)
class Approach:
  name: str
  title: str
  element: str
  points: tuple[str, ...]
  impact: str
  status: str
  # Recipe parameter -> runner-config attribute path ("rl.x" or "alg.x").
  params: dict[str, str] = field(default_factory=dict)
  detect: Detect | None = None
  conflicts: tuple[str, ...] = ()
  # Run before the parameters are set (e.g. swap in an algorithm config that
  # has the parameter fields).
  prepare: Callable[[Any], None] | None = None

  @property
  def card(self) -> Path:
    return CARDS / self.element / f"{self.name}.md"

  def read(self, rl_cfg: Any) -> dict[str, Any]:
    return {p: _get(rl_cfg, path) for p, path in self.params.items()}

  def apply(self, rl_cfg: Any, values: dict[str, Any]) -> None:
    """Set this method's parameters on a runner config (field-mapped methods)."""
    if self.prepare is not None:
      self.prepare(rl_cfg)
    for p, v in values.items():
      if p not in self.params:
        raise KeyError(f"{self.name}: unknown parameter {p!r}")
      _set(rl_cfg, self.params[p], v)


def _resolve(rl_cfg: Any, path: str) -> tuple[Any, str]:
  scope, attr = path.split(".", 1)
  obj = rl_cfg.algorithm if scope == "alg" else rl_cfg
  return obj, attr


def _get(rl_cfg: Any, path: str) -> Any:
  obj, attr = _resolve(rl_cfg, path)
  value = getattr(obj, attr, None)
  return list(value) if isinstance(value, tuple) else value


def _set(rl_cfg: Any, path: str, value: Any) -> None:
  obj, attr = _resolve(rl_cfg, path)
  if not hasattr(obj, attr):
    raise AttributeError(f"{type(obj).__name__} has no field {attr!r}")
  current = getattr(obj, attr)
  if isinstance(current, tuple) or (current is None and isinstance(value, list)):
    value = tuple(value)
  setattr(obj, attr, value)


def _when(pred: Callable[[Any, Any], bool], method_name: str) -> Detect:
  def detect(env_cfg: Any, rl_cfg: Any) -> dict[str, Any] | None:
    if not pred(env_cfg, rl_cfg):
      return None
    return APPROACHES[method_name].read(rl_cfg)

  return detect


def _alg(rl_cfg: Any, attr: str, default: Any = None) -> Any:
  return getattr(getattr(rl_cfg, "algorithm", None), attr, default)


def _is_amp(rl_cfg: Any) -> bool:
  return hasattr(rl_cfg, "discriminator") and hasattr(rl_cfg, "dataset_root")


def _amp_detect(env_cfg: Any, rl_cfg: Any) -> dict[str, Any] | None:
  if not _is_amp(rl_cfg):
    return None
  out = APPROACHES["amp"].read(rl_cfg)
  curriculum = getattr(env_cfg, "curriculum", None) or {}
  if "amp_style_weight" in curriculum:
    p = curriculum["amp_style_weight"].params
    out["style_start"], out["style_end"] = p["start_weight"], p["end_weight"]
  return out


def _symmetry_detect(env_cfg: Any, rl_cfg: Any) -> dict[str, Any] | None:
  sym = _alg(rl_cfg, "symmetry_cfg")
  if not sym or not (sym.get("use_data_augmentation") or sym.get("use_mirror_loss")):
    return None
  return {
    "augmentation": sym.get("data_augmentation_func"),
    "mirror_loss": bool(sym.get("use_mirror_loss")),
  }


def _cond_amp_detect(env_cfg: Any, rl_cfg: Any) -> dict[str, Any] | None:
  groups = getattr(env_cfg, "observations", None) or {}
  if "amp_cond" not in groups:
    return None
  return APPROACHES["conditioned_amp"].read(rl_cfg)


def _anchor_prepare(rl_cfg: Any) -> None:
  """Tasks whose algorithm config has no anchor fields (the kick loop) get the
  anchored one; the recipe's values are set on it next (2026-10-27)."""
  if hasattr(rl_cfg.algorithm, "anchor_checkpoint"):
    return
  from k1.tasks.velocity.rl.anchor import with_anchor  # mjlab import, lazily

  rl_cfg.algorithm = with_anchor(rl_cfg.algorithm, checkpoint="", coef=0.0)


def _anchor_detect(env_cfg: Any, rl_cfg: Any) -> dict[str, Any] | None:
  if _alg(rl_cfg, "anchor_coef") is None:
    return None
  return APPROACHES["kl_anchor"].read(rl_cfg)


def _fast_sac_detect(env_cfg: Any, rl_cfg: Any) -> dict[str, Any] | None:
  name = type(rl_cfg).__name__
  return {} if "Sac" in name or "SAC" in name else None


_METHOD_LIST = [
  Approach(
    "amp",
    "Adversarial motion priors (AMP-PPO)",
    "reward",
    ("algorithm", "reward", "data"),
    "training-only",
    "adopted",
    {
      "style_reward_weight": "rl.style_reward_weight",
      "dataset_root": "rl.dataset_root",
      "dataset_weights": "rl.dataset_weights",
      "num_amp_obs_steps": "rl.num_amp_obs_steps",
    },
    _amp_detect,
  ),
  Approach(
    "muon",
    "Muon optimizer for actor and critic",
    "optimisation",
    ("optimizer",),
    "training-only",
    "adopted",
    {
      "momentum": "alg.muon_momentum",
      "weight_decay": "alg.muon_weight_decay",
      "ns_steps": "alg.muon_ns_steps",
    },
    _when(lambda e, r: bool(_alg(r, "use_muon", False)), "muon"),
  ),
  Approach(
    "symmetry_aug",
    "Left-right symmetry data augmentation",
    "agent",
    ("data",),
    "training-only",
    "adopted",
    {},
    _symmetry_detect,
  ),
  Approach(
    "decap",
    "Decaying action prior (DecAP, from APEX)",
    "agent",
    ("action prior",),
    "training-only",
    "experimental",
    {"source": "rl.decap_source", "gamma": "rl.decap_gamma", "k": "rl.decap_k"},
    _when(lambda e, r: bool(getattr(r, "decap", False)), "decap"),
  ),
  Approach(
    "multi_critic",
    "Multi-critic advantage mix (APEX)",
    "value",
    ("critic",),
    "training-only",
    "experimental",
    {"alphas": "alg.multi_critic_alphas", "extra_group": "rl.extra_reward_group"},
    _when(lambda e, r: _alg(r, "multi_critic_alphas") is not None, "multi_critic"),
  ),
  Approach(
    "caps",
    "CAPS action smoothness (temporal and spatial)",
    "agent",
    ("smoothness",),
    "training-only",
    "experimental",
    {
      "temporal": "alg.caps_temporal_coef",
      "spatial": "alg.caps_spatial_coef",
      "spatial_sigma": "alg.caps_spatial_sigma",
      "near_ball_scale": "alg.caps_near_ball_scale",
      "near_ball_dist": "alg.caps_near_ball_dist",
    },
    _when(
      lambda e, r: (_alg(r, "caps_temporal_coef", 0.0) or 0.0) > 0
      or (_alg(r, "caps_spatial_coef", 0.0) or 0.0) > 0,
      "caps",
    ),
  ),
  Approach(
    "kl_anchor",
    "KL anchor to a frozen reference policy (AnchoredAmpPPO)",
    "agent",
    ("algorithm",),
    "training-only",
    "experimental",
    {
      "checkpoint": "alg.anchor_checkpoint",
      "coef": "alg.anchor_coef",
      "coef_final": "alg.anchor_coef_final",
      "decay_updates": "alg.anchor_decay_updates",
      "loss": "alg.anchor_loss",
    },
    _anchor_detect,
    prepare=_anchor_prepare,
  ),
  Approach(
    "kick_teacher",
    "Teacher imitation near the ball (kick-loop or B-Human teacher)",
    "agent",
    ("data", "algorithm"),
    "training-only",
    "experimental",
    {
      "coef": "alg.imitation_coef",
      "decay_updates": "alg.imitation_decay_updates",
      "checkpoint": "rl.kick_teacher_checkpoint",
      "dist": "rl.kick_teacher_dist",
      "max_offset_deg": "rl.kick_teacher_max_offset_deg",
      "arms": "rl.kick_teacher_arms",
      "bhuman_dist": "rl.kick_teacher_bhuman_dist",
      "takeover_prob": "rl.kick_takeover_prob",
    },
    _when(lambda e, r: (_alg(r, "imitation_coef", 0.0) or 0.0) > 0, "kick_teacher"),
  ),
  Approach(
    "conditioned_amp",
    "Command-conditioned AMP discriminator (amp_cond)",
    "reward",
    ("observation", "reward"),
    "training-only",
    "experimental",
    {"free_prob": "rl.amp_cond_free_prob", "speed_mass": "rl.amp_speed_mass"},
    _cond_amp_detect,
  ),
  Approach(
    "swa_blend",
    "Weight averaging and weight-space blends of checkpoints",
    "optimisation",
    ("post-training",),
    "training-only",
    "adopted",
  ),
  Approach(
    "reward_grammar",
    "JSON reward programs (KICK_REWARD_PROGRAM)",
    "reward",
    ("reward",),
    "training-only",
    "experimental",
  ),
  Approach(
    "fast_sac",
    "FastSAC off-policy training",
    "value",
    ("algorithm",),
    "training-only",
    "parked",
    {},
    _fast_sac_detect,
    conflicts=("amp",),
  ),
  Approach(
    "bhuman_action_imitation",
    "Plain action imitation of B-Human's kick policy",
    "agent",
    ("data",),
    "training-only",
    "rejected",
  ),
]

APPROACHES: dict[str, Approach] = {m.name: m for m in _METHOD_LIST}
# Old names (k1.methods), kept for existing imports.
Method = Approach
METHODS = APPROACHES


def detect_all(env_cfg: Any, rl_cfg: Any) -> dict[str, dict[str, Any]]:
  """Every registered approach that is on in these configs, with its parameters."""
  out = {}
  for m in _METHOD_LIST:
    if m.detect is None:
      continue
    found = m.detect(env_cfg, rl_cfg)
    if found is not None:
      out[m.name] = found
  return out


def _validate() -> None:
  for m in _METHOD_LIST:
    assert m.status in STATUSES, m
    assert m.impact in IMPACTS, m
    assert m.element in ELEMENTS, m
    assert all(p in POINTS for p in m.points), m
    assert all(c in APPROACHES for c in m.conflicts), m


_validate()
