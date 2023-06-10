from collections import defaultdict

from marshmallow import Schema, fields, validate
from sqlalchemy.orm import validates

from database import db


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
    'assists': (10, 20, 30),
}


class Probability(db.Model):
    __tablename__ = 'probability'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    prob_units: db.Mapped[list['ProbUnit']] = db.relationship('ProbUnit', back_populates='probability')

    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('league.id'))

    team: db.Mapped['Team'] = db.relationship('Team', back_populates='probabilities')

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
                prob_unit = ProbUnit(type, grouped_stats[type], self.id)
                session.add(prob_unit)
        session.commit()

    @classmethod
    def calc_prob_win(cls, list):
        count = 0
        prob_total = 0
        prob_ini = cls.PROB_INI
        prob_res = 0
        for i in list:
            count += 1
            if i:
                prob_res += prob_ini
            prob_total += prob_ini
            if prob_ini > cls.JUMP:
                prob_ini -= cls.JUMP
            if prob_total >= 100:
                break
        if len(list) < cls.LEN_MIN:
            prob_res *= 100 / prob_total

        return cls.justify_probability(round(prob_res / 100.00, 2))

    @classmethod
    def calc_prob_percent(cls, list):
        prob_total = 0
        prob_ini = cls.PROB_INI
        prob_res = 0
        for i in list:

            if i >= 0.5:
                prob_res += prob_ini
            prob_total += prob_ini
            if prob_ini > cls.JUMP:
                prob_ini -= cls.JUMP
            if prob_total >= 100:
                break

        if len(list) < cls.LEN_MIN:
            prob_res *= 100 / prob_total

        return cls.justify_probability(round(prob_res / 100.00, 2))

    def __str__(self):
        return f"Probability: {self.id}\n" \
               f"Probability_win: {self.prob_win}%\n" \
               f"Probability gold: {self.prob_gold}%\n" \
               f"Probability exp: {self.prob_exp}%\n" \
               f"Probability towers: {self.prob_towers}\n" \
               f"Probability drakes: {self.prob_drakes}\n" \
               f"Probability inhibitors: {self.prob_inhibitors}\n" \
               f"Probability elders: {self.prob_elders}\n" \
               f"Probability barons: {self.prob_barons}\n" \
               f"Probability heralds: {self.prob_heralds}\n" \
               f"Probability kills: {self.prob_kills}\n" \
               f"Probability deaths: {self.prob_deaths}\n" \
               f"Probability assists: {self.prob_assists}\n"


class ProbUnit(db.Model):
    PROB_INI = 16
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

    def __init__(self, prob_type, res_list, prob_id):
        self.update_data(prob_type, res_list)
        super().__init__(type=prob_type, probs=self.probs, probability_id=prob_id)

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
    def calc_prob(cls, list, multiplier=(1, 2, 3)):
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
        if len_min:
            prob_res[0] *= 100 / prob_total
            prob_res[1] *= 100 / prob_total
            prob_res[2] *= 100 / prob_total

        res = {}
        for i in range(3):
            prob_res[i] = round(prob_res[i] / 100.0, 2)
            if len_min:
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
    team_id = fields.Integer(metadata={'description': '#### TeamId of the Probability'})
    season_id = fields.Integer(metadata={'description': '#### SeasonId of the Probability'})


class ProbabilityCreateSchema(Schema):
    team_id = fields.Integer(required=True, metadata={'description': '#### TeamId of the Probability'})
    league_id = fields.Integer(allow_none=True, metadata={'description': '#### LeagueId of the Probability'})
