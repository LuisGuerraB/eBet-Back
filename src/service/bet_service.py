from flask_login import login_required, current_user
from flask_smorest import Blueprint, abort

from src.models import Bet, BetSchema
from src.models.bet import InsuficientFundsException, BettingOddsNotFoundException, MultiplierNoMatchException, \
    ExistingBetException

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
        bet = Bet.create(user, **params)
        return bet
    except (InsuficientFundsException, BettingOddsNotFoundException, MultiplierNoMatchException, ExistingBetException) as e:
        abort(409, message=e.message)

