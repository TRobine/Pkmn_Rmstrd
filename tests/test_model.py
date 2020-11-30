import json
import pathlib

import pytest
from pydantic import ValidationError

from pokejdr import base_stats
from pokejdr.model import Pokemon, dealt_damage, erratic_leveling, fluctuating_leveling

CURRENT_DIR = pathlib.Path(__file__).parent


class TestGeneration:
    def test_generated_pokemon(self):
        poke = Pokemon.generate_random("Dracaufeu", 100)
        assert isinstance(poke, Pokemon)
        assert poke.name == "Dracaufeu"
        assert poke.level == 100
        assert hasattr(poke, "code")
        assert hasattr(poke, "number")
        assert hasattr(poke, "health")
        assert hasattr(poke, "attack")
        assert hasattr(poke, "defense")
        assert hasattr(poke, "special_attack")
        assert hasattr(poke, "special_defense")
        assert hasattr(poke, "speed")
        assert hasattr(poke, "nature")
        assert hasattr(poke, "iv")
        assert hasattr(poke, "ev")
        assert hasattr(poke, "accuracy")
        assert hasattr(poke, "dodge")
        assert hasattr(poke, "base_xp")
        assert hasattr(poke, "base_ev")

    def test_generating_true_random(self):
        random_poke = Pokemon.generate_random("random", 10)
        assert random_poke.name in base_stats.POKEMONS_DF.name.to_numpy()

    def test_generation_fails_with_invalid_name(self, caplog):
        with pytest.raises(ValueError):
            _ = Pokemon.generate_random("Human", 50)

        for record in caplog.records:
            assert record.levelname == "ERROR"
            assert "An invalid pokemon name was provided" in record.message


class TestPokemon:
    def test_attributes_conversions(self):
        poke = Pokemon(
            code="50",
            number=37.0,
            name="Goupix",
            level=15,
            health=38.0,
            attack="41",
            defense=40.0,
            special_attack=50.0,
            special_defense=65.0,
            speed=65.0,
        )
        assert isinstance(poke.code, int)
        assert isinstance(poke.number, int)
        assert isinstance(poke.name, str)
        assert isinstance(poke.level, int)
        assert isinstance(poke.health, int)
        assert isinstance(poke.attack, int)
        assert isinstance(poke.defense, int)
        assert isinstance(poke.special_attack, int)
        assert isinstance(poke.special_defense, int)
        assert isinstance(poke.speed, int)
        assert isinstance(poke.total, int)
        assert isinstance(poke.iv, list)
        assert isinstance(poke.ev, list)
        assert isinstance(poke.accuracy, float)
        assert isinstance(poke.dodge, float)

    def test_total(self):
        poke = Pokemon(
            code=50,
            number=37,
            name="Goupix",
            level=15,
            health=38,
            attack=41,
            defense=40,
            special_attack=50,
            special_defense=65,
            speed=65,
        )
        assert poke.total == 299

    def test_level_up(self):
        poke = Pokemon.generate_random("Reptincel", 75)
        poke.ev = [50, 50, 50, 50, 50, 50]  # give it life experience
        before_level_up = poke.copy()

        assert poke.level == 75
        assert before_level_up.level == 75

        poke.level_up()
        assert poke.level == 76
        assert poke.health != before_level_up.health
        assert poke.attack != before_level_up.attack
        assert poke.defense != before_level_up.defense
        assert poke.special_attack != before_level_up.special_attack
        assert poke.special_defense != before_level_up.special_defense
        assert poke.speed != before_level_up.speed
        assert poke.total != before_level_up.total

    @pytest.mark.parametrize(
        "target_level, result",
        [
            (35, 55737.5),
            (60, 194400),
            (72, 296358.912),
            (85, 429478.083),
            (92, 503551.573),
            (100, 600000),
        ],
    )
    def test_erratic_leveling_curve(self, target_level, result):
        assert erratic_leveling(target_level) == result

    @pytest.mark.parametrize("target_level", [150, 200, 250])
    def test_erratic_leveling_curve_fails_on_high_levels(self, target_level):
        with pytest.raises(ValueError):
            erratic_leveling(target_level)

    @pytest.mark.parametrize("target_level, result", [(9, 398.52), (28, 18439.68), (70, 459620)])
    def test_fluctuating_leveling_curve(self, target_level, result):
        assert fluctuating_leveling(target_level) == result

    @pytest.mark.parametrize("target_level", [150, 200, 250])
    def test_fluctuating_leveling_curve_fails_on_high_levels(self, target_level):
        with pytest.raises(ValueError):
            fluctuating_leveling(target_level)

    @pytest.mark.parametrize("target_level", [150, 200, 250])
    def test_experience_to_level_invalid_level(self, target_level, caplog):
        poke = Pokemon.generate_random("random", 30)
        with pytest.raises(ValueError):
            poke.experience_to_level(target_level, "slow")

        for record in caplog.records:
            assert record.levelname == "ERROR"
            assert "Invalid target level: too high." in record.message

    @pytest.mark.parametrize("leveling_type", ["invalid", "inexistent", "???", "not good"])
    def test_experience_to_level_invalid_curve(self, leveling_type, caplog):
        poke = Pokemon.generate_random("random", 30)
        with pytest.raises(ValueError):
            poke.experience_to_level(31, leveling_type)

        for record in caplog.records:
            assert record.levelname == "ERROR"
            assert "Invalid leveling curve." in record.message

    @pytest.mark.parametrize(
        "level, curve, result",
        [(15, "quick", 2700), (55, "parabolic", 159635), (100, "slow", 1250000)],
    )
    def test_experience_to_level(self, _attacker_pokemon, level, curve, result):
        assert _attacker_pokemon.experience_to_level(level, curve) == result

    @pytest.mark.parametrize(
        "leveling_curve, result",
        [
            ("quick", 2233),
            ("average", 2791),
            ("parabolic", 2534),
            ("slow", 3489),
            ("erratic", 3312),
            ("fluctuating", 3052),
        ],
    )
    def test_experience_to_next_level(self, leveling_curve, result, _attacker_pokemon):
        assert _attacker_pokemon.experience_to_next_level(leveling_curve) == result


