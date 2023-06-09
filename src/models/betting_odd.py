from marshmallow import Schema, fields
from sqlalchemy import or_

from database import db
from src.models import Probability
from .play import Play

odds_related = ['winner']
odds_not_related = ['kills', 'deaths', 'assists', 'towerKills', 'inhibitorKills', 'heraldKills', 'dragonKills',
                    'elderDrakeKills', 'baronKills']


class BettingOdd(db.Model):
    __tablename__ = 'betting_odd'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    updated = db.Column(db.Boolean, nullable=False, server_default='0')
    play_id = db.Column(db.Integer, db.ForeignKey('play.id'), nullable=False)

    odds: db.Mapped[list['Odd']] = db.relationship('Odd', back_populates='betting_odd')
    play: db.Mapped['Play'] = db.relationship('Play', back_populates='betting_odd')

    @classmethod
    def create(cls, session, match, team_id, opposing_team_id):
        play = session.query(Play).filter(Play.match_id == match.id, Play.team_id == team_id).first()

        if play.betting_odd is None:
            betting_odd = BettingOdd(play_id=play.id)
            session.add(betting_odd)
            session.commit()
            betting_odd.update_data(session, opposing_team_id)
        else:
            play.betting_odd.update_data(session, opposing_team_id)
        session.commit()
        return play.betting_odd

    def update_data(self, session, opposing_team_id: int):
        if self.updated:
            return
        match_league_id = self.play.match.tournament.league.id

        team_probs = (session.query(Probability)
                      .filter(Probability.team_id == self.play.team_id,
                              or_(Probability.league_id == match_league_id, Probability.league_id == None))
                      .order_by(Probability.league_id).all())

        opposing_team_probs = (session.query(Probability)
                               .filter(Probability.team_id == opposing_team_id,
                                       or_(Probability.league_id == match_league_id, Probability.league_id == None))
                               .order_by(Probability.league_id).all())

        number_off_probs = min(len(team_probs), len(opposing_team_probs))
        if number_off_probs == 0:
            raise Exception('no-probabilities-found')
        percentage = 1 / number_off_probs

        own_prob_units = []
        away_prob_units = []
        for i in range(number_off_probs):
            own_prob_units += team_probs[i].prob_units
            away_prob_units += opposing_team_probs[i].prob_units

        grouped_prob_units = {}
        for prob_unit in own_prob_units + away_prob_units:
            prob_unit_type = prob_unit.type
            if prob_unit_type in grouped_prob_units:
                grouped_prob_units[prob_unit_type].append(prob_unit)
            else:
                grouped_prob_units[prob_unit_type] = [prob_unit]
        for prob_unit_type, prob_units in grouped_prob_units.items():
            if len(prob_units) == (2 * number_off_probs):
                if prob_unit_type in odds_related:
                    odd = Odd.create_related(prob_unit_type, prob_units[:number_off_probs],
                                             prob_units[number_off_probs:], self.id, percentage)
                else:
                    odd = Odd.create_unrelated(prob_unit_type, prob_units[:number_off_probs],
                                               prob_units[number_off_probs:], self.id, percentage)
                session.add(odd)
                session.commit()
        self.updated = True
        session.commit()

    def __str__(self):
        return f'<BettingOdd : {self.id} - {self.updated} - {self.play.match}>'


class Odd(db.Model):
    __tablenmame__ = 'odd'
    LEVERAGE = 0.05

    type = db.Column(db.String(15), primary_key=True)
    value = db.Column(db.JSON())

    betting_odd_id = db.Column(db.Integer, db.ForeignKey('betting_odd.id'), primary_key=True)
    betting_odd: db.Mapped['BettingOdd'] = db.relationship('BettingOdd', back_populates='odds')

    def __repr__(self):
        return f'<Odd : {self.type} - {self.value}>'

    @classmethod
    def calc_odds(cls, team_prob: float, opposing_team_prob: float, percentage=1.0) -> float:
        return round((1 / ((team_prob + cls.LEVERAGE) / (team_prob + opposing_team_prob))) * percentage, 2)

    @classmethod
    def calc_odds_not_related(cls, team_prob: float, opposing_team_prob: float, percentage=1.0) -> float:
        both_prob = (team_prob * opposing_team_prob) / 2
        res = 1 / (both_prob + team_prob + cls.LEVERAGE)
        return round(res * percentage, 2)

    @classmethod
    def create_related(cls, type, team_prob_list, opposing_prob_list, betting_odd_id, percentage=1.0):
        res_value = {}
        for i in range(len(team_prob_list)):
            team_prob = team_prob_list[i].probs
            opposing_prob = opposing_prob_list[i].probs
            res_value["1"] = res_value.get("1", 0) + cls.calc_odds(team_prob.get("1"), opposing_prob.get("1"), percentage)
        odd = cls.query.filter(cls.type == type, cls.betting_odd_id == betting_odd_id).first()

        if odd is None:
            odd = Odd(type=type, value=res_value, betting_odd_id=betting_odd_id)
        else:
            odd.value = res_value
        return odd

    @classmethod
    def create_unrelated(cls, type, team_prob_list, opposing_prob_list, betting_odd_id, percentage=1.0):
        res_value = {}
        for i in range(len(team_prob_list)):
            team_prob = team_prob_list[i].probs
            opposing_prob = opposing_prob_list[i].probs
            for subtype in team_prob.keys() & opposing_prob.keys():
                res_value[subtype] = res_value.get(subtype, 0) + cls.calc_odds_not_related(team_prob[subtype],
                                                                                           opposing_prob[subtype],
                                                                                           percentage)
        res_value = {subtype: value for subtype, value in res_value.items() if value > 1}
        odd = cls.query.filter(cls.type == type, cls.betting_odd_id == betting_odd_id).first()
        if odd is None:
            odd = Odd(type=type, value=res_value, betting_odd_id=betting_odd_id)
        else:
            odd.value = res_value
        return odd


class OddSchema(Schema):
    type = fields.String(required=True, metadata={'description': '#### Odd type'})
    value = fields.Dict(keys=fields.String(), values=fields.Float(), metadata={'description': '#### Odd value'})


class BettingOddsByMatchSchema(Schema):
    away_team_odds = fields.Nested(OddSchema, many=True, metadata={'description': '#### Away team odds'})
    local_team_odds = fields.Nested(OddSchema, many=True, metadata={'description': '#### Local team odds'})
    prob_finish_early = fields.Float()
