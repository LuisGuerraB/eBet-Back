from marshmallow import Schema, fields

from database import db


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


class SeasonSchema(Schema):
    id = fields.Integer(dump_only=True, metadata={'description': '#### Id of the Season'})
    name = fields.String(metadata={'description': '#### Name of the Season'})
    serie_id = fields.Integer(metadata={'description': '#### SerieId of the Season'})
    ini_date = fields.Date(metadata={'description': '#### Ini date of the Season'})
    end_date = fields.Date(metadata={'description': '#### End date of the Season'})
    league_id = fields.Integer(metadata={'description': '#### LeagueId of the Season'})
