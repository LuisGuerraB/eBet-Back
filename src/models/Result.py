from app import db
from src.models import Team,Match


class Result(db.Model):
    __tablename__ = 'result'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    winner = db.Column(db.Boolean,nullable=False)
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

    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    set = db.Column(db.Integer, nullable=False)

    team: db.Mapped['Team'] = db.relationship('Team', back_populates='results')
    match: db.Mapped['Match'] = db.relationship('Match', back_populates='results')

    @classmethod
    def create_from_web_json(cls,json):
        pass

    def __obatin_percentage(self):
        pass