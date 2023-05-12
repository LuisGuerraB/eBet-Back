from flask_smorest import Blueprint, abort
from app import db

from src.models import Bet, BetSchema

api_url = '/bet'
api_name = 'Bet'
api_description = 'Database bet methods'

bet_blp = Blueprint(
    name=api_name,
    description=api_description,
    url_prefix=api_url,
    import_name=__name__,
)


@bet_blp.route('/', methods=['POST'])
@bet_blp.doc(tags=[api_name])
@bet_blp.arguments(BetSchema)
@bet_blp.response(200, BetSchema)
def create_bet(params):
    with db.session() as session:
        # TODO Find out if the user has enough balance to make the bet
        if Bet.exist(params['match_id'], params['user_id'], params['type'], params['subtype']):
            abort(400, message='You already have a bet on this match. Try updating the already existing bet')
        try:
            bet = Bet(**params)
            session.add(bet)
            session.commit()
            return BetSchema().dump(bet)
        except:
            abort(400, message='Invalid bet parameters')
