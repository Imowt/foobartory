from pathlib import Path

from pydantic import BaseSettings, root_validator


class Settings(BaseSettings):
    TIME_RATIO: float

    DEFAULT_ROBOTS: int
    MAX_ROBOTS: int

    ROBOT_COST: float
    ROBOT_FOO_COST: int

    ROBOT_MINING_FOO_DURATION: float
    ROBOT_MINING_BAR_DURATION_MIN: float
    ROBOT_MINING_BAR_DURATION_MAX: float

    ROBOT_ASSEMBLING_FOOBAR_DURATION: float
    ROBOT_ASSEMBLING_FOOBAR_SUCCESS_RATE: float

    ROBOT_SELLING_FOOBARS_DURATION: float
    ROBOT_SELLING_FOOBARS_MIN: int
    ROBOT_SELLING_FOOBARS_MAX: int

    FOOBAR_VALUE: float

    ROBOT_MOVING_DURATION: float

    MONITORING_REFRESH_RATE: int

    class Config:
        env_file_encoding = "utf-8"

    @root_validator
    def validate_values(cls, values):
        """
        Verify the values validity
        :param values: values
        :return: values
        """
        cls.validate_mining_bar_min_max(
            values.get("ROBOT_MINING_BAR_DURATION_MIN"), values.get("ROBOT_MINING_BAR_DURATION_MAX")
        )
        cls.validate_selling_foobar_min_man(
            values.get("ROBOT_SELLING_FOOBARS_MIN"), values.get("ROBOT_SELLING_FOOBARS_MAX")
        )
        for key, value in values.items():
            if (type(value) is int or type(value) is float) and value < 0:
                raise ValueError(f"{key}: has to be positive")
        return values

    @classmethod
    def validate_mining_bar_min_max(cls, duration_min: float, duration_max: float) -> None:
        """
        Validate the mining bar duration min max values
        :return:
        """
        if duration_min > duration_max:
            raise ValueError("ROBOT_MINING_BAR_DURATION_MIN has to be lower than ROBOT_MINING_BAR_DURATION_MAX")

    @classmethod
    def validate_selling_foobar_min_man(cls, selling_min: int, selling_max: int) -> None:
        """
        Validate the selling foobar min and max values
        :return:
        """
        if selling_min > selling_max:
            raise ValueError("ROBOT_SELLING_FOOBARS_MIN has to be lower than ROBOT_SELLING_FOOBARS_MAX")


dot_env_path: Path = Path(__file__).parents[2].resolve() / ".env"
settings: Settings = Settings(_env_file=str(dot_env_path))
