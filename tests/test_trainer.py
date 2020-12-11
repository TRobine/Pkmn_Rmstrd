import pathlib

import pytest
from pydantic import ValidationError

from pokejdr.models.trainer import Trainer

CURRENT_DIR = pathlib.Path(__file__).parent


class TestTrainer:
    def test_attributes_conversions(self):
        player = Trainer(
            code="50",
            number=37.0,
            name="SwaggerBoy",
            level=15,
            health=38.0,
            attack="41",
            defense=40.0,
            special_attack=50.0,
            special_defense=65.0,
            speed=65.0,
        )
        assert isinstance(player.code, int)
        assert isinstance(player.number, int)
        assert isinstance(player.name, str)
        assert isinstance(player.level, int)
        assert isinstance(player.health, int)
        assert isinstance(player.attack, int)
        assert isinstance(player.defense, int)
        assert isinstance(player.special_attack, int)
        assert isinstance(player.special_defense, int)
        assert isinstance(player.speed, int)
        assert isinstance(player.total, int)
        assert isinstance(player.iv, list)
        assert isinstance(player.ev, list)
        assert isinstance(player.accuracy, float)
        assert isinstance(player.dodge, float)

    def test_total(self):
        player = Trainer(
            name="SwaggerBoy",
            level=15,
            health=38,
            attack=41,
            defense=40,
            special_attack=50,
            special_defense=65,
            speed=65,
        )
        assert player.total == 299


class TestValidations:
    @pytest.mark.parametrize("invalid_code", [-5, -10, "-20"])
    @pytest.mark.parametrize("invalid_number", [-100, "-1", 0])
    def test_positive_integers(self, invalid_code, invalid_number):
        with pytest.raises(ValidationError):
            _ = Trainer(
                code=invalid_code,
                number=37.0,
                name="SwaggerBoy",
                level=15,
                health=38.0,
                attack="41",
                defense=40.0,
                special_attack=50.0,
                special_defense=65.0,
                speed=65.0,
            )

        with pytest.raises(ValidationError):
            _ = Trainer(
                number=invalid_number,
                name="SwaggerBoy",
                level=15,
                health=38.0,
                attack="41",
                defense=40.0,
                special_attack=50.0,
                special_defense=65.0,
                speed=65.0,
            )

    def test_health_drops_below_0(self, caplog):
        player = Trainer(
            name="SwaggerBoy",
            level=15,
            health=38,
            attack=41,
            defense=40,
            special_attack=50,
            special_defense=65,
            speed=65,
        )

        player.health -= 1000  # to make sure we get below 0
        assert player.health == 0  # make sure checks have handled the pokemon fainting

        for record in caplog.records:
            assert record.levelname == "CRITICAL"
            assert "HP have dropped below 0, pokemon has fainted!" in record.message

    def test_negative_health_attribution(self, caplog):
        player = Trainer(
            name="SwaggerBoy",
            level=15,
            health=38,
            attack=41,
            defense=40,
            special_attack=50,
            special_defense=65,
            speed=65,
        )

        player.health = -20  # health should never be a negative value
        assert player.health == 0  # make sure checks have handled the pokemon fainting

        for record in caplog.records:
            assert record.levelname == "CRITICAL"
            assert "HP have dropped below 0, pokemon has fainted!" in record.message

    @pytest.mark.parametrize("invalid_type", [dict(), tuple(), bytearray()])
    def test_invalid_health_type_attribution(self, invalid_type):
        player = Trainer(
            name="SwaggerBoy",
            level=15,
            health=38,
            attack=41,
            defense=40,
            special_attack=50,
            special_defense=65,
            speed=65,
        )

        with pytest.raises(ValidationError):
            player.health = invalid_type


class TestIO:
    def test_load_json(self, _trainer_json_file):
        player = Trainer.from_json(_trainer_json_file)

        assert player.code is None
        assert player.number is None
        assert player.name == "SwaggerBoy"
        assert player.level == 15
        assert player.health == 38
        assert player.attack == 41
        assert player.defense == 40
        assert player.special_attack == 50
        assert player.special_defense == 65
        assert player.speed == 65
        assert player.nature is None
        assert player.total == 299
        assert player.iv == [0, 0, 0, 0, 0, 0]
        assert player.ev == [0, 0, 0, 0, 0, 0]
        assert player.accuracy == 1.0
        assert player.dodge == 1.0
        assert player.base_xp == 0
        assert player.base_ev == [0, 0, 0, 0, 0, 0]

    def test_load_pickle(self, _trainer_pickle_file):
        player = Trainer.from_pickle(_trainer_pickle_file)

        assert player.code is None
        assert player.number is None
        assert player.name == "SwaggerBoy"
        assert player.level == 15
        assert player.health == 38
        assert player.attack == 41
        assert player.defense == 40
        assert player.special_attack == 50
        assert player.special_defense == 65
        assert player.speed == 65
        assert player.nature is None
        assert player.total == 299
        assert player.iv == [0, 0, 0, 0, 0, 0]
        assert player.ev == [0, 0, 0, 0, 0, 0]
        assert player.accuracy == 1.0
        assert player.dodge == 1.0
        assert player.base_xp == 0
        assert player.base_ev == [0, 0, 0, 0, 0, 0]

    def test_write_read_json(self, tmp_path):
        player = Trainer(
            name="SwaggerBoy",
            level=15,
            health=38,
            attack=41,
            defense=40,
            special_attack=50,
            special_defense=65,
            speed=65,
        )
        player.to_json(tmp_path / "save.json")

        read_player = Trainer.from_json(tmp_path / "save.json")
        assert read_player == player

    def test_write_read_pickle(self, tmp_path):
        player = Trainer(
            name="SwaggerBoy",
            level=15,
            health=38,
            attack=41,
            defense=40,
            special_attack=50,
            special_defense=65,
            speed=65,
        )
        player.to_pickle(tmp_path / "save.pkl")

        read_player = Trainer.from_pickle(tmp_path / "save.pkl")
        assert read_player == player


# ----- Fixtures ----- #


@pytest.fixture()
def _trainer_json_file() -> pathlib.Path:
    return CURRENT_DIR / "inputs" / "player.json"


@pytest.fixture()
def _trainer_pickle_file() -> pathlib.Path:
    return CURRENT_DIR / "inputs" / "player.pkl"
