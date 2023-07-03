from marshmallow import Schema, fields

from database import db
from .team import TeamSchema
from .tournament import Tournament



class Participation(db.Model):
    __tablename__ = 'participation'

    id = db.Column(db.Integer, primary_key=True)
    position = db.Column(db.Integer, nullable=False)
    points = db.Column(db.Integer, nullable=False, default=0)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)

    tournament: db.Mapped['Tournament'] = db.relationship('Tournament', back_populates='teams')
    team: db.Mapped['Team'] = db.relationship('Team', back_populates='tournaments')

    @classmethod
    def get_standings(cls, league_id: int):
        regular_tournaments = Tournament.get_regular_tournaments(league_id)
        if regular_tournaments is None:
            raise Exception('control-error.no-regular-tournament')
        return Participation.query.filter(cls.tournament_id == regular_tournaments[0].id).order_by(cls.position).all()


class ParticipationSchema(Schema):
    id = fields.Integer(dump_only=True, metadata={'description': '#### Id of the Participation'})
    position = fields.Integer(required=True, metadata={'description': '#### Actual Position of the team'})
    points = fields.Integer(required=True, metadata={'description': '#### Points of the team'})
    team = fields.Nested(TeamSchema, required=True, metadata={'description': '#### TeamId of the Participation'})


class ParticipationListSchema(Schema):
    items = fields.List(fields.Nested(ParticipationSchema), metadata={'description': '#### List of the Participation'})
    total = fields.Integer(metadata={'description': '#### Total of the Participation'})
