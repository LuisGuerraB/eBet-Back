from flask_login import login_required, current_user
from flask_smorest import Blueprint, abort
from app import db

from src.models import Bet, BetSchema

api_url = '/bet'
api_name = 'Bet'
api_description = 'Database bet methods'

bet_blp = Blueprint(
    name=api_name,
    description=api_description,
    import_name=__name__,
)


@bet_blp.route(api_url + '/', methods=['POST'])
@bet_blp.doc(tags=[api_name])
@login_required
@bet_blp.arguments(BetSchema)
@bet_blp.response(200, BetSchema)
def create_bet(params):
    with db.session() as session:
        user = current_user
        if user.balance < params['amount']:
            abort(400, message='Insufficient funds')
        if Bet.exist(params['match_id'], user.id, params['type'], params['subtype']):
            abort(400, message='You already have a bet on this match. Try updating the already existing bet')
        try:
            bet = Bet(
                date=params['date'],
                type=params['type'],
                subtype=params['subtype'],
                multiplier=params['multiplier'],
                amount=params['amount'],
                match_id=params['match_id'],
                user_id=user.id
            )
            session.add(bet)
            session.commit()
            bet = Bet.query.get(bet.id)
            return bet
        except:
            abort(400, message='Invalid bet parameters')
