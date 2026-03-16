# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
import pytest
from fdl.fdl_types import DimensionsFloat
from fdl.rounding import RoundStrategy

from fdl import DEFAULT_ROUNDING_STRATEGY, get_rounding, set_rounding


@pytest.fixture(autouse=True)
def _reset_rounding():
    """Reset the global rounding strategy after each test."""
    yield
    set_rounding(DEFAULT_ROUNDING_STRATEGY)


def test_set_rounding_strategy():
    assert get_rounding() == DEFAULT_ROUNDING_STRATEGY

    override = RoundStrategy(even="whole", mode="up")
    set_rounding(override)
    assert get_rounding() == override


def test_rounding_strategy_validation():
    """Invalid rounding enum values are rejected when used."""
    dim = DimensionsFloat(width=19, height=79)

    rs_bad_even = RoundStrategy(even="wrong", mode="up")
    with pytest.raises(KeyError):
        dim.round(rs_bad_even.even, rs_bad_even.mode)

    rs_bad_mode = RoundStrategy(even="even", mode="wrong")
    with pytest.raises(KeyError):
        dim.round(rs_bad_mode.even, rs_bad_mode.mode)


@pytest.mark.parametrize(
    ("rules", "dimensions", "expected"),
    [
        ({"even": "even", "mode": "up"}, {"width": 19, "height": 79}, (20, 80)),
        ({"even": "even", "mode": "down"}, {"width": 19, "height": 79}, (18, 78)),
        ({"even": "even", "mode": "round"}, {"width": 19, "height": 79}, (20, 80)),
        ({"even": "even", "mode": "round"}, {"width": 19.456, "height": 79.456}, (20, 80)),
        ({"even": "whole", "mode": "up"}, {"width": 19.5, "height": 79.5}, (20, 80)),
        ({"even": "whole", "mode": "down"}, {"width": 19.5, "height": 79.5}, (19, 79)),
        ({"even": "whole", "mode": "round"}, {"width": 19.5, "height": 79.5}, (20, 80)),
        ({"even": "whole", "mode": "round"}, {"width": 19.456, "height": 79.456}, (19, 79)),
    ],
)
def test_rounding_strategy_rounding(rules, dimensions, expected):
    rnd = RoundStrategy(**rules)
    dim = DimensionsFloat(**dimensions)
    result = dim.round(rnd.even, rnd.mode)

    assert (result.width, result.height) == expected
