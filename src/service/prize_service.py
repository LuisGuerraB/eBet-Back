from flask import request
from flask_login import login_required, current_user
from flask_smorest import Blueprint, abort

from database import db
from src.models.prize import PrizeSchema, Prize, FileSchema, PrizeListSchema

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
    if current_user.has_privilege('marketing'):
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
