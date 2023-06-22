from enum import Enum


class MatchStatus(Enum):
    NOT_STARTED = 'not_started'
    FINISHED = 'finished'


class Privilege(Enum):
    MARKETING = 'marketing'
    ADMIN = 'admin'
