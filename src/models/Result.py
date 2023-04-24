from app import db


class Result(db.Model):
    __tablename__ = 'result'

    id = db.Column(db.Integer, primary_key=True)
    gold_percent = db.Column(db.Float(precision=2))
    exp_percent = db.Column(db.Float(precision=2))
    elders = db.Column(db.Integer)
    towers = db.Column(db.Integer)
    drakes = db.Column(db.Integer)
    inhibitors = db.Column(db.Integer)
    barons = db.Column(db.Integer)
    heralds = db.Column(db.Integer)
    kills = db.Column(db.Integer)
    deaths = db.Column(db.Integer)
    assists = db.Column(db.Integer)

    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'))

    team: db.Mapped['Team'] = db.relationship('Team', back_populates='results')
    match: db.Mapped['Match'] = db.relationship('Match', back_populates='results')
