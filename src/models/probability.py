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


class Probability(db.Model):
    __tablename__ = 'probability'

    PROB_INI = 10
    JUMP = 2
    LEN_MIN = calc_len_min(PROB_INI, JUMP)

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    prob_win = db.Column(db.Float(2))
    prob_gold = db.Column(db.Float(2))
    prob_exp = db.Column(db.Float(2))
    prob_towers = db.Column(db.JSON())
    prob_drakes = db.Column(db.JSON())
    prob_inhibitors = db.Column(db.JSON())
    prob_elders = db.Column(db.JSON())
    prob_barons = db.Column(db.JSON())
    prob_heralds = db.Column(db.JSON())
    prob_kills = db.Column(db.JSON())
    prob_deaths = db.Column(db.JSON())
    prob_assists = db.Column(db.JSON())

    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('league.id'))

    team: db.Mapped['Team'] = db.relationship('Team', back_populates='probabilities')

    @validates(
        'prob_towers',
        'prob_drakes',
        'prob_inhibitors',
        'prob_elders',
        'prob_barons',
        'prob_heralds',
        'prob_kills',
        'prob_deaths',
        'prob_assists'
    )
    def validate_len(self, key, value):
        if len(value) > 3:
            raise ValueError("JSON can't have more than 3 elements")
        return value

    def update_data(self, results, team_id, league_id):
        self.prob_win = self.calc_prob_win([result.winner for result in results])
        self.prob_gold = self.calc_prob_percent([result.gold_percent for result in results])
        self.prob_exp = self.calc_prob_percent([result.exp_percent for result in results])
        self.prob_towers = self.calc_prob_numbers([result.towers for result in results], (3, 6, 10))
        self.prob_drakes = self.calc_prob_numbers([result.drakes for result in results], (0, 2, 4))
        self.prob_inhibitors = self.calc_prob_numbers([result.inhibitors for result in results], (0, 2, 3))
        self.prob_elders = self.calc_prob_numbers([result.elders for result in results])
        self.prob_barons = self.calc_prob_numbers([result.barons for result in results])
        self.prob_heralds = self.calc_prob_numbers([result.heralds for result in results])
        self.prob_kills = self.calc_prob_numbers([result.kills for result in results], (10, 20, 30))
        self.prob_deaths = self.calc_prob_numbers([result.deaths for result in results], (10, 20, 30))
        self.prob_assists = self.calc_prob_numbers([result.assists for result in results], (10, 20, 30))
        self.team_id = team_id,
        self.league_id = league_id

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

    @classmethod
    def calc_prob_numbers(cls, list, multiplier=(1, 2, 3)):
        prob_total = 0
        prob_ini = cls.PROB_INI
        prob_res = [0, 0, 0]
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
        if len(list) < cls.LEN_MIN:
            prob_res[0] *= 100 / prob_total
            prob_res[1] *= 100 / prob_total
            prob_res[2] *= 100 / prob_total

        res = {}
        for i in range(3):
            prob_res[i] = round(prob_res[i] / 100.0, 2)
            if 1 > prob_res[i] > 0:
                res[multiplier[i]] = prob_res[i]
        return res

    @classmethod
    def justify_probability(cls, prob):
        if 1 >= prob > 0.98:
            prob = 0.98
        elif 0.02 > prob >= 0:
            prob = 0.02
        return prob

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


class ProbabilitySchema(Schema):
    id = fields.Integer(dump_only=True, metadata={'description': '#### ID of the probability'})
    prob_win = fields.Decimal(places=2, required=True, metadata={'description': '#### Probability of wining the game'})
    prob_gold = fields.Decimal(places=2, required=True, metadata={'description': '#### Probability of wining in gold'})
    prob_exp = fields.Decimal(places=2, required=True, metadata={'description': '#### Probability of wining in exp'})
    prob_towers = fields.List(fields.Decimal(places=2), validate=validate.Length(3), required=True,
                              metadata={'description': '#### Probability of towers'})
    prob_drakes = fields.List(fields.Decimal(places=2), validate=validate.Length(3), required=True,
                              metadata={'description': '#### Probability of drakes'})
    prob_inhibitors = fields.List(fields.Decimal(places=2), validate=validate.Length(3), required=True,
                                  metadata={'description': '#### Probability of inhibitors'})
    prob_elders = fields.List(fields.Decimal(places=2), validate=validate.Length(3), required=True,
                              metadata={'description': '#### Probability of elders'})
    prob_barons = fields.List(fields.Decimal(places=2), validate=validate.Length(3), required=True,
                              metadata={'description': '#### Probability of barons'})
    prob_heralds = fields.List(fields.Decimal(places=2), validate=validate.Length(3), required=True,
                               metadata={'description': '#### Probability of heralds'})
    prob_kills = fields.List(fields.Decimal(places=2), validate=validate.Length(3), required=True,
                             metadata={'description': '#### Probability of kills'})
    prob_deaths = fields.List(fields.Decimal(places=2), validate=validate.Length(3), required=True,
                              metadata={'description': '#### Probability of deaths'})
    prob_assists = fields.List(fields.Decimal(places=2), validate=validate.Length(3), required=True,
                               metadata={'description': '#### Probability of assists'})
    team_id = fields.Integer(metadata={'description': '#### TeamId of the Probability'})
    season_id = fields.Integer(metadata={'description': '#### SeasonId of the Probability'})


class ProbabilityCreateSchema(Schema):
    team_id = fields.Integer(required=True, metadata={'description': '#### TeamId of the Probability'})
    league_id = fields.Integer(allow_none=True, metadata={'description': '#### LeagueId of the Probability'})
