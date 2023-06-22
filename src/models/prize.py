import os
from flask_smorest.fields import Upload

from marshmallow import Schema, fields, validate
from werkzeug.utils import secure_filename

from config import Config
from database import db


class Prize(db.Model):
    __tablename__ = 'prize'

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    amount = db.Column(db.Integer(), nullable=False)
    img = db.Column(db.String(), nullable=False)
    price = db.Column(db.Integer(), nullable=True)

    @classmethod
    def create_prize(cls, amount, img, price):
        saving_route = os.path.join(Config.UPLOAD_FOLDER, 'images', secure_filename(img.filename))
        img.save(saving_route)

        prize = Prize(amount=amount, img=saving_route, price=price)
        with db.session() as session:
            session.add(prize)
            session.commit()
            return True

    def delete(self, session):
        try:
            os.remove(self.img)
            session.delete(self)
            session.commit()
            return True
        except:
            return False

    def buy(self, session):
        self.amount -= 1
        if self.amount == 0:
            self.delete(session)
        session.commit()


class PrizeSchema(Schema):
    id = fields.Integer(dump_only=True, metadata={'description': '#### Id of the Prize'})
    amount = fields.Integer(required=True, load_only=True, validate=validate.Range(min=1),
                            metadata={'description': '#### Amount of the Prize'})
    price = fields.Integer(required=True, validate=validate.Range(min=1),
                           metadata={'description': '#### Price of the Prize'})
    img = fields.String(required=True, dump_only=True, metadata={'description': '#### Image of the Prize'})


class EmailSchema(Schema):
    email = fields.Email(required=False)


class PrizeListSchema(Schema):
    items = fields.List(fields.Nested(PrizeSchema), dump_only=True, required=True,
                        metadata={'description': '#### List of Prize'})
    total = fields.Integer(dump_only=True, required=True, metadata={'description': '#### Total number of prizes'})
