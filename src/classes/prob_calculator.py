from src.models import Result, Match, Probability
from sqlalchemy import or_, desc


class ProbCalculator:

    def __init__(self, db):
        self.db = db


    def create_probabilities_from_team_at_season(self, session, team_id, league_id=None):
        # Obtener los partidos del equipo en la liga
        if league_id:
            matches = session.query(Match).filter(
                Match.season.has(league_id=league_id),
                or_(Match.local_team_id == team_id, Match.away_team_id == team_id)).all()
        else:
            matches = session.query(Match).filter(
                or_(Match.local_team_id == team_id, Match.away_team_id == team_id)).all()

        # Obtener los resultados de los partidos y ordenarlos por la fecha de inicio
        results = session.query(Result).filter(
            Result.match_id.in_([match.id for match in matches]),
            Result.team_id == team_id
        ).join(Result.match).order_by(desc(Match.ini_date)).all()

        if results:
            probability = session.query(Probability).filter_by(team_id=team_id, league_id=league_id).first()

            if probability is None:
                probability = Probability()
                probability.update_data(results, team_id, league_id)
                session.add(probability)
            else:
                probability.update_data(results, team_id, league_id)
            session.commit()

