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


class Result(db.Model):
    __tablename__ = 'result'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    winner = db.Column(db.Boolean, nullable=False)
    gold_percent = db.Column(db.Float(2))
    exp_percent = db.Column(db.Float(2))
    elders = db.Column(db.Integer)
    towers = db.Column(db.Integer)
    drakes = db.Column(db.Integer)
    inhibitors = db.Column(db.Integer)
    barons = db.Column(db.Integer)
    heralds = db.Column(db.Integer)
    kills = db.Column(db.Integer)
    deaths = db.Column(db.Integer)
    assists = db.Column(db.Integer)

    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    set = db.Column(db.Integer, nullable=False)

    team: db.Mapped['Team'] = db.relationship('Team', back_populates='results')
    match: db.Mapped['Match'] = db.relationship('Match', back_populates='results')

    __table_args__ = (Index('idx_match_set_team', 'match_id', 'set', 'team_id'),)

    @classmethod
    def create_from_web_json(cls, json, match_id, set):
        winner_id = json['winner']['id']
        teams = json['teams']
        n_teams = len(teams)
        result = []
        for i in range(n_teams):
            team = teams[i]
            result.append(Result(
                winner=team['team']['id'] == winner_id,
                gold_percent=obtain_percentage(team['frames'], teams[(i + 1) % n_teams]['frames'], 'gold'),
                exp_percent=obtain_percentage(team['frames'], teams[(i + 1) % n_teams]['frames'], 'xp'),
                elders=team['elderDrakeKills'],
                towers=team['towerKills'],
                drakes=team['dragonKills'],
                inhibitors=team['inhibitorKills'],
                barons=team['baronKills'],
                heralds=team['heraldKills'],
                kills=team['kills'],
                deaths=team['deaths'],
                assists=team['assists'],
                team_id=team['team']['id'],
                match_id=match_id,
                set=set
            ))
        return result


class ResultSchema(Schema):
    id = fields.Integer(metadata={'description': '#### Id of the Result'})
    winner = fields.Boolean(metadata={'description': '#### Winner of the Result'})
    gold_percent = fields.Integer(metadata={'description': '#### Percentage winning at gold of the Result'})
    exp_percent = fields.Integer(metadata={'description': '#### Percentage winning at exp of the Result'})
    elders = fields.Integer(metadata={'description': '#### Number of elders of the Result'})
    towers = fields.Integer(metadata={'description': '#### Number of towers of the Result'})
    drakes = fields.Integer(metadata={'description': '#### Number of drakes of the Result'})
    inhibitors = fields.Integer(metadata={'description': '#### Number of inhibitors of the Result'})
    barons = fields.Integer(metadata={'description': '#### Number of barons of the Result'})
    heralds = fields.Integer(metadata={'description': '#### Number of heralds of the Result'})
    kills = fields.Integer(metadata={'description': '#### Number of kills of the Result'})
    deaths = fields.Integer(metadata={'description': '#### Number of deaths of the Result'})
    assists = fields.Integer(metadata={'description': '#### Number of assists of the Result'})
    team_id = fields.Integer(metadata={'description': '#### TeamId of the Result'})
    match_id = fields.Integer(metadata={'description': '#### MatchId of the Result'})
    set = fields.Integer(metadata={'description': '#### Set of the Result'})
