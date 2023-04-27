from src.Enums import MatchStatus
from src.classes.ApiScrapper import ApiScrapper
from src.models import Match, Season, League, Result
from src.models.Team import Team
import datetime


class DbPopulator:

    def __init__(self, db):
        self.db = db
        self.api = ApiScrapper()

    def populate_DB(self):
        today = datetime.date.today()
        year = today.year
        year = year
        limit = 500
        total_matchs_with_results = []

        for month in range(1, 13):
            matchs_finished_list = self.populate_matchs(MatchStatus.FINISHED, year=year, month=month, limit=limit)
            total_matchs_with_results += matchs_finished_list

        for match in total_matchs_with_results:
            for set in range(match.sets):
                result = self.db.session.query(Result).filter_by(match_id=match.id, set=set + 1).first()
                if result is None:
                    self.populate_result(match.id, set + 1)

    def populate_matchs(self, status, year=None, month=None, leagueId=None, limit=5, page=0):
        match_list = self.api.get_list_match(status, year, month, leagueId, limit, page)
        match_list_result = []
        for match_json in match_list:
            match_obj = self.db.session.get(Match, match_json['id'])
            if match_obj is None:
                if (self.db.session.get(Team, match_json['awayTeamId']) is None or
                        self.db.session.get(Team, match_json['homeTeamId']) is None):
                    self.populate_teams(match_json['tournamentId'])
                if self.db.session.get(Season, match_json['tournamentId']) is None:
                    self.populate_seasons(int(match_json['scheduledAt'][:4]), int(match_json['scheduledAt'][5:7]))
                match_obj = Match(
                    id=match_json['id'],
                    name=match_json['name'],
                    sets=match_json['numberOfGames'],
                    plan_date=match_json['scheduledAt'],
                    away_team_id=match_json['awayTeamId'],
                    local_team_id=match_json['homeTeamId'],
                    season_id=match_json['tournamentId'],
                    ini_date=match_json['beginAt'],
                    end_date=match_json['endAt']
                )
                self.db.session.add(match_obj)
            match_list_result.append(match_obj)
        self.db.session.commit()
        return match_list_result

    def populate_seasons(self, year, month):
        season_list = self.api.get_seasons(year, month)
        for season_json in season_list:
            season_obj = self.db.session.get(Season, season_json['id'])
            if season_obj is None:
                league_json = season_json['serie']['league']
                if self.db.session.get(League, league_json['id']) is None:
                    league_obj = League(
                        id=league_json['id'],
                        name=league_json['name'],
                        acronym=league_json['shortName'],
                        img=league_json['imageUrl'],
                    )
                    self.db.session.add(league_obj)
                season_obj = Season(
                    id=season_json['id'],
                    name=season_json['name'],
                    serie_id=season_json['serie']['id'],
                    ini_date=season_json['beginAt'],
                    end_date=season_json['endAt'],
                    league_id=league_json['id']
                )
                self.db.session.add(season_obj)
        self.db.session.commit()

    def populate_result(self, match_id, set=1):
        load = True
        result_json = self.api.get_match_result(match_id, set)
        if result_json:
            if self.db.session.get(Match, match_id) is None:  # If doesn't exist match at DB
                self.populate_matchs(MatchStatus.FINISHED, year=int(result_json['beginAt'][:4]),
                                     month=int(result_json['beginAt'][5:7]), limit=100)
            match_obj = self.db.session.get(Match, match_id)
            for result_obj in match_obj.results:
                if result_obj.set == set:
                    load = False
            if load:
                result_obj_1, result_obj_2 = Result.create_from_web_json(result_json, match_id, set)
                self.db.session.add(result_obj_1)
                self.db.session.add(result_obj_2)
                self.db.session.commit()

    def populate_teams(self, season_id):
        team_list = self.api.get_teams(season_id)
        for team in team_list:
            team_json = team['team']
            if self.db.session.get(Team, team_json['id']) is None:
                team_obj = Team(
                    id=int(team_json['id']),
                    name=team_json['name'],
                    acronym=team_json['acronym'],
                    img=team_json['imageUrl'],
                    website=team_json['website'],
                    nationality=team_json['nationality'],
                )
                self.db.session.add(team_obj)
        self.db.session.commit()
