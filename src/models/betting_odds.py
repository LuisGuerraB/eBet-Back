from marshmallow import Schema, fields, validate
from sqlalchemy import or_

from database import db
from src.models import Probability, Match


class BettingOdds(db.Model):
    __tablename__ = 'betting_odds'
    LEVERAGE = 0.03

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    win_odds = db.Column(db.Float(2), nullable=False)
    gold_odds = db.Column(db.Float(2), nullable=False)
    exp_odds = db.Column(db.Float(2), nullable=False)
    towers_odds = db.Column(db.JSON(), nullable=False)
    drakes_odds = db.Column(db.JSON(), nullable=False)
    inhibitors_odds = db.Column(db.JSON(), nullable=False)
    elders_odds = db.Column(db.JSON(), nullable=False)
    barons_odds = db.Column(db.JSON(), nullable=False)
    heralds_odds = db.Column(db.JSON(), nullable=False)
    kills_odds = db.Column(db.JSON(), nullable=False)
    deaths_odds = db.Column(db.JSON(), nullable=False)
    assists_odds = db.Column(db.JSON(), nullable=False)

    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)

    def __init__(self, match_id: int, team_id: int, opposing_team_id: int):
        self.update_data(db.session(), match_id, team_id, opposing_team_id)
        super().__init__()

    def update_data(self, session, match_id: int, team_id: int, opposing_team_id: int):
        self.team_id = team_id
        self.match_id = match_id
        match_league_id = session.query(Match).get(match_id).season.league.id

        team_probs = (session.query(Probability)
                      .filter(Probability.team_id == team_id,
                              or_(Probability.league_id == match_league_id, Probability.league_id == None))
                      .order_by(Probability.league_id).all())

        opposing_team_probs = (session.query(Probability)
                               .filter(Probability.team_id == opposing_team_id,
                                       or_(Probability.league_id == match_league_id, Probability.league_id == None))
                               .order_by(Probability.league_id).all())

        odds_attributes = ['win', 'gold', 'exp']
        json_attributes = ['towers', 'drakes', 'inhibitors', 'elders', 'barons', 'heralds', 'kills', 'deaths',
                           'assists']
        number_off_probs = min(len(team_probs), len(opposing_team_probs))
        percentage = 1 / number_off_probs

        for i in range(number_off_probs):
            for attr in odds_attributes:
                team_prob = getattr(team_probs[i], f'prob_{attr}')
                opposing_team_prob = getattr(opposing_team_probs[i], f'prob_{attr}')
                odds_attr = f'{attr}_odds'
                if i == 0:
                    setattr(self, odds_attr, self.calc_odds(team_prob, opposing_team_prob, percentage))
                else:
                    setattr(self, odds_attr,
                            getattr(self, odds_attr) + self.calc_odds(team_prob, opposing_team_prob, percentage))

            for attr in json_attributes:
                dicRes = {}

                for number, prob in getattr(team_probs[i], f'prob_{attr}').items():
                    if (opposing_team_probs[i].__dict__[f'prob_{attr}'].get(number, None) is None
                            or team_probs[i].__dict__[f'prob_{attr}'].get(number, None) is None):
                        continue
                    if i == 0:
                        odd = self.calc_odds_not_related(prob, getattr(opposing_team_probs[i], f'prob_{attr}')[number],
                                                         percentage)
                        dicRes[number] = odd
                    else:
                        odd = self.calc_odds_not_related(prob, getattr(opposing_team_probs[i], f'prob_{attr}')[number],
                                                         percentage)
                        getattr(self, f'{attr}_odds')[number] += odd

                if i == 0:
                    setattr(self, f'{attr}_odds', dicRes)

    def calc_odds(self, team_prob: float, opposing_team_prob: float, percentage=1.0) -> float:
        return round((1 / ((team_prob + self.LEVERAGE) / (team_prob + opposing_team_prob))) * percentage, 2)

    def calc_odds_not_related(self, team_prob: float, opposing_team_prob: float, percentage=1.0) -> float:
        both_prob = team_prob * opposing_team_prob
        res = 1 / (both_prob + team_prob + self.LEVERAGE)
        return round(res * percentage, 2)

    def __str__(self):
        return f'{self.win_odds} {self.gold_odds} {self.exp_odds}' \
               f' {self.towers_odds} {self.drakes_odds} {self.inhibitors_odds} {self.elders_odds} {self.barons_odds}' \
               f' {self.heralds_odds} {self.kills_odds} {self.deaths_odds} {self.assists_odds}'


class BettingOddSchema(Schema):
    id = fields.Int(dump_only=True, required=True, metadata={'description': '#### Id of the Betting Odds'})
    win_odds = fields.Float(format='0.00', required=True, metadata={'description': '#### Win odds'})
    gold_odds = fields.Float(format='0.00', required=True, metadata={'description': '#### Gold odds'})
    exp_odds = fields.Float(format='0.00', required=True, metadata={'description': '#### Exp odds'})
    towers_odds = fields.Dict(keys=fields.Str(), values=fields.Float(format='0.00'), validate=validate.Length(3),
                              required=True, metadata={'description': '#### Tower odds'})
    drakes_odds = fields.Dict(keys=fields.Str(), values=fields.Float(format='0.00'), validate=validate.Length(3),
                              required=True, metadata={'description': '#### Drakes odds'})
    inhibitors_odds = fields.Dict(keys=fields.Str(), values=fields.Float(format='0.00'), validate=validate.Length(3),
                                  required=True, metadata={'description': '#### Inhibitors odds'})
    elders_odds = fields.Dict(keys=fields.Str(), values=fields.Float(format='0.00'), validate=validate.Length(3),
                              required=True, metadata={'description': '#### Elders odds'})
    barons_odds = fields.Dict(keys=fields.Str(), values=fields.Float(format='0.00'), validate=validate.Length(3),
                              required=True, metadata={'description': '#### Barons odds'})
    heralds_odds = fields.Dict(keys=fields.Str(), values=fields.Float(format='0.00'), validate=validate.Length(3),
                               required=True, metadata={'description': '#### Herald odds'})
    kills_odds = fields.Dict(keys=fields.Str(), values=fields.Float(format='0.00'), validate=validate.Length(3),
                             required=True, metadata={'description': '#### Kills odds'})
    deaths_odds = fields.Dict(keys=fields.Str(), values=fields.Float(format='0.00'), validate=validate.Length(3),
                              required=True, metadata={'description': '#### Deaths odds'})
    assists_odds = fields.Dict(keys=fields.Str(), values=fields.Float(format='0.00'), validate=validate.Length(3),
                               required=True, metadata={'description': '#### Assists odds'})


class BettingOddsByMatchSchema(Schema):
    away_team_odds = fields.Nested(BettingOddSchema)
    local_team_odds = fields.Nested(BettingOddSchema)
