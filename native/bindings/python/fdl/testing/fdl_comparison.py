# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
FDL comparison utilities for integration tests.

Extracted from tests/utils.py:run_template_test for reuse in UI tests.
"""

import math
import unittest

from fdl.fdl_types import _FP_ABS_TOL, _FP_REL_TOL


class FDLComparison:
    """
    Assertion-based FDL comparison utilities.

    Provides methods to compare FDL objects field-by-field with clear
    error messages for mismatches.

    Parameters
    ----------
    test_case : unittest.TestCase, optional
        TestCase instance for assertion methods. If not provided,
        uses plain assert statements.
    """

    def __init__(self, test_case: unittest.TestCase | None = None):
        """
        Initialize with optional TestCase for assertion methods.

        Parameters
        ----------
        test_case : unittest.TestCase, optional
            If provided, uses TestCase.assertEqual for better error messages.
        """
        self.test_case = test_case

    def _assertEqual(self, expected, actual, msg: str):
        """
        Use TestCase.assertEqual if available, else plain assert.

        Parameters
        ----------
        expected : Any
            Expected value.
        actual : Any
            Actual value.
        msg : str
            Error message on mismatch.
        """
        if self.test_case:
            self.test_case.assertEqual(expected, actual, msg)
        else:
            assert expected == actual, f"{msg}: expected {expected}, got {actual}"

    def _assertAlmostEqual(self, expected: float, actual: float, msg: str):
        """
        Tolerance-aware float comparison using project FP tolerances.

        Parameters
        ----------
        expected : float
            Expected value.
        actual : float
            Actual value.
        msg : str
            Error message on mismatch.
        """
        close = math.isclose(expected, actual, rel_tol=_FP_REL_TOL, abs_tol=_FP_ABS_TOL)
        if self.test_case:
            self.test_case.assertTrue(close, f"{msg}: expected {expected}, got {actual}")
        else:
            assert close, f"{msg}: expected {expected}, got {actual}"

    def _fail(self, msg: str):
        """Raise an assertion failure."""
        if self.test_case:
            self.test_case.fail(msg)
        else:
            raise AssertionError(msg)

    def compare_custom_attrs(self, expected_obj, actual_obj, prefix: str = ""):
        """
        Compare all custom attributes between two FDL objects.

        Iterates every custom attribute on both objects and asserts that
        they have the same keys with matching values. Uses tolerance-aware
        comparison for bare ``float`` values; compound types
        (``DimensionsFloat``, ``PointFloat``, etc.) use their own
        tolerance-aware ``__eq__``.

        Parameters
        ----------
        expected_obj : Any
            Expected FDL object with a ``.custom_attrs`` property.
        actual_obj : Any
            Actual FDL object with a ``.custom_attrs`` property.
        prefix : str
            Label prefix for error messages (e.g. ``"canvas"``).
        """
        expected_attrs = expected_obj.custom_attrs
        actual_attrs = actual_obj.custom_attrs

        expected_keys = set(expected_attrs.keys())
        actual_keys = set(actual_attrs.keys())

        missing = expected_keys - actual_keys
        extra = actual_keys - expected_keys

        if missing:
            self._fail(f"{prefix} custom attrs: missing keys {sorted(missing)}")
        if extra:
            self._fail(f"{prefix} custom attrs: unexpected keys {sorted(extra)}")

        for key in sorted(expected_keys & actual_keys):
            expected_val = expected_attrs[key]
            actual_val = actual_attrs[key]
            label = f"{prefix}.custom_attrs['{key}']"

            if isinstance(expected_val, float) and isinstance(actual_val, float):
                self._assertAlmostEqual(expected_val, actual_val, f"{label} mismatch")
            else:
                self._assertEqual(expected_val, actual_val, f"{label} mismatch")

    def compare_context(self, expected_ctx, actual_ctx):
        """
        Compare context fields.

        Compares: label, context_creator, clip_id

        Parameters
        ----------
        expected_ctx : Context
            Expected context object.
        actual_ctx : Context
            Actual context object.
        """
        self._assertEqual(expected_ctx.label, actual_ctx.label, "context.label mismatch")
        self._assertEqual(expected_ctx.context_creator, actual_ctx.context_creator, "context.context_creator mismatch")
        # clip_id is optional, only compare if present
        expected_clip_id = getattr(expected_ctx, "clip_id", None)
        actual_clip_id = getattr(actual_ctx, "clip_id", None)
        self._assertEqual(expected_clip_id, actual_clip_id, "context.clip_id mismatch")
        self.compare_custom_attrs(expected_ctx, actual_ctx, "context")

    def compare_canvas(
        self,
        expected_canvas,
        actual_canvas,
        expected_id: str | None = None,
    ):
        """
        Compare canvas fields.

        Compares: id (optional), source_canvas_id, label, dimensions,
        effective_dimensions, effective_anchor_point, photosite_dimensions,
        physical_dimensions, anamorphic_squeeze

        Parameters
        ----------
        expected_canvas : Canvas
            Expected canvas object.
        actual_canvas : Canvas
            Actual canvas object.
        expected_id : str, optional
            If provided, validates canvas.id matches this value.
        """
        if expected_id:
            self._assertEqual(expected_id, actual_canvas.id, "canvas.id mismatch")

        self._assertEqual(expected_canvas.source_canvas_id, actual_canvas.source_canvas_id, "canvas.source_canvas_id mismatch")
        self._assertEqual(expected_canvas.label, actual_canvas.label, "canvas.label mismatch")
        self._assertEqual(expected_canvas.dimensions, actual_canvas.dimensions, "canvas.dimensions mismatch")
        self._assertEqual(expected_canvas.effective_dimensions, actual_canvas.effective_dimensions, "canvas.effective_dimensions mismatch")
        self._assertEqual(
            expected_canvas.effective_anchor_point, actual_canvas.effective_anchor_point, "canvas.effective_anchor_point mismatch"
        )
        self._assertEqual(expected_canvas.photosite_dimensions, actual_canvas.photosite_dimensions, "canvas.photosite_dimensions mismatch")
        self._assertEqual(expected_canvas.physical_dimensions, actual_canvas.physical_dimensions, "canvas.physical_dimensions mismatch")
        self._assertEqual(expected_canvas.anamorphic_squeeze, actual_canvas.anamorphic_squeeze, "canvas.anamorphic_squeeze mismatch")
        self.compare_custom_attrs(expected_canvas, actual_canvas, "canvas")

    def compare_framing_decision(
        self,
        expected_fd,
        actual_fd,
        expected_id: str | None = None,
    ):
        """
        Compare framing decision fields.

        Compares: id (optional), framing_intent_id, label, dimensions,
        anchor_point, protection_dimensions, protection_anchor_point

        Parameters
        ----------
        expected_fd : FramingDecision
            Expected framing decision object.
        actual_fd : FramingDecision
            Actual framing decision object.
        expected_id : str, optional
            If provided, validates framing_decision.id matches this value.
        """
        if expected_id:
            self._assertEqual(expected_id, actual_fd.id, "framing_decision.id mismatch")

        self._assertEqual(expected_fd.framing_intent_id, actual_fd.framing_intent_id, "framing_decision.framing_intent_id mismatch")
        self._assertEqual(expected_fd.label, actual_fd.label, "framing_decision.label mismatch")
        self._assertEqual(expected_fd.dimensions, actual_fd.dimensions, "framing_decision.dimensions mismatch")
        self._assertEqual(expected_fd.anchor_point, actual_fd.anchor_point, "framing_decision.anchor_point mismatch")
        self._assertEqual(
            expected_fd.protection_dimensions, actual_fd.protection_dimensions, "framing_decision.protection_dimensions mismatch"
        )
        self._assertEqual(
            expected_fd.protection_anchor_point, actual_fd.protection_anchor_point, "framing_decision.protection_anchor_point mismatch"
        )
        self.compare_custom_attrs(expected_fd, actual_fd, "framing_decision")

    def compare_canvas_template(self, expected_tmpl, actual_tmpl):
        """
        Compare canvas template fields.

        Compares: id, target_dimensions, target_anamorphic_squeeze, fit_source,
        fit_method, label, alignment_method_vertical, alignment_method_horizontal,
        preserve_from_source_canvas, maximum_dimensions, pad_to_maximum, round

        Parameters
        ----------
        expected_tmpl : CanvasTemplate
            Expected canvas template object.
        actual_tmpl : CanvasTemplate
            Actual canvas template object.
        """
        self._assertEqual(expected_tmpl.id, actual_tmpl.id, "template.id mismatch")
        self._assertEqual(expected_tmpl.target_dimensions, actual_tmpl.target_dimensions, "template.target_dimensions mismatch")
        self._assertEqual(
            expected_tmpl.target_anamorphic_squeeze, actual_tmpl.target_anamorphic_squeeze, "template.target_anamorphic_squeeze mismatch"
        )
        self._assertEqual(expected_tmpl.fit_source, actual_tmpl.fit_source, "template.fit_source mismatch")
        self._assertEqual(expected_tmpl.fit_method, actual_tmpl.fit_method, "template.fit_method mismatch")
        self._assertEqual(expected_tmpl.label, actual_tmpl.label, "template.label mismatch")
        self._assertEqual(
            expected_tmpl.alignment_method_vertical, actual_tmpl.alignment_method_vertical, "template.alignment_method_vertical mismatch"
        )
        self._assertEqual(
            expected_tmpl.alignment_method_horizontal,
            actual_tmpl.alignment_method_horizontal,
            "template.alignment_method_horizontal mismatch",
        )
        self._assertEqual(
            expected_tmpl.preserve_from_source_canvas,
            actual_tmpl.preserve_from_source_canvas,
            "template.preserve_from_source_canvas mismatch",
        )
        self._assertEqual(expected_tmpl.maximum_dimensions, actual_tmpl.maximum_dimensions, "template.maximum_dimensions mismatch")
        self._assertEqual(expected_tmpl.pad_to_maximum, actual_tmpl.pad_to_maximum, "template.pad_to_maximum mismatch")
        # Compare round sub-object
        self._assertEqual(expected_tmpl.round.even, actual_tmpl.round.even, "template.round.even mismatch")
        self._assertEqual(expected_tmpl.round.mode, actual_tmpl.round.mode, "template.round.mode mismatch")
        self.compare_custom_attrs(expected_tmpl, actual_tmpl, "template")

    def compare_framing_intent(self, expected_fi, actual_fi, index: int = 0):
        """
        Compare framing intent fields.

        Compares: id, label, aspect_ratio, protection

        Parameters
        ----------
        expected_fi : FramingIntent
            Expected framing intent object.
        actual_fi : FramingIntent
            Actual framing intent object.
        index : int
            Index for error message context.
        """
        prefix = f"framing_intents[{index}]"
        self._assertEqual(expected_fi.id, actual_fi.id, f"{prefix}.id mismatch")
        self._assertEqual(expected_fi.label, actual_fi.label, f"{prefix}.label mismatch")
        self._assertEqual(expected_fi.aspect_ratio, actual_fi.aspect_ratio, f"{prefix}.aspect_ratio mismatch")
        self._assertAlmostEqual(expected_fi.protection, actual_fi.protection, f"{prefix}.protection mismatch")

    def compare_framing_intents(self, expected_fdl, actual_fdl):
        """
        Compare all framing intents and default_framing_intent between two FDLs.

        Parameters
        ----------
        expected_fdl : FDL
            Expected FDL object.
        actual_fdl : FDL
            Actual FDL object.
        """
        self._assertEqual(
            expected_fdl.default_framing_intent,
            actual_fdl.default_framing_intent,
            "default_framing_intent mismatch",
        )
        expected_fis = list(expected_fdl.framing_intents)
        actual_fis = list(actual_fdl.framing_intents)
        self._assertEqual(len(expected_fis), len(actual_fis), "framing_intents count mismatch")
        for i, (expected_fi, actual_fi) in enumerate(zip(expected_fis, actual_fis)):
            self.compare_framing_intent(expected_fi, actual_fi, index=i)

    def compare_fdl_output(
        self,
        expected_fdl,
        actual_fdl,
        context_label: str,
        canvas_label: str,
    ):
        """
        Compare full FDL output after transformation.

        Finds matching context/canvas by label and compares all fields.

        Parameters
        ----------
        expected_fdl : FDL
            Expected FDL object (from reference file).
        actual_fdl : FDL
            Actual FDL object (from transformation).
        context_label : str
            Label (or partial label) to identify the context.
        canvas_label : str
            Label (or partial label) to identify the canvas.
        """
        # Find expected context
        expected_ctx = None
        for ctx in expected_fdl.contexts:
            if ctx.label == context_label or context_label in ctx.label:
                expected_ctx = ctx
                break
        assert expected_ctx is not None, f"Expected context '{context_label}' not found"

        # Find expected canvas
        expected_canvas = None
        for canvas in expected_ctx.canvases:
            if canvas.label == canvas_label or canvas_label in canvas.label:
                expected_canvas = canvas
                break
        assert expected_canvas is not None, f"Expected canvas '{canvas_label}' not found"

        # Find actual canvas (match by dimensions since labels may differ)
        actual_canvas = None
        for ctx in actual_fdl.contexts:
            for canvas in ctx.canvases:
                if (
                    canvas.dimensions.width == expected_canvas.dimensions.width
                    and canvas.dimensions.height == expected_canvas.dimensions.height
                ):
                    actual_canvas = canvas
                    break
            if actual_canvas:
                break
        assert actual_canvas is not None, "Matching actual canvas not found"

        # Compare canvas
        self.compare_canvas(expected_canvas, actual_canvas)

        # Compare first framing decision if present
        if expected_canvas.framing_decisions and actual_canvas.framing_decisions:
            self.compare_framing_decision(expected_canvas.framing_decisions[0], actual_canvas.framing_decisions[0])
