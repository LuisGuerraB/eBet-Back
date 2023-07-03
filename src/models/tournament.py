from marshmallow import Schema, fields

from database import db
from .league import LeagueSchema

class Tournament(db.Model):
    __tablename__ = 'tournament'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    serie_id = db.Column(db.Integer(), nullable=False)
    ini_date = db.Column(db.Date(), nullable=False)
    end_date = db.Column(db.Date())
    league_id = db.Column(db.Integer, db.ForeignKey('league.id'), nullable=False)

    teams: db.Mapped[list['Participation']] = db.relationship(back_populates='tournament')
    league: db.Mapped['League'] = db.relationship('League', back_populates='tournaments')
    matches: db.Mapped[list['Match']] = db.relationship('Match', back_populates='tournament')

    @classmethod
    def get_regular_tournaments(cls, league_id: int):
        regular_tournaments = Tournament.query.filter(Tournament.league_id == league_id, Tournament.name.ilike('%regular%')).order_by(
            Tournament.ini_date.desc()).all()
        if regular_tournaments is None:
            return None
        return regular_tournaments


class TournamentSchema(Schema):
    id = fields.Integer(dump_only=True, metadata={'description': '#### Id of the Tournament'})
    name = fields.String(required=True, metadata={'description': '#### Name of the Tournament'})
    serie_id = fields.Integer(required=True, metadata={'description': '#### SerieId of the Tournament'})
    ini_date = fields.Date(required=True, metadata={'description': '#### Ini date of the Tournament'})
    end_date = fields.Date(metadata={'description': '#### End date of the Tournament'})
    league = fields.Nested(LeagueSchema, required=True, metadata={'description': '#### League of the Tournament'})
