import os
from copy import copy

from PIL import Image
from flask_smorest.fields import Upload

from marshmallow import Schema, fields, validate
from werkzeug.utils import secure_filename

from config import Config
from database import db


class Prize(db.Model):
    __tablename__ = 'prize'

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String(), nullable=False)
    amount = db.Column(db.Integer(), nullable=False)
    img = db.Column(db.String(), nullable=False)
    price = db.Column(db.Integer(), nullable=True)

    @classmethod
    def create_prize(cls, name, amount, img, price):
        saving_route = os.path.join(Config.UPLOAD_FOLDER, secure_filename(img.filename))
        img.save(saving_route)

        prize = Prize(name=name, amount=amount, img=saving_route, price=price)
        with db.session() as session:
            session.add(prize)
            session.commit()
            return True


    @classmethod
    def verify_img(cls, img_file):
        try:
            img_verify = copy(img_file)
            img_verify = Image.open(img_verify)
            img_verify.verify()
            print('cool')
            return True
        except:
            return False


class PrizeSchema(Schema):
    id = fields.Integer(dump_only=True, metadata={'description': '#### Id of the Prize'})
    name = fields.String(required=True, metadata={'description': '#### Name of the Prize'})
    amount = fields.Integer(required=True, validate=validate.Range(min=1),
                            metadata={'description': '#### Amount of the Prize'})
    price = fields.Integer(required=True, validate=validate.Range(min=1),
                           metadata={'description': '#### Price of the Prize'})
    img = fields.String(required=True, dump_only=True, metadata={'description': '#### Image of the Prize'})


class FileSchema(Schema):
    img = Upload(required=False)
