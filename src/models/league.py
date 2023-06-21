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
    tournaments: db.Mapped[list['Tournament']] = db.relationship('Tournament', back_populates='league')


class LeagueSchema(Schema):
    id = fields.Integer(dump_only=True, metadata={'description': '#### Id of the League'})
    name = fields.String(required=True, metadata={'description': '#### Name of the League'})
    acronym = fields.String(required=True, metadata={'description': '#### Acronym of the League'})
    img = fields.String(required=True, metadata={'description': '#### Image of the League'})
    esport_id = fields.Integer(required=True,
                               metadata={'description': '#### Id of the Esport associated to the League'})


class LeagueListSchema(Schema):
    items = fields.List(fields.Nested(LeagueSchema), dump_only=True, required=True,
                        metadata={'description': '#### List of Leagues'})
    total = fields.Integer(dump_only=True, required=True, metadata={'description': '#### Total number of leagues'})
