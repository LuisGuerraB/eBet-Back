from collections import defaultdict

from marshmallow import Schema, fields
from sqlalchemy import desc
from sqlalchemy.orm import validates

from database import db
from src.models import Match, Result
from .play import Play


def calc_len_min(prob_ini, jump):
    count = 0
    prob_total = 0
    prob_ini = prob_ini
    while prob_total < 100:
        count += 1
        prob_total += prob_ini
        if prob_ini > jump:
            prob_ini -= jump
    return count


type_multiplier_dictionary = {
    'towerKills': (3, 6, 10),
    'dragonKills': (0, 2, 4),
    'kills': (10, 20, 30),
    'deaths': (10, 20, 30),
    'assists': (20, 40, 60),
}


class Probability(db.Model):
    __tablename__ = 'probability'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    prob_units: db.Mapped[list['ProbUnit']] = db.relationship('ProbUnit', back_populates='probability')
    prob_finish_early = db.Column(db.Float, nullable=False, server_default='0')
    updated = db.Column(db.Boolean, nullable=False, server_default='0')

    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('league.id'))

    team: db.Mapped['Team'] = db.relationship('Team', back_populates='probabilities')

    @classmethod
    def create_probabilities_from_team_at_league(cls, team_id, league_id=None, session=None):
        # Get match of the team at a league
        if session is None:
            session = db.session(expire_on_commit=False)

        probability = session.query(Probability).filter_by(team_id=team_id, league_id=league_id).first()
        if probability is not None and probability.updated:
            return
        if league_id:
            plays = session.query(Play).join(Match, Play.match_id == Match.id).filter(
                Play.team_id == team_id, Match.tournament.has(league_id=league_id), Match.end_date.isnot(None),
            ).order_by(desc(Match.ini_date)).all()
        else:
            plays = session.query(Play).join(Match, Play.match_id == Match.id).filter(
                Play.team_id == team_id, Match.end_date.isnot(None),
            ).order_by(desc(Match.ini_date)).all()

        # Get the results of the match an order it by match.ini_date
        results = session.query(Result).filter(Result.play_id.in_([play.id for play in plays])).all()
        matches = [play.match for play in plays if play.match is not None]
        if len(results) != 0:
            prob_finished_early = ProbUnit.calc_prob(
                [1 if match.get_final_number_of_sets() is not None and match.sets > match.get_final_number_of_sets() else 0
                 for match in matches if match.sets != 1], force=True)
            if probability is None:
                probability = Probability(team_id=team_id, league_id=league_id)
                session.add(probability)
                session.commit()
                probability.update_data(session, results)
                probability.prob_finish_early = prob_finished_early.get(1)
            else:
                probability.prob_finish_early = prob_finished_early.get(1)
                probability.update_data(session, results)
            probability.updated = True
            session.commit()

    def update_data(self, session, results):
        grouped_stats = defaultdict(list)
        for result in results:
            for stat in result.stats:
                stat_type = stat.type
                grouped_stats[stat_type].append(stat)
        for type in grouped_stats:
            prob_unit = next((prob_unit for prob_unit in self.prob_units if prob_unit.type == type), None)
            if prob_unit is not None:
                prob_unit.update_data(type, grouped_stats[type])
            else:
                prob_unit = ProbUnit(type=type, probs={}, probability_id=self.id)
                prob_unit.update_data(type, grouped_stats[type])
                session.add(prob_unit)
        session.commit()

    @classmethod
    def finish_early_match(self, session, match):
        probabilities = session.query(Probability).filter(
            Probability.team_id.in_([play.team_id for play in match.plays])).all()
        prob_finish_early_array = [prob.prob_finish_early for prob in probabilities]
        prob_finish_early = sum(prob_finish_early_array) / len(prob_finish_early_array)
        return prob_finish_early

    def __repr__(self):
        return f"<Probability: {self.id}\n" \
               f"Prob_finish_early: {self.prob_finish_early}%\n" \
               f"Updated: {self.updated}%\n" \
               f"Prob_units : {self.prob_units}>"


class ProbUnit(db.Model):
    PROB_INI = 18
    JUMP = 2
    LEN_MIN = calc_len_min(PROB_INI, JUMP)

    __tablename__ = 'prob_unit'

    type = db.Column(db.String(15), primary_key=True)
    probs = db.Column(db.JSON())
    probability_id = db.Column(db.Integer, db.ForeignKey('probability.id'), primary_key=True)
    probability: db.Mapped['Probability'] = db.relationship('Probability', back_populates="prob_units")

    @validates('probs')
    def validate_len(self, key, value):
        if len(value) > 3:
            raise ValueError("JSON can't have more than 3 elements")
        return value

    def update_data(self, prob_type, res_list):
        multiplier = type_multiplier_dictionary.get(prob_type, None)
        if multiplier is not None:
            self.probs = self.calc_prob([stat.value for stat in res_list], multiplier)
        else:
            self.probs = self.calc_prob([stat.value for stat in res_list])

    @classmethod
    def justify_probability(cls, prob):
        if 1 >= prob > 0.95:
            prob = 0.95
        elif 0.05 > prob >= 0:
            prob = 0.05
        return prob

    @classmethod
    def calc_prob(cls, list, multiplier=(1, 2, 3), force=False):
        prob_total = 0
        prob_ini = cls.PROB_INI
        prob_res = [0, 0, 0]
        len_min = len(list) < cls.LEN_MIN

        for i in list:
            if i >= multiplier[0]:
                prob_res[0] += prob_ini
            if i >= multiplier[1]:
                prob_res[1] += prob_ini
            if i >= multiplier[2]:
                prob_res[2] += prob_ini
            prob_total += prob_ini
            if prob_ini > cls.JUMP:
                prob_ini -= cls.JUMP
            if prob_total >= 100:
                break
        if len_min and prob_total != 0:
            prob_res[0] *= 100 / prob_total
            prob_res[1] *= 100 / prob_total
            prob_res[2] *= 100 / prob_total

        res = {}
        for i in range(3):
            prob_res[i] = round(prob_res[i] / 100.0, 2)
            if len_min or force:
                res[multiplier[i]] = cls.justify_probability(prob_res[i])
            elif 1 > prob_res[i] > 0:
                res[multiplier[i]] = prob_res[i]
        return res

    def __repr__(self):
        return f'<ProbUnit : {self.type} - {self.probs}>'


class ProbUnitSchema(Schema):
    type = fields.String(dump_only=True)
    prob = fields.List(fields.Decimal(places=2), required=True, dump_only=True)


class ProbabilitySchema(Schema):
    id = fields.Integer(dump_only=True, metadata={'description': '#### ID of the probability'})
    prob_units = fields.Nested(ProbUnitSchema, many=True)
    prob_finish_early = fields.Float(dump_only=True,
                                     metadata={'description': '#### Probability of finishing the game early'})
    team_id = fields.Integer(metadata={'description': '#### TeamId of the Probability'})
    league_id = fields.Integer(metadata={'description': '#### LeagueId of the Probability'})


class ProbabilityCreateSchema(Schema):
    team_id = fields.Integer(required=True, metadata={'description': '#### TeamId of the Probability'})
    league_id = fields.Integer(allow_none=True, metadata={'description': '#### LeagueId of the Probability'})
