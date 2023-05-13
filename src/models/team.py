from marshmallow import Schema, fields

from database import db


class Team(db.Model):
    __tablename__ = 'team'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    acronym = db.Column(db.String, nullable=False)
    img = db.Column(db.String)
    website = db.Column(db.String)
    nationality = db.Column(db.String)
    league_id = db.Column(db.Integer, db.ForeignKey('league.id'))

    seasons: db.Mapped[list['Participation']] = db.relationship(back_populates='team')
    results: db.Mapped[list['Result']] = db.relationship(back_populates='team')
    probabilities: db.Mapped[list['Probability']] = db.relationship(back_populates='team')
    matches: db.Mapped[list['Match']] = db.relationship('Match', secondary='match',
                                                        primaryjoin='or_(Team.id == Match.local_team_id, Team.id == Match.away_team_id)',
                                                        secondaryjoin='or_(Team.id == Match.local_team_id, Team.id == Match.away_team_id)')

    def __repr__(self) -> str:
        return f'<Team #{self.id} ({self.acronym})>'


class TeamSchema(Schema):
    id = fields.Integer(dump_only=True, metadata={'description': '#### Id of the Team'})
    name = fields.String(required=True, metadata={'description': '#### Name of the Team'})
    acronym = fields.String(required=True, metadata={'description': '#### Acronym of the Team'})
    img = fields.String(metadata={'description': '#### Image of the Team'})
    website = fields.String(metadata={'description': '#### Website of the Team'})
    nationality = fields.String(metadata={'description': '#### Nationality of the Team'})
