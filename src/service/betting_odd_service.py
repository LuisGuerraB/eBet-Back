from flask_smorest import Blueprint, abort

from database import db

from src.models import BettingOddsByMatchSchema, Match, BettingOdd, Probability

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
            abort(404, message='control-error.match-not-found')
        for play in match.plays:
            if play.local:
                local_team_id = play.team_id
            else:
                away_team_id = play.team_id
        # This wont be necesarly when autopopulate is up
        Probability.create_probabilities_from_team_at_league(session, local_team_id, match.tournament.league.id)
        Probability.create_probabilities_from_team_at_league(session, local_team_id)
        Probability.create_probabilities_from_team_at_league(session, away_team_id, match.tournament.league.id)
        Probability.create_probabilities_from_team_at_league(session, away_team_id)
        prob_finish_early = Probability.finish_early_match(session, match)
        #try:
        betting_odds_local_team = BettingOdd.create(session, match, local_team_id, away_team_id)
        betting_odds_away_team = BettingOdd.create(session, match, away_team_id, local_team_id)
        #except Exception as e:
        #    abort(404, message='control-error.' + str(e))
        return {'away_team_odds': betting_odds_away_team.odds, 'local_team_odds': betting_odds_local_team.odds, 'prob_finish_early' : prob_finish_early}
