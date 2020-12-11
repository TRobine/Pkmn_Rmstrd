import sys
from random import uniform

from loguru import logger

from pokejdr.constants import LOGURU_FORMAT

logger.add(sys.stderr, format=LOGURU_FORMAT)


def dealt_damage(
    attacker,
    defender,
    attack_type: str,
    attack_power: float,
    attack_modifier: float = 1,
    defense_modifier: float = 1,
    global_modifier: float = 1,
) -> float:
    """
    Calculates the damage dealt by a pokemon to another one.

    Args:
        attacker (Element): Generic object of the element (pokemon / trainer / element) attacking.
        defender (Element): Generic object of the element (pokemon / trainer / element) getting
            damaged.
        attack_type (str): either 'normal' / 'physical' or 'special' / 'spe'.
        attack_power (float): determined by the attack move used.
        attack_modifier (float): modifier of the attacker's attack, depending on effects
            currently on the pokemon (from objects, previous moves etc). Defaults to 1,
            aka no modification.
        defense_modifier (float): modifier of the defender's defense, depending on effects
            currently on the pokemon (from objects, previous moves etc). Defaults to 1,
            aka no modification.
        global_modifier (float): input by GM, really weird calculation. Defaults to 1,
            aka no modification.

    Returns:
        The damage dealt by the attack.
    """
    _assert_valid_attack_type(attack_type)
    randomness_factor = uniform(0.85, 1)

    attack_value = attack_modifier * (
        attacker.attack
        if attack_type.lower() in ("normal", "physical")
        else attacker.special_attack
    )
    defense_value = defense_modifier * (
        defender.defense
        if attack_type.lower() in ("normal", "physical")
        else defender.special_defense
    )
    damage = (
        (2 + (attacker.level * 0.4 + 2) * attack_value * attack_power / defense_value / 50)
        * global_modifier
        * randomness_factor
    )
    logger.info(
        f"{attacker.name} performs a {attack_type} attack on {defender.name} that deals "
        f"{round(damage)} damage"
    )
    return round(damage)


def _assert_valid_attack_type(type_name: str) -> None:
    """
    Ensure the given attack type is valid, log then raise ValueError if not.

    Args:
        type_name (str): type of attack used, which should be normal or special.
    """
    logger.trace("Checking provided attack type validity")
    if type_name.lower() not in ("normal", "physical", "special", "spe"):
        logger.error(f"An invalid attack type was provided: '{type_name}'")
        raise ValueError("Invalid attack type.")
