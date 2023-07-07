from marshmallow.schema import Schema
from marshmallow import fields, validate
from sqlalchemy import or_

from database import db
from .api_scrapper_interface import ApiScrapperInterface
from .scheduler import Scheduler
from src.enums import MatchStatus
from .api_scrapper_lol import ApiScrapperLol
from src.models import Match, Tournament, League, Result, Team, Participation, Probability, Play, Bet, BettingOdd
import datetime


def get_iniciales(string):
    words = string.split()  # Divide la cadena en palabras
    inicial_letters = [word[0] for word in words]  # Obtiene el primer carácter de cada palabra
    return ''.join(inicial_letters)


class DbPopulator:

    def __init__(self, api_scrapper=ApiScrapperLol()):
        self.api_scrapper = api_scrapper

    def set_api_scrapper(self, api_scrapper):
        if isinstance(api_scrapper, ApiScrapperInterface):
            self.api_scrapper = api_scrapper

    def populate_DB(self):
        today = datetime.date.today()
        year = today.year
        current_month = today.month
        limit = 500
        total_matches_with_results = []
        # Fill the DB with matchs that have not yet occured
        with db.session(expire_on_commit=False) as session:
            # Fill the DB with matchs that have not yet occured
            for month in range(current_month, 13):
                self.populate_matches(MatchStatus.NOT_STARTED, year=year, month=month, limit=limit, session=session)

            # Fill the DB with matchs that have finished
            for month in range(current_month + 1, 0, -1):
                matches_finished_list = self.populate_matches(MatchStatus.FINISHED, year=year, month=month,
                                                              limit=limit, session=session)
                total_matches_with_results += matches_finished_list

            # Fill the DB with the results of finished matches
            for match in total_matches_with_results:
                if match is None:
                    raise Exception(str(match))
                Result.update_result_from_match(match, session=session)
                sets = match.get_final_number_of_sets() if match.get_final_number_of_sets() is not None else match.sets
                plays = session.query(Play).filter(Play.match_id == match.id).all()
                for play in plays:
                    for set in range(sets):
                        result = session.query(Result).filter_by(play_id=play.id, set=set + 1).first()
                        if result is None:
                            self.populate_result(match.id, set + 1, session=session)
                self.resolve_bets(match, session=session)

            leagues = League.query.all()
            for league in leagues:
                self.populate_teams(league.id, session)

            # Fill the DB with the probabilities of teams in general
            teams = Team.query.all()
            for team in teams:
                prob = session.query(Probability).filter(Probability.team_id == team.id,
                                                         Probability.league_id is None).first()
                if prob is not None:
                    prob.updated = False
                Probability.create_probabilities_from_team_at_league(team.id, session=session)

    def populate_probabilites(self, team_id, league_id=None, session=None):
        Probability.create_probabilities_from_team_at_league(team_id, league_id, session)

    def populate_matches(self, status, year=None, month=None, leagueId=None, limit=5, page=0, session=None):
        if session is None:
            session = db.session()
        match_list = self.api_scrapper.get_list_match(status, year, month, leagueId, limit, page)
        match_list_result = []
        scheduler = Scheduler(DbPopulator())
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
                    self.populate_tournaments(status, int(match_json['scheduledAt'][:4]),
                                              int(match_json['scheduledAt'][5:7]), session=session)
                if (session.get(Team, match_json['awayTeamId']) is None or
                        session.get(Team, match_json['homeTeamId']) is None):
                    self.populate_teams(match_json['tournament']['serie']['league']['id'], session=session)
                match_obj = Match(
                    id=match_json['id'],
                    sets=match_json['numberOfGames'],
                    plan_date=match_json['scheduledAt'],
                    tournament_id=match_json['tournamentId'],
                    ini_date=match_json['beginAt'],
                    end_date=match_json['endAt']
                )
                session.add(match_obj)
                if session.get(Team, match_json['homeTeamId']) is not None:
                    play_local = Play(team_id=match_json['homeTeamId'], match_id=match_obj.id, local=True)
                    session.add(play_local)
                if session.get(Team, match_json['awayTeamId']) is not None:
                    play_away = Play(team_id=match_json['awayTeamId'], match_id=match_obj.id, local=False)
                    session.add(play_away)
            match_obj.plan_date = match_json['scheduledAt']
            match_obj.ini_date = match_json['beginAt']
            match_obj.end_date = match_json['endAt']
            if match_json['endAt']:
                self.resolve_bets(match_obj, session=session)
            match_list_result.append(match_obj)
        session.commit()
        return match_list_result

    def populate_tournaments(self, status, year, month, session=None):
        if session is None:
            session = db.session()
        tournament_list = self.api_scrapper.get_tournaments(status, year, month)
        for tournament_json in tournament_list:
            tournament_obj = session.get(Tournament, tournament_json['id'])
            if tournament_obj is None:
                league_json = tournament_json['serie']['league']
                if session.get(League, league_json['id']) is None:
                    league_obj = League(
                        id=league_json['id'],
                        name=league_json['name'],
                        acronym=league_json['shortName'],
                        img=league_json['imageUrl'].replace('black', 'white'),
                    )
                    session.add(league_obj)
                tournament_obj = Tournament(
                    id=tournament_json['id'],
                    name=tournament_json['name'],
                    ini_date=tournament_json['beginAt'],
                    end_date=tournament_json['endAt'],
                    league_id=league_json['id']
                )
                session.add(tournament_obj)
        session.commit()

    def populate_result(self, match_id, set=1, session=None):
        if session is None:
            session = db.session()
        load = True
        result_json = self.api_scrapper.get_match_result(match_id, set)
        if result_json:
            if session.get(Match, match_id) is None:  # If doesn't exist match at DB
                self.populate_matches(MatchStatus.FINISHED, year=int(result_json['beginAt'][:4]),
                                      month=int(result_json['beginAt'][5:7]), limit=500, session=session)
            match_obj = session.get(Match, match_id)
            for result_obj in [play.result for play in match_obj.plays if
                               play.result is not None and len(play.result.stats) != 0]:
                if result_obj.set == set:
                    load = False
            if load:
                Result.create_from_web_json(session, result_json, match_id, set)
            Result.update_result_from_match(match_obj, session=session)
            if match_obj.get_final_number_of_sets() is not None:
                match_obj.end_date = result_json['endAt']
            session.commit()
            return result_json

    def populate_teams(self, league_id, session=None):
        if session is None:
            session = db.session()
        regular_tournaments = Tournament.get_regular_tournaments(league_id)
        for regular_tournament in regular_tournaments:
            team_list = self.api_scrapper.get_teams(regular_tournament.id)
            for team in team_list:
                team_json = team['team']
                team_obj = session.get(Team, team_json['id'])
                img = team_json['imageUrlDarkMode'] if 'imageUrlDarkMode' in team_json else team_json['imageUrl']
                if team_obj is None:
                    team_obj = Team(
                        id=int(team_json['id']),
                        name=team_json['name'],
                        acronym=team_json['acronym'] if team_json['acronym'] is not None else get_iniciales(
                            team_json['name']),
                        img=img,
                        website=team_json['website'],
                        nationality=team_json['nationality'],
                        league_id=league_id
                    )
                    session.add(team_obj)
                self.populate_participations(team_obj, team['position'], team['point'], regular_tournament.id)
        session.commit()

    def populate_participations(self, team, position, points, tournament_id):
        with db.session() as session:
            participation = session.query(Participation).filter_by(team_id=team.id, tournament_id=tournament_id).first()
            if participation is None:
                participation = Participation(team_id=team.id, tournament_id=tournament_id, position=position,
                                              points=points)
                session.add(participation)
            participation.position = position
            participation.points = points
            session.commit()

    def update_data_from_match(self, match, session):
        league_id_of_match = match.tournament.league_id
        for play in match.plays:
            self.populate_teams(league_id_of_match, session=session)
            probabilities = session.query(Probability).filter(
                Probability.team_id == play.team_id,
                or_(Probability.league_id == league_id_of_match, Probability.league_id == None)
            ).all()
            for prob in probabilities:
                prob.updated = False
            self.populate_probabilites(play.team_id, league_id_of_match, session=session)
            self.populate_probabilites(play.team_id, session=session)
            betting_odds = session.query(BettingOdd).join(Play, BettingOdd.play_id == Play.id).filter(
                Play.team_id == play.team_id).all()
            for betting_odd in betting_odds:
                betting_odd.updated = False
        session.commit()

    def resolve_bets(self, match, session):
        bets = session.query(Bet).join(Play, Play.id == Bet.play_id).filter(Play.match_id == match.id).all()
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
