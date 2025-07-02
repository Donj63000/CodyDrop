# Import core probability functions
from graph import DropCalc
from calc.core import (
    indiv_prob,
    group_prob,
    fights_needed,
    cumulative,
)

# --------------------------------------------------
#  ---  LANCEMENT  ---------------------------------
# --------------------------------------------------

if __name__ == "__main__":
    app = DropCalc(group_prob, fights_needed, cumulative)
    app.mainloop()
