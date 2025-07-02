import importlib.util
from pathlib import Path
import sys

import pytest

# Dynamically load the module since its filename contains a hyphen
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
module_path = root / "test-cody.py"
spec = importlib.util.spec_from_file_location("cody", module_path)
cody = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cody)


def test_indiv_prob_typical():
    """individual probability with 100 PP and 0.02% base rate"""
    prob = cody.indiv_prob(0.0002, 100)
    assert prob == pytest.approx(0.0002)


def test_group_prob_multiple_characters():
    pp_values = [100, 150, 120]
    result = cody.group_prob(0.0002, pp_values)
    expected = 1.0
    for pp in pp_values:
        expected *= 1 - cody.indiv_prob(0.0002, pp)
    expected = 1 - expected
    assert result == pytest.approx(expected)


def test_fights_needed_typical():
    assert cody.fights_needed(0.5, 0.1) == 7


def test_cumulative_typical():
    assert cody.cumulative(0.2, 3) == pytest.approx(0.488)
