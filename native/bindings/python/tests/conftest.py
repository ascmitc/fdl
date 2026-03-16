# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
import tempfile
from pathlib import Path

import pytest
from fdl.canvas import Canvas
from fdl.context import Context
from fdl.fdl_types import DimensionsFloat, DimensionsInt, PointFloat
from fdl.framing_decision import FramingDecision
from fdl.framing_intent import FramingIntent
from fdl.testing import (
    SCENARIO_CONFIGS,
    build_test_params,
    get_scenario_test_id,
)

from fdl import DEFAULT_ROUNDING_STRATEGY, set_rounding


def pytest_configure(config):
    config.addinivalue_line("markers", "thread_safety: marks tests as thread-safety tests")


@pytest.fixture(autouse=True)
def _reset_rounding():
    """Reset the global rounding strategy after each test."""
    yield
    set_rounding(DEFAULT_ROUNDING_STRATEGY)


@pytest.fixture(autouse=True)
def _cleanup_temp_files():
    yield

    files = list(Path(tempfile.gettempdir()).glob("*.fdl"))
    files += Path(tempfile.gettempdir()).glob("*.yml")
    # Remove temp files (ignore PermissionError on Windows where parallel
    # workers may still hold a file lock)
    for file in files:
        try:
            file.unlink(missing_ok=True)
        except PermissionError:
            pass


@pytest.fixture
def sample_framing_intent_obj():
    return FramingIntent(
        label="1.78-1 Framing",
        id="FDLSMP03",
        aspect_ratio=DimensionsInt(width=16, height=9),
        protection=0.088,
    )


@pytest.fixture
def sample_framing_decision_obj():
    return FramingDecision(
        label="1.78-1 Framing",
        id="20220310-FDLSMP03",
        framing_intent_id="FDLSMP03",
        dimensions=DimensionsFloat(width=4728, height=3456),
        anchor_point=PointFloat(x=228, y=432),
        protection_dimensions=DimensionsFloat(width=5184, height=3790),
        protection_anchor_point=PointFloat(x=0, y=265),
    )


@pytest.fixture
def sample_canvas_obj():
    return Canvas(
        label="Open Gate RAW",
        id="20220310",
        source_canvas_id="20220310",
        dimensions=DimensionsInt(width=5184, height=4320),
        effective_dimensions=DimensionsInt(width=5184, height=4320),
        effective_anchor_point=PointFloat(x=0, y=0),
        photosite_dimensions=DimensionsInt(width=5184, height=4320),
        physical_dimensions=DimensionsFloat(width=25.92, height=21.60),
        anamorphic_squeeze=1.30,
    )


@pytest.fixture
def sample_context_obj():
    return Context(label="PanavisionDXL2", context_creator="ASC FDL Committee")


def pytest_generate_tests(metafunc):
    """
    Pytest hook to generate parameterized tests for template scenarios.

    Generates (scen_num, variant_letter) parameters for any test function
    that declares both 'scen_num' and 'variant_letter' fixtures.
    """
    if "scen_num" in metafunc.fixturenames and "variant_letter" in metafunc.fixturenames:
        params = [p for p in build_test_params() if not SCENARIO_CONFIGS[p[0]].is_error_test]
        ids = [get_scenario_test_id(p) for p in params]
        metafunc.parametrize("scen_num,variant_letter", params, ids=ids)
