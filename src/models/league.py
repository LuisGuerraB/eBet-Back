from database import db


class League(db.Model):
    __tablename__ = 'league'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    acronym = db.Column(db.String(), unique=True, nullable=False)
    img = db.Column(db.String(), unique=True, nullable=False)
    esport_id = db.Column(db.Integer(), db.ForeignKey('esport.id'))

    esport: db.Mapped['Esport'] = db.relationship('Esport', back_populates='leagues')
    seasons: db.Mapped[list['Season']] = db.relationship('Season', back_populates='league')
