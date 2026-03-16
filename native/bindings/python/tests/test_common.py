# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
import pytest
from fdl.fdl_types import DimensionsFloat, DimensionsInt, PointFloat


@pytest.mark.parametrize(
    ("cls", "kwargs"),
    [
        (DimensionsInt, {"width": 1000, "height": 1000}),
        (DimensionsFloat, {"width": 1000.0, "height": 1000.0}),
    ],
)
def test_dimensions_init(cls, kwargs):
    dim = cls(**kwargs)
    assert dim.width == kwargs["width"]
    assert dim.height == kwargs["height"]


def test_dimensions_scale():
    # DimensionsFloat.scale returns DimensionsFloat
    dim_f = DimensionsFloat(width=1.0, height=2.0)
    result = dim_f.scale(2.0, 1.0)
    assert isinstance(result, DimensionsFloat)
    assert result.width == 2.0
    assert result.height == 4.0

    # DimensionsFloat.scale_by is in-place multiply
    dim_f2 = DimensionsFloat(width=1.1, height=2.2)
    dim_f2.scale_by(2)
    assert dim_f2.width == pytest.approx(2.2)
    assert dim_f2.height == pytest.approx(4.4)

    # Scale then round with explicit strategy
    dim_f3 = DimensionsFloat(width=1.0, height=2.0)
    scaled = dim_f3.scale(2.1, 1.0)
    rounded = scaled.round(even="whole", mode="up")
    assert (int(rounded.width), int(rounded.height)) == (3, 5)


def test_dimensions_duplicate():
    dim_1 = DimensionsFloat(width=1.1, height=2.2)
    dim_2 = dim_1.duplicate()
    assert dim_1 == dim_2
    assert dim_1.width.__class__ == dim_2.width.__class__
    assert id(dim_1) != id(dim_2)


@pytest.mark.parametrize(
    ("source_dim", "compare_dim", "expected"),
    [
        ({"width": 1920, "height": 1080}, {"width": 1921, "height": 1080}, False),
        ({"width": 1920, "height": 1080}, {"width": 1920, "height": 1081}, False),
        ({"width": 1920, "height": 1080}, {"width": 1920, "height": 1080}, True),
    ],
)
def test_dimensions_eq(source_dim, compare_dim, expected):
    assert (DimensionsInt(**source_dim) == DimensionsInt(**compare_dim)) is expected


@pytest.mark.parametrize(
    ("source_dim", "compare_dim", "expected"),
    [
        ({"width": 1920, "height": 1080}, {"width": 1921, "height": 1080}, False),
        ({"width": 1920, "height": 1080}, {"width": 1920, "height": 1081}, False),
        ({"width": 1920, "height": 1080}, {"width": 1921, "height": 1081}, False),
        ({"width": 1920, "height": 1080}, {"width": 1919, "height": 1080}, True),
        ({"width": 1920, "height": 1080}, {"width": 1920, "height": 1079}, True),
        ({"width": 1920, "height": 1080}, {"width": 1920, "height": 1080}, False),
    ],
)
def test_dimensions_gt(source_dim, compare_dim, expected):
    assert (DimensionsInt(**source_dim) > DimensionsInt(**compare_dim)) is expected


@pytest.mark.parametrize(
    ("source_dim", "compare_dim", "expected"),
    [
        ({"width": 1920, "height": 1080}, {"width": 1921, "height": 1080}, True),
        ({"width": 1920, "height": 1080}, {"width": 1920, "height": 1081}, True),
        ({"width": 1920, "height": 1080}, {"width": 1921, "height": 1081}, True),
        ({"width": 1920, "height": 1080}, {"width": 1919, "height": 1080}, False),
        ({"width": 1920, "height": 1080}, {"width": 1920, "height": 1079}, False),
        ({"width": 1920, "height": 1080}, {"width": 1920, "height": 1080}, False),
    ],
)
def test_dimensions_lt(source_dim, compare_dim, expected):
    assert (DimensionsInt(**source_dim) < DimensionsInt(**compare_dim)) is expected


def test_point_init():
    point_f = PointFloat(x=1000.0, y=1000.0)
    assert point_f.x.__class__ is float
    assert point_f.y.__class__ is float

    point_default = PointFloat()
    assert point_default.x == 0
    assert point_default.y == 0
