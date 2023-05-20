from marshmallow import Schema, fields

from database import db
from src.enums import BetType


class Bet(db.Model):
    __tablename__ = 'bet'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    type = db.Column(db.Enum(BetType), nullable=False)
    subtype = db.Column(db.Integer)
    multiplier = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    match: db.Mapped['Match'] = db.relationship('Match', back_populates='bets')
    user: db.Mapped['User'] = db.relationship('User', back_populates='bets')

    @classmethod
    def exist(cls, match_id, user_id, type, subtype=None) -> bool:
        return cls.query.filter(cls.match_id == match_id, cls.user_id == user_id, cls.type == type,
                                cls.subtype == subtype).first()


class BetSchema(Schema):
    id = fields.Integer(dump_only=True, metadata={'description': '#### Id of the Bet'})
    date = fields.DateTime(required=True, metadata={'description': '#### Date of the Bet'})
    type = fields.Enum(BetType, required=True, metadata={'description': '#### Type of the Bet'})
    subtype = fields.Integer(metadata={'description': '#### Subtype of the Bet'})
    multiplier = fields.Integer(required=True, metadata={'description': '#### Multiplier of the Bet'})
    amount = fields.Integer(required=True, metadata={'description': '#### Amount of the Bet'})
    match_id = fields.Integer(required=True, metadata={'description': '#### MatchId of the Bet'})