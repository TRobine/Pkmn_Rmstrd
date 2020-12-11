import json
import pickle
import sys
from pathlib import Path
from typing import Dict, Union

import numpy as np
import pandas as pd
from loguru import logger

from pokejdr.base_stats import NATURES_DF, POKEMONS_DF
from pokejdr.constants import LOGURU_FORMAT
from pokejdr.models.base import Element

logger.add(sys.stderr, format=LOGURU_FORMAT)


# ----- Models ----- #

# TODO: maybe store all stats once initialized to get as 'base_stats' that can be used in leveling.
class Trainer(Element):

    # ----- Experience Functionality ----- #

    # def level_up(self) -> None:
    #     """
    #     Convenience function to increment the pokemon's level and trigger an update of its stats.
    #     """
    #     self.level += 1
    #     self._update_stats_on_levelup()
    #
    # @logger.catch()
    # def _update_stats_on_levelup(self) -> None:
    #     """
    #     Called when the level attribute is changed, triggering a re-calculation of the
    #     pokemon's stats based on its EVs.
    #     """
    #     logger.info(f"{self.name} has reached level {self.level}, updating stats now.")
    #     defaults: Pokemon = _base_pokemon_stats(self.name)
    #     nature_stat: pd.DataFrame = NATURES_DF[NATURES_DF.nature == self.nature]
    #     self.health = (
    #         (2 * defaults.health + self.iv[0] + self.ev[0] / 4) * self.level / 100 + self.level + 10
    #     )
    #     self.attack = (
    #         (2 * defaults.attack + self.iv[1] + self.ev[1] / 4) * self.level / 100 + 5
    #     ) * nature_stat.attack.to_numpy()[0]
    #     self.defense = (
    #         (2 * defaults.defense + self.iv[2] + self.ev[2] / 4) * self.level / 100 + 5
    #     ) * nature_stat.defense.to_numpy()[0]
    #     self.special_attack = (
    #         (2 * defaults.special_attack + self.iv[3] + self.ev[3] / 4) * self.level / 100 + 5
    #     ) * nature_stat.special_attack.to_numpy()[0]
    #     self.special_defense = (
    #         (2 * defaults.special_defense + self.iv[4] + self.ev[4] / 4) * self.level / 100 + 5
    #     ) * nature_stat.special_defense.to_numpy()[0]
    #     self.speed = (
    #         (2 * defaults.speed + self.iv[5] + self.ev[5] / 4) * self.level / 100 + 5
    #     ) * nature_stat.speed.to_numpy()[0]
    #     logger.debug(f"{self.name}'s stats have been updated!")

    # ----- I/O Functionality ----- #

    def to_json(self, json_file: Union[Path, str]) -> None:
        """
        Export the instance's data to disk in the JSON format.

        Args:
            json_file (Union[Path, str]): PosixPath object or string with the save file location.
        """
        logger.info(f"Saving Pokemon data as JSON at '{Path(json_file).absolute()}'")
        with Path(json_file).open("w") as disk_data:
            json.dump(self.dict(), disk_data)

    @classmethod
    def from_json(cls, json_file: Union[Path, str]):
        """
        Load a Pokemon instance's data from disk, saved in the JSON format.

        Args:
            json_file (Union[Path, str]): PosixPath object or string with the save file location.
        """
        logger.info(f"Loading JSON Pokemon data from file at '{Path(json_file).absolute()}'")
        return cls.parse_file(json_file, content_type="application/json")

    def to_pickle(self, pickle_file: Union[Path, str]) -> None:
        """
        Export the instance's data to disk as serialized binary data.

        Args:
            pickle_file (Union[Path, str]): PosixPath object or string with the save file location.
        """
        logger.info(f"Saving Pokemon data as PICKLE at '{Path(pickle_file).absolute()}'")
        with Path(pickle_file).open("wb") as disk_data:
            pickle.dump(self, disk_data)

    @classmethod
    def from_pickle(cls, pickle_file: Union[Path, str]):
        """
        Load a Pokemon instance's data from disk, saved as serialized binary data.

        Args:
            pickle_file (Union[Path, str]): PosixPath object or string with the save file location.
        """
        logger.info(f"Loading PICKLE Pokemon data from file at '{Path(pickle_file).absolute()}'")
        return cls.parse_file(pickle_file, content_type="application/pickle", allow_pickle=True)
