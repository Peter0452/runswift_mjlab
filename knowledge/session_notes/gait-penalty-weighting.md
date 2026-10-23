---
name: gait-penalty-weighting
description: "Gait-shaping terms (flat foot etc.) must stay light; target the AMP walk's own levels, not maximum flatness, and avoid heavy foot contact"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 18ee3867-4055-4a59-a7b5-2a798a71780f
  modified: 2026-10-19T23:12:15.813Z
---

When adding gait-shaping penalties (for example foot_flat against tiptoe walking), weight them lightly. The user (2026-10-20) stopped a −200 foot_flat for the dribble: "dont weight it too much causing heavy feet contact, should be feet flat of 70-80 percent amp walk, whilst stable".

**Why:** strong pose penalties make the robot slap its feet down, which stresses the ankles and the robot as much as tiptoeing does.

**How to apply:**
- Target the deployed AMP walk's own numbers in the runner sim: amp_models/model_9950 has 73% flat stance and a first loaded step of 0.77× body weight (p90 0.91).
- Measure flat stance and landing force (scratchpad tiptoe_sim.py) on every checkpoint, alongside success and falls.
- Start low (−30 for foot_flat) with the settle window.

Related: [[k1-dribble-speed]].
