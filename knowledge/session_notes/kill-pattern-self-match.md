---
name: kill-pattern-self-match
description: pgrep/pkill -f on a run name kills my own shell if that command also contains the name (e.g. a launch of stage3_v52b while killing stage3_v52)
metadata:
  type: feedback
---
Never put `pgrep -f`/`pkill -f "<run-name>"` in the same Bash command as a launch or edit whose text contains that run name (or a longer name with it as a prefix, e.g. killing `stage3_v52` while launching `stage3_v52b`). The pattern matches the shell's own command line, the shell dies (exit 144) and the rest of the command never runs. Happened three times in the K1 kick work (2026-10-03) and again 2026-10-06 (killing `blend_search.py x4_g004` in the same command that relaunched it).

**Why:** silently skipped edits/launches and wasted GPU time.
**How to apply:** kill by PID in its own Bash call, with an anchored pattern like `"[r]un-name stage3_v52 "` or check `ps` first; launch in a separate call. Related: [[k1-kick-staged-training]]
