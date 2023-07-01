from abc import ABC, abstractmethod

from src.enums import MatchStatus


class ApiScrapperInterface(ABC):

    @abstractmethod
    def get_list_match(cls, status: MatchStatus, year=None, month=None, leagueId=None, limit=5, page=0):
        raise Exception('Not implemented')

    @abstractmethod
    def get_match_result(cls, match_id: int, set=1):
        raise Exception('Not implemented')

    @abstractmethod
    def get_teams(cls, tournament_id: int):
        raise Exception('Not implemented')

    @abstractmethod
    def get_tournaments(cls, status: MatchStatus, year: int, month: int):
        raise Exception('Not implemented')