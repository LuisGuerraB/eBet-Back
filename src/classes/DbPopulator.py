from src.Enums import MatchStatus
from src.classes.ApiScrapper import ApiScrapper
from src.models import Match, Season, League, Result
from src.models.Team import Team


class DbPopulator:

    def __init__(self, db):
        self.db = db
        self.api = ApiScrapper()

    def populate_matchs(self, status, year=None, month=None, leagueId=None, limit=5, page=0):
        match_list = self.api.get_list_match(status, year, month, leagueId, limit, page)
        for match_json in match_list:
            match_obj = self.db.session.get(Match, match_json.get('id'))
            if match_obj is None:
                match_obj = Match(
                    id=match_json.get('id'),
                    name=match_json.get('name'),
                    plan_date=match_json.get('scheduledAt'),
                    away_team_id=match_json.get('awayTeamId'),
                    local_team_id=match_json.get('homeTeamId'),
                    season_id=match_json.get('tournamentId'),
                    ini_date=match_json.get('beginAt'),
                    end_date=match_json.get('endAt')
                )
                if (self.db.session.get(Team, match_json.get('awayTeamId')) is None or
                        self.db.session.get(Team, match_json.get('homeTeamId')) is None):
                    self.populate_teams(match_json.get('tournamentId'))
                if self.db.session.get(Season, match_json.get('tournamentId')) is None:
                    self.populate_seasons(int(match_json.get('scheduledAt')[:4]))
                self.db.session.add(match_obj)
        self.db.session.commit()

    def populate_seasons(self, year):
        match_list = self.api.get_seasons(year)
        for match_json in match_list:
            season_json = match_json.get('tournament')
            if self.db.session.get(Season, season_json.get('id')) is None:
                league_json = season_json.get('serie').get('league')
                if self.db.session.get(League, league_json.get('id')) is None:
                    league_obj = League(
                        id=league_json.get('id'),
                        name=league_json.get('name'),
                        acronym=league_json.get('shortName'),
                        img=league_json.get('imageUrl'),
                    )
                    self.db.session.add(league_obj)
                season_obj = Season(
                    id=season_json.get('id'),
                    name=season_json.get('name'),
                    serie_id=season_json.get('serie').get('id'),
                    ini_date=season_json.get('beginAt'),
                    end_date=season_json.get('endAt'),
                    league_id=league_json.get('id')
                )
                self.db.session.add(season_obj)
        self.db.session.commit()

    def populate_result(self, match_id, set=1):
        load = True
        result_json = self.api.get_match_result(match_id, set)
        if (result_json):  # If there is a result to get for the match pass
            if self.db.session.get(Match, match_id) is None:  # If doesn't exist match at DB
                self.populate_matchs(MatchStatus.FINISHED, year=int(result_json.get('beginAt')[:4]),
                                     month=int(result_json.get('beginAt')[5:7]), limit=100)
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
            team_json = team.get('team')
            if self.db.session.get(Team, team_json.get('id')) is None:
                team_obj = Team(
                    id=int(team_json.get('id')),
                    name=team_json.get('name'),
                    acronym=team_json.get('acronym'),
                    img=team_json.get('imageUrl'),
                    website=team_json.get('website'),
                    nationality=team_json.get('nationality'),
                )
                self.db.session.add(team_obj)
        self.db.session.commit()
