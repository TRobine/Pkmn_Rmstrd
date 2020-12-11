import sys
from typing import List, Optional

from loguru import logger
from pydantic import BaseModel, PositiveInt, validator

from pokejdr.constants import LOGURU_FORMAT
from pokejdr.models.utils import dealt_damage

logger.remove(0)
logger.add(sys.stderr, format=LOGURU_FORMAT)


# ----- Generic Element Model ----- #


class Element(BaseModel):
    code: Optional[PositiveInt]
    number: Optional[PositiveInt]
    name: str
    level: Optional[PositiveInt]
    health: int
    attack: int
    defense: int
    special_attack: int
    special_defense: int
    speed: int
    nature: Optional[str]
    iv: Optional[List[int]] = [0, 0, 0, 0, 0, 0]
    ev: Optional[List[int]] = [0, 0, 0, 0, 0, 0]
    accuracy: float = 1.0
    dodge: float = 1.0
    base_xp: Optional[int] = 0
    base_ev: Optional[List[int]] = [0, 0, 0, 0, 0, 0]

    @validator("health")
    def doesnt_drop_below_0(cls, v) -> int:
        """
        Custom validation rule for a Pokemon's health, ensuring the value does not drop below 0.
        If it does, then log that the pokemon has fainted and set health value to 0.
        """
        if v < 0:
            logger.critical(f"HP have dropped below 0, Pokemon has fainted!")
            logger.trace("Setting HP to 0 now")
            return 0
        return int(v)

    class Config:
        validate_assignment = True  # force custom validation rules on assignments

    @property
    def total(self) -> int:
        return (
            self.health
            + self.attack
            + self.defense
            + self.special_attack
            + self.special_defense
            + self.speed
        )

    # ----- Generic Experience Functionality ----- #

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

    # ----- Generic Combat Functionality ----- #

    def hit_probability(self, target_element, move_accuracy: float) -> float:
        """
        Calculate the probability of hitting an ennemy pokemon with a specific attack move.

        Args:
            target_element (Pokemon): Pokemon object of the pokemon getting attacked.
            move_accuracy (float): the accuracy of the attack move attempted, as a float between
                0 and 1.

        Returns:
            The probability as a float between 0 and 1, rounded to 3 digits precision.
        """
        probability = self.accuracy * move_accuracy / target_element.dodge
        logger.info(f"{self.name} has a {probability:.2%} change of hitting {target_element.name}")
        return round(probability, 3)

    def perform_physical_attack(
        self,
        target_element,
        attack_power: float,
        attack_modifier: float = 1,
        defense_modifier: float = 1,
        global_modifier: float = 1,
    ) -> None:
        """
        Performs an attack of type normal / physical onto the target pokemon. The damage is
        calculated, then the target's health is updated.

        Args:
            target_element (Pokemon): Pokemon object of the pokemon getting damaged.
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
            target_element,
            "physical",
            attack_power,
            attack_modifier,
            defense_modifier,
            global_modifier,
        )
        target_element.health -= damage_dealt
        logger.info(f"{target_element.name}'s health is now at {target_element.health}")

    def perform_special_attack(
        self,
        target_element,
        attack_power: float,
        attack_modifier: float = 1,
        defense_modifier: float = 1,
        global_modifier: float = 1,
    ) -> None:
        """
        Performs an attack of type special onto the target pokemon. The damage is
        calculated, then the target's health is updated.

        Args:
            target_element (Pokemon): Pokemon object of the pokemon getting damaged.
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
            target_element,
            "special",
            attack_power,
            attack_modifier,
            defense_modifier,
            global_modifier,
        )
        target_element.health -= damage_dealt
        logger.info(f"{target_element.name}'s health is now at {target_element.health}")
