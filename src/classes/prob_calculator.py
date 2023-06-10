from src.models import Result, Match, Probability
from sqlalchemy import or_, desc


class ProbCalculator:

    def __init__(self, db):
        self.db = db

    def create_probabilities_from_team_at_season(self, session, team_id, league_id=None):
        # Get match of the team at a league
        if league_id:
            matches = session.query(Match).filter(
                Match.season.has(league_id=league_id), Match.end_date.isnot(None),
                or_(Match.local_team_id == team_id, Match.away_team_id == team_id)).all()
        else:
            matches = session.query(Match).filter(Match.end_date.isnot(None),
                                                  or_(Match.local_team_id == team_id,
                                                      Match.away_team_id == team_id)).all()
        # Get the results of the match an order it by match.ini_date
        results = session.query(Result).filter(
            Result.match_id.in_([match.id for match in matches]),
            Result.team_id == team_id
        ).join(Result.match).order_by(desc(Match.ini_date)).all()
        if results:
            probability = session.query(Probability).filter_by(team_id=team_id, league_id=league_id).first()
            if probability is None:
                probability = Probability(team_id=team_id, league_id=league_id)
                session.add(probability)
                probability.update_data(session, results)
            else:
                probability.update_data(session, results)
            session.commit()
