from marshmallow import Schema, fields

from database import db

class Esport(db.Model):
    __tablename__ = 'esport'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    img = db.Column(db.String)

    leagues: db.Mapped[list['League']] = db.relationship('League', back_populates='esport')

class EsportSchema(Schema):
    id = fields.Integer(dump_only=True,metadata={'description':'#### Id of the Esport'})
    name = fields.String(metadata={'description':'#### Name of the Esport'})
    img = fields.String(metadata={'description':'#### Image of the Esport'})