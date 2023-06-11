from marshmallow import Schema, fields
from sqlalchemy import Index
from database import db


def obtain_percentage(json_frame, json_frame_opposite, type):
    if len(json_frame) == 0 or len(json_frame_opposite) == 0:
        return -1.00
    total = len(json_frame) - 1
    count = 0
    for i in range(total):
        if json_frame[i + 1][type] > json_frame_opposite[i + 1][type]:
            count += 1
    if type == 'xp':
        total -= 1
    return count / float(total)


avoid_types = ['frames','team','goldEarned']

class Result(db.Model):
    __tablename__ = 'result'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stats: db.Mapped[list['Stat']] = db.relationship('Stat', back_populates='result')

    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    set = db.Column(db.Integer, nullable=False)

    team: db.Mapped['Team'] = db.relationship('Team', back_populates='results')
    match: db.Mapped['Match'] = db.relationship('Match', back_populates='results')

    __table_args__ = (Index('idx_match_set_team', 'match_id', 'set', 'team_id', unique=True),)

    @classmethod
    def create_from_web_json(cls, session, json, match_id, set):
        winner_id = json['winner']['id']
        teams = json['teams']
        n_teams = len(teams)
        for i in range(n_teams):
            team = teams[i]
            result = Result(team_id=team['team']['id'], match_id=match_id, set=set)
            session.add(result)
            session.commit()
            if team['team']['id'] == winner_id:
                session.add(Stat(type='winner', value=1, result_id=result.id))
            else:
                session.add(Stat(type='winner', value=0, result_id=result.id))
            for stat in team:
                if stat not in avoid_types:
                    session.add(Stat(type=stat, value=team[stat], result_id=result.id))
            session.commit()


class Stat(db.Model):
    __tablename__ = 'stat'

    type = db.Column(db.String(15), nullable=False, primary_key=True)
    value = db.Column(db.Integer, nullable=False)
    result_id = db.Column(db.Integer, db.ForeignKey('result.id'), nullable=False, primary_key=True)
    result: db.Mapped['Result'] = db.relationship('Result', back_populates='stats')

    def __repr__(self):
        return f'<Stat : {self.type} - {self.value}>'

    def __str__(self):
        return f'{self.type} - {self.value}'

class StatSchema(Schema):
    type = fields.String(metadata={'description': '#### Type of the Stat'})
    value = fields.Integer(metadata={'description': '#### Value of the Stat'})


class ResultSchema(Schema):
    id = fields.Integer(dump_only=True, metadata={'description': '#### Id of the Result'})
    set = fields.Integer(metadata={'description': '#### Set of the Result'})
    stats = fields.Nested(StatSchema, many=True, metadata={'description': '#### Stats of the Result'})
