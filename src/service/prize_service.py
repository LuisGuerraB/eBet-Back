import smtplib

from flask import request, current_app
from flask_login import login_required, current_user
from flask_mail import Mail, Message
from flask_smorest import Blueprint, abort

from database import db
from src.enums import Privilege
from src.models.prize import PrizeSchema, Prize, PrizeListSchema, EmailSchema

api_url = '/prize'
api_name = 'Prize'
api_description = 'Methods over Prize'

prize_blp = Blueprint(
    name=api_name,
    description=api_description,
    import_name=__name__,
)


@prize_blp.route(api_url + '/', methods=['POST'])
@prize_blp.doc(tags=[api_name])
@prize_blp.arguments(PrizeSchema, location='query')
@login_required
@prize_blp.response(201)
def create_prize(params):
    if current_user.has_privilege(Privilege.MARKETING):
        if not request.files.get('img'):
            abort(404, message='control-error.no-img')
        if Prize.create_prize(params['amount'], request.files.get('img'), params['price']):
            return
        else:
            abort(404, message='control-error.invalid-prize')

    else:
        abort(401, message='control-error.no-privileges')


@prize_blp.route(api_url + '/list', methods=['GET'])
@prize_blp.doc(tags=[api_name])
@prize_blp.response(200, PrizeListSchema)
def get_prizes():
    with db.session() as session:
        prizes = session.query(Prize).filter(Prize.amount > 0).all()
        if prizes is None:
            prizes = []
        return {'items': prizes, 'total': len(prizes)}


@prize_blp.route(api_url + '/<int:prize_id>', methods=['DELETE'])
@prize_blp.doc(tags=[api_name])
@login_required
@prize_blp.response(201)
def delete_prize(prize_id):
    if current_user.has_privilege(Privilege.MARKETING):

        with db.session() as session:
            prize = session.query(Prize).get(prize_id)
            if prize is not None:
                if prize.delete(session):
                    return
                else:
                    abort(404, message='control-error.unable-prize-deletion')
            else:
                abort(404, message='control-error.no-prize-found')
    else:
        abort(401, message='control-error.no-privileges')

@prize_blp.route(api_url + '/buy/<int:prize_id>', methods=['POST'])
@prize_blp.doc(tags=[api_name])
@login_required
@prize_blp.arguments(EmailSchema, location='json')
@prize_blp.response(200)
def buy_prize(email, prize_id):
    with db.session() as session:
        prize = session.query(Prize).get(prize_id)
        if prize is None or prize.amount < 1:
            abort(404, message='control-error.no-prize-found')
        if current_user.balance < prize.price:
            abort(404, message='control-error.insufficient-balance')
        prize.buy(session)
        current_user.balance -= prize.price
        mail = Mail(current_app)
        receiver = email.get('email')
        subject = 'E-Bet Prize'
        content = """
            <html>
                <body>
                    <h1>Prize bought</h1>
                    <h2>Here is your code:</h2>
                    <p>XXXX-YYYY-ZZZZ</p>
                </body>
            </html>
        """
        message = Message(subject, recipients=[receiver])
        message.html = content
        mail.send(message)
        return 200
