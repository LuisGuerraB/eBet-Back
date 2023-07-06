from marshmallow import Schema, fields
from sqlalchemy import UniqueConstraint

from database import db
from .match import Match
from .play import Play


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


avoid_types = ['frames', 'team', 'goldEarned', 'deaths']


class Result(db.Model):
    __tablename__ = 'result'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stats: db.Mapped[list['Stat']] = db.relationship('Stat', back_populates='result')

    play_id = db.Column(db.Integer, db.ForeignKey('play.id'), nullable=False)
    set = db.Column(db.Integer, nullable=False)

    play: db.Mapped['Play'] = db.relationship('Play', back_populates='result')

    __table_args__ = (
        UniqueConstraint('play_id', 'set', name='_play_set_uc'),
    )

    @classmethod
    def create_from_web_json(cls, session, json, match_id, set):
        winner_id = json['winner']['id']
        teams = json['teams']
        n_teams = len(teams)
        for i in range(n_teams):
            team = teams[i]
            play = session.query(Play).filter_by(match_id=match_id, team_id=team['team']['id']).first()
            if session.query(Result).filter_by(play_id=play.id, set=set).first() is None:
                result = Result(play_id=play.id, set=set)
                session.add(result)
                session.commit()
                if team['team']['id'] == winner_id:
                    session.add(Stat(type='winner', value=1, result_id=result.id))
                else:
                    session.add(Stat(type='winner', value=0, result_id=result.id))
                for stat in team:
                    if stat not in avoid_types:
                        session.add(Stat(type=stat, value=team[stat], result_id=result.id))

    @classmethod
    def get_from_match(cls, match):
        res = {
            'away_team_result': [],
            'local_team_result': [],
        }
        with db.session() as session:
            if match is None:
                return res
            for play in match.plays:
                results = session.query(Result).filter_by(play_id=play.id).order_by(Result.set).all()
                if results is None:
                    continue
                for result in results:
                    result.stats.sort(key=lambda x: x.type, reverse=True)
                    if play.local:
                        res['local_team_result'].append(result)
                    else:
                        res['away_team_result'].append(result)
            return res

    @classmethod
    def update_result_from_match(self, match, session=None):
        if session is None:
            session = db.session()
        match_res = {}
        results = session.query(Result).join(Play, Result.play_id == Play.id).filter(Play.match_id == match.id).all()
        if len(results) == 0:
            return
        for result in results:
            win_stat = next((stat.value for stat in result.stats if stat.type == 'winner'), None)
            if win_stat is not None:
                match_res[result.play.team.acronym] = match_res.get(result.play.team.acronym, 0) + win_stat
        match.result = match_res
        session.commit()

    @classmethod
    def get_statistics_from_team(self, team_id):
        query = db.session.query(
            Stat.type,
            db.func.sum(Stat.value).label('sum_values'),
            db.func.count(Stat.type).label('cont_values')
        ).join(Result).join(Play).join(Match).filter(Play.team_id == team_id).filter(Match.id.in_(
            db.session.query(Match.id).join(Play).filter(Play.team_id == team_id).filter(
                Match.end_date.isnot(None)).order_by(Match.end_date.desc()).limit(10)
        )).group_by(Stat.type)

        # Ejecutar la consulta
        result = []
        for row in query.all():
            result.append({'type': row.type, 'sum_values': row.sum_values, 'count_values': row.cont_values})
        return result

    def __repr__(self):
        return f'<Result : {self.play_id} - {self.set} - {self.stats}>'

    def __str__(self):
        return f'{self.play_id} - {self.set} - {self.stats}'


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


class ResultByMatchSchema(Schema):
    away_team_result = fields.Nested(ResultSchema, many=True, metadata={'description': '#### Away team odds'})
    local_team_result = fields.Nested(ResultSchema, many=True, metadata={'description': '#### Local team odds'})


class TeamStatisticSchema(Schema):
    type = fields.String(metadata={'description': '#### Type of the Stat'})
    sum_values = fields.Integer(metadata={'description': '#### Sum of the values of the Stat'})
    count_values = fields.Integer(metadata={'description': '#### Count of how much values of the Stat'})
