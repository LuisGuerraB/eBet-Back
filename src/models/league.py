from marshmallow import Schema, fields

from database import db


class League(db.Model):
    __tablename__ = 'league'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    acronym = db.Column(db.String(), unique=True, nullable=False)
    img = db.Column(db.String(), unique=True, nullable=False)
    esport_id = db.Column(db.Integer(), db.ForeignKey('esport.id'), nullable=False)

    esport: db.Mapped['Esport'] = db.relationship('Esport', back_populates='leagues')
    seasons: db.Mapped[list['Season']] = db.relationship('Season', back_populates='league')


class LeagueSchema(Schema):
    id = fields.Integer(dump_only=True, metadata={'description': '#### Id of the League'})
    name = fields.String(metadata={'description': '#### Name of the League'})
    acronym = fields.String(metadata={'description': '#### Acronym of the League'})
    img = fields.String(metadata={'description': '#### Image of the League'})
    esport_id = fields.Integer(metadata={'description': '#### Id of the Esport associated to the League'})
