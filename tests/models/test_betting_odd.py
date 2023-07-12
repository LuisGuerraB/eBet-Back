import pytest

from app import app
from database import db
from src.models.betting_odd import Odd


def test_update(betting_odd):
    with app.app_context():
        new_betting_odd = betting_odd
        new_betting_odd.updated = True
        new_betting_odd.update_data(db.session(), 2)
        assert new_betting_odd == betting_odd


def test_calc_odds():
    # Test with valid values
    Odd.LEVERAGE = 0
    assert Odd.calc_odds(0.7, 0.5, 1.0) == 1.71
    assert Odd.calc_odds(0.5, 0.7, 1.0) == 2.4
    assert Odd.calc_odds(0.2, 0.8, 0.5) == 2.5

def test_calc_odds_2():
    # Test with edge cases
    Odd.LEVERAGE = 0
    assert Odd.calc_odds(0.05, 0.05, 1.0) == 2
    assert Odd.calc_odds(0.95, 0.95, 1.0) == 2

def test_calc_odds_3():
    # Test with negative values
    with pytest.raises(ZeroDivisionError):
        Odd.calc_odds(0.0, 0.0, 1.0)

def test_calc_odds_4():
    # Test with incorrect values
    with pytest.raises(TypeError):
        Odd.calc_odds("0.7", 0.5, 1.0)


def test_calc_odds_not_related():
    # Test with valid values
    Odd.LEVERAGE = 0
    assert Odd.calc_odds_not_related(0.7, 0.5, 1.0) == 1.14
    assert Odd.calc_odds_not_related(0.5, 0.7, 1.0) == 1.48
    assert Odd.calc_odds_not_related(0.2, 0.8, 1.0) == 3.57

def test_calc_odds_not_related_2():
    # Test with edge cases
    Odd.LEVERAGE = 0
    assert Odd.calc_odds_not_related(0.05, 0.05, 1.0) > 2
    assert Odd.calc_odds_not_related(0.95, 0.95, 1.0) < 2

def test_calc_odds_not_related_3():
    # Test with negative values
    with pytest.raises(ZeroDivisionError):
        Odd.calc_odds_not_related(0.0, 0.0, 1.0)

def test_calc_odds_not_related_4():
    # Test with incorrect values
    with pytest.raises(TypeError):
        Odd.calc_odds_not_related("0.7", 0.5, 1.0)