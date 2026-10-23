# Approach loop (L5): finding, integrating and evolving methods (proposal, 2026-10-06)

> **Scope (user, 2026-10-06):** one **end-to-end kick policy** only. No policy
> switching or hybrid walk / kick policies for now. Methods are adopted only
> if they end up inside this single policy: data, scenarios, rewards,
> constraints, training algorithm, or distillation into it. The loop runs
> **every few hours, at most every half day**, and is triggered early
> whenever the lower loops finish their queue.

The reward-design loop (`K1_KICK_REWARD_EVOLUTION_DESIGN.md`, L0–L4) improves
the reward and scenarios inside our current approach: one AMP-PPO policy, 83
inputs, a fixed benchmark. This loop sits above it. It asks **which methods
(ours or anyone's) should our system be built from**, integrates the promising
ones, keeps only what beats the benchmark, and keeps learning which kinds of
ideas pay off.

## 1. The ladder, complete

| Level | Evolves | Loop |
|---|---|---|
| L0 | weights, constants | gene search (`evolve_kick.py`) |
| L1–L2 | reward terms, composition, constraints | reward grammar + lint |
| L3 | scenarios, curriculum | scenario genes, adaptive sampling |
| L4 | who proposes L1–L3 changes | LLM proposer |
| **L5** | **the approach: data, algorithm, architecture, training pipeline, deployment split** | **this design** |

L5 decisions are larger than nightly tuning, so this loop runs **every few
hours (at most every half day)**, and immediately whenever the lower loops run
out of queued work. Each method it adopts becomes new material (data, scenario
genes, reward terms, operators) for the lower loops to exploit every night.

## 2. Components

### 2.1 Method catalogue (knowledge base)

One card per source, split into **method atoms**: the smallest separable
ideas.

```yaml
source: humanoid-soccer (ICRA 2026), local: RL/humanoid-soccer
atoms:
  - id: teacher_student_dagger
    idea: privileged teacher (true ball / goal) distilled by DAgger into a
      student on noisy, delayed, occluded inputs
    claims: robust striking from noisy sensing on Booster K1/T1
    our_fit: high (we already model vision noise / delay / dropout)
    level: algorithm / architecture
    constraints: student obs must stay our 83 inputs (teacher may be privileged)
    cost: medium
    targets: [h2h_first_on_target_pct, search, push falls]
  - id: np3o_constrained_rl
    idea: online constrained RL (N-P3O) for refinement, smoothing via
      heterogeneous credit assignment
    our_fit: high (= our L2 constraints plan)
    ...
evidence: []   # filled by our own experiments; overrides the paper's claims
licence: ...
```

Sources:
- **Seeded from the RL folder.**
- **Extended by literature search:** arXiv, project pages, RoboCup team
  releases.
- **Refreshed periodically:** new papers, repo updates.

### 2.2 Gap analysis → opportunities

- **Input:**
  - the current benchmark versus B-Human and versus our targets;
  - the situation breakdown (approach angle × range × ball offset);
  - the anatomy, style and torque diagnostics;
  - the objectives list;
  - the lessons file.
- **Mapping:** each gap goes to the atoms whose claims address it, e.g.
  "first kick 3.5 s vs 2.9 s" → separate approach policy, teacher-student,
  motion-guided curriculum.
- **Opportunity score** = expected gain on the gap metrics × fit with our
  invariants × confidence (paper claim < reproduced elsewhere < reproduced by
  us) ÷ integration cost × risk.
- **Output:** a ranked opportunity list with a hypothesis and a minimal
  experiment for each.

### 2.3 Integration adapters (harmony with what we have)

Each atom is integrated at the lowest level that can express it, so it
composes with everything else:

| Adapter | Examples | Lands as |
|---|---|---|
| **Data** | new clips (GMR retarget of human / G1 kicks to K1), recorded kicks from other policies | AMP clips, RSI start states, tracking references |
| **Scenario** | start-state mixes, ball dynamics, opponents, ground | L3 genes |
| **Reward / constraint** | new terms or constraints from a method | L1 / L2 grammar entries |
| **Algorithm** | DAgger distillation, constrained PPO, action priors, imitation losses | training options of our runner (A/B against plain AMP-PPO) |
| **Training architecture** | privileged teacher → our end-to-end student (the deployed policy stays one network) | new training stages |
| ~~Deployment / policy switching~~ | ~~separate walk / kick policies, hybrids~~ | **out of scope for now** (user) |

**Invariants** every adapter must respect:
- the fixed benchmark;
- one policy lineage, with branches as experiments;
- 83 deployed inputs unless approved;
- domain randomization changed only with robot evidence;
- licence check.

### 2.4 Evaluation (shared with the lower loops)

- **Same benchmark,** two-seed confirmation, a control run, no-regression
  gates.
- **New capabilities** (e.g. dribbling) get *new* benchmark metrics, added
  with human sign-off. Metrics are never removed or loosened by the loop.
- **Fairness:**
  - an approach is judged on its best result after the lower loops have tuned
    it for a fixed budget (e.g. one night), against the incumbent with the
    same budget;
  - a new pipeline is not judged against a heavily tuned one at its first
    attempt.

### 2.5 Selection and archive

- **Approach archive:** each integrated atom records:
  - its variant;
  - its benchmark result and which metrics it moved;
  - its cost;
  - whether it was kept, parked or rejected, and why.
- **Quality-diversity across approaches.** A method that is best only in some
  situations (side-foot for long kicks, a separate kick policy close to the
  ball) is kept as a specialist. Combination happens by:
  - weight blending (same architecture);
  - distillation (teacher → student);
  - policy switching (different architectures).
- **Promotion:** as in the lower loops (Pareto + gates + two seeds), plus the
  runner-sim bench and robot logs before deployment.

### 2.6 Self-evolution: learning which ideas pay

- **Evidence on cards:** every experiment's outcome is written back to its
  atom card, so local evidence replaces paper claims.
- **Meta-statistics:** which kinds of atoms (data, reward, algorithm,
  architecture), sources and levels have produced gains here, which guides
  the next search (bandit-style allocation of the weekly budget).
- **Lessons:** `K1_KICK_LESSONS.md` grows from every loop, and lessons become
  lint rules (L1) and proposer context (L4, L5).
- **Re-survey:** new papers, and our own gaps as they change.

### 2.7 Orchestration and human gates

- **L5 round, every few hours (at most half a day), or as soon as the lower
  loops' queue is empty:**
  1. refresh the catalogue;
  2. re-run the gap analysis;
  3. pick 1–2 opportunities;
  4. build the adapters (with review);
  5. hand them to the nightly L0–L4 loops for tuning;
  6. decide on keep / park / reject.
- **Automatic:** data and scenario adapters, reward entries, nightly tuning.
- **Human approval:** observation changes, runner changes, licences,
  anything going to the robot. Policy switching is out of scope.

## 3. First round from the RL folder

| Source (local) | Atom | Fits gap | Fit / cost | First experiment |
|---|---|---|---|---|
| `MachineLearning/IsaacGymRL` (B-Human) | side-foot kick while walking, planted support, kick-pose shaping (already partly in: momentum, planted support, RSI) | long power, torque, accuracy | high / low | side-foot specialist (queued tonight); kick-pose and foot-yaw shaping as grammar terms |
| same | B-Human kick as a *teacher*: record its kicks in our sim → AMP / RSI clips (done), or distil its near-ball actions into our policy as an auxiliary imitation target | long power, first-kick time | medium / medium | DAgger-style imitation of B-Human near the ball, gated by the benchmark (no switching) |
| `humanoid-soccer` (ICRA 2026, Booster) | 4-stage teacher-student (privileged teacher → DAgger student) + N-P3O constrained refinement | robustness to noisy vision, first-kick accuracy, smoothness | high / medium | privileged teacher on our task (true ball, no vision noise) distilled into our 83-input student |
| `RoboNaldo` (G1) | motion-guided curriculum: track a reference kick, then relax to task reward | long power, kick shape | medium / medium | retarget its kick (and a side-foot kick) to K1 with GMR, then curriculum stage on top of our policy |
| `GMR` + `data/GMR_CMU` + `data/retargeted/k1` | human-motion → K1 retargeting | new kick styles (side-foot, instep drive), cadence-correct walking | high / low–medium | retarget CMU soccer-kick clips to K1 → AMP / RSI clips; check cadence of retargeted walks |
| `APEX` (IROS 2026) | action priors for efficient exploration in motion tracking | discovering new kick styles (side-foot was never tried) | medium / medium | action prior from reference kick clips near the ball |
| `htwk-gym` (K1 / T1) | parameterized walking, kick task with target-based ball velocity | cadence, speed-cap use (0.55 of 2.0 m/s) | medium / low | compare gait parameters; borrow cadence / step-length terms |
| `DribbleMaster` | agile dribbling through locomotion | new capability (dribble), close ball control | low now / medium | parked until the kick is ahead of B-Human |
| `booster_mjlab` | our AMP / velocity base | — | — | the base we already use |
| `harbor-rl` | automated task / reward design and tuning agents | infrastructure for L1–L4 | medium / medium | evaluate as the engine for the reward grammar and proposer loops |

**Suggested first two:**
1. **Teacher-student distillation** (humanoid-soccer): a privileged teacher on
   our task, distilled into our 83-input end-to-end student.
2. **GMR-retargeted kick clips** (side-foot and instep, from CMU / RoboNaldo)
   as AMP / RSI data for the single policy.

Both are judged on the existing benchmark. (Policy switching / hybrid is out
of scope.)

## 4. Build order

1. Catalogue cards for the 10 local sources (atoms, fit, cost, licence) and
   the gap → atom mapping. ~1 day.
2. Approach archive + opportunity scoring + weekly report. ~0.5 day.
3. Adapters in order of cost: data (GMR → clips) → scenario → reward /
   constraint → algorithm (DAgger, constrained PPO) → architecture /
   deployment (hybrid, with approval).
4. Self-evolution statistics and the literature refresh.
5. L5 trigger: run a round when the nightly loops' queue empties or every ~4–12 h.

## 5. Risks

- **Scope creep:** many attractive methods, little compute. Mitigated by the
  weekly budget, opportunity scoring, and "smallest experiment first".
- **Incompatible assumptions** (Isaac Gym vs MuJoCo Warp, different robot,
  inputs): handled by atoms + adapters, never by copying pipelines wholesale.
- **Benchmark overfitting:** the benchmark is fixed and owned by a human, new
  metrics only add, and robot logs stay the final judge.
- **Licences:** checked per atom before code or weights are used.
