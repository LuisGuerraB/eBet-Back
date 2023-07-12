def test_get_final_number(match):
    match.sets = 3
    match.result = {"A": 1, "B": 1}
    assert match.get_final_number_of_sets() is None


def test_get_final_number_2(match):
    match.sets = 3
    match.result = {"A": 1, "B": 2}
    assert match.get_final_number_of_sets() == 3


def test_get_final_number_3(match):
    match.sets = 3
    match.result = {"A": 0, "B": 2}
    assert match.get_final_number_of_sets() == 2


def test_get_final_number_4(match):
    match.result = {"A": 1, "B": 0}
    assert match.get_final_number_of_sets() == 1