class TestValidations:
    @pytest.mark.parametrize("invalid_pokemon_code", [-5, -10, "-20"])
    @pytest.mark.parametrize("invalid_pokemon_number", [-100, "-1", 0])
    def test_positive_integers(self, invalid_pokemon_code, invalid_pokemon_number):
        with pytest.raises(ValidationError):
            _ = Pokemon(
                code=invalid_pokemon_code,
                number=37.0,
                name="Goupix",
                level=15,
                health=38.0,
                attack="41",
                defense=40.0,
                special_attack=50.0,
                special_defense=65.0,
                speed=65.0,
            )

        with pytest.raises(ValidationError):
            _ = Pokemon(
                code=5,
                number=invalid_pokemon_number,
                name="Goupix",
                level=15,
                health=38.0,
                attack="41",
                defense=40.0,
                special_attack=50.0,
                special_defense=65.0,
                speed=65.0,
            )

    def test_health_drops_below_0(self, caplog):
        poke = Pokemon.generate_random("Paras", 10)
        poke.health -= 1000  # to make sure we get below 0
        assert poke.health == 0  # make sure checks have handled the pokemon fainting

        for record in caplog.records:
            assert record.levelname == "CRITICAL"
            assert "HP have dropped below 0, pokemon has fainted!" in record.message

    def test_negative_health_attribution(self, caplog):
        poke = Pokemon.generate_random("Paras", 10)
        poke.health = -20  # health should never be a negative value
        assert poke.health == 0  # make sure checks have handled the pokemon fainting

        for record in caplog.records:
            assert record.levelname == "CRITICAL"
            assert "HP have dropped below 0, pokemon has fainted!" in record.message

    @pytest.mark.parametrize("invalid_type", [dict(), tuple(), bytearray()])
    def test_invalid_health_type_attribution(self, invalid_type):
        poke = Pokemon.generate_random("random", 50)

        with pytest.raises(ValidationError):
            poke.health = invalid_type


