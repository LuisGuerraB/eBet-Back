from marshmallow import Schema, fields
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

    PROB_INI = 25
    JUMP = 5
    LEN_MIN = calc_len_min(PROB_INI, JUMP)

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    prob_win = db.Column(db.Float(2))
    prob_gold = db.Column(db.Float(2))
    prob_exp = db.Column(db.Float(2))
    prob_towers = db.Column(db.ARRAY(db.Float(2), dimensions=1))
    prob_drakes = db.Column(db.ARRAY(db.Float(2), dimensions=1))
    prob_inhibitors = db.Column(db.ARRAY(db.Float(2), dimensions=1))
    prob_elders = db.Column(db.ARRAY(db.Float(2), dimensions=1))
    prob_barons = db.Column(db.ARRAY(db.Float(2), dimensions=1))
    prob_heralds = db.Column(db.ARRAY(db.Float(2), dimensions=1))
    prob_kills = db.Column(db.ARRAY(db.Float(2), dimensions=1))
    prob_deaths = db.Column(db.ARRAY(db.Float(2), dimensions=1))
    prob_assists = db.Column(db.ARRAY(db.Float(2), dimensions=1))

    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    season_id = db.Column(db.Integer, db.ForeignKey('season.id'))

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
            raise ValueError("Array can't have more than 3 elements")
        return value

    def update_data(self, results, team_id, season_id):
        self.prob_win = self.calc_prob_win([result.winner for result in results]),
        self.prob_gold = self.calc_prob_percent([result.gold_percent for result in results]),
        self.prob_exp = self.calc_prob_percent([result.exp_percent for result in results]),
        self.prob_towers = self.calc_prob_numbers([result.towers for result in results], (3, 6, 9)),
        self.prob_drakes = self.calc_prob_numbers([result.drakes for result in results], (0, 2, 3)),
        self.prob_inhibitors = self.calc_prob_numbers([result.inhibitors for result in results], (0, 2, 3)),
        self.prob_elders = self.calc_prob_numbers([result.elders for result in results]),
        self.prob_barons = self.calc_prob_numbers([result.barons for result in results]),
        self.prob_heralds = self.calc_prob_numbers([result.heralds for result in results]),
        self.prob_kills = self.calc_prob_numbers([result.kills for result in results], (10, 20, 30)),
        self.prob_deaths = self.calc_prob_numbers([result.deaths for result in results], (10, 20, 30)),
        self.prob_assists = self.calc_prob_numbers([result.assists for result in results], (10, 20, 30)),
        self.team_id = team_id,
        self.season_id = season_id

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
            print('putadon', len(list))

        return prob_res / 100.00

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
            print('putadon', len(list))

        return prob_res / 100.00

    @classmethod
    def calc_prob_numbers(cls, list, multiplier=(0, 1, 2)):
        prob_total = 0
        prob_ini = cls.PROB_INI
        prob_res = [0, 0, 0]
        for i in list:
            if i <= multiplier[0]:
                prob_res[0] += prob_ini
            if i <= multiplier[1]:
                prob_res[1] += prob_ini
            if i <= multiplier[2]:
                prob_res[2] += prob_ini
            prob_total += prob_ini
            if prob_ini > cls.JUMP:
                prob_ini -= cls.JUMP
            if prob_total >= 100:
                break
        if len(list) < cls.LEN_MIN:
            print('putadon', len(list))

        return [prob_i / 100.00 for prob_i in prob_res]


class ProbabilitySchema(Schema):
    id = fields.Integer(dump_only=True, metadata={'description': '#### Id of the Probability'})
    prob_win = fields.Float(metadata={'description': '#### Probability of wining the game'})
    prob_gold = fields.Float(metadata={'description': '#### Probability of wining in gold'})
    prob_exp = fields.Float(metadata={'description': '#### Probability of wining in exp'})
    prob_towers = fields.Integer(metadata={'description': '#### Probability of towers'})
    prob_drakes = fields.Integer(metadata={'description': '#### Probability of drakes'})
    prob_inhibitors = fields.Integer(metadata={'description': '#### Probability of inhibitors'})
    prob_elders = fields.Integer(metadata={'description': '#### Probability of elders'})
    prob_barons = fields.Integer(metadata={'description': '#### Probability of barons'})
    prob_heralds = fields.Integer(metadata={'description': '#### Probability of heralds'})
    prob_kills = fields.Integer(metadata={'description': '#### Probability of kills'})
    prob_deaths = fields.Integer(metadata={'description': '#### Probability of deaths'})
    prob_assists = fields.Integer(metadata={'description': '#### Probability of assists'})
    team_id = fields.Integer(metadata={'description': '#### TeamId of the Probability'})
    season_id = fields.Integer(metadata={'description': '#### SeasonId of the Probability'})
