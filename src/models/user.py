from database import db


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    bets: db.Mapped[list['Bet']] = db.relationship('Bet', back_populates='user')
