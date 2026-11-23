# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Reusable template scenario tests for FDL.

Classes:
    TestFDLTemplatesParameterized — exercises all template scenarios (1-32,
        excluding error tests 21-22). Uses composition with BaseFDLTestCase
        and extensibility hooks so that higher layers (imaging, Nuke) can
        inherit and add their own checks.

    TestScenarioErrorValidation — every scenario flagged is_error_test (21-22),
        driven generically from the ScenarioConfig error_* fields.

    TestFitSourceValidation — fit_source effective_dimensions path validation.

    TestPreserveFromSourceCanvasValidation — preserve_from_source_canvas
        effective_dimensions path validation.

Usage at the fdl level:
    from fdl.testing.template_tests import TestFDLTemplatesParameterized  # noqa: F401
    from fdl.testing.template_tests import TestScenarioErrorValidation  # noqa: F401
    from fdl.testing.template_tests import TestFitSourceValidation  # noqa: F401
    from fdl.testing.template_tests import TestPreserveFromSourceCanvasValidation  # noqa: F401

Usage at a higher layer (e.g. Nuke):
    from fdl.testing.template_tests import TestFDLTemplatesParameterized as _FDLBase

    class TestFDLTemplatesParameterized(_FDLBase):
        def _create_test_case(self):
            return NukeBaseFDLTestCase()

        def _build_run_kwargs(self, config, variant, paths, test_name):
            kwargs = super()._build_run_kwargs(config, variant, paths, test_name)
            kwargs["input_dims"] = variant.input_dims
            kwargs["source_image"] = paths["source_tif"]
            return kwargs
