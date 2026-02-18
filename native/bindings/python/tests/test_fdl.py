# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path

import pytest
from fdl.context import Context
from fdl.errors import FDLValidationError
from fdl.fdl import FDL
from fdl.fdl_types import DimensionsFloat, DimensionsInt, PointFloat

from fdl import read_from_file, read_from_string

SAMPLE_FDL_DIR = Path(__file__).parent.joinpath("sample_data")
SAMPLE_FDL_FILE = Path(SAMPLE_FDL_DIR, "Scenario-9__FDL_DeliveredToVFXVendor.fdl")


def test_read_from_file_unvalidated():
    result = read_from_file(SAMPLE_FDL_FILE, validate=False)

    assert isinstance(result, FDL)


def test_read_from_file_validated():
    result = read_from_file(SAMPLE_FDL_FILE, validate=True)

    assert isinstance(result, FDL)


def test_read_from_string():
    raw = SAMPLE_FDL_FILE.read_text(encoding="utf-8")
    result = read_from_string(raw)
    assert isinstance(result, FDL)
    assert result.as_dict()


def test_write_to_file(tmp_path):
    my_path = Path(tmp_path, "myfdl.fdl")
    fdl1 = read_from_file(SAMPLE_FDL_FILE)

    my_path.write_text(fdl1.as_json(), encoding="utf-8")
    fdl2 = read_from_file(my_path)

    assert fdl1.as_dict() == fdl2.as_dict()


def test_write_to_string():
    raw = SAMPLE_FDL_FILE.read_text(encoding="utf-8")
    result = read_from_string(raw)

    json_str = result.as_json()
    roundtripped = FDL.parse(json_str.encode("utf-8"))
    assert roundtripped.as_dict() == result.as_dict()


def test_init_empty_fdl():
    result = FDL()
    assert isinstance(result, FDL)


def test_setting_default_framing_id():
    my_fdl = FDL()

    fi = my_fdl.add_framing_intent(
        id="FDLSMP03",
        label="1.78-1 Framing",
        aspect_ratio=DimensionsInt(width=16, height=9),
        protection=0.088,
    )
    my_fdl.default_framing_intent = fi.id
    assert my_fdl.default_framing_intent == fi.id

    my_fdl.default_framing_intent = "nogood"
    with pytest.raises(FDLValidationError, match="nogood"):
        my_fdl.validate()


def test_add_canvas_to_context():
    my_fdl = FDL()
    ctx = my_fdl.add_context(label="PanavisionDXL2", context_creator="ASC FDL Committee")

    canvas = ctx.add_canvas(
        id="20220310",
        label="Open Gate RAW",
        source_canvas_id="20220310",
        dimensions=DimensionsInt(width=5184, height=4320),
        anamorphic_squeeze=1.30,
    )

    assert ctx.canvases.get_by_id("20220310") == canvas
    assert len(ctx.canvases) == 1

    # Add a second context and verify it gets its own canvas
    ctx2 = my_fdl.add_context(label="SecondContext")
    assert isinstance(ctx2, Context)
    canvas2 = ctx2.add_canvas(
        id="20220310",
        label="Open Gate RAW",
        source_canvas_id="20220310",
        dimensions=DimensionsInt(width=5184, height=4320),
        anamorphic_squeeze=1.30,
    )
    assert ctx2.canvases.get_by_id("20220310") == canvas2


def test_validate_schema_rule():
    my_fdl = FDL()

    # id too long violates JSON schema (maxLength: 32) — caught by C core schema validation
    my_fdl.add_framing_intent(
        id="x" * 33,
        label="test",
        aspect_ratio=DimensionsInt(width=16, height=9),
        protection=0.0,
    )
    with pytest.raises(FDLValidationError):
        my_fdl.validate()


def test_validate_missing_source_framing_intent():
    my_fdl = FDL()
    ctx = my_fdl.add_context(label="test")
    canvas = ctx.add_canvas(
        id="20220310",
        label="Open Gate RAW",
        source_canvas_id="20220310",
        dimensions=DimensionsInt(width=5184, height=4320),
        anamorphic_squeeze=1.0,
    )

    # Framing decision references intent "FDLSMP03" which is NOT in the doc's framing_intents
    canvas.add_framing_decision(
        id="fd1",
        label="1.78-1 Framing",
        framing_intent_id="FDLSMP03",
        dimensions=DimensionsFloat(width=4728.0, height=3456.0),
        anchor_point=PointFloat(x=228.0, y=432.0),
    )
    with pytest.raises(FDLValidationError):
        my_fdl.validate()


def test_validate_missing_source_canvas_id():
    my_fdl = FDL()
    ctx = my_fdl.add_context(label="test")

    # Canvas references source_canvas_id="shouldnotbethere" which doesn't exist
    ctx.add_canvas(
        id="20220310",
        label="Open Gate RAW",
        source_canvas_id="shouldnotbethere",
        dimensions=DimensionsInt(width=5184, height=4320),
        anamorphic_squeeze=1.0,
    )
    with pytest.raises(FDLValidationError):
        my_fdl.validate()
