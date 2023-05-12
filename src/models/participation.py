from marshmallow import Schema, fields

from database import db


class Participation(db.Model):
    __tablename__ = 'participation'

    id = db.Column(db.Integer, primary_key=True)
    position = db.Column(db.Integer, nullable=False)
    season_id = db.Column(db.Integer, db.ForeignKey('season.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)

    season: db.Mapped['Season'] = db.relationship('Season', back_populates='teams')
    team: db.Mapped['Team'] = db.relationship('Team', back_populates='seasons')


class ParticipationSchema(Schema):
    id = fields.Integer(dump_only=True, metadata={'description': '#### Id of the Participation'})
    position = fields.Integer(required=True, metadata={'description': '#### Actual Position of the team'})
    season_id = fields.Integer(required=True, metadata={'description': '#### SeasonId of the Participation'})
    team_id = fields.Integer(required=True, metadata={'description': '#### TeamId of the Participation'})
