from app import db
from src.models import Team,Season,Result


class Match(db.Model):
    __tablename__ = 'match'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    plan_date = db.Column(db.DateTime, nullable=False)
    ini_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    away_team_id = db.Column(db.Integer, db.ForeignKey('team.id'),nullable=False)
    local_team_id = db.Column(db.Integer, db.ForeignKey('team.id'),nullable=False)
    season_id = db.Column(db.Integer, db.ForeignKey('season.id'), nullable=False)

    away_team: db.Mapped['Team'] = db.relationship('Team', back_populates='matches', foreign_keys=[away_team_id])
    local_team: db.Mapped['Team'] = db.relationship('Team', back_populates='matches', foreign_keys=[local_team_id])
    season: db.Mapped['Season'] = db.relationship('Season', back_populates='matches')
    results: db.Mapped[list['Result']] = db.relationship('Result', back_populates='match')