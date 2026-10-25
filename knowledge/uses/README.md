# Uses

A use records one application of an approach (or part of one) in one task:
what we took, from which source, in what context, and what happened. Uses are
how results come back into the knowledge base, and how an approach is reused
or repurposed later: the context says why it worked or didn't.

All uses are in `uses.yaml`, one entry each:

| Field | Meaning |
|---|---|
| `id` | `uNNN`, never reused |
| `approach` | card id in `knowledge/approaches/` |
| `source` | source id in `knowledge/sources/` the idea came from (`ours` for our own) |
| `part` | which part of the approach was used |
| `task` | task family or task request (`kick`, `dribble`, `selfplay`, `striker`, `walk`, ...) |
| `context` | the run(s), lineage, situation |
| `settings` | key parameters (optional) |
| `result` | `positive`, `negative`, `mixed` or `none` (not tested) |
| `finding` | what happened, with numbers |
| `evidence` | where the full record is: a knowledge page, a doc, or a run's `run.json` |
| `date` | when the result was recorded (optional) |
| `status_effect` | how it changed the approach's status (optional) |

Rules: negative results stay (they stop repeats); a use cites our evidence,
never a paper's claim; the engine appends a use when a verdict on a run that
changed one approach comes back (not built yet: added by hand until then).