"""

from pathlib import Path

import pytest

from fdl.testing.base import BaseFDLTestCase
from fdl.testing.scenario_config import (
    SCENARIO_CONFIGS,
    ScenarioConfig,
    SourceVariant,
    get_scenario_paths,
    get_template_path,
    get_variant_by_letter,
)


class TestFDLTemplatesParameterized:
    """
    Parameterized tests for scenarios 1-32 (excluding error tests 21-22).

    Pure FDL tests: loads FDLs, applies templates, compares results.
    No image processing, no Nuke script generation.

    Uses composition with BaseFDLTestCase for shared test infrastructure.
    Subclass this and override _create_test_case() and _build_run_kwargs()
    to add imaging or Nuke-specific checks at higher layers.
    """

    def _create_test_case(self) -> BaseFDLTestCase:
        """Create the test case helper. Override in subclasses for extended test cases."""
        return BaseFDLTestCase()

    def setup_method(self, method):
        """Setup test case helper for each test."""
        self._test_case = self._create_test_case()
        self._test_case.setUp()
        self._test_case.maxDiff = None

    def teardown_method(self, method):
        """Tear down test case helper."""
        if hasattr(self, "_test_case"):
            self._test_case.tearDown()

    def _get_resources_folder(self) -> Path:
        """Get resources folder. Delegates to BaseFDLTestCase."""
        return BaseFDLTestCase.get_resources_folder()

    def _build_run_kwargs(self, config: ScenarioConfig, variant: SourceVariant, paths: dict, test_name: str) -> dict:
        """
        Build kwargs for run_template_test. Override to add extra params.

        Returns dict of keyword arguments for self._test_case.run_template_test().
        Subclasses should call super() and add imaging/Nuke params to the result.
        """
        context_label = variant.context_label if variant.context_label else config.context_label
        canvas_label = variant.canvas_label if variant.canvas_label else config.canvas_label

        return {
            "canvas_label": canvas_label,
            "context_creator": config.context_creator,
            "context_label": context_label,
            "expected_fdl_path": paths["expected_fdl"],
            "framing_intent_id": config.framing_intent_id,
            "source_fdl_path": paths["source_fdl"],
            "template_fdl_path": paths["template"],
            "template_label": config.template_label,
            "test_name": test_name,
        }

    def test_apply_fdl_template(self, scen_num, variant_letter):
        """
        Test FDL template transformation for a scenario/variant.

        Parameters
        ----------
        scen_num : int
            Scenario number (1-32, excluding 21-22).
        variant_letter : str
            Variant identifier (e.g., "B", "D", "G").
        """
        config = SCENARIO_CONFIGS[scen_num]
        variant = get_variant_by_letter(config, variant_letter)
        assert variant is not None, f"Variant {variant_letter} not found in scenario {scen_num}"

        # Get all paths for this scenario/variant
        sample_files_dir = self._get_resources_folder() / "Scenarios_For_Implementers"
        paths = get_scenario_paths(sample_files_dir, config, variant)

        # Build test name (use custom suffix if defined, otherwise use lowercase letter)
        suffix = variant.test_name_suffix if variant.test_name_suffix else variant_letter.lower()
        test_name = f"test_apply_fdl_template_scen{scen_num}_{suffix}"

        # Set the test method name on the test case instance for proper output naming
        self._test_case._testMethodName = test_name

        # Verify required files exist
        assert paths["template"].exists(), f"Template FDL not found: {paths['template']}"
        assert paths["source_fdl"].exists(), f"Source FDL not found: {paths['source_fdl']}"

        # Build kwargs and run
        kwargs = self._build_run_kwargs(config, variant, paths, test_name)
        self._test_case.run_template_test(**kwargs)


# ---------------------------------------------------------------------------
# Error validation tests (scenarios 21-22)
# ---------------------------------------------------------------------------


class _ErrorValidationBase:
    """Shared setup/teardown for error validation test classes."""

    def setup_method(self, method):
        self._tc = BaseFDLTestCase()
        self._tc.setUp()
        self._tc.maxDiff = None

    def teardown_method(self, method):
        if hasattr(self, "_tc"):
            self._tc.tearDown()

    def _resources(self) -> Path:
        return BaseFDLTestCase.get_resources_folder()

    def _load_source_components(self, config: ScenarioConfig | None = None):
        """Load the source FDL used by error tests (defaults from ScenarioConfig error_* fields)."""
        config = config or next(c for c in SCENARIO_CONFIGS.values() if c.is_error_test)
        source_fdl_path = self._resources() / config.error_source_fdl
        assert source_fdl_path.exists(), f"Source FDL not found: {source_fdl_path}"

        source_fdl, error = self._tc.load_fdl_with_validation(source_fdl_path)
        assert error is None, f"Source FDL validation failed: {error}"

        context = self._tc.get_component_from_fdl(source_fdl, "context", label=config.error_source_context_label)
        assert context is not None, f"Context '{config.error_source_context_label}' not found"

        canvas = self._tc.get_component_from_fdl(source_fdl, "canvas", label=config.error_source_canvas_label, context=context)
        assert canvas is not None, f"Canvas '{config.error_source_canvas_label}' not found"

        fd = self._tc.get_component_from_fdl(source_fdl, "framing_decision", canvas=canvas, framing_intent_id=config.framing_intent_id)
        assert fd is not None, f"Framing decision with intent_id '{config.framing_intent_id}' not found"

        return context, canvas, fd


ERROR_SCENARIO_NUMBERS = sorted(n for n, c in SCENARIO_CONFIGS.items() if c.is_error_test)


class TestScenarioErrorValidation(_ErrorValidationBase):
    """
    Scenarios flagged ``is_error_test`` (currently 21-22), driven from config.

    Applies the scenario's template to its configured source and verifies a
    ValueError mentioning ``error_match`` is raised.
    """

    @pytest.mark.parametrize("scen_num", ERROR_SCENARIO_NUMBERS, ids=lambda n: f"scen{n}")
    def test_template_apply_raises(self, scen_num):
        config = SCENARIO_CONFIGS[scen_num]
        template_path = get_template_path(self._resources() / "Scenarios_For_Implementers", config)
        assert template_path.exists(), f"Template FDL not found: {template_path}"

        template_fdl, error = self._tc.load_fdl_with_validation(template_path)
        assert error is None, f"Template FDL validation failed: {error}"

        template = self._tc.get_component_from_fdl(template_fdl, "template", label=config.template_label)
        assert template is not None, f"Template '{config.template_label}' not found"

        context, canvas, fd = self._load_source_components(config)
        assert fd.protection_dimensions is None, "Source should have no protection_dimensions"

        with pytest.raises(ValueError, match=config.error_match):
            template.apply(
                source_canvas=canvas,
                source_framing=fd,
                new_fd_name="",
                new_canvas_id="test",
                source_context_label=context.label,
                context_creator=config.context_creator,
            )


class TestFitSourceValidation(_ErrorValidationBase):
    """
    Scenario 21: fit_source path validation.

    Verifies that ValueError is raised when a template's fit_source
    references a path that doesn't exist in the source FDL.
    """

    def test_fit_source_effective_dimensions_missing(self):
        """ValueError when fit_source references effective_dimensions but source has none."""
        from fdl import CanvasTemplate, DimensionsInt, RoundStrategy

        context, canvas, fd = self._load_source_components()
        assert canvas.effective_dimensions is None, "Source should have no effective_dimensions"

        template = CanvasTemplate(
            label="Test Template - Effective Dims",
            id="test-effective-dims",
            target_dimensions=DimensionsInt(width=3840, height=2160),
            target_anamorphic_squeeze=1.0,
            fit_source="canvas.effective_dimensions",
            fit_method="fit_all",
            alignment_method_vertical="center",
            alignment_method_horizontal="center",
            round=RoundStrategy(even="even", mode="round"),
        )

        with pytest.raises(ValueError, match="effective_dimensions"):
            template.apply(
                source_canvas=canvas,
                source_framing=fd,
                new_fd_name="",
                new_canvas_id="test",
                source_context_label=context.label,
                context_creator="ASC FDL Tools",
            )


class TestPreserveFromSourceCanvasValidation(_ErrorValidationBase):
    """
    Scenario 22: preserve_from_source_canvas path validation.

    Verifies that ValueError is raised when a template's preserve_from_source_canvas
    references a path that doesn't exist in the source FDL.
    """

    def test_preserve_from_source_canvas_effective_dimensions_missing(self):
        """ValueError when preserve_from_source_canvas references effective_dimensions but source has none."""
        from fdl import CanvasTemplate, DimensionsInt, RoundStrategy

        context, canvas, fd = self._load_source_components()
        assert canvas.effective_dimensions is None, "Source should have no effective_dimensions"

        template = CanvasTemplate(
            label="Test Template - Preserve Effective Dims",
            id="test-preserve-effective-dims",
            target_dimensions=DimensionsInt(width=3840, height=2160),
            target_anamorphic_squeeze=1.0,
            fit_source="framing_decision.dimensions",
            fit_method="fit_all",
            alignment_method_vertical="center",
            alignment_method_horizontal="center",
            preserve_from_source_canvas="canvas.effective_dimensions",
            round=RoundStrategy(even="even", mode="round"),
        )

        with pytest.raises(ValueError, match="effective_dimensions"):
            template.apply(
                source_canvas=canvas,
                source_framing=fd,
                new_fd_name="",
                new_canvas_id="test",
                source_context_label=context.label,
                context_creator="ASC FDL Tools",
            )
