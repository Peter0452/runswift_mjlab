# Approaches

An approach is one technique a task implementation can use (AMP, CAPS, a
privileged teacher, a scenario, ...). Approaches are filed by the **element**
of the learning system their mechanism changes, so any paper or method can be
described in the same terms and approaches can be combined or used alone.
Implementations draw their options from here; results come back as uses
(`knowledge/uses/`).

## Elements

The four elements of an RL agent, plus two context axes for what changes the
experience or the optimisation rather than the agent:

| Element | Mechanism it changes | Examples |
|---|---|---|
| `agent` | the mapping from state to action: architecture, inputs, action priors, policy losses and regularisers, hierarchy, distillation | DecAP, CAPS, KL anchor, teacher imitation (BC loss), two-level controller |
| `reward` | what is rewarded: task and shaping terms, imitation and style rewards, intrinsic rewards, constraints | AMP, reward grammar, momentum kick, constrained falls |
| `value` | value functions: critic structure, off-policy Q learning, cost critics | multi-critic, FastSAC |
| `model` | the agent's own model of the dynamics: planning, MPC, model-based RL, world models | none yet (gap) |
| `environment` | (context) what the agent experiences: scenarios, curricula, DR, observation noise, opponents and self-play, demonstrations as data, actuator and ball models | DR from the AMP walk, self-play, ball-behind starts, retargeted clips |
| `optimisation` | (context) how learning proceeds: algorithm settings, optimiser, weight averaging | Muon, SWA and blends |

Rules:

- **File by mechanism, not by goal.** Imitation can be a reward (AMP, tracking
  reward) or an agent loss (behaviour cloning, teacher matching); the goal goes
  in `tags`.
- An approach that spans elements has one primary `element` and the rest in
  `also`.
- A model that makes the *simulator* faithful (actuator net, ball model) is
  `environment`; `model` is only the agent's own dynamics model.

## Goal tags

Free, but prefer these so symptoms find candidates: `imitation`, `style`,
`exploration`, `sample-efficiency`, `sim2real`, `perception`, `smoothness`,
`stability` (fine-tuning drift, forgetting), `multi-skill`, `multi-objective`,
`safety`, `power`, `accuracy`, `speed`.

## Card format

`<element>/<id>.md`: YAML front matter, then the body.

```yaml
---
id: caps
title: CAPS action smoothness (temporal and spatial)
element: agent
also: []
tags: [smoothness]
status: experimental      # candidate | experimental | trial | adopted | rejected | parked
impact: training-only     # or runtime (changes what runs on the robot)
sources: [mysore2021_caps]   # ids in knowledge/sources/
registry: caps            # name in k1.approaches (code that turns it on), or null
trial:                    # how the engine switches it on in a recipe, or null
  methods: {caps: {temporal: 1.5}}      # and/or genes: {s.spawn_any_prob: 0.3}
tune:                     # parameters the engine may step once it is on, or null
  methods.caps.temporal: {range: [0.5, 1.5], tags: [smoothness], step: up}
---
```

`trial` and `tune` are what makes an approach usable by the engine's approach
designer (`k1/engine/designers/approach.py`). It reads the champion's measured
gaps, matches their tags (`symptoms.yaml`: metric and situation → tags) to
cards, and proposes either **add** (apply the `trial`) or **tune** (step one
`tune` parameter ×1.25 or ×0.8 within its range, in the `step` direction). A card
without either is "blocked" for the engine: it needs building, a runtime change
or a person, and escalation packets and `rsw review gaps` list it. Give a
`trial` only when a recipe can apply it: parameters of a registered approach
or genes the task reads.

Body: **What**, **Where it plugs in**, **Deployment impact**, **Evidence**
(ours, summarised; each result is a use record), **Pitfalls**.

Status follows the promotion rule (`knowledge/architecture.md`): `adopted`
means in a deployed model; a status changes only on our evidence, never on a
paper's claims. A rejected approach needs a new reason before it is retried.

## Checks

`tests/test_k1_approaches.py` checks every card against the registry and the
source and use records; `rsw approaches [--element E] [ID]` lists them.
