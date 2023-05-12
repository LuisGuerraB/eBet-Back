from enum import Enum


class MatchStatus(Enum):
    NOT_STARTED = 'not_started'
    FINISHED = 'finished'

class BetType(Enum):
    WINNER = 'winner'
    EXP = 'exp'
    GOLD = 'gold'
    DRAKES = 'drakes'
    INHIBITORS = 'inhibitors'
    ELDER = 'elder'
    TOWER = 'tower'
    BARON = 'baron'
    HERALD = 'herald'
    KILL = 'kill'
    DEATH = 'death'
    ASSIST = 'assist'
