from enum import Enum


class RobotActivity(str, Enum):
    MINING_FOO = "mining foo"
    MINING_BAR = "mining bar"
    ASSEMBLING_FOOBAR = "assembling foobar"
    SELLING_FOOBARS = "selling foobar"
    BUYING_ROBOT = "buying robot"
