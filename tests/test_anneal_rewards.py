"""Linear annealing of task-shaping rewards (self-play)."""

from types import SimpleNamespace

from k1.tasks.velocity.mdp.curriculums import anneal_rewards


def _setup():
  terms = {
    n: SimpleNamespace(weight=w)
    for n, w in {"kick_vel": 900.0, "walk_speed": 5.0, "contest_score": 1500.0}.items()
  }
  env = SimpleNamespace(
    reward_manager=SimpleNamespace(get_term_cfg=lambda n: terms[n]),
    common_step_counter=0,
  )
  cfg = SimpleNamespace(
    params={
      "reward_names": ("kick_vel", "walk_speed"),
      "start_step": 100,
      "end_step": 300,
    }
  )
  return anneal_rewards(cfg, env), env, terms  # type: ignore[arg-type]


def _step_to(term, env, counter):
  env.common_step_counter = counter
  return float(term(env, slice(None))["alpha"])


def test_task_rewards_fall_linearly_and_others_stay():
  term, env, terms = _setup()
  for step, alpha in [(50, 1.0), (100, 1.0), (200, 0.5), (300, 0.0), (400, 0.0)]:
    assert abs(_step_to(term, env, step) - alpha) < 1e-6
    assert abs(terms["kick_vel"].weight - 900.0 * alpha) < 1e-6
    assert abs(terms["walk_speed"].weight - 5.0 * alpha) < 1e-6
    assert terms["contest_score"].weight == 1500.0


def test_warm_start_counter_jump_is_ignored_and_resume_continues():
  term, env, terms = _setup()
  _step_to(term, env, 150)
  # A warm start restores the source run's counter (~400k): no annealing.
  assert abs(_step_to(term, env, 400_000) - 0.75) < 1e-6
  assert abs(_step_to(term, env, 400_050) - 0.5) < 1e-6
  # Resume into a fresh term: the checkpointed elapsed steps carry over.
  state = term.state_dict()
  fresh, env2, terms2 = _setup()
  env2.common_step_counter = 400_050
  fresh.load_state_dict(state, env2)
  assert abs(terms2["kick_vel"].weight - 450.0) < 1e-6
  assert abs(_step_to(fresh, env2, 400_100) - 0.25) < 1e-6
