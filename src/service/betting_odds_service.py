from flask_smorest import Blueprint, abort
from app import db
from src.classes import ProbCalculator

from src.models import BettingOddsByMatchSchema, Match, BettingOdds, BettingOddSchema

api_url = '/betting_odds'
api_name = 'BettingOdds'
api_description = 'Database betting odds methods'

betting_odds_blp = Blueprint(
    name=api_name,
    description=api_description,
    import_name=__name__,
)


@betting_odds_blp.route(api_url + '/<int:match_id>', methods=['GET'])
@betting_odds_blp.doc(tags=[api_name])
@betting_odds_blp.response(200, BettingOddsByMatchSchema)
def get_betting_ods_from_match(match_id):
    with db.session() as session:
        match = session.query(Match).get(match_id)
        if not match:
            abort(404, 'Match not found')
        prob = ProbCalculator(db)
        prob.create_probabilities_from_team_at_season(session, match.local_team_id, match.season.league.id)
        prob.create_probabilities_from_team_at_season(session, match.local_team_id)
        prob.create_probabilities_from_team_at_season(session, match.away_team_id, match.season.league.id)
        prob.create_probabilities_from_team_at_season(session, match.away_team_id)

        betting_odds_away_team = session.query(BettingOdds).filter(BettingOdds.team_id == match.away_team_id,
                                                                   BettingOdds.match_id == match_id).first()
        if not betting_odds_away_team:
            betting_odds_away_team = BettingOdds(match_id, match.away_team_id, match.local_team_id)
            session.add(betting_odds_away_team)
        betting_odds_away_team.update_data(session, match_id, match.away_team_id, match.local_team_id)

        betting_odds_local_team = session.query(BettingOdds).filter(BettingOdds.team_id == match.local_team_id,
                                                                    BettingOdds.match_id == match_id).first()
        if not betting_odds_local_team:
            betting_odds_local_team = BettingOdds(match_id, match.local_team_id, match.away_team_id)
            session.add(betting_odds_local_team)
        betting_odds_local_team.update_data(session, match_id, match.local_team_id, match.away_team_id)
        session.commit()
        return {'away_team_odds': BettingOddSchema().dump(betting_odds_away_team), 'local_team_odds': BettingOddSchema().dump(betting_odds_local_team)}
