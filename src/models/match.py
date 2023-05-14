from marshmallow import Schema, fields

from database import db
from .team import TeamSchema
from .season import SeasonSchema


class Match(db.Model):
    __tablename__ = 'match'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    plan_date = db.Column(db.DateTime, nullable=False)
    ini_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    away_team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    local_team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    season_id = db.Column(db.Integer, db.ForeignKey('season.id'), nullable=False)

    away_team: db.Mapped['Team'] = db.relationship('Team', back_populates='matches', foreign_keys=[away_team_id])
    local_team: db.Mapped['Team'] = db.relationship('Team', back_populates='matches', foreign_keys=[local_team_id])
    season: db.Mapped['Season'] = db.relationship('Season', back_populates='matches')
    results: db.Mapped[list['Result']] = db.relationship('Result', back_populates='match')
    bets: db.Mapped[list['Bet']] = db.relationship('Bet', back_populates='match')

class MatchSchema(Schema):
    id = fields.Integer(dump_only=True, metadata={'description': '#### Id of the Match'})
    name = fields.String(required=True, metadata={'description': '#### Name of the Match'})
    sets = fields.Integer(required=True, metadata={'description': '#### Number of sets of the Match'})
    plan_date = fields.DateTime(required=True, metadata={'description': '#### Planned date of the Match'})
    ini_date = fields.DateTime(metadata={'description': '#### Iniciation date of the Match'})
    end_date = fields.DateTime(metadata={'description': '#### End date of the Match'})
    away_team = fields.Nested(TeamSchema, required=True, metadata={'description': '#### Away team of the Match'})
    local_team = fields.Nested(TeamSchema, required=True, metadata={'description': '#### Local team of the Match'})
    season = fields.Nested(SeasonSchema, required=True, metadata={'description': '#### Season of the Match'})
