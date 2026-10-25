"""Approach registry, cards, sources, uses and detection on the registered K1 tasks."""

import dataclasses

import pytest

import mjlab.tasks  # noqa: F401
from k1 import recipes
from k1.approaches import APPROACHES, detect_all, knowledge
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg

STAGE3 = "Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1"


def test_every_approach_has_a_card() -> None:
  for m in APPROACHES.values():
    assert m.card.is_file(), m.name
    assert "**Deployment impact.**" in m.card.read_text()


def test_knowledge_graph_connects() -> None:
  assert knowledge.check() == []


def test_every_element_is_known_and_cards_cover_the_registry() -> None:
  cards = knowledge.cards()
  assert {c.meta["registry"] for c in cards.values()} - {None} == set(APPROACHES)
  assert {c.meta["element"] for c in cards.values()} <= set(knowledge.ELEMENTS)


def test_check_flags_a_use_of_an_unknown_approach(monkeypatch) -> None:
  bad = [{"id": "u999", "approach": "nope", "source": "ours", "result": "none"}]
  monkeypatch.setattr(knowledge, "uses", lambda: bad)
  problems = knowledge.check()
  assert any("unknown approach nope" in p for p in problems)


def test_detect_on_stage3() -> None:
  found = detect_all(load_env_cfg(STAGE3), load_rl_cfg(STAGE3))
  assert {"amp", "muon", "symmetry_aug", "decap", "multi_critic", "caps"} <= set(found)
  assert found["decap"]["source"] == "kick"
  assert found["multi_critic"]["alphas"] == [0.5, 0.5]


def test_detect_on_selfplay_finds_the_anchor() -> None:
  task = "Mjlab-Velocity-Kick-SelfPlay-Amp-DA-Muon-Booster-K1"
  found = detect_all(load_env_cfg(task), load_rl_cfg(task))
  assert found["kl_anchor"]["coef"] == 0.5


def _stage3_recipe(**changes) -> recipes.Recipe:
  recipe = recipes.load(recipes.RECIPES / "kick" / "kick_stage3_default.yaml")
  return dataclasses.replace(recipe, **changes)


def test_default_recipe_verifies() -> None:
  recipe = _stage3_recipe()
  assert recipes.verify(recipe, *recipes.build(recipe)) == []


def test_verify_flags_an_undeclared_method() -> None:
  recipe = _stage3_recipe()
  methods = dict(recipe.methods)
  methods.pop("caps")
  recipe = dataclasses.replace(recipe, methods=methods)
  problems = recipes.verify(recipe, *recipes.build(recipe))
  assert any("caps is on but not declared" in p for p in problems)


def test_verify_flags_a_wrong_parameter() -> None:
  recipe = _stage3_recipe()
  env_cfg, rl_cfg = recipes.build(recipe)
  rl_cfg.decap_gamma = 0.9  # the config no longer matches the declaration
  problems = recipes.verify(recipe, env_cfg, rl_cfg)
  assert any("decap.gamma" in p for p in problems)


def test_turning_methods_off_and_overriding_rewards() -> None:
  recipe = _stage3_recipe(
    methods={**_stage3_recipe().methods, "decap": False, "multi_critic": False},
    rewards={"ball_avoidance": -5.0},
  )
  env_cfg, rl_cfg = recipes.build(recipe)
  assert rl_cfg.decap is False and rl_cfg.algorithm.multi_critic_alphas is None
  assert env_cfg.rewards["ball_avoidance"].weight == -5.0
  assert recipes.verify(recipe, env_cfg, rl_cfg) == []


def test_changed_actor_inputs_need_touches_runtime() -> None:
  recipe = _stage3_recipe()
  env_cfg, rl_cfg = recipes.build(recipe)
  env_cfg.observations["actor"].terms.pop("kick_range")
  problems = recipes.verify(recipe, env_cfg, rl_cfg)
  assert any("touches: runtime" in p for p in problems)
  runtime = dataclasses.replace(recipe, touches="runtime")
  assert not any("touches" in p for p in recipes.verify(runtime, env_cfg, rl_cfg))


def test_unknown_reward_term_is_an_error() -> None:
  with pytest.raises(KeyError):
    recipes.build(_stage3_recipe(rewards={"no_such_term": 1.0}))


def test_kick_prior_turns_ball_avoidance_off_in_recipes() -> None:
  h022 = recipes.load(recipes.RECIPES / "kick" / "kick_stage3_h022.yaml")
  assert h022.rewards["ball_avoidance"] == -5.0
  methods = {**h022.methods, "decap": {"source": "kick"}}
  env_cfg, _ = recipes.build(
    dataclasses.replace(h022, methods=methods, genes={}, reward_program=None)
  )
  assert env_cfg.rewards["ball_avoidance"].weight == 0.0
