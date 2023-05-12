from database import db
from src.enums import BetType


class Bet(db.Model):
    __tablename__ = 'bet'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    type = db.Column(db.Enum(BetType), nullable=False)
    subtype = db.Column(db.Integer)
    multiplier = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    match: db.Mapped['Match'] = db.relationship('Match', back_populates='bets')
    user: db.Mapped['User'] = db.relationship('User', back_populates='bets')
