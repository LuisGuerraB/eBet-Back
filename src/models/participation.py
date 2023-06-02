from marshmallow import Schema, fields

from database import db
from .season import Season, SeasonSchema
from .team import TeamSchema



class Participation(db.Model):
    __tablename__ = 'participation'

    id = db.Column(db.Integer, primary_key=True)
    position = db.Column(db.Integer, nullable=False)
    points = db.Column(db.Integer, nullable=False, default=0)
    season_id = db.Column(db.Integer, db.ForeignKey('season.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)

    season: db.Mapped['Season'] = db.relationship('Season', back_populates='teams')
    team: db.Mapped['Team'] = db.relationship('Team', back_populates='seasons')

    @classmethod
    def get_standings(cls, league_id: int):
        regular_season = Season.get_regular_season(league_id)
        return Participation.query.filter(cls.season_id == regular_season.id).all()


class ParticipationSchema(Schema):
    id = fields.Integer(dump_only=True, metadata={'description': '#### Id of the Participation'})
    position = fields.Integer(required=True, metadata={'description': '#### Actual Position of the team'})
    points = fields.Integer(required=True, metadata={'description': '#### Points of the team'})
    season = fields.Nested(SeasonSchema,required=True, metadata={'description': '#### SeasonId of the Participation'})
    team = fields.Nested(TeamSchema, required=True, metadata={'description': '#### TeamId of the Participation'})


class ParticipationListSchema(Schema):
    items = fields.List(fields.Nested(ParticipationSchema), metadata={'description': '#### List of the Participation'})
    total = fields.Integer(metadata={'description': '#### Total of the Participation'})
