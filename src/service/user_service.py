from flask_smorest import Blueprint, abort
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError

from database import db
from src.models import UserSchema, User

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
def register_user(params):
    if User.query.filter_by(username=params['username']).first():
        abort(409, message='Username already exists')

    try:
        validate_email(params['email'])
    except EmailNotValidError:
        abort(409, message="Email format isn't correct")

    for user in User.query.all():
        if check_password_hash(user.email, params['email']):
            abort(409, message='Email already registered')

    hashed_password = generate_password_hash(params['password'])
    hashed_email = generate_password_hash(params['email'])
    user = User(username=params['username'], password=hashed_password, email=hashed_email)
    with db.session() as session:
        session.add(user)
        session.commit()
    return {'message': 'User register successfully'}, 201
