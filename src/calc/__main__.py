from .graph import DropCalc
from .core import fight_prob, fights_needed, cumulative


if __name__ == "__main__":
    app = DropCalc(fight_prob, fights_needed, cumulative)
    app.mainloop()