class TestIO:
    def test_load_json(self, _pokemon_json_file):
        bulbizarre = Pokemon.from_json(_pokemon_json_file)

        assert bulbizarre.code == 1
        assert bulbizarre.number == 1
        assert bulbizarre.name == "Bulbizarre"
        assert bulbizarre.level == 30
        assert bulbizarre.health == 221
        assert bulbizarre.attack == 103
        assert bulbizarre.defense == 117
        assert bulbizarre.special_attack == 162
        assert bulbizarre.special_defense == 169
        assert bulbizarre.speed == 96
        assert bulbizarre.total == 868
        assert bulbizarre.iv == [21, 0, 14, 27, 19, 12]
        assert bulbizarre.ev == [0, 0, 0, 0, 0, 0]
        assert bulbizarre.accuracy == 1.0
        assert bulbizarre.dodge == 1.0

    def test_load_pickle(self, _pokemon_pickle_file):
        nosferapti = Pokemon.from_pickle(_pokemon_pickle_file)

        assert nosferapti.code == 56
        assert nosferapti.number == 41
        assert nosferapti.name == "Nosferapti"
        assert nosferapti.level == 5
        assert nosferapti.health == 39
        assert nosferapti.attack == 25
        assert nosferapti.defense == 14
        assert nosferapti.special_attack == 14
        assert nosferapti.special_defense == 19
        assert nosferapti.speed == 24
        assert nosferapti.total == 135
        assert nosferapti.iv == [12, 27, 2, 3, 14, 16]
        assert nosferapti.ev == [0, 0, 0, 0, 0, 0]
        assert nosferapti.accuracy == 1.0
        assert nosferapti.dodge == 1.0

    def test_write_read_json(self, tmp_path):
        random_pikachu = Pokemon.generate_random("Pikachu", 25)
        random_pikachu.to_json(tmp_path / "save.json")

        read_pikachu = Pokemon.from_json(tmp_path / "save.json")
        assert read_pikachu == random_pikachu

    def test_write_read_pickle(self, tmp_path):
        random_salameche = Pokemon.generate_random("Salameche", 37)
        random_salameche.to_pickle(tmp_path / "save.pkl")

        read_salameche = Pokemon.from_pickle(tmp_path / "save.pkl")
        assert read_salameche == random_salameche


class TestDamageCalculation:
    @pytest.mark.parametrize(
        "attack_power, attack_modifier, defense_modifier, global_modifier, "
        "lower_bound, higher_bound",
        [(10, 1, 1, 1, 19, 23), (35, 2, 0.8, 1.1, 170, 200), (50, 1.5, 2, 1.3, 88, 103)],
    )
    def test_damage_calculation_normal_attack(
        self,
        _attacker_pokemon,
        _defender_pokemon,
        attack_power,
        attack_modifier,
        defense_modifier,
        global_modifier,
        lower_bound,
        higher_bound,
        caplog,
    ):
        damage = dealt_damage(
            attacker=_attacker_pokemon,
            defender=_defender_pokemon,
            attack_type="normal",
            attack_power=attack_power,
            attack_modifier=attack_modifier,
            defense_modifier=defense_modifier,
            global_modifier=global_modifier,
        )
        # not an equality statement because of the random factor [0.85, 1] in calculation
        assert lower_bound <= damage <= higher_bound

        for record in caplog.records:
            assert record.levelname == "INFO"
            assert (
                f"Bulbizarre performs a normal attack on Nosferapti that deals {damage} "
                f"damage" in record.message
            )

    @pytest.mark.parametrize(
        "attack_power, attack_modifier, defense_modifier, global_modifier, "
        "lower_bound, higher_bound",
        [
            (10, 1, 1, 1, 22, 26),
            (15, 1, 1, 1, 32, 38),
            (35, 2, 0.8, 1.1, 197, 232),
            (50, 1.5, 2, 1.3, 101, 119),
        ],
    )
    def test_damage_calculation_special_attack(
        self,
        _attacker_pokemon,
        _defender_pokemon,
        attack_power,
        attack_modifier,
        defense_modifier,
        global_modifier,
        lower_bound,
        higher_bound,
        caplog,
    ):
        damage = dealt_damage(
            attacker=_attacker_pokemon,
            defender=_defender_pokemon,
            attack_type="special",
            attack_power=attack_power,
            attack_modifier=attack_modifier,
            defense_modifier=defense_modifier,
            global_modifier=global_modifier,
        )
        # not an equality statement because of the random factor [0.85, 1] in calculation
        assert lower_bound <= damage <= higher_bound

        for record in caplog.records:
            assert record.levelname == "INFO"
            assert (
                f"Bulbizarre performs a special attack on Nosferapti that deals {damage} "
                f"damage" in record.message
            )

    @pytest.mark.parametrize("attack_type", ["invalid", "incorrect", "not_accepted"])
    def test_invalid_attack_type(self, attack_type, caplog):
        with pytest.raises(ValueError):
            _ = dealt_damage(
                attacker=Pokemon.generate_random("random", 10),
                defender=Pokemon.generate_random("random", 10),
                attack_type=attack_type,
                attack_power=1,
                attack_modifier=1,
                defense_modifier=1,
                global_modifier=1,
            )

        for record in caplog.records:
            assert record.levelname == "ERROR"
            assert "An invalid attack type was provided" in record.message


