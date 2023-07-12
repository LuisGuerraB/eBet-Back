from datetime import datetime, timedelta

import pytest
from app import app
from src.models import Match, Bet, Team, Play, User, BettingOdd, Prize
from src.models.betting_odd import Odd


@pytest.fixture()
def app():
    """
    :return: Base2 app
    """
    return app


@pytest.fixture
def user():
    return User(username='test_user', password='password', email='test@example.com')


@pytest.fixture
def play():
    return Play(id=1, team_id=1, match_id=1, local=False)


def team():
    return Team(id=1, name="name", acronym='acr', img='img', website='web', nationality='nat', league_id=1)


@pytest.fixture
def match():
    return Match(id=1, sets=1, plan_date=datetime.now(), ini_date=datetime.now(), end_date=datetime.now(),
                 tournament_id=1)


@pytest.fixture
def bet():
    return Bet(id=1, type="winner", subtype=1, amount=10, multiplier=1.1, set=1, play_id=1,
               date=(datetime.now() - timedelta(days=1, seconds=1)))


@pytest.fixture()
def betting_odd():
    return BettingOdd(id=1, play_id=1)


@pytest.fixture
def odd():
    return Odd(betting_odd_id=1, type='winner', value={1: 2.0})


@pytest.fixture
def prize():
    return Prize(id=1, amount=100, img='img', price=100)
