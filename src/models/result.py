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
