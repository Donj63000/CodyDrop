from enum import Enum, auto


class GameVersion(Enum):
    RETRO = auto()  # formule linéaire PP/100
    V2 = auto()     # formule sigmoïde 2.42+
