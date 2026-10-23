"""Loop state: one JSON file, one writer, safe to resume after a crash.

Writes go to a temporary file and are renamed into place, so a crash never
leaves half a state; a lock file keeps a second loop from writing at once.
"""

from __future__ import annotations

import json
import os
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterator

from k1.recipes import ROOT

DIR = ROOT / "experiments" / "evolution"


@dataclass
class State:
  champion: dict[str, Any]  # {"recipe": path, "checkpoint": path, "verdict": {...}}
  in_flight: list[dict[str, Any]] = field(default_factory=list)
  history: list[dict[str, Any]] = field(default_factory=list)
  non_improving: int = 0
  counter: int = 0

  def next_id(self) -> str:
    self.counter += 1
    return f"e{self.counter:04d}"


def load(path: Path) -> State:
  return State(**json.loads(path.read_text()))


def save(state: State, path: Path) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  tmp = path.with_suffix(".tmp")
  tmp.write_text(json.dumps(asdict(state), indent=2, default=str))
  os.replace(tmp, path)


@contextmanager
def single_writer(path: Path) -> Iterator[None]:
  """Hold ``<state>.lock`` for the duration; refuse if another loop holds it."""
  lock = path.with_suffix(".lock")
  lock.parent.mkdir(parents=True, exist_ok=True)
  try:
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
  except FileExistsError:
    raise RuntimeError(
      f"another loop holds {lock} (delete it if that loop is dead)"
    ) from None
  try:
    os.write(fd, str(os.getpid()).encode())
    yield
  finally:
    os.close(fd)
    lock.unlink(missing_ok=True)
