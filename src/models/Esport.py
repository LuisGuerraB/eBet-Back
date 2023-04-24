from app import db

class Esport(db.Model):
    __tablename__='esport'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    img = db.Column(db.String)

    leagues : db.Mapped[list['League']] = db.relationship('League', back_populates='esport')