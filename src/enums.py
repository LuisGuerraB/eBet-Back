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


ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'svg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
