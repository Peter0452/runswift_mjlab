"""Approach knowledge: cards (knowledge/approaches/<element>/<id>.md), sources
(knowledge/sources/<id>.md), uses (knowledge/uses/uses.yaml), the symptom index
(knowledge/approaches/symptoms.yaml: measured gap -> goal tags) and literature
reviews (knowledge/reviews/*.md; an approved review's ``shortlist`` feeds the
engine's approach designer).

A card's ``trial`` says how the engine can switch the approach on in a recipe:
``{methods: {<registry name>: {params}}}`` and/or ``{genes: {<gene>: value}}``;
``null`` when it needs building, a runtime change or a person. Its ``tune``
lists the parameters the engine may step once the approach is on:
``{"methods.<name>.<param>" | "genes.<gene>": {range: [lo, hi], tags: [...]}}``.

Cards and sources are Markdown with YAML front matter; ``check()`` lists every
broken cross-reference (a card without its registry entry, a use naming a
missing approach or source, ...) so the knowledge stays one connected graph:
source -> approach -> use.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from k1.approaches.registry import APPROACHES, CARDS, ELEMENTS, IMPACTS, STATUSES

KNOWLEDGE = CARDS.parent
SOURCES = KNOWLEDGE / "sources"
USES = KNOWLEDGE / "uses" / "uses.yaml"
SYMPTOMS = CARDS / "symptoms.yaml"
REVIEWS = KNOWLEDGE / "reviews"
CARD_FIELDS = (
  "id", "title", "element", "also", "tags", "status", "impact", "sources",
  "registry", "trial", "tune",
)  # fmt: skip
TAGS = (
  "imitation", "style", "exploration", "sample-efficiency", "sim2real", "perception",
  "smoothness", "stability", "multi-skill", "multi-objective", "safety", "power",
  "accuracy", "speed",
)  # fmt: skip
SOURCE_KINDS = ("paper", "repo", "ours")
RESULTS = ("positive", "negative", "mixed", "none")


@dataclass(frozen=True)
class Card:
  meta: dict[str, Any]
  path: Path

  @property
  def id(self) -> str:
    return self.meta["id"]


def front_matter(path: Path) -> dict[str, Any]:
  text = path.read_text()
  if not text.startswith("---\n"):
    raise ValueError(f"{path}: no front matter")
  return yaml.safe_load(text[4 : text.index("\n---", 4)]) or {}


def cards() -> dict[str, Card]:
  out = {}
  for path in sorted(CARDS.glob("*/*.md")):
    if path.name == "README.md":
      continue
    meta = front_matter(path)
    out[meta["id"]] = Card(meta, path)
  return out


def sources() -> dict[str, dict[str, Any]]:
  return {
    p.stem: front_matter(p) for p in sorted(SOURCES.glob("*.md")) if p.stem != "README"
  }


def uses() -> list[dict[str, Any]]:
  return yaml.safe_load(USES.read_text()) or []


def symptoms() -> dict[str, Any]:
  return yaml.safe_load(SYMPTOMS.read_text()) or {}


def reviews() -> dict[str, dict[str, Any]]:
  """Front matter of each review (``{}`` for a review without one)."""
  out = {}
  for path in sorted(REVIEWS.glob("*.md")):
    if path.name == "README.md":
      continue
    has_meta = path.read_text().startswith("---\n")
    out[path.stem] = front_matter(path) if has_meta else {}
  return out


def approved_shortlist(task: str) -> list[dict[str, Any]]:
  """Shortlist entries of approved reviews for a task, newest review first."""
  out = []
  for name, meta in sorted(reviews().items(), reverse=True):
    if meta.get("approved") and meta.get("task") == task:
      out += [{**e, "review": name} for e in meta.get("shortlist") or []]
  return out


def uses_of(approach: str) -> list[dict[str, Any]]:
  return [u for u in uses() if u["approach"] == approach]


def check() -> list[str]:
  """Every broken field or cross-reference in the approach knowledge."""
  problems = []
  cs, ss, us = cards(), sources(), uses()
  for cid, c in cs.items():
    m, where = c.meta, c.path.relative_to(KNOWLEDGE)
    if list(m) != list(CARD_FIELDS):
      problems.append(f"{where}: fields must be {CARD_FIELDS}")
      continue
    if c.path.stem != cid or c.path.parent.name != m["element"]:
      problems.append(f"{where}: must be at approaches/{m['element']}/{cid}.md")
    if m["element"] not in ELEMENTS or any(e not in ELEMENTS for e in m["also"]):
      problems.append(f"{where}: unknown element")
    if m["status"] not in STATUSES or m["impact"] not in IMPACTS:
      problems.append(f"{where}: bad status or impact")
    problems += [f"{where}: unknown source {s}" for s in m["sources"] if s not in ss]
    problems += [f"{where}: unknown tag {t}" for t in m["tags"] if t not in TAGS]
    trial = m["trial"]
    if trial is not None:
      if not trial or set(trial) - {"methods", "genes"}:
        problems.append(f"{where}: trial takes methods and/or genes")
      for name in (trial.get("methods") or {}) if isinstance(trial, dict) else []:
        if name not in APPROACHES:
          problems.append(f"{where}: trial method {name} not in the registry")
      if m["impact"] == "runtime":
        problems.append(f"{where}: a runtime approach can't have an engine trial")
    for path, spec in (m["tune"] or {}).items():
      kind, _, rest = path.partition(".")
      if kind not in ("methods", "genes") or not rest:
        problems.append(f"{where}: tune path {path} must start methods. or genes.")
      elif kind == "methods" and rest.split(".")[0] not in APPROACHES:
        problems.append(f"{where}: tune path {path} names no registry entry")
      lo, hi = spec.get("range", (None, None))
      if lo is None or hi is None or not lo < hi:
        problems.append(f"{where}: tune {path} needs range [lo, hi] with lo < hi")
      problems += [f"{where}: tune {path}: unknown tag {t}"
                   for t in spec.get("tags", []) if t not in TAGS]  # fmt: skip
    if m["tune"] and m["impact"] == "runtime":
      problems.append(f"{where}: a runtime approach can't be tuned by the engine")
    reg = m["registry"]
    if reg is not None:
      a = APPROACHES.get(reg)
      if a is None:
        problems.append(f"{where}: registry entry {reg} missing")
      elif (a.element, a.status, a.impact) != (m["element"], m["status"], m["impact"]):
        problems.append(f"{where}: element/status/impact differ from the registry")
  for name in APPROACHES:
    if not any(c.meta.get("registry") == name for c in cs.values()):
      problems.append(f"registry entry {name} has no card")
  for sid, s in ss.items():
    if s.get("id") != sid or s.get("kind") not in SOURCE_KINDS:
      problems.append(f"sources/{sid}.md: bad id or kind")
    problems += [
      f"sources/{sid}.md: unknown approach {a}"
      for a in s.get("approaches", [])
      if a not in cs
    ]
  for family, spec in symptoms().items():
    for metric, entry in (spec.get("metrics") or {}).items():
      problems += [
        f"symptoms {family}.{metric}: unknown tag {t}"
        for t in entry["tags"]
        if t not in TAGS
      ]
    for word, tags in (spec.get("situations") or {}).items():
      problems += [
        f"symptoms {family}.{word}: unknown tag {t}" for t in tags if t not in TAGS
      ]
  for name, meta in reviews().items():
    for e in meta.get("shortlist") or []:
      if e.get("approach") not in cs:
        problems.append(f"reviews/{name}: shortlist names unknown approach {e}")
  seen = set()
  for u in us:
    uid = u.get("id")
    if uid in seen:
      problems.append(f"uses: duplicate id {uid}")
    seen.add(uid)
    if u.get("approach") not in cs:
      problems.append(f"uses {uid}: unknown approach {u.get('approach')}")
    if u.get("source") not in ss:
      problems.append(f"uses {uid}: unknown source {u.get('source')}")
    if u.get("result") not in RESULTS:
      problems.append(f"uses {uid}: result must be one of {RESULTS}")
  return problems
