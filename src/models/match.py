from datetime import datetime
from operator import or_
from marshmallow import Schema, fields, validate

from database import db
from .play import Play
from .team import PlayTeamSchema
from .tournament import TournamentSchema, Tournament


class Match(db.Model):
    __tablename__ = 'match'

    id = db.Column(db.Integer, primary_key=True)
    sets = db.Column(db.Integer, nullable=False)
    plan_date = db.Column(db.DateTime, nullable=False)
    ini_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=False)
    result = db.Column(db.JSON(), nullable=True)

    plays: db.Mapped[list['Play']] = db.relationship('Play', back_populates='match')
    tournament: db.Mapped['Tournament'] = db.relationship('Tournament', back_populates='matches')

    @classmethod
    def get_list(cls, league_id=None,team_id=None, finished=None, year=None, month=None, page=1, limit=10):
        query = cls.query
        if league_id is not None:
            query = query.join(Tournament, Tournament.id == Match.tournament_id).filter(Tournament.league_id == league_id)
        if team_id is not None:
            query = query.join(Play, Play.match_id == Match.id).filter(Play.team_id == team_id)
        if year is not None:
            query = query.filter(db.extract('year', cls.plan_date) == year)
        if month is not None:
            query = query.filter(db.extract('month', cls.plan_date) == month)
        if finished is not None:
            now = datetime.now()
            if finished:
                query = query.filter(or_(cls.end_date <= now, cls.end_date.isnot(None))).order_by(
                    Match.plan_date.desc())
            else:
                query = query.filter(cls.end_date.is_(None)).order_by(Match.plan_date.asc())
        matches = query.paginate(page=page, per_page=limit)
        return matches.items

    def get_final_number_of_sets(self):
        if self.result is not None and len(self.result) > 0:
            for team, winning in self.result.entries():
                if winning > self.sets:
                    return sum(self.result.values())
            return None
        else:
            return None


class MatchSchema(Schema):
    id = fields.Integer(dump_only=True, metadata={'description': '#### Id of the Match'})
    name = fields.String(required=True, metadata={'description': '#### Name of the Match'})
    sets = fields.Integer(required=True, metadata={'description': '#### Number of sets of the Match'})
    plan_date = fields.DateTime(required=True, metadata={'description': '#### Planned date of the Match'})
    ini_date = fields.DateTime(metadata={'description': '#### Iniciation date of the Match'})
    end_date = fields.DateTime(metadata={'description': '#### End date of the Match'})
    plays = fields.List(fields.Nested(PlayTeamSchema), dump_only=True, required=True,
                        metadata={'description': '#### List of Plays'})
    tournament = fields.Nested(TournamentSchema, required=True,
                               metadata={'description': '#### Tournament of the Match'})
    result = fields.Dict(keys=fields.String(required=True), values=fields.Integer(required=True), required=False)


class MatchListArgumentSchema(Schema):
    league_id = fields.Integer(metadata={'description': '#### Id of the League to match'})
    team_id = fields.Integer(metadata={'description': '#### Id of the Team'})
    finished = fields.Boolean(metadata={'description': '#### If the match is finished'})
    year = fields.Integer(validate=validate.Range(min=2022), metadata={'description': '#### Year of the Match'})
    month = fields.Integer(validate=validate.Range(min=1, max=12), metadata={'description': '#### Month of the Match'})
    limit = fields.Integer(validate=validate.Range(min=1), metadata={'description': '#### Limit of the Match'})
    page = fields.Integer(validate=validate.Range(min=1), metadata={'description': '#### Page of the Match'})


class MatchListSchema(Schema):
    items = fields.List(fields.Nested(MatchSchema), dump_only=True, required=True,
                        metadata={'description': '#### List of Matches'})
    total = fields.Integer(dump_only=True, required=True, metadata={'description': '#### Total number of matches'})


class PlayMatchSchema(Schema):
    match = fields.Nested(MatchSchema, required=True, metadata={'description': '#### Match of the Play'})
    team_id = fields.Integer(required=True, metadata={'description': '#### TeamId of the Play'})
