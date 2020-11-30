# Pokejdr

This package provides functionality for our pokemon role playing game.

## Installing

The `omc3` package is `Python 3.6+` compatible.
The best way to install is though pip:
```bash
pip install pokejdr
```

One can also install from source through VCS:
```bash
git clone https://github.com/TRobine/Pkmn_Rmstrd.git
cd Pkmn_Rmstrd
pip install .
```

Or simply from the online master branch, which is stable:
```bash
pip install git+https://github.com/TRobine/Pkmn_Rmstrd.git#egg=pokejdr
```

## Running

Functionality is provided through a single high level object, named `Pokemon`.
You can be set up with a single line:
```python
from pokejdr import Pokemon
```

A demo jupyter notebook to walk through most of the implemented functionality can be found in the [notebooks](notebooks) folder.

## License

This project is licensed under the `MIT License` - see the [LICENSE](LICENSE) file for details.