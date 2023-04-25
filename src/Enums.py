from enum import Enum


class SeasonsEnum(Enum):
    'AUTUMN'
    'WINTER'
    'SUMMER'
    'SPRING'

class MatchStatus(Enum):
    'not_started'
    'finished'