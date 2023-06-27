from flask import current_app
from marshmallow.schema import Schema
from marshmallow import fields, validate
from sqlalchemy import or_

from database import db
from .scheduler import Scheduler
from src.enums import MatchStatus
from src.classes.api_scrapper import ApiScrapper
from src.models import Match, Tournament, League, Result, Team, Participation, Probability, Bet
import datetime


class DbPopulator:

    @classmethod
    def populate_DB(cls):
        today = datetime.date.today()
        year = today.year
        actual_month = today.month
        limit = 500
        total_matches_with_results = []
        # Fill the DB with matchs that have not yet occured
        with db.session(expire_on_commit=False) as session:
            # Fill the DB with matchs that have not yet occured
            for month in range(actual_month, 13):
                cls.populate_matches(MatchStatus.NOT_STARTED, year=year, month=month, limit=limit)

            # Fill the DB with matchs that have finished
            for month in range(actual_month + 1, 1, -1):
                matches_finished_list = cls.populate_matches(MatchStatus.FINISHED, year=year, month=month,
                                                             limit=limit, session=session)
                total_matches_with_results += matches_finished_list

            # Fill the DB with the results of finished matches
            for match in total_matches_with_results:
                match.update_result()
                sets = match.final_set if match.final_set is not None else match.sets
                for set in range(sets):
                    result = session.query(Result).filter_by(match_id=match.id, set=set + 1).first()
                    if result is None:
                        cls.populate_result(match.id, set + 1, session=session)

            # Fill the DB with the probabilities of teams in general
            teams = Team.query.all()
            for team in teams:
                Probability.create_probabilities_from_team_at_league(team.id)

    @classmethod
    def populate_probabilites(cls, team_id, league_id=None, session=None):
        if session is None:
            session = db.session()
        Probability.create_probabilities_from_team_at_league(session, team_id, league_id)

    @classmethod
    def populate_matches(cls, status, year=None, month=None, leagueId=None, limit=5, page=0, session=None):
        if session is None:
            session = db.session()
        match_list = ApiScrapper.get_list_match(status, year, month, leagueId, limit, page)
        match_list_result = []
        scheduler = Scheduler(cls())
        if match_list is None:
            return []
        for match_json in match_list:
            if match_json['awayTeamId'] is None or match_json['homeTeamId'] is None:
                continue
            match_obj = session.get(Match, match_json['id'])
            if status == MatchStatus.NOT_STARTED:
                scheduler.add_match_to_scheduler(match_json['id'], match_json['numberOfGames'],
                                                 match_json['scheduledAt'])
            if match_obj is None:
                if session.get(Tournament, match_json['tournamentId']) is None:
                    cls.populate_tournaments(status, int(match_json['scheduledAt'][:4]),
                                             int(match_json['scheduledAt'][5:7]))
                if (session.get(Team, match_json['awayTeamId']) is None or
                        session.get(Team, match_json['homeTeamId']) is None):
                    cls.populate_teams(match_json['tournament']['serie']['league']['id'])
                match_obj = Match(
                    id=match_json['id'],
                    name=match_json['name'],
                    sets=match_json['numberOfGames'],
                    plan_date=match_json['scheduledAt'],
                    away_team_id=match_json['awayTeamId'],
                    local_team_id=match_json['homeTeamId'],
                    tournament_id=match_json['tournamentId'],
                    ini_date=match_json['beginAt'],
                    end_date=match_json['endAt']
                )
                session.add(match_obj)
            match_obj.ini_date = match_json['beginAt']
            match_obj.end_date = match_json['endAt']
            match_list_result.append(match_obj)
        session.commit()
        return match_list_result

    @classmethod
    def populate_tournaments(cls, status, year, month):
        with db.session() as session:
            tournament_list = ApiScrapper.get_tournaments(status, year, month)
            for tournament_json in tournament_list:
                tournament_obj = session.get(Tournament, tournament_json['id'])
                if tournament_obj is None:
                    league_json = tournament_json['serie']['league']
                    if session.get(League, league_json['id']) is None:
                        league_obj = League(
                            id=league_json['id'],
                            name=league_json['name'],
                            acronym=league_json['shortName'],
                            img=league_json['imageUrl'],
                        )
                        session.add(league_obj)
                    tournament_obj = Tournament(
                        id=tournament_json['id'],
                        name=tournament_json['name'],
                        serie_id=tournament_json['serie']['id'],
                        ini_date=tournament_json['beginAt'],
                        end_date=tournament_json['endAt'],
                        league_id=league_json['id']
                    )
                    session.add(tournament_obj)
            session.commit()

    @classmethod
    def populate_result(cls, match_id, set=1, session=None):
        if session is None:
            session = db.session()

        load = True
        result_json = ApiScrapper.get_match_result(match_id, set)
        if result_json:
            if session.get(Match, match_id) is None:  # If doesn't exist match at DB
                cls.populate_matches(MatchStatus.FINISHED, year=int(result_json['beginAt'][:4]),
                                     month=int(result_json['beginAt'][5:7]), limit=100)
            match_obj = session.get(Match, match_id)
            for result_obj in match_obj.results:
                if result_obj.set == set:
                    load = False
            if load:
                Result.create_from_web_json(session, result_json, match_id, set)
        match_obj = session.get(Match, match_id)
        if match_obj.end_date is not None:
            match_obj.update_result()
        session.commit()
        return

    @classmethod
    def populate_teams(cls, league_id, session=None):
        with current_app.app_context():
            if session is None:
                session = db.session()

            regular_tournament = Tournament.get_regular_tournament(league_id)
            if regular_tournament is not None:
                reg_tournament_id = regular_tournament.id
                team_list = ApiScrapper.get_teams(reg_tournament_id)
                for team in team_list:
                    team_json = team['team']
                    team_obj = session.get(Team, team_json['id'])
                    img = team_json['imageUrlDarkMode'] if 'imageUrlDarkMode' in team_json else team_json['imageUrl']
                    if team_obj is None:
                        team_obj = Team(
                            id=int(team_json['id']),
                            name=team_json['name'],
                            acronym=team_json['acronym'],
                            img=img,
                            website=team_json['website'],
                            nationality=team_json['nationality'],
                            league_id=league_id
                        )
                        session.add(team_obj)
                    cls.populate_participations(team_obj, team['position'], team['point'],
                                                reg_tournament_id)
            session.commit()

    @classmethod
    def populate_participations(cls, team, position, points, tournament_id):
        with db.session() as session:
            participation = session.query(Participation).filter_by(team_id=team.id, tournament_id=tournament_id).first()
            if participation is None:
                participation = Participation(team_id=team.id, tournament_id=tournament_id, position=position,
                                              points=points)
                session.add(participation)
            participation.position = position
            participation.points = points
            session.commit()

    @classmethod
    def update_data_from_match(cls, match, session):
        league_id_of_match = match.tournament.league_id
        cls.populate_teams(league_id_of_match, session=session)
        probabilities = Probability.query.filter(
            or_(Probability.team_id == match.away_team_id, Probability.team_id == match.local_team_id),
            or_(Probability.league_id == league_id_of_match, Probability.league_id == None)
        ).all()
        for prob in probabilities:
            prob.updated = False
        cls.populate_probabilites(match.away_team_id, league_id_of_match, session=session)
        cls.populate_probabilites(match.local_team_id, league_id_of_match, session=session)
        cls.populate_probabilites(match.away_team_id, session=session)
        cls.populate_probabilites(match.local_team_id, session=session)

    @classmethod
    def resolve_bets(cls, match, session):
        bets = session.query(Bet).filter_by(match_id=match.id).all()
        for bet in bets:
            bet.resolve(session)


class MatchPopulateSchema(Schema):
    status = fields.Enum(MatchStatus, required=True, metadata={'description': '#### Status of matches'})
    year = fields.Integer(required=False, validate=validate.Range(min=2020),
                          metadata={'description': '#### Year of the matches'})
    month = fields.Integer(required=False, validate=validate.Range(min=1, max=12),
                           metadata={'description': '#### Month of the matches'})
    leagueId = fields.Integer(required=False, default=None, metadata={'description': '#### League of the matches'})
    limit = fields.Integer(required=False, default=50, metadata={'description': '#### Number of matches you want'})
    page = fields.Integer(required=False, default=0, metadata={'description': '#### Page you want'})
