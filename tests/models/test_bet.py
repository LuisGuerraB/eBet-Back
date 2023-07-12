import pytest

from app import app
from database import db


def test_update_amount(user, bet, play):
    with app.app_context():
        user.balance = 100
        bet.user = user
        bet.update_amount(db.session(), 20)
        assert bet.amount == 20
        assert user.balance == 90


def test_update_amount_2(user, bet, play):
    with app.app_context():
        user.balance = 100
        bet.user = user
        with pytest.raises(Exception):
            bet.update_amount(db.session(), 200)


def test_create(user, bet):
    with app.app_context():
        user.balance = 100
        bet.user = user
        with pytest.raises(Exception):
            bet.create(user, amount=110)


def test_create_2(user, bet):
    with app.app_context():
        user.balance = 100
        bet.user = user
        with pytest.raises(Exception):
            bet.create(user, amount=-10)


