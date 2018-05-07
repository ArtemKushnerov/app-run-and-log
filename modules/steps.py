from enum import Enum, auto


class Step(Enum):
    ORIGINAL = auto()
    SIGN = auto()
    REBUILD = auto()
    INSTRUMENT = auto()
