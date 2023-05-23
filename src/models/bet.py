from marshmallow import Schema, fields

from database import db
from src.enums import BetType
from .match import Match
from .betting_odds import BettingOdds


class InsuficientFundsException(Exception):
    message = "insuficient-funds"


class ExistingBetException(Exception):
    message = "existing-bet"


class MultiplierNoMatchException(Exception):
    message = "multiplier-no-match"


class BettingOddsNotFoundException(Exception):
    message = "betting-odds-not-found"


class Bet(db.Model):
    __tablename__ = 'bet'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    type = db.Column(db.Enum(BetType), nullable=False)
    subtype = db.Column(db.Integer)
    multiplier = db.Column(db.Float(2), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)

    match: db.Mapped['Match'] = db.relationship('Match', back_populates='bets')
    user: db.Mapped['User'] = db.relationship('User', back_populates='bets')

    @classmethod
    def exist(cls, match_id, user_id, type, subtype=None) -> bool:
        return cls.query.filter(cls.match_id == match_id, cls.user_id == user_id, cls.type == type,
                                cls.subtype == subtype).first()

    @classmethod
    def create(self, user, **params):
        if user.balance < params['amount']:
            raise InsuficientFundsException()
        if Bet.exist(params['match_id'], user.id, params['type'], params.get('subtype', None)):
            raise ExistingBetException()
        with db.session() as session:
            betting_odd = BettingOdds.query.filter_by(match_id=params['match_id'], team_id=params['team_id']).first()
            if betting_odd is None:
                raise BettingOddsNotFoundException()
            attr = getattr(betting_odd, params['type'].value + '_odds')
            if params.get('subtype', None):
                attr = attr.get(str(params['subtype']))
            if params['multiplier'] != attr:
                raise MultiplierNoMatchException()
            user.balance -= params['amount']
            bet = Bet(
                date=params['date'],
                type=params['type'],
                subtype=params.get('subtype', None),
                multiplier=attr,
                amount=params['amount'],
                match_id=params['match_id'],
                team_id=params['team_id'],
                user_id=user.id
            )
            session.add(bet)
            session.commit()
            return Bet.query.get(bet.id)


class BetSchema(Schema):
    id = fields.Integer(dump_only=True, metadata={'description': '#### Id of the Bet'})
    date = fields.DateTime(required=True, metadata={'description': '#### Date of the Bet'})
    type = fields.Enum(BetType, required=True, metadata={'description': '#### Type of the Bet'})
    subtype = fields.Integer(metadata={'description': '#### Subtype of the Bet'})
    multiplier = fields.Float(format='0.00', required=True, metadata={'description': '#### Multiplier of the Bet'})
    amount = fields.Integer(required=True, metadata={'description': '#### Amount of the Bet'})
    match_id = fields.Integer(required=True, metadata={'description': '#### MatchId of the Bet'})
    team_id = fields.Integer(required=True, metadata={'description': '#### TeamId of the Bet'})
