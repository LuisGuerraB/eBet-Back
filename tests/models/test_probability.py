import pytest
from unittest import mock
from src.models import Match, Result, Stat
from src.models import Probability, ProbUnit
from src.models.probability import calc_len_min

def test_calc_len_min():
    assert calc_len_min(18, 2) == 14

def test_justify_probability():
    assert ProbUnit.justify_probability(0.96) == 0.95
    assert ProbUnit.justify_probability(0.04) == 0.05

def test_calc_prob_with_multiplier():
    prob_unit = ProbUnit()
    res_list = [10,20,30]
    multiplier = (10, 20, 30)
    result = prob_unit.calc_prob(res_list, multiplier)
    assert result == {10: 0.95, 20: 0.63, 30: 0.29}

def test_calc_prob_without_multiplier():
    prob_unit = ProbUnit()
    res_list = [1, 2, 3]
    result = prob_unit.calc_prob(res_list)
    assert result == {1: 0.95, 2: 0.63, 3: 0.29}