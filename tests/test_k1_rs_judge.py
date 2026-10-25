"""Paired comparisons of the runswift-spec kick judge."""

import pytest

from k1.eval import rs_judge


def test_paired_margin_and_interval() -> None:
  p = rs_judge.paired([1.0, 0.8, 0.9, 1.0], [0.9, 0.8, 0.8, 0.9])
  assert p.mean == pytest.approx(0.075)
  assert p.lo < p.mean < p.hi


def test_paired_needs_the_same_trials() -> None:
  with pytest.raises(ValueError):
    rs_judge.paired([1.0], [1.0, 0.5])


def test_references_exist() -> None:
  assert all(path.is_file() for path in rs_judge.BHUMAN.values())
  assert all(path.is_file() for path in rs_judge.CHAMPION.values())
