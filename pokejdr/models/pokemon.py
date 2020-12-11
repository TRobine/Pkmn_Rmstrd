import json
import pickle
import sys
from pathlib import Path
from random import uniform
from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd
from loguru import logger
from pydantic import BaseModel, PositiveInt, validator

from pokejdr.base_stats import NATURES_DF, POKEMONS_DF
from pokejdr.constants import LOGURU_FORMAT
from pokejdr.models.base import Element
from pokejdr.models.utils import dealt_damage

logger.add(sys.stderr, format=LOGURU_FORMAT)


# ----- Models ----- #


class Pokemon(Element):

    # ----- Experience Functionality ----- #

    def experience_given(self, contextual_bonus: float = 1) -> int:
        """
        Calculate the experience gained from defeating this Pokemon in combat.

        Args:
            contextual_bonus (float): a bonus coefficient depending on context such as an object
                held by the pokemon. Defaults to 1.

        Returns:
            The amount of experience gained.
        """
        experience = round(contextual_bonus * self.base_xp * self.level / 7)
        logger.info(f"{experience} experience is gained for defeating {self.name}")
        logger.info(f"The following EV are gained for defeating {self.name}: {self.base_ev}")
        return experience

    def experience_to_level(self, target_level: int, leveling_type: str) -> int:
        """
        Calculate the total amount of experience to reach the next level. Take in account that
        this is the amount of experience needed from 0, not from the current level.

        Args:
            target_level (int): the level to reach.
            leveling_type (str): name of the leveling curve for the pokemon.

        Returns:
            The total experience needed to reach the target level.
        """
        _assert_valid_leveling_cruve(leveling_type)
        _assert_valid_target_level(target_level)
        required_experience = round(LEVELING_CURVES[leveling_type](target_level))
        logger.info(
            f"The amount of experience {self.name} needs to reach level {target_level} "
            f"is {required_experience:,}".replace(",", " ")
        )
        return required_experience

    def experience_to_next_level(self, leveling_type: str) -> int:
        """
        Calculate the total amount of experience to go from the pokemon's current level to the next
        level. This does not take in account how much experience the pokemon has accumulated in
        the current level, which is up to the players to keep track of.

        Args:
            leveling_type (str): name of the leveling curve for the pokemon.

        Returns:
            The experience needed to reach the next level from the current level.
        """
        required_experience = self.experience_to_level(
            self.level + 1, leveling_type
        ) - self.experience_to_level(self.level, leveling_type)
        logger.info(
            f"The amount of experience {self.name} needs to reach the next level "
            f"is {required_experience:,}".replace(",", " ")
        )
        return required_experience

    def level_up(self) -> None:
        """
        Convenience function to increment the pokemon's level and trigger an update of its stats.
        """
        self.level += 1
        self._update_stats_on_levelup()

    @logger.catch()
    def _update_stats_on_levelup(self) -> None:
        """
        Called when the level attribute is changed, triggering a re-calculation of the
        pokemon's stats based on its EVs.
        """
        logger.info(f"{self.name} has reached level {self.level}, updating stats now.")
        defaults: Pokemon = _base_pokemon_stats(self.name)
        nature_stat: pd.DataFrame = NATURES_DF[NATURES_DF.nature == self.nature]
        self.health = (
            (2 * defaults.health + self.iv[0] + self.ev[0] / 4) * self.level / 100 + self.level + 10
        )
        self.attack = (
            (2 * defaults.attack + self.iv[1] + self.ev[1] / 4) * self.level / 100 + 5
        ) * nature_stat.attack.to_numpy()[0]
        self.defense = (
            (2 * defaults.defense + self.iv[2] + self.ev[2] / 4) * self.level / 100 + 5
        ) * nature_stat.defense.to_numpy()[0]
        self.special_attack = (
            (2 * defaults.special_attack + self.iv[3] + self.ev[3] / 4) * self.level / 100 + 5
        ) * nature_stat.special_attack.to_numpy()[0]
        self.special_defense = (
            (2 * defaults.special_defense + self.iv[4] + self.ev[4] / 4) * self.level / 100 + 5
        ) * nature_stat.special_defense.to_numpy()[0]
        self.speed = (
            (2 * defaults.speed + self.iv[5] + self.ev[5] / 4) * self.level / 100 + 5
        ) * nature_stat.speed.to_numpy()[0]
        logger.debug(f"{self.name}'s stats have been updated!")

    # ----- Combat Functionality ----- #

    def hit_probability(self, target_pokemon, move_accuracy: float) -> float:
        """
        Calculate the probability of hitting an ennemy pokemon with a specific attack move.

        Args:
            target_pokemon (Pokemon): Pokemon object of the pokemon getting attacked.
            move_accuracy (float): the accuracy of the attack move attempted, as a float between
                0 and 1.

        Returns:
            The probability as a float between 0 and 1, rounded to 3 digits precision.
        """
        probability = self.accuracy * move_accuracy / target_pokemon.dodge
        logger.info(f"{self.name} has a {probability:.2%} change of hitting {target_pokemon.name}")
        return round(probability, 3)

    def perform_physical_attack(
        self,
        target_pokemon,
        attack_power: float,
        attack_modifier: float = 1,
        defense_modifier: float = 1,
        global_modifier: float = 1,
    ) -> None:
        """
        Performs an attack of type normal / physical onto the target pokemon. The damage is
        calculated, then the target's health is updated.

        Args:
            target_pokemon (Pokemon): Pokemon object of the pokemon getting damaged.
            attack_power (float): determined by the attack move used.
            attack_modifier (float): modifier of the attacker's attack, depending on effects
                currently on the pokemon (from objects, previous moves etc). Defaults to 1,
                aka no modification.
            defense_modifier (float): modifier of the defender's defense, depending on effects
                currently on the pokemon (from objects, previous moves etc). Defaults to 1,
                aka no modification.
            global_modifier (float): input by GM, really weird calculation. Defaults to 1,
                aka no modification.
        """
        damage_dealt = dealt_damage(
            self,
            target_pokemon,
            "physical",
            attack_power,
            attack_modifier,
            defense_modifier,
            global_modifier,
        )
        target_pokemon.health -= damage_dealt
        logger.info(f"{target_pokemon.name}'s health is now at {target_pokemon.health}")

    def perform_special_attack(
        self,
        target_pokemon,
        attack_power: float,
        attack_modifier: float = 1,
        defense_modifier: float = 1,
        global_modifier: float = 1,
    ) -> None:
        """
        Performs an attack of type special onto the target pokemon. The damage is
        calculated, then the target's health is updated.

        Args:
            target_pokemon (Pokemon): Pokemon object of the pokemon getting damaged.
            attack_power (float): determined by the attack move used.
            attack_modifier (float): modifier of the attacker's attack, depending on effects
                currently on the pokemon (from objects, previous moves etc). Defaults to 1,
                aka no modification.
            defense_modifier (float): modifier of the defender's defense, depending on effects
                currently on the pokemon (from objects, previous moves etc). Defaults to 1,
                aka no modification.
            global_modifier (float): input by GM, really weird calculation. Defaults to 1,
                aka no modification.
        """
        damage_dealt = dealt_damage(
            self,
            target_pokemon,
            "special",
            attack_power,
            attack_modifier,
            defense_modifier,
            global_modifier,
        )
        target_pokemon.health -= damage_dealt
        logger.info(f"{target_pokemon.name}'s health is now at {target_pokemon.health}")

    # ----- Random Generation ----- #

    @classmethod
    def generate_random(cls, name: str, level: int):
        """
        Generate a random specific pokemon of the given level.

        Args:
            name (str): name of the encountered pokemon, must be a valid name from the games.
            level (int): level of the encountered pokemon.

        Returns:
            A Pokemon object with generated stats.
        """
        name = _get_random_pokemon_name() if name == "random" else name
        _assert_pokemon_exists(name)
        logger.info(f"Creating a random {name.capitalize()} of level {level}")

        base_pokemon = _base_pokemon_stats(name)
        logger.debug(f"Generating random IV for {name}")
        randiv = list(np.random.randint(0, 32, 6))
        random_nature = _random_nature_attributes()

        logger.debug(
            f"Computing attributes based on provided level ({level}) and attributed nature "
            f"({random_nature.nature.to_numpy()[0]})"
        )
        return cls(
            code=base_pokemon.code,
            number=base_pokemon.number,
            name=base_pokemon.name,
            level=level,
            health=round((2 * base_pokemon.health + randiv[0]) * level / 100 + level + 10),
            attack=round(
                ((2 * base_pokemon.attack + randiv[1]) * level / 100 + 5) * random_nature.attack
            ),
            defense=round(
                ((2 * base_pokemon.defense + randiv[2]) * level / 100 + 5) * random_nature.defense
            ),
            special_attack=round(
                ((2 * base_pokemon.special_attack + randiv[3]) * level / 100 + 5)
                * random_nature.special_attack
            ),
            special_defense=round(
                ((2 * base_pokemon.special_defense + randiv[4]) * level / 100 + 5)
                * random_nature.special_defense
            ),
            speed=round(
                ((2 * base_pokemon.speed + randiv[5]) * level / 100 + 5) * random_nature.speed
            ),
            nature=random_nature.nature.to_numpy()[0],
            iv=randiv,
            base_xp=base_pokemon.base_xp,
            base_ev=base_pokemon.base_ev,
        )

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


