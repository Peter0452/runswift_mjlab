"""Recipes: one YAML file per training run (``experiments/recipes/<family>/``).

A recipe is a registered task plus explicit, checked deltas::

  name: kick_stage3_h022
  task: Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1
  change: what differs from the control (one change per run)
  why: the reason, with evidence
  touches: training-only        # or runtime (needs runner change + parity)
  control: kick_stage3_default  # same-length run to judge against (or null)
  init: null                    # checkpoint to start from
  ball: ours                    # K1_BALL: ours | bhuman
  genes: {}                     # KICK_GENES / DRIBBLE_GENES (read at import)
  methods:                      # every method that is on, with its parameters;
    decap: false                # false turns a method off
    caps: {temporal: 1.0}
  rewards: {kick_vel: 900.0}    # reward term -> weight
  rl: {algorithm.learning_rate: 1.0e-4}   # other runner fields (dotted paths)
  env: {scene.num_envs: 4096}             # other env fields (dotted paths)

``check`` builds the recipe in a fresh process (genes and the ball are read
when modules are imported) and verifies it: every method that is on must be
declared with matching parameters, every declared override must exist, and a
recipe that changes the deployed actor inputs must say ``touches: runtime``.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
RECIPES = ROOT / "experiments" / "recipes"
TOUCHES = ("training-only", "runtime")


@dataclass
class Recipe:
  name: str
  task: str
  change: str
  why: str
  touches: str = "training-only"
  control: str | None = None
  init: str | None = None
  ball: str = "ours"
  genes: dict[str, Any] = field(default_factory=dict)
  methods: dict[str, Any] = field(default_factory=dict)
  rewards: dict[str, float] = field(default_factory=dict)
  rl: dict[str, Any] = field(default_factory=dict)
  env: dict[str, Any] = field(default_factory=dict)
  reward_program: str | None = None
  budget: dict[str, Any] = field(default_factory=dict)
  path: Path | None = None

  @property
  def genes_var(self) -> str:
    return "DRIBBLE_GENES" if "Dribble" in self.task else "KICK_GENES"

  def env_vars(self) -> dict[str, str]:
    """Environment the recipe must be built and trained under."""
    env = {"K1_BALL": self.ball, self.genes_var: json.dumps(self.genes, sort_keys=True)}
    if self.reward_program:
      env["KICK_REWARD_PROGRAM"] = str(ROOT / self.reward_program)
    return env


def load(path: str | Path) -> Recipe:
  path = Path(path).resolve()
  data = yaml.safe_load(path.read_text()) or {}
  missing = {"name", "task", "change", "why"} - set(data)
  if missing:
    raise ValueError(f"{path}: missing {sorted(missing)}")
  unknown = set(data) - (set(Recipe.__dataclass_fields__) - {"path"})
  if unknown:
    raise ValueError(f"{path}: unknown fields {sorted(unknown)}")
  recipe = Recipe(**data, path=path)
  if recipe.touches not in TOUCHES:
    raise ValueError(f"{path}: touches must be one of {TOUCHES}")
  if recipe.ball not in ("ours", "bhuman"):
    raise ValueError(f"{path}: ball must be 'ours' or 'bhuman'")
  return recipe


def all_recipes() -> list[Path]:
  return sorted(RECIPES.glob("*/*.yaml"))


def _set_path(obj: Any, dotted: str, value: Any) -> None:
  *parents, last = dotted.split(".")
  for p in parents:
    obj = getattr(obj, p)
  if not hasattr(obj, last):
    raise AttributeError(f"no field {dotted!r} on {type(obj).__name__}")
  current = getattr(obj, last)
  if isinstance(current, tuple) and isinstance(value, list):
    value = tuple(value)
  setattr(obj, last, value)


def _disable(name: str, rl_cfg: Any, env_cfg: Any) -> None:
  alg = rl_cfg.algorithm
  if name == "decap":
    rl_cfg.decap = False
  elif name == "multi_critic":
    alg.multi_critic_alphas = None
    rl_cfg.extra_reward_group = None
  elif name == "caps":
    alg.caps_temporal_coef = 0.0
    alg.caps_spatial_coef = 0.0
  elif name == "kick_teacher":
    alg.imitation_coef = 0.0
  elif name == "symmetry_aug":
    alg.symmetry_cfg = None
  else:
    raise ValueError(f"method {name!r} cannot be turned off by a recipe")


def _enable(name: str, rl_cfg: Any) -> None:
  if name == "decap":
    rl_cfg.decap = True
  elif name == "muon":
    rl_cfg.algorithm.use_muon = True


def build(recipe: Recipe) -> tuple[Any, Any]:
  """Env and runner configs of a recipe. The calling process must already run
  under ``recipe.env_vars()`` (genes and the ball are read at import)."""
  defaults = {"K1_BALL": "ours"}  # what an unset variable means
  for key, value in recipe.env_vars().items():
    current = os.environ.get(key) or defaults.get(
      key, "{}" if key.endswith("GENES") else ""
    )
    if current != value:
      raise RuntimeError(
        f"build {recipe.name}: run with {key}={value} (see run_with_env)"
      )
  import mjlab.tasks  # noqa: F401  (registers the tasks)
  from k1.methods import METHODS
  from mjlab.tasks.registry import load_env_cfg, load_rl_cfg

  env_cfg, rl_cfg = load_env_cfg(recipe.task), load_rl_cfg(recipe.task)
  for name, params in recipe.methods.items():
    if name not in METHODS:
      raise KeyError(f"unknown method {name!r}")
    if params is False:
      _disable(name, rl_cfg, env_cfg)
    elif isinstance(params, dict):
      _enable(name, rl_cfg)
      settable = {k: v for k, v in params.items() if k in METHODS[name].params}
      METHODS[name].apply(rl_cfg, settable)
  for term, weight in recipe.rewards.items():
    if term not in env_cfg.rewards:
      raise KeyError(f"unknown reward term {term!r}")
    env_cfg.rewards[term].weight = float(weight)
  for dotted, value in recipe.rl.items():
    _set_path(rl_cfg, dotted, value)
  for dotted, value in recipe.env.items():
    _set_path(env_cfg, dotted, value)
  # User rule (2026-10-23): ball_avoidance stays -5 except when the kick-retarget
  # prior places the ball at the foot; it wins over a recipe's reward override.
  if getattr(rl_cfg, "decap", False) and getattr(rl_cfg, "decap_source", "") == "kick":
    if "ball_avoidance" in env_cfg.rewards:
      env_cfg.rewards["ball_avoidance"].weight = 0.0
  return env_cfg, rl_cfg


def _canonical(value: str) -> str:
  """A ``module:name`` path with old module paths resolved (k1.compat)."""
  from k1.compat import _target

  module, sep, name = value.partition(":")
  seen = set()
  while sep and module not in seen:
    seen.add(module)
    new = _target(module)
    if new is None:
      break
    module = new
  return f"{module}{sep}{name}"


def _same(a: Any, b: Any) -> bool:
  if isinstance(a, str) and isinstance(b, str) and ":" in a and ":" in b:
    return _canonical(a) == _canonical(b)
  if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
    return len(a) == len(b) and all(_same(x, y) for x, y in zip(a, b, strict=True))
  if isinstance(a, float) or isinstance(b, float):
    try:
      return abs(float(a) - float(b)) <= 1e-9 * max(1.0, abs(float(a)))
    except (TypeError, ValueError):
      return False
  return a == b


def verify(recipe: Recipe, env_cfg: Any, rl_cfg: Any) -> list[str]:
  """Problems with a built recipe (empty when it is true to the code)."""
  from k1.deploy.obs_layout import LAYOUTS
  from k1.methods import detect_all

  problems = []
  found = detect_all(env_cfg, rl_cfg)
  for name, params in found.items():
    declared = recipe.methods.get(name)
    if declared is None or declared is False:
      problems.append(f"method {name} is on but not declared (declare it: {params})")
      continue
    if isinstance(declared, dict):
      for k, v in declared.items():
        if k not in params:
          problems.append(f"method {name}: unknown parameter {k!r}")
        elif not _same(params[k], v):
          problems.append(
            f"method {name}.{k}: declared {v!r}, config has {params[k]!r}"
          )
  for name, declared in recipe.methods.items():
    if declared is False and name in found:
      problems.append(f"method {name} declared off but is on")
    if isinstance(declared, dict) and name not in found:
      problems.append(f"method {name} declared on but is off")
  actor = getattr(env_cfg.observations.get("actor"), "terms", {}) or {}
  for lay in LAYOUTS.values():
    if lay.task == recipe.task and list(actor) != [b.term for b in lay.blocks]:
      if recipe.touches != "runtime":
        problems.append(
          f"actor inputs differ from deployed layout {lay.name}: set touches: runtime "
          "(runner change + parity needed)"
        )
  return problems


# Run bookkeeping that legitimately differs between a recipe and a past run.
_RUN_FIELDS = {
  "run_name",
  "load_run",
  "load_checkpoint",
  "resume",
  "logger",
  "wandb_project",
  "wandb_tags",
  "upload_model",
  "experiment_name",
  "seed",
}


class _RunYamlLoader(yaml.SafeLoader):
  """Reads params/*.yaml written by the trainer: tuples as lists, names as text."""


def _python_tag(loader: yaml.SafeLoader, suffix: str, node: yaml.Node) -> Any:
  if isinstance(node, yaml.SequenceNode):
    return loader.construct_sequence(node, deep=True)
  if isinstance(node, yaml.MappingNode):
    return loader.construct_mapping(node, deep=True)
  return (
    suffix.split(":", 1)[-1]
    if suffix.startswith("name:")
    else loader.construct_scalar(node)
  )


_RunYamlLoader.add_multi_constructor("tag:yaml.org,2002:python/", _python_tag)


def _flatten(d: Any, prefix: str = "") -> dict[str, Any]:
  if isinstance(d, dict):
    out = {}
    for k, v in d.items():
      out.update(_flatten(v, f"{prefix}{k}."))
    return out
  return {prefix[:-1]: list(d) if isinstance(d, tuple) else d}


def _cfg_to_dict(cfg: Any) -> Any:
  """A config as the trainer's params/env.yaml writes it (functions as names)."""
  import tempfile

  from mjlab.utils.os import dump_yaml  # noqa: F401  (same conversion as the trainer)

  with tempfile.TemporaryDirectory() as d:
    path = Path(d) / "env.yaml"
    from mjlab.utils.os import dump_yaml as _dump

    _dump(path, cfg)
    return yaml.load(path.read_text(), Loader=_RunYamlLoader)


def _dotted_canonical(value: Any) -> Any:
  """``a.b.c.func`` written by the trainer, as the object it names (old module
  paths and re-export shims resolve to the same object); text if not importable."""
  if isinstance(value, str) and value.count(".") >= 2 and not set(value) & set(" /:"):
    import importlib

    module, _, name = value.rpartition(".")
    try:
      obj = getattr(importlib.import_module(module), name)
    except (ImportError, AttributeError, ValueError):
      return _canonical(f"{module}:{name}")
    return f"<object {id(obj)}>"
  return value


def _derived(key: str) -> bool:
  """Env fields filled in while the env is built (the trainer saves params after
  that): the seed, the terrain's env count, and sub-terrain sizes copied from the
  generator (terrain_generator.py)."""
  return (
    key == "seed"
    or key == "scene.terrain.num_envs"
    or (".sub_terrains." in key and key.endswith(".size"))
  )


def diff_run(
  recipe: Recipe, env_cfg: Any, rl_cfg: Any, run_dir: str | Path
) -> list[str]:
  """Differences between a built recipe and a past run's saved params: runner
  fields present in both, and reward weights (a term the run did not have must
  have weight 0 in the recipe)."""
  import dataclasses

  params = Path(run_dir) / "params"
  agent = yaml.load((params / "agent.yaml").read_text(), Loader=_RunYamlLoader)
  ours = _flatten(dataclasses.asdict(rl_cfg))
  theirs = _flatten(agent)
  out = []
  for key in sorted(set(ours) & set(theirs)):
    if key.split(".")[0] in _RUN_FIELDS:
      continue
    if not _same(ours[key], theirs[key]):
      out.append(f"rl {key}: recipe {ours[key]!r}, run {theirs[key]!r}")
  env = yaml.load((params / "env.yaml").read_text(), Loader=_RunYamlLoader)
  run_env = _flatten(env)
  our_env = _flatten(_cfg_to_dict(env_cfg))
  for key in sorted(set(our_env) & set(run_env)):
    if _derived(key):
      continue
    a, b = _dotted_canonical(our_env[key]), _dotted_canonical(run_env[key])
    if not _same(a, b):
      out.append(f"env {key}: recipe {our_env[key]!r}, run {run_env[key]!r}")
  for term, cfg in env_cfg.rewards.items():
    if f"rewards.{term}.weight" not in run_env and cfg.weight != 0.0:
      out.append(f"reward {term}: recipe {cfg.weight}, absent from the run")
  run_rewards = {k: v.get("weight") for k, v in (env.get("rewards") or {}).items()}
  for term in sorted(set(run_rewards) - set(env_cfg.rewards)):
    if run_rewards[term]:
      out.append(f"reward {term}: run {run_rewards[term]}, absent from the recipe")
  return out


def run_with_env(
  recipe: Recipe, *args: str, capture: bool = True
) -> subprocess.CompletedProcess:
  env = {**os.environ, **recipe.env_vars()}
  return subprocess.run(
    [sys.executable, "-m", "k1.recipes", *args, str(recipe.path)],
    env=env,
    capture_output=capture,
    text=True,
  )


def check(path: str | Path) -> list[str]:
  """Build and verify a recipe in a fresh process; returns the problems."""
  recipe = load(path)
  proc = run_with_env(recipe, "_verify")
  out = [ln for ln in proc.stdout.splitlines() if ln.startswith("RECIPE ")]
  if proc.returncode != 0 or not out:
    tail = (proc.stderr or proc.stdout).strip().splitlines()[-5:]
    return [f"build failed: {' | '.join(tail)}"]
  return json.loads(out[-1][len("RECIPE ") :])


def diff(path: str | Path, run_dir: str | Path) -> list[str]:
  """Build a recipe in a fresh process and diff it against a past run."""
  recipe = load(path)
  proc = run_with_env(recipe, "_diff", str(run_dir))
  out = [ln for ln in proc.stdout.splitlines() if ln.startswith("RECIPE ")]
  if proc.returncode != 0 or not out:
    tail = (proc.stderr or proc.stdout).strip().splitlines()[-5:]
    return [f"build failed: {' | '.join(tail)}"]
  return json.loads(out[-1][len("RECIPE ") :])


def train(path: str | Path, extra_args: list[str], go: bool) -> int:
  """Train a recipe in a fresh process under its env vars. Without ``go`` only
  print what would run."""
  recipe = load(path)
  problems = check(path)
  if problems:
    print("recipe check failed:\n  " + "\n  ".join(problems))
    return 1
  env = " ".join(f"{k}='{v}'" for k, v in recipe.env_vars().items())
  print(f"{env} {sys.executable} -m k1.recipes _train {' '.join(extra_args)} {path}")
  if not go:
    print("(dry run: add --go to train)")
    return 0
  return run_with_env(recipe, "_train", *extra_args, capture=False).returncode


def _train(recipe: Recipe, env_cfg: Any, rl_cfg: Any, extra_args: list[str]) -> int:
  import tyro

  import mjlab
  from k1 import runs
  from mjlab.scripts.train import TrainConfig, launch_training, run_log_dir

  rl_cfg.run_name = rl_cfg.run_name or recipe.name
  if recipe.init:
    init = ROOT / recipe.init
    rl_cfg.resume = True
    rl_cfg.load_run = init.parent.name
    rl_cfg.load_checkpoint = init.name
  args = tyro.cli(
    TrainConfig,
    args=extra_args,
    default=TrainConfig(env=env_cfg, agent=rl_cfg),
    config=mjlab.TYRO_FLAGS,
  )
  log_dir = run_log_dir(args)
  info = runs.describe(recipe, args.env, args.agent, extra_args)
  print(f"[k1] run.json -> {runs.write(log_dir, info)}")
  launch_training(task_id=recipe.task, args=args, log_dir=log_dir)
  return 0


def _main(argv: list[str]) -> int:
  cmd, path = argv[0], argv[-1]
  recipe = load(path)
  env_cfg, rl_cfg = build(recipe)
  if cmd == "_train":
    return _train(recipe, env_cfg, rl_cfg, argv[1:-1])
  if cmd == "_verify":
    print("RECIPE " + json.dumps(verify(recipe, env_cfg, rl_cfg)))
    return 0
  if cmd == "_diff":
    print("RECIPE " + json.dumps(diff_run(recipe, env_cfg, rl_cfg, argv[1])))
    return 0
  raise SystemExit(f"unknown command {cmd}")


if __name__ == "__main__":
  sys.exit(_main(sys.argv[1:]))
