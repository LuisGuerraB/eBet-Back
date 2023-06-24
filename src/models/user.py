import os
from datetime import datetime

from marshmallow import Schema, fields, validate
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from config import Config
from database import db
from flask_login import UserMixin, login_user

from src.enums import Privilege


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    email = db.Column(db.String(), nullable=False)
    password = db.Column(db.String(), nullable=False)
    balance = db.Column(db.Integer, default=100, nullable=False)
    img = db.Column(db.String(), default='assets/users_profile/user.svg', nullable=False)
    last_login = db.Column(db.DateTime, server_default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), nullable=False)
    privileges = db.Column(db.String(3), server_default='', nullable=False)

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
            raise Exception("control-error.invalid-credentials")

    def redeem_prize(self):
        if (datetime.now() - self.last_login).total_seconds() > 86400:
            self.last_login = datetime.now()
            self.balance += 100
            db.session().commit()
            return True
        return False

    def has_privilege(self, privilege):
        return True if privilege.value[0] in self.privileges else False

    def parse_privileges(self):
        privileges = []
        for p in self.privileges:
            if p == 'a':
                privileges.append(Privilege.ADMIN.value)
                privileges.append(Privilege.MARKETING.value)
            if p == 'm':
                privileges.append(Privilege.MARKETING.value)
        return privileges

    def update_img(self, img_file):
        saving_route = os.path.join(Config.UPLOAD_FOLDER, 'users_profile',
                                    str(self.id) + '_' + secure_filename(img_file.filename))
        img_file.save(saving_route)
        old_img = self.img
        self.img = saving_route
        db.session().commit()
        os.remove(old_img)
        return saving_route

    def update(self, user):
        user_same_username = User.query.filter_by(username=user['username']).first()
        if user_same_username is not None:
            raise Exception('control-error.username-taken')
        with db.session() as session:
            self.username = user['username']
            session.commit()

    def check_attribute(self, attribute, value):
        if check_password_hash(getattr(self, attribute), value):
            return True
        else:
            return False

    def update_attribute(self, attribute, value):
        with db.session() as session:
            setattr(self, attribute, generate_password_hash(value))
            session.commit()

    def __str__(self):
        return f'{self.username} {self.balance} {self.privileges}'


class UserSchema(Schema):
    id = fields.Integer(dump_only=True, metadata={'description': '#### Id of the User'})
    username = fields.String(required=True, metadata={'description': '#### Username of the User'})
    email = fields.String(load_only=True, required=True, metadata={'description': '#### Email of the User'})
    password = fields.String(load_only=True, required=True, validate=validate.Length(min=6),
                             metadata={'description': '#### Password of the User'})
    balance = fields.Integer(dump_only=True, metadata={'description': '#### Balance of the User'})
    img = fields.String(metadata={'description': '#### Image of the User'})


class SimpleUserSchema(Schema):
    username = fields.String(required=True, metadata={'description': '#### Username of the User'})
    balance = fields.Integer(required=True, metadata={'description': '#### Balance of the User'})
    img = fields.String(required=True, metadata={'description': '#### Image of the User'})


class UserLoginSchema(Schema):
    username = fields.String(required=True, metadata={'description': '#### Username of the User'})
    password = fields.String(required=True, metadata={'description': '#### Password of the User'})


class UserLoginResponseSchema(Schema):
    username = fields.String(dump_only=True, required=True, metadata={'description': '#### Username of the User'})
    balance = fields.Integer(dump_only=True, required=True, metadata={'description': '#### Balance of the User'})
    img = fields.String(dump_only=True, required=True, metadata={'description': '#### Image of the User'})
    prize = fields.Boolean(dump_only=True, required=True, metadata={'description': '#### If the User have price'})
    last_login = fields.DateTime(dump_only=True, required=True, metadata={'description': '#### Last login of the User'})


class PrivilegesSchema(Schema):
    privileges = fields.List(fields.String(), required=True, metadata={'description': '#### Privilege of the User'})


class ChangeSchema(Schema):
    field = fields.String(required=True, metadata={'description': '#### Value of the field'})
