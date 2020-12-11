import json
import pickle
import sys
from pathlib import Path
from typing import List, Optional, Union

from loguru import logger
from pydantic import BaseModel, PositiveInt, validator

from pokejdr.constants import LOGURU_FORMAT

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
