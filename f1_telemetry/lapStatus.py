from enum import IntEnum


class LapStatus(IntEnum):
    Invalid = 0
    Inactive = 1
    Active = 2
    Finished = 3
    Disqualified = 4
    NotClassified = 5
    Retired = 6
