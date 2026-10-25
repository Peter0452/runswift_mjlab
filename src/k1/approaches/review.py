"""Literature reviews, started from measured gaps (``rsw review``).

``new`` writes a review skeleton in ``knowledge/reviews/<date>_<topic>.md``:

- front matter: ``task``, ``trigger``, ``gaps``, ``approved: false``, an empty
  ``shortlist``
- body: the question with the measured numbers, what the knowledge base already
  holds for the gap tags (runnable approaches, blocked ones, rejected ones with
  their uses), and the procedure

The research itself (search related tasks, read papers and local clones, write
source records and cards, judge fit, fill the shortlist) is done by a person or
an agent (``.claude/commands/review.md``). Once the requester approves
(``rsw review approve NAME --agreed``), the shortlist feeds the engine's
approach designer, ahead of tag matches.
"""

from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Any

import yaml

from k1.approaches import knowledge
from k1.engine.gaps import Gap

TASKS = {"kick": "Mjlab-Velocity-Kick-Stage3-Amp-DA-Muon-Booster-K1"}


def gaps_for(family: str, top: int = 8) -> list[Gap]:
  from k1.engine.gaps import champion_gaps

  task = TASKS.get(family)
  if task is None:
    raise KeyError(f"no measured gaps for {family!r} yet (judged: {sorted(TASKS)})")
  seen, out = set(), []
  for g in champion_gaps(task):
    key = (g.key, g.metric)  # one line per situation and metric (caps merged)
    if key not in seen:
      seen.add(key)
      out.append(g)
  return out[:top]


def knowledge_for(tags: set[str]) -> dict[str, list[tuple[Any, list]]]:
  """Cards matching any tag, grouped: runnable / blocked / rejected-or-parked."""
  groups: dict[str, list[tuple[Any, list]]] = {
    "runnable": [],
    "blocked": [],
    "rejected": [],
  }
  for card in knowledge.cards().values():
    m = card.meta
    if not set(m["tags"]) & tags:
      continue
    if m["status"] in ("rejected", "parked"):
      group = "rejected"
    elif m["trial"] is None or m["impact"] == "runtime":
      group = "blocked"
    else:
      group = "runnable"
    groups[group].append((card, knowledge.uses_of(card.id)))
  return groups


def _card_line(card: Any, uses: list) -> str:
  m = card.meta
  u = "; ".join(f"{x['id']} {x['task']} {x['result']}" for x in uses) or "no uses"
  return f"- `{card.id}` ({m['element']}, {m['status']}, {', '.join(m['tags'])}): {u}"


def new(topic: str, family: str, trigger: str, top: int = 8) -> Path:
  gaps = gaps_for(family, top)
  tags = {t for g in gaps for t in g.tags}
  groups = knowledge_for(tags)
  slug = re.sub(r"[^a-z0-9]+", "_", topic.lower()).strip("_")
  path = knowledge.REVIEWS / f"{time.strftime('%Y-%m-%d')}_{slug}.md"
  if path.exists():
    raise FileExistsError(path)
  meta = {
    "task": family,
    "trigger": trigger,
    "gaps": [g.describe() for g in gaps],
    "tags": sorted(tags),
    "approved": False,
    "shortlist": [],
  }
  body = [
    f"# {topic}",
    "",
    f"- **Trigger:** {trigger}",
    f"- **Question:** which approaches could close these gaps of the {family} "
    "champion (benchmark v2, full, seed 1; vs B-Human or the 0-falls target)?",
    "",
    *[f"  {i + 1}. {g.describe()}" for i, g in enumerate(gaps)],
    "",
    "## What the knowledge base already holds (tags: " + ", ".join(sorted(tags)) + ")",
    "",
    "Runnable by the engine (have a `trial`):",
    *[_card_line(c, u) for c, u in groups["runnable"]],
    "",
    "Matching, but need building, a runtime change or a person:",
    *[_card_line(c, u) for c, u in groups["blocked"]],
    "",
    "Rejected or parked (a retry needs a new reason):",
    *[_card_line(c, u) for c, u in groups["rejected"]],
    "",
    "## Search",
    "",
    "(Related tasks first: humanoid soccer, kicking, dribbling, multi-skill; then "
    "methods for the tags above. Record queries and where you looked.)",
    "",
    "## Sources found",
    "",
    "(Each becomes or updates `knowledge/sources/<id>.md`, approach as elements.)",
    "",
    "## Approaches extracted",
    "",
    "(New or updated cards; give a `trial` only when a recipe can apply it: "
    "registered approach parameters or genes.)",
    "",
    "## Fit for our task",
    "",
    "(Per candidate: relevance to a gap above, fit, evidence transfer from their "
    "robot and setting, cost and risk, our track record.)",
    "",
    "## Shortlist",
    "",
    "(Ranked; mirror it in the front matter `shortlist:` as "
    "`{approach, gap, hypothesis}`; the engine reads it once approved.)",
    "",
    "## Outcome",
    "",
    "(Later: links to the use records the trials produced.)",
    "",
  ]
  path.write_text(
    "---\n"
    + yaml.safe_dump(meta, sort_keys=False, width=88)
    + "---\n\n"
    + "\n".join(body)
  )
  return path


def approve(name: str) -> Path:
  """Set ``approved: true`` (the requester's sign-off is the caller's job)."""
  path = knowledge.REVIEWS / f"{name.removesuffix('.md')}.md"
  meta = knowledge.front_matter(path)
  if not meta.get("shortlist"):
    raise ValueError(f"{path.name}: empty shortlist, nothing to approve")
  text = path.read_text()
  path.write_text(text.replace("\napproved: false\n", "\napproved: true\n", 1))
  return path