class TestCombat:
    @pytest.mark.parametrize("move_accuracy, result", [(1, 1), (1.1, 1.1), (2, 2)])
    def test_hit_probability(self, _attacker_pokemon, _defender_pokemon, move_accuracy, result):
        assert _attacker_pokemon.hit_probability(_defender_pokemon, move_accuracy) == result

    def test_perform_physical_attack(self, _attacker_pokemon, _defender_pokemon, caplog):
        with caplog.at_level("CRITICAL"):
            for _ in range(2):
                initial_health = _defender_pokemon.health
                _attacker_pokemon.perform_physical_attack(
                    target_pokemon=_defender_pokemon, attack_power=15
                )
                assert _defender_pokemon.health != initial_health  # target health should be updated

            assert _defender_pokemon.health == 0  # lvl 5 nosferapti will have fainted

            for record in caplog.records:
                assert record.levelname == "CRITICAL"
                assert "HP have dropped below 0, pokemon has fainted!" in record.message

    def test_perform_special_attack(self, _attacker_pokemon, _defender_pokemon, caplog):
        with caplog.at_level("CRITICAL"):
            for _ in range(2):
                initial_health = _defender_pokemon.health
                _attacker_pokemon.perform_special_attack(
                    target_pokemon=_defender_pokemon, attack_power=15
                )
                assert _defender_pokemon.health != initial_health  # target health should be updated

            assert _defender_pokemon.health == 0  # lvl 5 nosferapti will have fainted

            for record in caplog.records:
                assert record.levelname == "CRITICAL"
                assert "HP have dropped below 0, pokemon has fainted!" in record.message

    @pytest.mark.parametrize(
        "bonus, att_xp, def_xp", [(1, 274, 114), (1.5, 411, 170), (2, 549, 227)]
    )
    def test_experience_given(self, bonus, att_xp, def_xp, _attacker_pokemon, _defender_pokemon):
        assert _attacker_pokemon.experience_given(bonus) == att_xp
        assert _defender_pokemon.experience_given(bonus) == def_xp


# ----- Fixtures ----- #


@pytest.fixture()
def _pokemon_json_file() -> pathlib.Path:
    return CURRENT_DIR / "inputs" / "bulbizarre.json"


@pytest.fixture()
def _pokemon_pickle_file() -> pathlib.Path:
    return CURRENT_DIR / "inputs" / "nosferapti.pkl"


@pytest.fixture()
def _attacker_pokemon() -> Pokemon:
    return Pokemon.from_json(CURRENT_DIR / "inputs" / "bulbizarre.json")


@pytest.fixture()
def _defender_pokemon() -> Pokemon:
    return Pokemon.from_pickle(CURRENT_DIR / "inputs" / "nosferapti.pkl")
