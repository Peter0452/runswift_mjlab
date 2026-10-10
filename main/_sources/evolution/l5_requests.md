# L5 atoms without an adapter (need code before the loop can test them)

- bhuman_isaacgymrl/side_foot_kick (reward + data (RSI / AMP clips)): strike with the inside of the foot (sole yaw ~90 deg to kick direction)
- bhuman_isaacgymrl/continuous_range_and_strong_flag (reward + obs semantics (slots 80-82, same dims, runner change)): kick speed command from a continuous range + strong-kick flag, Gaussian speed reward
- humanoid_soccer/privileged_teacher_dagger (algorithm (student = our 83-input policy)): privileged teacher (true ball, no vision noise) distilled by DAgger into a noisy-input student
- humanoid_soccer/np3o_constrained (algorithm / constraints (= our L2 plan)): constrained RL (N-P3O) refinement; heterogeneous credit assignment for smooth kicks
- robonaldo/g1_kick_reference (data): right-foot push-kick motion (motions/right_kick.npz), retargetable to K1 with GMR
- gmr/retarget_human_kicks (data): retarget human soccer kicks (side-foot, instep drive) to K1 as AMP / RSI clips
- gmr/retarget_slow_cadence_walks (data): walking clips with longer steps / lower cadence for the AMP set
- apex/action_prior_exploration (algorithm): bias exploration with action priors from reference motions
- htwk_gym/parameterised_gait (reward): step length / frequency terms for controllable cadence
- harbor_rl/reward_tuning_engine (tooling): host the reward-grammar / proposer loops