# ----- Public Helpers ----- #


def erratic_leveling(target_level: int) -> int:
    """
    Non-trivial calculation of experience to next level for an erratic leveling curve.

    Args:
        target_level (int): the level to reach.

    Returns:
        The amount of experience to reach this level from the ground up (from experience 0),
        according to an erractic leveling curve.
    """
    if target_level <= 50:
        return (target_level ** 3) * (100 - target_level) / 50
    elif 51 <= target_level <= 68:
        return (target_level ** 3) * (150 - target_level) / 100
    elif 69 <= target_level <= 98:
        if target_level % 3 == 0:
            return round((target_level ** 3) * (1.274 - target_level / 150), 3)
        elif target_level % 3 == 1:
            return round((target_level ** 3) * (1.274 - target_level / 150 - 0.008), 3)
        else:
            return round((target_level ** 3) * (1.274 - target_level / 150 - 0.014), 3)
    elif 99 <= target_level <= 100:
        return (target_level ** 3) * (160 - target_level) / 100
    else:
        logger.error(
            f"An invalid target level was provided: {target_level} which is higher than "
            f"the highest reachable level (100)."
        )
        raise ValueError("Invalid target level: too high.")


def fluctuating_leveling(target_level: int) -> int:
    """
    Non-trivial calculation of experience to next level for a fluctuating leveling curve.

    Args:
        target_level (int): the level to reach.

    Returns:
        The amount of experience to reach this level from the ground up (from experience 0),
        according to a fluctuating leveling curve.
    """
    if target_level <= 15:
        return (target_level ** 3) / 50 * (24 + (target_level + 1) / 3)
    elif 16 <= target_level <= 35:
        return (target_level ** 3) / 50 * (14 + target_level)
    elif target_level <= 100:
        return (target_level ** 3) / 50 * (32 + target_level / 2)
    else:
        logger.error(
            f"An invalid target level was provided: {target_level} which is higher than "
            f"the highest reachable level (100)."
        )
        raise ValueError("Invalid target level: too high.")


