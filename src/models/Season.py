from database import db
from src.models import Participation, League, Match


class Season(db.Model):
    __tablename__ = 'season'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    serie_id = db.Column(db.Integer(), nullable=False)
    ini_date = db.Column(db.Date(), nullable=False)
    end_date = db.Column(db.Date())
    league_id = db.Column(db.Integer, db.ForeignKey('league.id'))

    teams: db.Mapped[list['Participation']] = db.relationship(back_populates='season')
    league: db.Mapped['League'] = db.relationship('League', back_populates='seasons')
    matches: db.Mapped[list['Match']] = db.relationship('Match', back_populates='season')
