# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
import pytest
from fdl.errors import FDLValidationError
from fdl.fdl import FDL
from fdl.fdl_types import DimensionsFloat, DimensionsInt, PointFloat


def test_source_canvas_id_valid():
    """A canvas whose source_canvas_id refers to itself passes validation."""
    my_fdl = FDL.create(uuid="00000000-0000-0000-0000-000000000001")
    fi = my_fdl.add_framing_intent(
        id="FI1",
        label="1.78-1",
        aspect_ratio=DimensionsInt(width=16, height=9),
        protection=0.0,
    )
    ctx = my_fdl.add_context("context1")
    canvas = ctx.add_canvas(
        id="20220310",
        label="Open Gate RAW",
        source_canvas_id="20220310",
        dimensions=DimensionsInt(width=5184, height=4320),
        anamorphic_squeeze=1.30,
    )
    canvas.add_framing_decision(
        id="20220310-FI1",
        label="1.78-1",
        framing_intent_id=fi.id,
        dimensions=DimensionsFloat(width=5184, height=4320),
        anchor_point=PointFloat(x=0, y=0),
    )
    my_fdl.validate()


def test_source_canvas_id_invalid():
    """Validation catches a source_canvas_id that doesn't exist."""
    my_fdl = FDL.create(uuid="00000000-0000-0000-0000-000000000002")
    fi = my_fdl.add_framing_intent(
        id="FI1",
        label="1.78-1",
        aspect_ratio=DimensionsInt(width=16, height=9),
        protection=0.0,
    )
    ctx = my_fdl.add_context("context1")
    canvas = ctx.add_canvas(
        id="456",
        label="Open Gate RAW",
        source_canvas_id="123",  # doesn't exist
        dimensions=DimensionsInt(width=5184, height=4320),
        anamorphic_squeeze=1.30,
    )
    canvas.add_framing_decision(
        id="456-FI1",
        label="1.78-1",
        framing_intent_id=fi.id,
        dimensions=DimensionsFloat(width=5184, height=4320),
        anchor_point=PointFloat(x=0, y=0),
    )

    with pytest.raises(FDLValidationError) as err:
        my_fdl.validate()

    assert "123" in str(err)


def test_add_framing_decision(sample_canvas_obj):
    """Framing decisions can be added to a canvas and retrieved by id."""
    canvas = sample_canvas_obj
    fd = canvas.add_framing_decision(
        id="20220310-FDLSMP03",
        label="1.78-1 Framing",
        framing_intent_id="FDLSMP03",
        dimensions=DimensionsFloat(width=4728, height=3456),
        anchor_point=PointFloat(x=228, y=432),
    )

    assert fd.id == "20220310-FDLSMP03"
    assert fd.label == "1.78-1 Framing"
    assert fd.framing_intent_id == "FDLSMP03"
    assert fd.dimensions == DimensionsFloat(width=4728, height=3456)
    assert fd.anchor_point == PointFloat(x=228, y=432)

    found = canvas.framing_decisions.get_by_id("20220310-FDLSMP03")
    assert found is not None
    assert found.id == fd.id


def test_set_effective(sample_canvas_obj):
    """Effective dimensions and anchor point can be set and read back."""
    canvas = sample_canvas_obj

    # Verify initial effective values
    assert canvas.effective_dimensions == DimensionsInt(width=5184, height=4320)
    assert canvas.effective_anchor_point == PointFloat(x=0, y=0)

    # Set new effective values
    canvas.set_effective(
        dims=DimensionsInt(width=3840, height=2160),
        anchor=PointFloat(x=10, y=20),
    )

    assert canvas.effective_dimensions == DimensionsInt(width=3840, height=2160)
    assert canvas.effective_anchor_point == PointFloat(x=10, y=20)

    # Reset to zero anchor
    canvas.set_effective(
        dims=DimensionsInt(width=3840, height=2160),
        anchor=PointFloat(x=0, y=0),
    )

    assert canvas.effective_anchor_point == PointFloat(x=0, y=0)
