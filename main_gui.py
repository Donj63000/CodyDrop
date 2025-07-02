# Import core probability functions
from calc.graph import DropCalc
from calc.core import fight_prob, fights_needed, cumulative

# --------------------------------------------------
#  ---  LANCEMENT  ---------------------------------
# --------------------------------------------------

if __name__ == "__main__":
    app = DropCalc(fight_prob, fights_needed, cumulative)
    app.mainloop()
