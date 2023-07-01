from flask_login import login_required, current_user
from flask_smorest import Blueprint, abort

from database import db
from src.models import Bet, BetSchema, BetListSchema

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
    user = current_user
    try:
        bet_id = Bet.create(user, **params)
        return Bet.query.get(bet_id)
    except Exception as e:
        abort(404, message="control-error." + str(e))


@bet_blp.route(api_url + '/list', methods=['GET'])
@bet_blp.doc(tags=[api_name])
@login_required
@bet_blp.response(200, BetListSchema)
def get_user_bets():
    user = current_user
    bets = Bet.get_user_bets(user)
    return {'items': bets, 'total': len(bets)}


@bet_blp.route(api_url + '/<int:bet_id>/amount/<int:amount>', methods=['PUT'])
@bet_blp.doc(tags=[api_name])
@login_required
@bet_blp.response(200, BetSchema())
def update_bet_amount(bet_id, amount):
    with db.session() as session:
        bet = session.query(Bet).get(bet_id)
        if bet is None:
            abort(404, message='control-error.bet-not-found')
        if bet.user_id != current_user.id:
            abort(403, message='control-error.permission-denied')
        try:
            bet.update_amount(session, amount)
            bet = session.query(Bet).get(bet_id)
            BetSchema().dump(bet)
            return bet
        except Exception as e:
            abort(403, message="control-error." + str(e))


@bet_blp.route(api_url + '/<int:bet_id>', methods=['DELETE'])
@bet_blp.doc(tags=[api_name])
@login_required
@bet_blp.response(201)
def delete_bet(bet_id):
    with db.session() as session:
        bet = session.query(Bet).get(bet_id)
        if bet is None:
            abort(404, message='control-error.bet-not-found')
        if bet.user_id != current_user.id:
            abort(403, message='control-error.permission-denied')
        bet.delete(session)
        return 201
