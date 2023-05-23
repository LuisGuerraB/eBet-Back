from enum import Enum


class MatchStatus(Enum):
    NOT_STARTED = 'not_started'
    FINISHED = 'finished'

class BetType(Enum):
    WIN = 'win'
    EXP = 'exp'
    GOLD = 'gold'
    DRAKES = 'drakes'
    INHIBITORS = 'inhibitors'
    ELDERS = 'elders'
    TOWERS = 'towers'
    BARONS = 'barons'
    HERALDS = 'heralds'
    KILLS = 'kills'
    DEATHS = 'deaths'
    ASSISTS = 'assists'
