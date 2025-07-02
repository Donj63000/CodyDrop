import math
from functools import reduce
from typing import Iterable

from .models import GameVersion

__all__ = [
    "indiv_prob",
    "group_prob",
    "fight_prob",
    "fights_needed",
    "cumulative",
]

CAP_RETRO = 0.9
_SIG_A = 0.74
_SIG_B = 1.756
_SIG_K = 85
_SIG_X0 = 250


def indiv_prob(
    base_rate: float,
    pp: float,
    version: GameVersion = GameVersion.RETRO,
    cap: float | None = None,
) -> float:
    """Probability for one character in a single fight."""
    if version is GameVersion.V2:
        mult = _SIG_A + _SIG_B / (1 + math.exp((_SIG_X0 - pp) / _SIG_K))
        p = base_rate * mult
    else:  # rétro linéaire
        p = base_rate * pp / 100
    if cap is None and version is GameVersion.RETRO:
        cap = CAP_RETRO
    if cap is not None:
        p = min(cap, p)
    return max(0.0, p)


def group_prob(
    base_rate: float,
    pp_values: Iterable[float],
    version: GameVersion = GameVersion.RETRO,
) -> float:
    """Probability that at least one character drops."""
    inv_prod = reduce(
        lambda a, b: a * (1 - b),
        (indiv_prob(base_rate, pp, version) for pp in pp_values),
        1.0,
    )
    return 1 - inv_prod


def fight_prob(
    base_rate: float,
    pp_values: Iterable[float],
    monsters: int = 1,
    version: GameVersion = GameVersion.RETRO,
) -> float:
    per = group_prob(base_rate, pp_values, version)
    return 1 - (1 - per) ** monsters


def fights_needed(target_p: float, p_fight: float) -> int | float:
    """Combats mini pour atteindre 'target_p'."""
    if p_fight <= 0:
        return math.inf
    return math.ceil(math.log1p(-target_p) / math.log1p(-p_fight))


def cumulative(p_fight: float, n: int) -> float:
    return 1 - (1 - p_fight) ** n
