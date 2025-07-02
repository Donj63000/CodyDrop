import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from calc.core import indiv_prob, group_prob, fights_needed, cumulative
from calc.models import GameVersion


def test_indiv_prob_retro():
    assert indiv_prob(0.0002, 100) == pytest.approx(0.0002)


def test_indiv_prob_v2():
    assert indiv_prob(0.0002, 200, GameVersion.V2) == pytest.approx(0.0002734, rel=1e-4)


def test_group_prob_multiple_characters():
    pp_values = [100, 150, 120]
    expected = 1.0
    for pp in pp_values:
        expected *= 1 - indiv_prob(0.0002, pp)
    expected = 1 - expected
    assert group_prob(0.0002, pp_values) == pytest.approx(expected)


def test_fights_needed_typical():
    assert fights_needed(0.5, 0.1) == 7


def test_cumulative_typical():
    assert cumulative(0.2, 3) == pytest.approx(0.488)
