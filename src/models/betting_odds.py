from marshmallow import Schema, fields

from database import db


class BettingOdds(db.Model):
    __tablename__ = 'betting_odds'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    win_odds = db.Column(db.Float(2))
    gold_odds = db.Column(db.Float(2))
    exp_odds = db.Column(db.Float(2))
    towers_odds = db.Column(db.ARRAY(db.Float(2), dimensions=1))
    drakes_odds = db.Column(db.ARRAY(db.Float(2), dimensions=1))
    inhibitors_odds = db.Column(db.ARRAY(db.Float(2), dimensions=1))
    elders_odds = db.Column(db.ARRAY(db.Float(2), dimensions=1))
    barons_odds = db.Column(db.ARRAY(db.Float(2), dimensions=1))
    heralds_odds = db.Column(db.ARRAY(db.Float(2), dimensions=1))
    kills_odds = db.Column(db.ARRAY(db.Float(2), dimensions=1))
    deaths_odds = db.Column(db.ARRAY(db.Float(2), dimensions=1))
    assists_odds = db.Column(db.ARRAY(db.Float(2), dimensions=1))

    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'))

    team: db.Mapped['Team'] = db.relationship('Team', back_populates='probabilities')
    match: db.Mapped['Match'] = db.relationship('Match', back_populates='probabilities')



