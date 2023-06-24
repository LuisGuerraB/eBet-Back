from flask import session, request
from flask_login import current_user, login_required, logout_user
from flask_smorest import Blueprint, abort
from werkzeug.security import check_password_hash
from email_validator import validate_email, EmailNotValidError

from database import db
from src.enums import allowed_file
from src.models import UserSchema, User, UserLoginSchema
from src.models.prize import FileSchema
from src.models.user import UserLoginResponseSchema, PrivilegesSchema, ChangeSchema, SimpleUserSchema

api_url = '/user'
api_name = 'User'
api_description = 'Methods over User'

user_blp = Blueprint(
    name=api_name,
    description=api_description,
    import_name=__name__,
)


@user_blp.route(api_url + '/register', methods=['POST'])
@user_blp.doc(tags=[api_name])
@user_blp.arguments(UserSchema)
@user_blp.response(201)
def register_user(params):
    if User.query.filter_by(username=params['username']).first():
        abort(409, message='control-error.username-taken')

    try:
        validate_email(params['email'])
    except EmailNotValidError:
        abort(409, message="control-error.email-format")

    for user in User.query.all():
        if check_password_hash(user.email, params['email']):
            abort(409, message='control-error.email-registered')

    try:
        User.register_user(params['username'], params['password'], params['email'])
        return 201
    except:
        abort(409, message='control-error.unexpected')


@user_blp.route(api_url + '/login', methods=['POST'])
@user_blp.doc(tags=[api_name])
@user_blp.arguments(UserLoginSchema)
@user_blp.response(200, UserLoginResponseSchema)
def login(params):
    user = User.query.filter_by(username=params['username']).first()
    if user:
        try:
            prize = user.login(params['password'])
            return {'prize': prize, 'username': user.username, 'balance': user.balance, 'img': user.img,
                    'last_login': user.last_login}
        except Exception as e:
            abort(401, message=str(e))
    else:
        abort(404, message='control-error.user-not-found')


@user_blp.route(api_url + '/logout', methods=['POST'])
@user_blp.doc(tags=[api_name])
@login_required
@user_blp.response(201)
def logout():
    # Cerrar sesión del usuario actual
    logout_user()
    return 201


@user_blp.route(api_url + '/redeem', methods=['POST'])
@user_blp.doc(tags=[api_name])
@login_required
@user_blp.response(201)
def redeem_prize():
    if current_user.redeem_prize():
        return 201
    else:
        abort(404, message='prize-unredeemable')


@user_blp.route(api_url + '/privileges', methods=['GET'])
@user_blp.doc(tags=[api_name])
@user_blp.response(200, PrivilegesSchema)
@login_required
def get_privileges():
    return {'privileges': current_user.parse_privileges()}


@user_blp.route(api_url, methods=['GET'])
@user_blp.doc(tags=[api_name])
@user_blp.response(200, UserSchema)
@login_required
def get_current_user():
    return current_user


@user_blp.route(api_url, methods=['PUT'])
@user_blp.doc(tags=[api_name])
@user_blp.arguments(SimpleUserSchema)
@user_blp.response(201)
@login_required
def update_user(new_user):
    try:
        current_user.update(new_user)
    except Exception as e:
        abort(404, message=str(e))


@user_blp.route(api_url + '/img', methods=['PUT'])
@user_blp.doc(tags=[api_name])
@user_blp.response(200, FileSchema)
@login_required
def update_user_img():
    if not request.files.get('file'):
        abort(404, message='control-error.no-img')
    if not allowed_file(request.files.get('file').filename):
        abort(404, message='control-error.img-format')
    file = request.files.get('file')
    try:
        saving_route = current_user.update_img(file)
        return {'img': saving_route}
    except:
        abort(404, message='control-error.unexpected')


@user_blp.route(api_url + '/check/<string:attribute>', methods=['POST'])
@user_blp.doc(tags=[api_name])
@user_blp.arguments(ChangeSchema, location='json')
@user_blp.response(200)
@login_required
def check_attribute(value, attribute):
    if current_user.check_attribute(attribute, value.get('field')):
        session['updating_' + attribute] = True
        return 200
    else:
        abort(404, message='control-error.no-match')


@user_blp.route(api_url + '/change/<string:attribute>', methods=['POST'])
@user_blp.doc(tags=[api_name])
@user_blp.arguments(ChangeSchema, location='json')
@user_blp.response(200)
@login_required
def change_atribute(value, attribute):
    if session.get('updating_' + attribute):
        session['updating_' + attribute] = False
        current_user.update_attribute(attribute, value.get('field'))
        return 200
    else:
        abort(404, message='control-error.check-first')
