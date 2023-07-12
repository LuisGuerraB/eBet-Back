import pytest
from datetime import datetime, timedelta

from werkzeug.security import check_password_hash

from app import app
from src.enums import Privilege
from src.models import User



def test_login_invalid_credentials(user):
    # Mock the check_password_hash function
    check_password_hash.return_value = False
    with pytest.raises(Exception) as e:
        user.login('incorrect_password')
    assert str(e.value) == 'control-error.invalid-credentials'


def test_redeem_prize(user):
    # Mock the datetime module to control the current time
    current_time = datetime.now()
    user.balance = 100
    with app.app_context():
        # Redeem prize when last login is more than 24 hours ago
        user.last_login = current_time - timedelta(days=1, seconds=1)
        assert user.redeem_prize() == True
        assert user.balance == 200

        # Redeem prize when last login is less than 24 hours ago
        user.last_login = current_time - timedelta(hours=23, minutes=59, seconds=59)
        assert user.redeem_prize() == False
        assert user.balance == 200


def test_has_privilege(user):
    user.privileges = 'a'
    assert user.has_privilege(Privilege.ADMIN) == True
    assert user.has_privilege(Privilege.MARKETING) == False
    user.privileges = 'm'
    assert user.has_privilege(Privilege.ADMIN) == False
    assert user.has_privilege(Privilege.MARKETING) == True


def test_parse_privileges(user):
    user.privileges = 'am'
    assert user.parse_privileges() == [Privilege.ADMIN.value, Privilege.MARKETING.value]
