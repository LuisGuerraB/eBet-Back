from datetime import datetime, timedelta

from flask import make_response
from flask_login import current_user, login_user
from flask_smorest import Blueprint, abort
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError

from database import db
from src.models import UserSchema, User, UserLoginSchema

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
@user_blp.response(200, UserSchema)
def login(params):
    user = User.query.filter_by(username=params['username']).first()
    if user and check_password_hash(user.password, params['password']):
        login_user(user)
        return user
    abort(401, message='control-error.invalid-credentials')
