import math
from functools import reduce
from itertools import repeat

from graph import DropCalc

# --------------------------------------------------
#  ---  LOGIQUE  -----------------------------------
# --------------------------------------------------

def indiv_prob(base_rate: float, pp: float) -> float:
    """Probabilité individuelle (décimale) pour un perso."""
    return max(0.0, min(1.0, base_rate * pp / 100))


def group_prob(base_rate: float, pp_values) -> float:
    """Proba décimale qu'au moins un perso drop, PP hétérogènes."""
    inv_prod = reduce(lambda a, b: a * (1 - b),
                      (indiv_prob(base_rate, p) for p in pp_values),
                      1.0)
    return 1 - inv_prod


def fights_needed(target_p: float, p_fight: float) -> int | float:
    """Combats mini pour atteindre 'target_p'."""
    if p_fight <= 0:
        return math.inf
    return math.ceil(math.log1p(-target_p) / math.log1p(-p_fight))


def cumulative(p_fight: float, n: int) -> float:
    return 1 - (1 - p_fight) ** n


# --------------------------------------------------
#  ---  LANCEMENT  ---------------------------------
# --------------------------------------------------

if __name__ == "__main__":
    app = DropCalc(group_prob, fights_needed, cumulative)
    app.mainloop()