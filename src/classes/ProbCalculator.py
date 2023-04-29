from src.models import Result, Match, Probability
from sqlalchemy import or_


class ProbCalculator:

    def __init__(self, db):
        self.db = db


    def create_probabilities_from_team_at_season(self, session, team_id, season_id=None):
        results = (
            session.query(Result)
            .join(Match)
            .filter(Result.team_id == team_id, or_(Match.season_id == season_id, season_id is None))
            .order_by(Match.ini_date)
            .all()
        )
        if results:
            probability = session.query(Probability).filter_by(team_id=team_id, season_id=season_id).first()
            if probability is None:
                print('crea uno nuevo')
                probability = Probability()
                probability.update_data(results, team_id, season_id)
                session.add(probability)
            else:
                print('actualiza uno existente')
                probability.update_data(results, team_id, season_id)
            session.commit()

