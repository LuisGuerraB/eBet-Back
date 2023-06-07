from datetime import datetime

from marshmallow import Schema, fields, validate
from werkzeug.security import generate_password_hash, check_password_hash

from database import db
from flask_login import UserMixin, login_user


class InvalidCredentialException(Exception):
    message = "control-error.invalid-credentials"


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    email = db.Column(db.String(), nullable=False)
    password = db.Column(db.String(), nullable=False)
    balance = db.Column(db.Integer, default=100, nullable=False)
    img = db.Column(db.String(), default='assets/img/user.svg', nullable=False)
    last_login = db.Column(db.DateTime, server_default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), nullable=False)

    bets: db.Mapped[list['Bet']] = db.relationship('Bet', back_populates='user')

    @classmethod
    def register_user(cls, username, password, email):
        hashed_password = generate_password_hash(password)
        hashed_email = generate_password_hash(email)
        user = User(username=username, password=hashed_password, email=hashed_email)
        with db.session() as session:
            session.add(user)
            session.commit()

    def login(self, password):
        if check_password_hash(self.password, password):
            login_user(self)
            return self.redeem_prize()
        else:
            raise InvalidCredentialException()

    def redeem_prize(self):
        if (datetime.now() - self.last_login).total_seconds() > 86400:
            self.last_login = datetime.now()
            self.balance += 100
            db.session().commit()
            return True
        return False


class UserSchema(Schema):
    id = fields.Integer(dump_only=True, metadata={'description': '#### Id of the User'})
    username = fields.String(required=True, metadata={'description': '#### Username of the User'})
    email = fields.String(load_only=True, required=True, metadata={'description': '#### Email of the User'})
    password = fields.String(load_only=True, required=True, validate=validate.Length(min=6),
                             metadata={'description': '#### Password of the User'})
    balance = fields.Integer(dump_only=True, metadata={'description': '#### Balance of the User'})
    img = fields.String(metadata={'description': '#### Image of the User'})


class UserLoginSchema(Schema):
    username = fields.String(required=True, metadata={'description': '#### Username of the User'})
    password = fields.String(required=True, metadata={'description': '#### Password of the User'})


class UserLoginResponseSchema(Schema):
    username = fields.String(dump_only=True, required=True, metadata={'description': '#### Username of the User'})
    balance = fields.Integer(dump_only=True, required=True, metadata={'description': '#### Balance of the User'})
    img = fields.String(dump_only=True, required=True, metadata={'description': '#### Image of the User'})
    prize = fields.Boolean(dump_only=True, required=True, metadata={'description': '#### If the User have price'})
    last_login = fields.DateTime(dump_only=True, required=True, metadata={'description': '#### Last login of the User'})
