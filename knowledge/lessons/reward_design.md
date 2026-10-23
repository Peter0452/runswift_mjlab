# Lessons: reward and task design

Each lesson: the rule, the evidence, the source. Status is `valid` unless
marked. Sources: `docs/K1_KICK_LESSONS.md` (§3, kick v1–v57),
`docs/K1_KICK_STAGE3_NOTES.md`, `docs/experience/README.md`, session memory
(k1-kick-staged-training, k1-striker-selfplay, k1-dribble-speed).

## Signal and shape

**R1. A reward must give signal at the policy's current behaviour.** A sharp
band or Gaussian centred far from what the policy does is ≈ 0 where the policy
is. Prefer monotonic ramps and linear slopes that reach back to current
behaviour. *Evidence:* kick v54 stop-position Gaussian (σ 0.5 m, misses 5–6 m)
changed nothing; v54b exp(−miss/2 m) + linear speed match improved passes in
250 iterations; long-kick swing speed moved only with a ramp (v36); dribble
kick aim paid 0 at the untrained 35° until a wide kernel was added (v22).
*Source:* LESSONS §3.1, memory.

**R2. Band penalties act only outside the band: move the edge, not the
weight.** *Evidence:* v50d leaned +2.2° inside a −5…+3° band; doubling the
weight (v51) did nothing; moving the edge to +1° (v53) fixed it. *Source:*
LESSONS §3.2.

**R3. Normalise speed rewards by min(cap, 1 m/s), and make them signed and
two-sided.** speed/cap made higher caps pay less (v34 walked slower);
speed/1 m/s made low caps not worth walking (v36 idled); unsigned speed can be
farmed by shuffling. *Source:* LESSONS §3.6, memory.

**R4. Cap squared penalties** so rare states can't dominate. *Source:*
LESSONS §3.6.

**R5. Never use absolute height on uneven terrain.** v48's world-z height term
gave −21.8 on raised terrain, the adaptive LR collapsed and the run died.
Measure relative to the robot's lowest foot. *Source:* LESSONS §3.9.

## Outcomes over motions

**R6. Tie rewards to outcomes, not motions.** Swing-speed reward alone gave
fast swings that missed the ball's centre (v49); fixed by scaling with
transfer = ball speed ÷ foot speed (v50). *Source:* LESSONS §3.4.

**R7. Scale per-kick aim by power,** or the policy farms weak taps
(v43/v44 → v45). *Source:* LESSONS §3.4, memory.

**R8. Gate kick speed rewards on aim,** or kicks spray (stage3_v3).
*Source:* memory k1-kick-staged-training.

**R9. Measure the real objective in all three axes.** Horizontal launch speed
counted lofted kicks as fast; v53 lofted 73 % of long kicks and was weaker on
the robot. Track launch angle and air time. (Later the user allowed air balls
for long kicks; count 3D speed.) *Source:* LESSONS §3.11, objectives.

**R10. Reward the net effect, not a rate that can oscillate.** A search reward
on |wz| was farmed by wiggling (3.7 rad of "turning", net ~0, v56b); pay signed
net rotation. Check with a step trace. *Source:* LESSONS §3.12.

**R11. The goal definition shapes behaviour more than any shaping term.** A
"ball passes the target" goal plus randomised ball mass made blasting every
kick the safe choice (short passes at ~1.8× needed speed). *Source:*
LESSONS §3.3.

## Paying and penalising

**R12. Paying enough is what moves a skill.** Long-kick power weight
900 → 2000 (v47) moved swing speed where a gradient alone (v46) did not; a
faster swing was worth ~+4.5 per kick against ≥ 50 for not falling after it.
*Source:* LESSONS §3.5.

**R13. Penalising a bad action teaches avoiding the action.** An
underpowered-long-kick penalty (−800, v54c) first restored power, then the
policy stopped kicking long (goals 0.98 → 0.69). Keep such penalties small next
to the reward for doing the action, or pay the good version. *Source:*
LESSONS §3.10.

**R14. Per-episode task reward must stay positive.** A child whose episode
reward went negative learned to end episodes at once (h018: episode length
1400 → 35 in ~25 iterations; stage3_v2 fell on purpose). Watch episode length
and illegal_contact after adding costs or harder scenarios. *Source:*
HANDOFF gotchas, memory.

**R15. Zone-tied costs fence the ball** (stage3_v1 hovered around it rather
than kick). *Source:* memory k1-kick-staged-training.

## Gating and scenarios

**R16. Gating windows decide what the policy can practise.** Cap tracking only
beyond 2.5 m while balls spawn 1–4 m away meant almost no room to reach cruise
speed. *Source:* LESSONS §3.7.

**R17. Cover every start the robot can meet** (ball behind, far, unknown).
Ball-at-any-bearing training cut ball-behind falls 36–38 % → 1–2.5 % and
doubled near-ball first-touch accuracy, at a cost in low-cap time to kick.
*Source:* experience README.

**R18. Check whether the current model already handles a scenario before
training on it.** The moving ball (v51) cost accuracy while the untrained v50d
already coped (0.95 vs 0.97 goals). *Source:* LESSONS §6.3.

**R19. Every new randomisation costs 5–20 % goals at first** (v48b, v50,
v51). Keep each mild, one per run, stop early if goals drift. 5 % detection
dropout + friction 0.5 made the policy cautious (~20 % fewer goals). *Source:*
ATTACK_PLAN risks, LESSONS §4.5.

## Skills that shaping can't find

**R20. Some skills can't be discovered by shaping alone.** Side kicks:
relaxing line-up terms changed nothing, a direct bonus reached ~3 %. A rising
target-angle curriculum (B-Human style) did teach the inside foot (88 % of
short kicks) where a fixed 90° target found 1 %. *Source:* LESSONS §3.8,
KICK_STYLES.

**R21. Let an existing skill do a new job by changing what it sees.** A
virtual ball beside the robot while the real one is lost reused
turn-toward-ball as a search spin (net turn 0.34 → 1.8 rad, v56d). The runner
must run the same rule. *Source:* LESSONS §3.13.

**R22. Free style choice collapses onto the most rewarded style** (hop for
everything, sty_free); scaling a side-kick bonus by speed removed side kicks
because they are slower (dribble v38). *Source:* experience README, memory.

**R23. Under self-play, re-audit every positive shaping term for farming.**
`search_turn` was farmed because the opponent takes the ball away; stage 3's
`walk_speed` paid following a carried-away ball. *Source:* memory
k1-striker-selfplay.

**R24. Annealing technique terms degrades technique.** Goals and territory
don't hold kick technique; anneal only positioning shaping, with a floor.
*Source:* memory k1-striker-selfplay.

## Style prior (AMP)

**R25. An unconditioned style prior copies the clips' posture.** A faster AMP
mix leaned the dribble 16° forward (v19); conditioning style on the command
(v20) helped a little. Raising the AMP style weight cuts task rewards
((1−w)·task). *Source:* memory k1-dribble-speed, k1-kick-staged-training.

**R26. Turn style off where the task needs freedom** (near the ball, around
the kick), and gate walking-pose terms to ball > 1 m; gating them up to 0.6 m
cost kick quality. *Source:* memory k1-kick-staged-training.

**R27. Weight blending the dribble and kick skills gives the worst of both**
(dribble v22 × v24 blends). Kick-loop blends with the champion, by contrast,
were the main promotion route. *Source:* memory k1-dribble-speed, experience.
