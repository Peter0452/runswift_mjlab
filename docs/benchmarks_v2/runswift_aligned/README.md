# runswift harness, aligned variants (2026-10-09)

Prefixes (see docs/evolution/monitor.md, 2026-10-09):
- `mf_*`  mesh feet (training foot mesh instead of 1 cm sole capsules), pelvis ball origin, runner default caps
- `al_*`  mesh feet + ball from the soles midpoint (KC_BALL_FEET=1, like training and like B-Human's input)
- `alhi_*` as al_, caps 2.0/1.5/1.5 (KC_CAPS)
- `alvis_*` as alhi_, camera perception (KC_VISION=1, what the deployed runner gets) instead of truth inputs
- `ns_*`  as alhi_, robot self-collision off
- `bhuman_*`, `al_bhuman_goal`, `mf_bhuman_near`: B-Human on the mesh-feet scene (its own soles input, truth)

Reproduce with `scripts/tools/rsw_aligned.sh` (+ KC_VISION=1 in the environment for alvis).
