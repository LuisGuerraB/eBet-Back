from flask_login import login_required, current_user
from flask_smorest import Blueprint, abort

from src.models import Bet, BetSchema
from src.models.bet import InsuficientFundsException, BettingOddsNotFoundException, MultiplierNoMatchException, \
    ExistingBetException, BetListSchema

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
    except (
    InsuficientFundsException, BettingOddsNotFoundException, MultiplierNoMatchException, ExistingBetException) as e:
        abort(409, message=e.message)


@bet_blp.route(api_url + '/list', methods=['GET'])
@bet_blp.doc(tags=[api_name])
@login_required
@bet_blp.response(200, BetListSchema)
def get_user_bets():
    user = current_user
    bets = Bet.get_user_bets(user)
    return {'items': bets, 'total': len(bets)}
