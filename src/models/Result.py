from app import db
from src.models import Team, Match


def obtain_percentage(json_frame, json_frame_opposite, type):
    total = len(json_frame)
    count = 0
    for i in range(total):
        if json_frame[i].get(type) > json_frame_opposite[i].get(type):
            count += 1
    if type == 'xp':
        total -= 2
    return count / float(total)


class Result(db.Model):
    __tablename__ = 'result'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    winner = db.Column(db.Boolean, nullable=False)
    gold_percent = db.Column(db.Float(precision=2))
    exp_percent = db.Column(db.Float(precision=2))
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

    @classmethod
    def create_from_web_json(cls, json, match_id, set):
        winner_id = json.get('winner').get('id')
        teams = json.get('teams')
        n_teams = len(teams)
        result = []
        for i in range(n_teams):
            team = teams[i]
            result.append(Result(
                winner=team.get('team').get('id') == winner_id,
                gold_percent=obtain_percentage(team.get('frames'), teams[(i + 1) % n_teams].get('frames'), 'gold'),
                exp_percent=obtain_percentage(team.get('frames'), teams[(i + 1) % n_teams].get('frames'), 'xp'),
                elders=team.get('elderDrakeKills'),
                towers=team.get('towerKills'),
                drakes=team.get('dragonKills'),
                inhibitors=team.get('inhibitorKills'),
                barons=team.get('baronKills'),
                heralds=team.get('heraldKills'),
                kills=team.get('kills'),
                deaths=team.get('deaths'),
                assists=team.get('assists'),
                team_id=team.get('team').get('id'),
                match_id=match_id,
                set=set
            ))
        return result
