from marshmallow import Schema, fields

from database import db

from .team import TeamSchema


class Play(db.Model):
    __tablename__ = 'play'
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    local = db.Column(db.Boolean, nullable=False)

    match: db.Mapped['Match'] = db.relationship('Match', back_populates='plays')
    team: db.Mapped['Team'] = db.relationship('Team', back_populates='plays')
    result: db.Mapped['Result'] = db.relationship('Result', back_populates='play')
    bets: db.Mapped['Bet'] = db.relationship('Bet', back_populates='play')
    betting_odd: db.Mapped['BettingOdd'] = db.relationship('BettingOdd', back_populates='play')
