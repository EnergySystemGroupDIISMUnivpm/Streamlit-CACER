import datetime

import pytest

from cacer_simulator.common import Tariff
from cacer_simulator.models.model import economical_benefit_b, optimal_members


def test_optimal_members():

    result = optimal_members(1000)

    assert result == {
        "bar": 0,
        "appartamenti": 10,
        "pmi": 0,
        "hotel": 0,
        "ristoranti": 0,
    }


def test_tariff():
    assert Tariff().get_tariff(1000) == 0

    with pytest.raises(AssertionError):
        Tariff().get_tariff(-1000)


def test_economical_benefit_b():

    result = economical_benefit_b(
        1000,
        datetime.date(2021, 12, 16),
        0,
        "Lazio",
        300,
    )

    assert result == 3.0
