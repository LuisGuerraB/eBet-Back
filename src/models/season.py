from marshmallow import Schema, fields

from database import db
from .league import LeagueSchema

class NoRegularSeasonException(Exception):
    message = "no-regular-season"
class Season(db.Model):
    __tablename__ = 'season'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    serie_id = db.Column(db.Integer(), nullable=False)
    ini_date = db.Column(db.Date(), nullable=False)
    end_date = db.Column(db.Date())
    league_id = db.Column(db.Integer, db.ForeignKey('league.id'), nullable=False)

    teams: db.Mapped[list['Participation']] = db.relationship(back_populates='season')
    league: db.Mapped['League'] = db.relationship('League', back_populates='seasons')
    matches: db.Mapped[list['Match']] = db.relationship('Match', back_populates='season')

    @classmethod
    def get_regular_season(cls, league_id: int):
        regular_season = Season.query.filter(Season.league_id == league_id, Season.name.ilike('%regular%')).order_by(
            Season.ini_date.desc()).first()
        if regular_season is None:
            raise NoRegularSeasonException()
        return regular_season


class SeasonSchema(Schema):
    id = fields.Integer(dump_only=True, metadata={'description': '#### Id of the Season'})
    name = fields.String(required=True, metadata={'description': '#### Name of the Season'})
    serie_id = fields.Integer(required=True, metadata={'description': '#### SerieId of the Season'})
    ini_date = fields.Date(required=True, metadata={'description': '#### Ini date of the Season'})
    end_date = fields.Date(metadata={'description': '#### End date of the Season'})
    league = fields.Nested(LeagueSchema, required=True, metadata={'description': '#### League of the Season'})
