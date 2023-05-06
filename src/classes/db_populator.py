from marshmallow.schema import Schema
from marshmallow import fields, validate

from src.enums import MatchStatus
from src.classes.prob_calculator import ProbCalculator
from src.classes.api_scrapper import ApiScrapper
from src.models import Match, Season, League, Result, Team, Probability
import datetime


class DbPopulator:

    def __init__(self, db):
        self.db = db
        self.prob = ProbCalculator(db)

    def populate_DB(self):
        today = datetime.date.today()
        year = today.year
        actual_month = today.month
        limit = 500
        total_matches_with_results = []
        with self.db.session() as session:

            # Fill the DB with matchs that have not yet occured
            for month in range(actual_month, 13):
                self.populate_matches(session, MatchStatus.NOT_STARTED, year=year, month=month, limit=limit)

            # Fill the DB with matchs that have finished
            for month in range(1, actual_month + 1):
                matches_finished_list = self.populate_matches(session, MatchStatus.FINISHED, year=year, month=month,
                                                              limit=limit)
                total_matches_with_results += matches_finished_list

            # Fill the DB with the results of finished matches
            for match in total_matches_with_results:
                for set in range(match.sets):
                    result = session.query(Result).filter_by(match_id=match.id, set=set + 1).first()
                    if result is None:
                        self.populate_result(session, match.id, set + 1)

            # Fill the DB with the probabilities of teams in general
            teams = session.query(Team).all()
            for team in teams:
                self.prob.create_probabilities_from_team_at_season(session, team.id)

    def populate_matches(self, session, status, year=None, month=None, leagueId=None, limit=5, page=0):
        match_list = ApiScrapper.get_list_match(status, year, month, leagueId, limit, page)
        match_list_result = []
        for match_json in match_list:
            if match_json['awayTeamId'] is None or match_json['homeTeamId'] is None:
                continue
            match_obj = session.get(Match, match_json['id'])
            if match_obj is None:
                if (session.get(Team, match_json['awayTeamId']) is None or
                        session.get(Team, match_json['homeTeamId']) is None):
                    self.populate_teams(session, match_json['tournamentId'])
                if session.get(Season, match_json['tournamentId']) is None:
                    self.populate_seasons(session, status, int(match_json['scheduledAt'][:4]),
                                          int(match_json['scheduledAt'][5:7]))
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
                session.add(match_obj)
            match_list_result.append(match_obj)
        session.commit()
        return match_list_result

    def populate_seasons(self, session, status, year, month):
        season_list = ApiScrapper.get_seasons(status, year, month)
        for season_json in season_list:
            season_obj = session.get(Season, season_json['id'])
            if season_obj is None:
                league_json = season_json['serie']['league']
                if session.get(League, league_json['id']) is None:
                    league_obj = League(
                        id=league_json['id'],
                        name=league_json['name'],
                        acronym=league_json['shortName'],
                        img=league_json['imageUrl'],
                    )
                    session.add(league_obj)
                season_obj = Season(
                    id=season_json['id'],
                    name=season_json['name'],
                    serie_id=season_json['serie']['id'],
                    ini_date=season_json['beginAt'],
                    end_date=season_json['endAt'],
                    league_id=league_json['id']
                )
                session.add(season_obj)
        session.commit()

    def populate_result(self, session, match_id, set=1):
        load = True
        result_json = ApiScrapper.get_match_result(match_id, set)
        if result_json:
            if session.get(Match, match_id) is None:  # If doesn't exist match at DB
                self.populate_matches(MatchStatus.FINISHED, year=int(result_json['beginAt'][:4]),
                                      month=int(result_json['beginAt'][5:7]), limit=100)
            match_obj = session.get(Match, match_id)
            for result_obj in match_obj.results:
                if result_obj.set == set:
                    load = False
            if load:
                result_obj_1, result_obj_2 = Result.create_from_web_json(result_json, match_id, set)
                session.add(result_obj_1)
                session.add(result_obj_2)
                session.commit()

    def populate_teams(self, session, season_id):
        team_list = ApiScrapper.get_teams(season_id)
        for team in team_list:
            team_json = team['team']
            if session.get(Team, team_json['id']) is None:
                team_obj = Team(
                    id=int(team_json['id']),
                    name=team_json['name'],
                    acronym=team_json['acronym'],
                    img=team_json['imageUrl'],
                    website=team_json['website'],
                    nationality=team_json['nationality'],
                )
                session.add(team_obj)
        session.commit()


class MatchPopulateSchema(Schema):
    status = fields.Enum(MatchStatus, required=True, metadata={'description': '#### Status of matches'})
    year = fields.Integer(required=False, validate=validate.Range(min=2020),
                          metadata={'description': '#### Year of the matches'})
    month = fields.Integer(required=False, validate=validate.Range(min=1, max=12),
                           metadata={'description': '#### Month of the matches'})
    leagueId = fields.Integer(required=False, default=None, metadata={'description': '#### League of the matches'})
    limit = fields.Integer(required=False, default=50, metadata={'description': '#### Number of matches you want'})
    page = fields.Integer(required=False, default=0, metadata={'description': '#### Page you want'})
