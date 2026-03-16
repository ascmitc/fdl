# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""Tests for FDL validation (C core semantic validators).

Ported from tests/test_fdlchecker.py to exercise validation through the
fdl bindings API (FDL.parse → .validate → FDLValidationError).
"""

from __future__ import annotations

import copy
import json

import pytest
from fdl.errors import FDLValidationError

from fdl import FDL

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Base FDL with protection dimensions (used by dimension hierarchy + others)
_BASE_WITH_PROTECTION = {
    "uuid": "12345678-1234-5678-1234-567812345678",
    "version": {"major": 2, "minor": 0},
    "fdl_creator": "Test",
    "default_framing_intent": "1",
    "framing_intents": [
        {
            "id": "1",
            "label": "Test Intent",
            "aspect_ratio": {"width": 16, "height": 9},
            "protection": 0.1,
        }
    ],
    "contexts": [
        {
            "label": "Test Context",
            "context_creator": "Test",
            "canvases": [
                {
                    "id": "1",
                    "label": "Test Canvas",
                    "source_canvas_id": "1",
                    "dimensions": {"width": 4096, "height": 2160},
                    "anamorphic_squeeze": 1.0,
                    "framing_decisions": [
                        {
                            "id": "1-1",
                            "label": "Test FD",
                            "framing_intent_id": "1",
                            "dimensions": {"width": 3000, "height": 1500},
                            "anchor_point": {"x": 100, "y": 100},
                            "protection_dimensions": {"width": 3500, "height": 1800},
                            "protection_anchor_point": {"x": 50, "y": 50},
                        }
                    ],
                }
            ],
        }
    ],
}

# Base FDL with effective + protection + framing anchors (for anchor hierarchy)
_BASE_WITH_EFFECTIVE = {
    "uuid": "12345678-1234-5678-1234-567812345678",
    "version": {"major": 2, "minor": 0},
    "fdl_creator": "Test",
    "default_framing_intent": "1",
    "framing_intents": [
        {
            "id": "1",
            "label": "Test Intent",
            "aspect_ratio": {"width": 16, "height": 9},
            "protection": 0.1,
        }
    ],
    "contexts": [
        {
            "label": "Test Context",
            "context_creator": "Test",
            "canvases": [
                {
                    "id": "1",
                    "label": "Test Canvas",
                    "source_canvas_id": "1",
                    "dimensions": {"width": 4096, "height": 2160},
                    "anamorphic_squeeze": 1.0,
                    "effective_dimensions": {"width": 3800, "height": 2000},
                    "effective_anchor_point": {"x": 100, "y": 80},
                    "framing_decisions": [
                        {
                            "id": "1-1",
                            "label": "Test FD",
                            "framing_intent_id": "1",
                            "dimensions": {"width": 3000, "height": 1500},
                            "anchor_point": {"x": 300, "y": 200},
                            "protection_dimensions": {"width": 3500, "height": 1800},
                            "protection_anchor_point": {"x": 200, "y": 150},
                        }
                    ],
                }
            ],
        }
    ],
}

# Simple base FDL without protection (for non-negative anchor + within-canvas tests)
_BASE_SIMPLE = {
    "uuid": "12345678-1234-5678-1234-567812345678",
    "version": {"major": 2, "minor": 0},
    "fdl_creator": "Test",
    "default_framing_intent": "1",
    "framing_intents": [
        {
            "id": "1",
            "label": "Test Intent",
            "aspect_ratio": {"width": 16, "height": 9},
        }
    ],
    "contexts": [
        {
            "label": "Test Context",
            "context_creator": "Test",
            "canvases": [
                {
                    "id": "1",
                    "label": "Test Canvas",
                    "source_canvas_id": "1",
                    "dimensions": {"width": 4096, "height": 2160},
                    "anamorphic_squeeze": 1.0,
                    "framing_decisions": [
                        {
                            "id": "1-1",
                            "label": "Test FD",
                            "framing_intent_id": "1",
                            "dimensions": {"width": 3840, "height": 2160},
                            "anchor_point": {"x": 100, "y": 50},
                        }
                    ],
                }
            ],
        }
    ],
}

# Small canvas base for anchors-within-canvas tests
_BASE_SMALL_CANVAS = {
    "uuid": "12345678-1234-5678-1234-567812345678",
    "version": {"major": 2, "minor": 0},
    "fdl_creator": "Test",
    "default_framing_intent": "1",
    "framing_intents": [
        {
            "id": "1",
            "label": "Test Intent",
            "aspect_ratio": {"width": 16, "height": 9},
        }
    ],
    "contexts": [
        {
            "label": "Test Context",
            "context_creator": "Test",
            "canvases": [
                {
                    "id": "1",
                    "label": "Test Canvas",
                    "source_canvas_id": "1",
                    "dimensions": {"width": 1920, "height": 1080},
                    "anamorphic_squeeze": 1.0,
                    "framing_decisions": [
                        {
                            "id": "1-1",
                            "label": "Test FD",
                            "framing_intent_id": "1",
                            "dimensions": {"width": 1600, "height": 900},
                            "anchor_point": {"x": 100, "y": 50},
                        }
                    ],
                }
            ],
        }
    ],
}


def _parse(data: dict) -> FDL:
    """Serialize a dict to JSON and parse via C core."""
    return FDL.parse(json.dumps(data).encode())


def _canvas(data: dict) -> dict:
    """Shortcut to the first canvas dict."""
    return data["contexts"][0]["canvases"][0]


def _fd(data: dict) -> dict:
    """Shortcut to the first framing decision dict."""
    return _canvas(data)["framing_decisions"][0]


# ---------------------------------------------------------------------------
# Dimension Hierarchy (canvas >= effective >= protection >= framing)
# ---------------------------------------------------------------------------


class TestDimensionHierarchy:
    def test_valid_fdl_passes(self):
        fdl = _parse(_BASE_WITH_PROTECTION)
        fdl.validate()  # should not raise

    def test_protection_exceeds_canvas_width(self):
        data = copy.deepcopy(_BASE_WITH_PROTECTION)
        _fd(data)["protection_dimensions"]["width"] = 5000
        fdl = _parse(data)
        with pytest.raises(FDLValidationError, match=r"(?i)protection.*canvas"):
            fdl.validate()

    def test_protection_exceeds_canvas_height(self):
        data = copy.deepcopy(_BASE_WITH_PROTECTION)
        _fd(data)["protection_dimensions"]["height"] = 3000
        fdl = _parse(data)
        with pytest.raises(FDLValidationError, match=r"(?i)protection"):
            fdl.validate()

    def test_framing_exceeds_protection_width(self):
        data = copy.deepcopy(_BASE_WITH_PROTECTION)
        _fd(data)["dimensions"]["width"] = 4000
        fdl = _parse(data)
        with pytest.raises(FDLValidationError, match=r"(?i)framing.*protection"):
            fdl.validate()

    def test_framing_exceeds_protection_height(self):
        data = copy.deepcopy(_BASE_WITH_PROTECTION)
        _fd(data)["dimensions"]["height"] = 2000
        fdl = _parse(data)
        with pytest.raises(FDLValidationError, match=r"(?i)framing"):
            fdl.validate()

    def test_framing_exceeds_canvas_without_protection(self):
        data = copy.deepcopy(_BASE_WITH_PROTECTION)
        del _fd(data)["protection_dimensions"]
        del _fd(data)["protection_anchor_point"]
        _fd(data)["dimensions"]["width"] = 5000
        fdl = _parse(data)
        with pytest.raises(FDLValidationError, match=r"(?i)framing.*canvas"):
            fdl.validate()

    def test_effective_exceeds_canvas(self):
        data = copy.deepcopy(_BASE_WITH_PROTECTION)
        _canvas(data)["effective_dimensions"] = {"width": 5000, "height": 2160}
        _canvas(data)["effective_anchor_point"] = {"x": 0, "y": 0}
        fdl = _parse(data)
        with pytest.raises(FDLValidationError, match=r"(?i)effective.*canvas"):
            fdl.validate()

    def test_protection_exceeds_effective(self):
        data = copy.deepcopy(_BASE_WITH_PROTECTION)
        _canvas(data)["effective_dimensions"] = {"width": 3000, "height": 1600}
        _canvas(data)["effective_anchor_point"] = {"x": 10, "y": 10}
        fdl = _parse(data)
        with pytest.raises(FDLValidationError, match=r"(?i)protection.*effective"):
            fdl.validate()

    def test_optional_fields_skipped_when_missing(self):
        data = copy.deepcopy(_BASE_WITH_PROTECTION)
        del _fd(data)["protection_dimensions"]
        del _fd(data)["protection_anchor_point"]
        fdl = _parse(data)
        fdl.validate()  # should not raise


# ---------------------------------------------------------------------------
# Anchor Hierarchy (outer <= inner)
# The C core does not have a dedicated anchor hierarchy validator, but its
# dimension hierarchy validator checks full regions (anchor + dimensions),
# so anchor hierarchy violations are caught as dimension hierarchy errors.
# ---------------------------------------------------------------------------


class TestAnchorHierarchy:
    def test_valid_anchor_hierarchy_passes(self):
        fdl = _parse(_BASE_WITH_EFFECTIVE)
        fdl.validate()  # should not raise

    def test_protection_anchor_outside_effective_x(self):
        data = copy.deepcopy(_BASE_WITH_EFFECTIVE)
        _fd(data)["protection_anchor_point"]["x"] = 50
        fdl = _parse(data)
        # Caught by dimension hierarchy (region check)
        with pytest.raises(FDLValidationError, match=r"(?i)is outside"):
            fdl.validate()

    def test_protection_anchor_outside_effective_y(self):
        data = copy.deepcopy(_BASE_WITH_EFFECTIVE)
        _fd(data)["protection_anchor_point"]["y"] = 50
        fdl = _parse(data)
        with pytest.raises(FDLValidationError, match=r"(?i)is outside"):
            fdl.validate()

    def test_framing_anchor_outside_protection_x(self):
        data = copy.deepcopy(_BASE_WITH_EFFECTIVE)
        _fd(data)["anchor_point"]["x"] = 100
        fdl = _parse(data)
        with pytest.raises(FDLValidationError, match=r"(?i)is outside"):
            fdl.validate()

    def test_framing_anchor_outside_protection_y(self):
        data = copy.deepcopy(_BASE_WITH_EFFECTIVE)
        _fd(data)["anchor_point"]["y"] = 100
        fdl = _parse(data)
        with pytest.raises(FDLValidationError, match=r"(?i)is outside"):
            fdl.validate()

    def test_framing_anchor_outside_effective_without_protection(self):
        data = copy.deepcopy(_BASE_WITH_EFFECTIVE)
        del _fd(data)["protection_dimensions"]
        del _fd(data)["protection_anchor_point"]
        _fd(data)["anchor_point"] = {"x": 50, "y": 50}
        fdl = _parse(data)
        with pytest.raises(FDLValidationError, match=r"(?i)is outside"):
            fdl.validate()

    def test_equal_anchors_valid(self):
        data = copy.deepcopy(_BASE_WITH_EFFECTIVE)
        _canvas(data)["effective_anchor_point"] = {"x": 100, "y": 100}
        _fd(data)["protection_anchor_point"] = {"x": 100, "y": 100}
        _fd(data)["anchor_point"] = {"x": 100, "y": 100}
        fdl = _parse(data)
        fdl.validate()  # should not raise


# ---------------------------------------------------------------------------
# Non-Negative Anchors
# ---------------------------------------------------------------------------


class TestNonNegativeAnchors:
    def test_valid_anchors_pass(self):
        fdl = _parse(_BASE_SIMPLE)
        fdl.validate()  # should not raise

    def test_negative_framing_anchor_x(self):
        data = copy.deepcopy(_BASE_SIMPLE)
        _fd(data)["anchor_point"]["x"] = -10
        fdl = _parse(data)
        # Schema validator catches minimum:0 constraint before semantic validators
        with pytest.raises(FDLValidationError, match=r"(?i)minimum.*0"):
            fdl.validate()

    def test_negative_framing_anchor_y(self):
        data = copy.deepcopy(_BASE_SIMPLE)
        _fd(data)["anchor_point"]["y"] = -5
        fdl = _parse(data)
        with pytest.raises(FDLValidationError, match=r"(?i)minimum.*0"):
            fdl.validate()

    def test_negative_protection_anchor_x(self):
        data = copy.deepcopy(_BASE_SIMPLE)
        _fd(data)["protection_dimensions"] = {"width": 3900, "height": 2100}
        _fd(data)["protection_anchor_point"] = {"x": -20, "y": 30}
        fdl = _parse(data)
        with pytest.raises(FDLValidationError, match=r"(?i)minimum.*0"):
            fdl.validate()

    def test_negative_protection_anchor_y(self):
        data = copy.deepcopy(_BASE_SIMPLE)
        _fd(data)["protection_dimensions"] = {"width": 3900, "height": 2100}
        _fd(data)["protection_anchor_point"] = {"x": 20, "y": -30}
        fdl = _parse(data)
        with pytest.raises(FDLValidationError, match=r"(?i)minimum.*0"):
            fdl.validate()

    def test_negative_effective_anchor_x(self):
        data = copy.deepcopy(_BASE_SIMPLE)
        _canvas(data)["effective_dimensions"] = {"width": 4000, "height": 2100}
        _canvas(data)["effective_anchor_point"] = {"x": -10, "y": 30}
        fdl = _parse(data)
        with pytest.raises(FDLValidationError, match=r"(?i)minimum.*0"):
            fdl.validate()

    def test_negative_effective_anchor_y(self):
        data = copy.deepcopy(_BASE_SIMPLE)
        _canvas(data)["effective_dimensions"] = {"width": 4000, "height": 2100}
        _canvas(data)["effective_anchor_point"] = {"x": 10, "y": -30}
        fdl = _parse(data)
        with pytest.raises(FDLValidationError, match=r"(?i)minimum.*0"):
            fdl.validate()

    def test_zero_anchors_valid(self):
        data = copy.deepcopy(_BASE_SIMPLE)
        _fd(data)["anchor_point"] = {"x": 0, "y": 0}
        fdl = _parse(data)
        fdl.validate()  # should not raise


# ---------------------------------------------------------------------------
# Anchors Within Canvas Bounds
# ---------------------------------------------------------------------------


class TestAnchorsWithinCanvas:
    def test_valid_anchors_within_canvas_pass(self):
        fdl = _parse(_BASE_SMALL_CANVAS)
        fdl.validate()  # should not raise

    def test_anchors_at_canvas_bounds_valid(self):
        data = copy.deepcopy(_BASE_SMALL_CANVAS)
        _fd(data)["anchor_point"] = {"x": 1920, "y": 1080}
        fdl = _parse(data)
        fdl.validate()  # should not raise

    def test_framing_anchor_exceeds_canvas_x(self):
        data = copy.deepcopy(_BASE_SMALL_CANVAS)
        _fd(data)["anchor_point"]["x"] = 2000
        fdl = _parse(data)
        with pytest.raises(FDLValidationError, match=r"(?i)exceeds.*canvas"):
            fdl.validate()

    def test_framing_anchor_exceeds_canvas_y(self):
        data = copy.deepcopy(_BASE_SMALL_CANVAS)
        _fd(data)["anchor_point"]["y"] = 1200
        fdl = _parse(data)
        with pytest.raises(FDLValidationError, match=r"(?i)exceeds.*canvas"):
            fdl.validate()

    def test_protection_anchor_exceeds_canvas_x(self):
        data = copy.deepcopy(_BASE_SMALL_CANVAS)
        _fd(data)["protection_dimensions"] = {"width": 1700, "height": 950}
        _fd(data)["protection_anchor_point"] = {"x": 2000, "y": 50}
        fdl = _parse(data)
        with pytest.raises(FDLValidationError, match=r"(?i)protection.*exceeds"):
            fdl.validate()

    def test_protection_anchor_exceeds_canvas_y(self):
        data = copy.deepcopy(_BASE_SMALL_CANVAS)
        _fd(data)["protection_dimensions"] = {"width": 1700, "height": 950}
        _fd(data)["protection_anchor_point"] = {"x": 50, "y": 1200}
        fdl = _parse(data)
        with pytest.raises(FDLValidationError, match=r"(?i)protection.*exceeds"):
            fdl.validate()

    def test_effective_anchor_exceeds_canvas_x(self):
        data = copy.deepcopy(_BASE_SMALL_CANVAS)
        _canvas(data)["effective_dimensions"] = {"width": 1800, "height": 1000}
        _canvas(data)["effective_anchor_point"] = {"x": 2000, "y": 40}
        fdl = _parse(data)
        with pytest.raises(FDLValidationError, match=r"(?i)effective.*exceeds"):
            fdl.validate()

    def test_effective_anchor_exceeds_canvas_y(self):
        data = copy.deepcopy(_BASE_SMALL_CANVAS)
        _canvas(data)["effective_dimensions"] = {"width": 1800, "height": 1000}
        _canvas(data)["effective_anchor_point"] = {"x": 60, "y": 1200}
        fdl = _parse(data)
        with pytest.raises(FDLValidationError, match=r"(?i)effective.*exceeds"):
            fdl.validate()


# ---------------------------------------------------------------------------
# ID Tree Validation
# ---------------------------------------------------------------------------


class TestIdTree:
    def test_duplicate_framing_intent_id(self):
        data = copy.deepcopy(_BASE_SIMPLE)
        data["framing_intents"].append(
            {
                "id": "1",  # Duplicate
                "label": "Duplicate Intent",
                "aspect_ratio": {"width": 16, "height": 9},
            }
        )
        fdl = _parse(data)
        with pytest.raises(FDLValidationError, match=r"(?i)duplicated"):
            fdl.validate()

    def test_invalid_framing_decision_id_format(self):
        data = copy.deepcopy(_BASE_SIMPLE)
        _fd(data)["id"] = "wrong-format"
        fdl = _parse(data)
        with pytest.raises(FDLValidationError, match=r"(?i)expected"):
            fdl.validate()

    def test_invalid_framing_intent_reference(self):
        data = copy.deepcopy(_BASE_SIMPLE)
        _fd(data)["framing_intent_id"] = "999"
        _fd(data)["id"] = "1-999"
        fdl = _parse(data)
        with pytest.raises(FDLValidationError, match=r"(?i)not in framing_intents"):
            fdl.validate()
