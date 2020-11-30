"""

WARNING: If updating these files with newer data, make sure to save the new data by specifying
the pickle protocol to be 4 for backwards compatibility with older Python versions (since pokejdr
is Python3.6+)
"""

from pathlib import Path

import pandas as pd

NATURES_DF = pd.read_pickle(Path(__file__).parent / "data" / "natures_en.pkl")
POKEMONS_DF = pd.read_pickle(Path(__file__).parent / "data" / "pokemons_en.pkl")
