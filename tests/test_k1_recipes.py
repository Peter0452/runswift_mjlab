"""Every recipe in experiments/recipes builds and is true to the code."""

from pathlib import Path

import pytest

from k1 import recipes

H022_RUN = recipes.ROOT / "logs/rsl_rl/k1_kick_stage3_amp/2026-10-09_07-17-43_h022_c2"


@pytest.mark.slow
@pytest.mark.parametrize(
  "path", recipes.all_recipes(), ids=lambda p: str(Path(p).relative_to(recipes.RECIPES))
)
def test_recipe_checks_clean(path: Path) -> None:
  assert recipes.check(path) == []


@pytest.mark.slow
@pytest.mark.skipif(not H022_RUN.is_dir(), reason="champion run not on disk")
@pytest.mark.skip(reason="h022 trained on our old ball, removed 2026-10-28")
def test_h022_recipe_reproduces_the_champion_run() -> None:
  path = recipes.RECIPES / "kick" / "kick_stage3_h022.yaml"
  # Only the speed caps differ: the chase caps (user decision 2026-10-23) are
  # wider than the caps h022 trained with.
  out = recipes.diff(path, H022_RUN)
  assert [line.split(":")[0] for line in out] == [
    "env commands.twist.speed_cap_final",
    "env commands.twist.speed_cap_start_max",
  ]
