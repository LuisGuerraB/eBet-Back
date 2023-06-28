from datetime import datetime

from marshmallow import Schema, fields

from database import db
from .probability import Probability
from .play import Play
from .match import PlayMatchSchema
from .betting_odd import BettingOdd


class Bet(db.Model):
    __tablename__ = 'bet'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    type = db.Column(db.String(15), nullable=False)
    subtype = db.Column(db.Integer)
    multiplier = db.Column(db.Float(2), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    result = db.Column(db.String(), nullable=False, server_default='waiting')
    set = db.Column(db.Integer, nullable=True)
    play_id = db.Column(db.Integer, db.ForeignKey('play.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    play: db.Mapped['Play'] = db.relationship('Play', back_populates='bets')
    user: db.Mapped['User'] = db.relationship('User', back_populates='bets')

    @classmethod
    def exist(cls, match_id, user_id, type, subtype=None) -> bool:
        return cls.query.filter(cls.match_id == match_id, cls.user_id == user_id, cls.type == type,
                                cls.subtype == subtype).first()

    @classmethod
    def create(self, user, **params):
        if user.balance < params['amount']:
            raise Exception("insuficient-funds")
        if Bet.exist(params['match_id'], user.id, params['type'], params.get('subtype', None)):
            raise Exception("existing-bet")
        with db.session() as session:
            play = session.query(Play).filter_by(match_id=params['match_id'], team_id=params['team_id']).first()
            betting_odd = BettingOdd.query.filter_by(play_id=play.id).first()
            if betting_odd is None:
                raise Exception("betting-odds-not-found")

            actual_odd = next((odd for odd in betting_odd.odds if odd.type.lower() == params['type'].lower()), None)
            if actual_odd is None:
                raise Exception("multiplier-no-match")
            elif params['multiplier'] != actual_odd.value[str(params['subtype'])]:
                prob_finish_early = Probability.finish_early_match(session, play.match)
                if params['multiplier'] != actual_odd.value[str(params['subtype'])] * (1 / (prob_finish_early * 1.1)):
                    raise Exception("multiplier-no-match")
            user.balance -= params['amount']
            bet = Bet(
                date=datetime.now(),
                type=params['type'],
                subtype=params.get('subtype', None),
                multiplier=actual_odd.value[str(params['subtype'])],
                amount=params['amount'],
                set=params.get('set', None),
                play_id=play.id,
                user_id=user.id
            )
            session.add(bet)
            session.commit()
            return bet.id

    @classmethod
    def get_user_bets(self, user):
        return sorted(user.bets, key=lambda bet: bet.date, reverse=True)

    def delete(self, session):
        user = self.user
        user.balance += self.amount
        session.delete(self)
        session.commit()

    def update_amount(self, session, new_amount):
        user = self.user
        amount_difference = new_amount - self.amount
        if user.balance < amount_difference:
            raise Exception("insufficient-funds")
        user.balance -= amount_difference
        self.amount = new_amount
        session.commit()


class BetSchema(Schema):
    id = fields.Integer(dump_only=True, metadata={'description': '#### Id of the Bet'})
    date = fields.DateTime(dump_only=True, metadata={'description': '#### Date of the Bet'})
    type = fields.String(required=True, metadata={'description': '#### Type of the Bet'})
    subtype = fields.Integer(required=True, metadata={'description': '#### Subtype of the Bet'})
    multiplier = fields.Float(format='0.00', required=True, metadata={'description': '#### Multiplier of the Bet'})
    amount = fields.Integer(required=True, metadata={'description': '#### Amount of the Bet'})
    result = fields.String(metadata={'description': '#### Result of the Bet'})
    set = fields.Integer(metadata={'description': '#### Set of the Bet'})
    play = fields.Nested(PlayMatchSchema, dump_only=True, required=True,
                         metadata={'description': '#### MatchId of the Bet'})
    match_id = fields.Integer(required=True, load_only=True, metadata={'description': '#### MatchId of the Bet'})
    team_id = fields.Integer(required=True, metadata={'description': '#### TeamId of the Bet'})


class BetListSchema(Schema):
    items = fields.Nested(BetSchema, many=True, dump_only=True, metadata={'description': '#### List of Bets'})
    total = fields.Integer(dump_only=True, metadata={'description': '#### Total of Bets'})