# ----- Leveling Curves ----- #


LEVELING_CURVES: Dict[str, callable] = {
    "quick": lambda x: 0.8 * (x ** 3),
    "average": lambda x: x ** 3,
    "parabolic": lambda x: 1.2 * (x ** 3) - 15 * (x ** 2) + 100 * x - 140,
    "slow": lambda x: 1.25 * (x ** 3),
    "erratic": erratic_leveling,
    "fluctuating": fluctuating_leveling,
}


# ----- Private Helpers ----- #


def _assert_valid_target_level(target_level: int) -> None:
    """
    Ensure the given target level is reachable, log then raise ValueError if not.

    Args:
        target_level (int): the level.
    """
    logger.trace("Checking provided level validity")
    if target_level > 100:
        logger.error(
            f"An invalid target level was provided: {target_level} which is higher than "
            f"the highest reachable level (100)."
        )
        raise ValueError("Invalid target level: too high.")


def _assert_valid_leveling_cruve(curve_name: str) -> None:
    """
    Ensure the given leveling curve type is valid, log then raise ValueError if not.

    Args:
        curve_name (str): name of the leveling curve to check.
    """
    logger.trace("Checking provided leveling curve validity")
    if curve_name.lower() not in [e.lower() for e in LEVELING_CURVES.keys()]:
        logger.error(f"An invalid leveling curve was provided: '{curve_name}'")
        raise ValueError("Invalid leveling curve.")


def _get_random_pokemon_name() -> str:
    """Gives back a valid name picked at random from the list of names from the games."""
    logger.trace("Picking a random name from Pokemon database")
    return POKEMONS_DF.name.sample(1, replace=True).to_numpy()[0]


def _assert_pokemon_exists(pokemon_name: str) -> None:
    """
    Ensure the given name is a valid Pokemon name from the games, log then raise ValueError if not.

    Args:
        pokemon_name (str): name to check the validity of.
    """
    logger.trace("Checking provided pokemon name validity")
    if pokemon_name not in POKEMONS_DF.name.to_numpy():
        logger.error(f"An invalid pokemon name was provided: '{pokemon_name}'")
        raise ValueError("Invalid Pokemon name.")


def _base_pokemon_stats(pokemon_name: str) -> Pokemon:
    """
    Return the base stats of a given pokemon, as a Pokemon object.

    Args:
        pokemon_name (str): name of a pokemon to get the base stats of.

    Returns:
        A Pokemon object with the base stats.
    """
    logger.trace(f"Loading base statistics for Pokemon '{pokemon_name}'")
    return Pokemon(**POKEMONS_DF[POKEMONS_DF.name == pokemon_name].to_dict("records")[0])


def _random_nature_attributes() -> pd.DataFrame:
    """
    Picks a random nature among the available ones for pokemons, and returns the corresponding
    subset of the NATURES_DF containing the attributes (modifiers) of the picked nature.

    Returns:
        A pandas DataFrame with the modifiers.
    """
    logger.trace(f"Picking a random nature")
    return NATURES_DF.sample(1, replace=True)
