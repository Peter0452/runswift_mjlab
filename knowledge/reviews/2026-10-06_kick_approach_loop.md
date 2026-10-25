# Kick approach loop (2026-10-06)

Recorded here as a review after the fact; the originals are unchanged.

- **Trigger:** the stage-3 kick plateaued behind B-Human on long power, time
  to first kick and aim.
- **Question:** which external methods can close the gaps (the `gaps:` table
  in `docs/approach_catalogue.yaml`: long kick 6.90 vs 8.27 m/s, first kick
  3.54 vs 2.94 s, aim 91 vs 98 %, ...) within one end-to-end 83-input policy?
- **Search:** local clones of related work: B-Human IsaacGymRL,
  humanoid-soccer, RoboNaldo, GMR, APEX, htwk-gym, DribbleMaster, harbor-rl,
  plus our own benchmark v2 findings.
- **Sources and approaches:** now in `knowledge/sources/` and
  `knowledge/approaches/` (every catalogue atom has a card).
- **Design and ranking:** `docs/K1_KICK_APPROACH_LOOP_DESIGN.md` (L5 loop),
  `docs/evolution/l5_requests.md` (atoms that still need an adapter).
- **Outcome:** momentum kick and planted support adopted; torque clip adopted;
  side-foot strike not discovered by shaping; B-Human action imitation
  rejected (uses u008, u014-u017).
