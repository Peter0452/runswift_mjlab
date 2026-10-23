"""Anchor of a self-play policy to its warm start (``rl.anchor``)."""

from types import SimpleNamespace

import torch
from rsl_rl.models import MLPModel
from tensordict import TensorDict

from k1.tasks.velocity.rl import anchor as anc
from mjlab.amp.runners.amp_on_policy_runner import AmpRslRlMuonPpoAlgorithmCfg

DIST = {
  "class_name": "rsl_rl.modules.distribution:GaussianDistribution",
  "init_std": 0.6,
  "std_range": (0.05, 0.6),
}


def _model(in_dim: int, seed: int) -> MLPModel:
  torch.manual_seed(seed)
  obs = TensorDict({"actor": torch.zeros(4, in_dim)}, batch_size=[4])
  return MLPModel(
    obs, {"actor": ["actor"]}, "actor", 22, (32, 32), "elu", True, dict(DIST)
  )


def _obs(n: int, in_dim: int) -> TensorDict:
  return TensorDict({"actor": torch.randn(n, in_dim)}, batch_size=[n])


def _anchored(actor: MLPModel, ckpt: str, **kw) -> anc.AnchoredAmpPPO:
  alg = anc.AnchoredAmpPPO.__new__(anc.AnchoredAmpPPO)
  alg.actor = actor
  alg.device = "cpu"
  alg.imitation_coef = 0.0
  alg.init_anchor(anchor_checkpoint=ckpt, **kw)
  return alg


def test_reference_is_padded_warm_start_and_frozen(tmp_path):
  src = _model(83, seed=0)
  ckpt = tmp_path / "h.pt"
  torch.save({"actor_state_dict": src.state_dict()}, ckpt)
  actor = _model(86, seed=1)
  ref = anc.load_reference(actor, str(ckpt), "cpu")
  x = _obs(16, 86)
  x86 = x.clone()
  x86["actor"][:, 83:] = 5.0  # the new (opponent) inputs have zero weights
  y_src = anc.model_mean(src, TensorDict({"actor": x["actor"][:, :83]}, [16]))
  torch.testing.assert_close(anc.model_mean(ref, x), y_src)
  torch.testing.assert_close(anc.model_mean(ref, x86), y_src)
  assert not any(p.requires_grad for p in ref.parameters())


def test_kl_zero_at_reference_and_pulls_back_only_the_actor(tmp_path):
  src = _model(83, seed=0)
  ckpt = tmp_path / "h.pt"
  torch.save({"actor_state_dict": src.state_dict()}, ckpt)
  actor = _model(86, seed=1)
  actor.load_state_dict(anc.pad_input_columns(src.state_dict(), 86))
  alg = _anchored(actor, str(ckpt), anchor_coef=1.0)
  x = _obs(64, 86)
  assert float(alg.anchor_loss(x)) < 1e-10
  with torch.no_grad():
    actor.mlp[-1].bias.add_(0.3)  # every mean moves by 0.3
  loss = alg.anchor_loss(x)
  # Shared std 0.6: KL = 22 · 0.3² / (2 · 0.36).
  torch.testing.assert_close(loss, torch.tensor(22 * 0.09 / 0.72), rtol=1e-4, atol=0)
  loss.backward()
  assert actor.mlp[-1].bias.grad is not None
  assert float(actor.mlp[-1].bias.grad.mean()) > 0.0  # gradient descent lowers it
  assert all(p.grad is None for p in alg.anchor_ref.parameters())


def test_beta_schedule_and_rollout_sampling(tmp_path):
  src = _model(83, seed=0)
  ckpt = tmp_path / "h.pt"
  torch.save({"actor_state_dict": src.state_dict()}, ckpt)
  alg = _anchored(
    _model(86, seed=1),
    str(ckpt),
    anchor_coef=1.0,
    anchor_coef_final=0.2,
    anchor_decay_updates=100,
  )
  for upd, beta in [(0, 1.0), (50, 0.6), (100, 0.2), (400, 0.2)]:
    alg.anchor_updates = upd
    assert abs(alg.imitation_coef_eff() - beta) < 1e-9
  obs = TensorDict({"actor": torch.randn(6, 8, 86)}, batch_size=[6, 8])
  alg.storage = SimpleNamespace(num_transitions_per_env=6, num_envs=8, observations=obs)
  loss = alg._imitation_loss(32)
  assert loss is not None and float(loss) > 0.0
  assert alg._anchor_n == 1


def test_off_without_checkpoint_or_coef_and_cfg_round_trip():
  alg = _anchored(_model(86, seed=1), "", anchor_coef=1.0)
  assert alg.anchor_ref is None
  assert alg.imitation_coef_eff() == 0.0
  assert alg._imitation_loss(8) is None
  base = AmpRslRlMuonPpoAlgorithmCfg()
  cfg = anc.with_anchor(base, "x.pt", coef=0.5, coef_final=0.1, decay_updates=10)
  assert cfg.class_name == "k1.tasks.velocity.rl.anchor:AnchoredAmpPPO"
  assert (cfg.anchor_coef, cfg.anchor_coef_final, cfg.anchor_decay_updates) == (
    0.5,
    0.1,
    10,
  )
  assert cfg.learning_rate == base.learning_rate and cfg.use_muon == base.use_muon
