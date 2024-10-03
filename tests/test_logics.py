import datetime

import pytest
import numpy as np
from cacer_simulator.common import Tariff
from cacer_simulator.models.model import (
    consumption_estimation,
    economical_benefit_b,
    optimal_members,
    optimal_sizing,
)
from multivector_simulator.models.model import calculate_cogen_size_optimized


def test_optimal_members():

    result = optimal_members(1000)

    assert result == {
        "bar": 0,
        "appartamenti": 2,
        "pmi": 0,
        "hotel": 0,
        "ristoranti": 0,
    }


def test_consumption_estimation():

    result = consumption_estimation(
        {
            "bar": 0,
            "appartamenti": 10,
            "pmi": 0,
            "hotel": 0,
            "ristoranti": 0,
        }
    )

    assert result == 20_000


def test_tariff():
    assert Tariff().get_tariff(1000) == 0

    with pytest.raises(
        AssertionError, match="plant power must be positive to compute tariff!"
    ):
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

    with pytest.raises(ValueError):
        result = economical_benefit_b(
            1000,
            datetime.date(2021, 12, 16),
            0,
            "THIS IS NOT A REGION",
            300,
        )


def test_optimal_sizing():
    result = optimal_sizing(
        1000,
        "Lazio",
        0.5,
    )

    # TODO: assert a precise value

    with pytest.raises(Exception, match="Input should be greater than 0"):
        optimal_sizing(-1000, "Lazio", 0.5)

    with pytest.raises(Exception, match="Input should be less than or equal to 1"):
        optimal_sizing(1000, "Lazio", 1.5)


def test_calculate_cogen_size():
    result = calculate_cogen_size_optimized(
        np.array([1000, 1000, 2000, 500, 500, 200, 1000, 3000, 1500, 1000])
    )
    assert result == 1000
