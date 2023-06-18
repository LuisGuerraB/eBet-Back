from datetime import datetime
from operator import or_

from marshmallow import Schema, fields, validate

from database import db
from .team import TeamSchema
from .tournament import TournamentSchema, Tournament


class Match(db.Model):
    __tablename__ = 'match'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    final_set = db.Column(db.Integer, nullable=True)
    plan_date = db.Column(db.DateTime, nullable=False)
    ini_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    away_team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    local_team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=False)
    result = db.Column(db.JSON(), nullable=True)

    away_team: db.Mapped['Team'] = db.relationship('Team', back_populates='matches', foreign_keys=[away_team_id])
    local_team: db.Mapped['Team'] = db.relationship('Team', back_populates='matches', foreign_keys=[local_team_id])
    tournament: db.Mapped['Tournament'] = db.relationship('Tournament', back_populates='matches')
    results: db.Mapped[list['Result']] = db.relationship('Result', back_populates='match')
    bets: db.Mapped[list['Bet']] = db.relationship('Bet', back_populates='match')

    @classmethod
    def get_list(cls, league_id=None, finished=None, year=None, month=None, page=1, limit=10):
        query = cls.query
        if league_id:
            query = query.join(Tournament).filter(Tournament.league_id == league_id)
        if year:
            query = query.filter(db.extract('year', cls.plan_date) == year)
        if month:
            query = query.filter(db.extract('month', cls.plan_date) == month)
        if finished is not None:
            now = datetime.now()
            if finished:
                query = query.filter(or_(cls.end_date <= now, cls.end_date.isnot(None))).order_by(
                    Match.plan_date.desc())
            else:
                query = query.filter(cls.end_date.is_(None)).order_by(Match.plan_date.asc())
        try:
            matches = query.paginate(page=page, per_page=limit)
            return matches.items
        except Exception as e:
            return []

    def update_result(self):
        match_res = {}
        results = self.results
        for result in results:
            win_stat = next((stat.value for stat in result.stats if stat.type == 'winner'), None)
            if win_stat is not None:
                match_res[result.team.acronym] = match_res.get(result.team.acronym, 0) + win_stat
        self.result = match_res
        self.final_set = len(results) // 2


class MatchSchema(Schema):
    id = fields.Integer(dump_only=True, metadata={'description': '#### Id of the Match'})
    name = fields.String(required=True, metadata={'description': '#### Name of the Match'})
    sets = fields.Integer(required=True, metadata={'description': '#### Number of sets of the Match'})
    plan_date = fields.DateTime(required=True, metadata={'description': '#### Planned date of the Match'})
    ini_date = fields.DateTime(metadata={'description': '#### Iniciation date of the Match'})
    end_date = fields.DateTime(metadata={'description': '#### End date of the Match'})
    away_team = fields.Nested(TeamSchema, required=True, metadata={'description': '#### Away team of the Match'})
    local_team = fields.Nested(TeamSchema, required=True, metadata={'description': '#### Local team of the Match'})
    tournament = fields.Nested(TournamentSchema, required=True, metadata={'description': '#### Tournament of the Match'})
    result = fields.Dict(keys=fields.String(required=True), values=fields.Integer(required=True), required=False)


class MatchListArgumentSchema(Schema):
    league_id = fields.Integer(validate=validate.Range(min=1),
                               metadata={'description': '#### Id of the League to match'})
    finished = fields.Boolean(metadata={'description': '#### If the match is finished'})
    year = fields.Integer(validate=validate.Range(min=2022), metadata={'description': '#### Year of the Match'})
    month = fields.Integer(validate=validate.Range(min=1, max=12), metadata={'description': '#### Month of the Match'})
    limit = fields.Integer(validate=validate.Range(min=1), metadata={'description': '#### Limit of the Match'})
    page = fields.Integer(validate=validate.Range(min=1), metadata={'description': '#### Page of the Match'})


class MatchListSchema(Schema):
    items = fields.List(fields.Nested(MatchSchema), dump_only=True, required=True,
                        metadata={'description': '#### List of Matches'})
    total = fields.Integer(dump_only=True, required=True, metadata={'description': '#### Total number of matches'})
