from app import db
from . import Match


class Team(db.Model):
    __tablename__ = 'team'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    acronym = db.Column(db.String, nullable=False)
    img = db.Column(db.String)
    website= db.Column(db.String)
    nationality = db.Column(db.String)

    seasons: db.Mapped[list['Participation']] = db.relationship(back_populates='team')
    results: db.Mapped[list['Result']] = db.relationship(back_populates='team')
    matches: db.Mapped[list['Match']] = db.relationship('Match',
                                                        primaryjoin='id == Match.local_team_id',
                                                        secondaryjoin='id == Match.away_team_id')
