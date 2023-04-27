from app import db
from src.models import Season,Team


class Participation(db.Model):
    __tablename__ = 'participation'

    id = db.Column(db.Integer, primary_key=True)
    position = db.Column(db.Integer)
    season_id = db.Column(db.Integer, db.ForeignKey('season.id'))
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))


    season: db.Mapped['Season'] = db.relationship('Season', back_populates='teams')
    team: db.Mapped['Team'] = db.relationship('Team', back_populates='seasons')