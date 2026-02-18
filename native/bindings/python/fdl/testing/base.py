# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Base test case for FDL template tests.

Provides FDL-only test functionality without image processing or Nuke dependencies.
"""

import unittest
import uuid
from pathlib import Path

from fdl import read_from_file, write_to_file
from fdl.testing.fdl_comparison import FDLComparison


class BaseFDLTestCase(unittest.TestCase):
    """
    Base test case class with shared helper methods for FDL testing.

    Subclass this for tests that only need FDL comparison (no image/nuke).
    """

    # Set to True to generate expected results instead of comparing against them
    generate_result = False

    def setUp(self):
        """Set up comparators for each test."""
        super().setUp()
        self._fdl_comparator = FDLComparison(test_case=self)

    @classmethod
    def normalize_paths(cls, text: str) -> str:
        """
        Normalize file paths in test output to make tests portable across machines.
        Replaces the absolute path to the resources folder with a placeholder.
        """
        resources_path = str(cls.get_resources_folder())
        return text.replace(resources_path, "<RESOURCES>")

    @classmethod
    def get_resources_folder(cls):
        """Gets the FDL test resources folder from the fdl package root."""
        # Navigate: fdl/testing/ -> fdl/ -> python/ -> bindings/ -> native/ -> packages/fdl/ -> resources/FDL
        return Path(__file__).parents[5] / "resources" / "FDL"

    @classmethod
    def get_outputs_folder(cls):
        """Gets the outputs folder, creating it if it doesn't exist."""
        # Navigate: fdl/testing/ -> fdl/ -> python/ -> tests/outputs
        output_path = Path(__file__).parents[1].parent / "tests" / "outputs"
        if not output_path.exists():
            output_path.mkdir(parents=True, exist_ok=True)
        return output_path

    @staticmethod
    def get_component_from_fdl(fdl, component_type, label=None, **kwargs):
        """
        Generic helper to extract a component from an FDL by label or other criteria.

        Parameters
        ----------
        fdl : FDL object
            The loaded FDL object
        component_type : str
            Type of component to extract: 'context', 'template', 'canvas', 'framing_decision'
        label : str, optional
            Label to match. If None and component_type needs a parent, must provide via kwargs
        **kwargs : dict
            Additional search criteria (e.g., framing_intent_id for framing decisions)
            For nested components, provide parent context/canvas via 'context' or 'canvas' keys

        Returns
        -------
        Component object or None if not found
        """
        if component_type == "context":
            for c in fdl.contexts:
                if c.label == label:
                    return c

        elif component_type == "template":
            for tmpl in fdl.canvas_templates:
                if tmpl.label == label:
                    return tmpl

        elif component_type == "canvas":
            context = kwargs.get("context")
            if context is None:
                raise ValueError("Must provide 'context' in kwargs for canvas lookup")
            for cv in context.canvases:
                if cv.label == label:
                    return cv

        elif component_type == "framing_decision":
            canvas = kwargs.get("canvas")
            if canvas is None:
                raise ValueError("Must provide 'canvas' in kwargs for framing_decision lookup")

            # Check for framing_intent_id first, then label
            framing_intent_id = kwargs.get("framing_intent_id")
            if framing_intent_id:
                for fd in canvas.framing_decisions:
                    if fd.framing_intent_id == framing_intent_id:
                        return fd
            elif label is not None:
                for fd in canvas.framing_decisions:
                    if fd.label == label:
                        return fd
        else:
            raise ValueError(f"Unknown component_type: {component_type}")

        return None

    @staticmethod
    def load_fdl_with_validation(fdl_path):
        """
        Load an FDL file and validate it against the schema.

        Parameters
        ----------
        fdl_path : Path
            Path to the FDL file to load

        Returns
        -------
        tuple (FDL, str or None)
            Returns (fdl_object, error_message). If validation passes, error_message is None.
            If validation fails, error_message contains the error string.
        """
        try:
            # read_from_file runs both Pydantic and structural validation by default
            fdl = read_from_file(fdl_path)
            return (fdl, None)
        except Exception as e:
            return (None, str(e))

    def run_template_test(
        self,
        canvas_label: str,
        context_creator: str,
        context_label: str,
        expected_fdl_path: Path,
        framing_intent_id: str,
        source_fdl_path: Path,
        template_fdl_path: Path,
        template_label: str,
        test_name: str,
        **kwargs,
    ):
        """
        Run an FDL template test: load, apply, validate, and compare.

        Subclasses can override or extend this to add image/nuke processing.

        Parameters
        ----------
        canvas_label : str
            Label of the source canvas.
        context_creator : str
            Creator string for the new context.
        context_label : str
            Label of the source context.
        expected_fdl_path : Path
            Path to the expected result FDL.
        framing_intent_id : str
            ID of the framing intent to select.
        source_fdl_path : Path
            Path to the source FDL file.
        template_fdl_path : Path
            Path to the template FDL file.
        template_label : str
            Label of the canvas template to apply.
        test_name : str
            Name for output files.
        **kwargs : dict
            Additional arguments passed to subclass overrides.
        """
        template_fdl, error = self.load_fdl_with_validation(template_fdl_path)
        if error:
            self.fail(f"Template FDL schema validation failed at {template_fdl_path}:\n{error}")

        template = self.get_component_from_fdl(template_fdl, "template", label=template_label)
        self.assertIsNotNone(template, f"Template {template_label} not found")

        source_fdl, error = self.load_fdl_with_validation(source_fdl_path)
        if error:
            self.fail(f"Source FDL schema validation failed at {source_fdl_path}:\n{error}")

        context = self.get_component_from_fdl(source_fdl, "context", label=context_label)
        self.assertIsNotNone(context, f"Context {context_label} not found")

        canvas = self.get_component_from_fdl(source_fdl, "canvas", label=canvas_label, context=context)
        self.assertIsNotNone(canvas, f"Canvas {context} not found")

        fd = self.get_component_from_fdl(source_fdl, "framing_decision", canvas=canvas, framing_intent_id=framing_intent_id)
        self.assertIsNotNone(fd, f"Framing decision with intent_id {framing_intent_id} not found")

        # Apply template with deterministic UUID for reproducible tests
        deterministic_uuid = uuid.UUID("12345678-1234-5678-1234-567812345678")
        new_canvas_id = deterministic_uuid.hex[:30]

        result = template.apply(
            source_canvas=canvas,
            source_framing=fd,
            new_canvas_id=new_canvas_id,
            new_fd_name="",
            source_context_label=context.label,
            context_creator=context_creator,
        )

        new_fdl_path = self.get_outputs_folder() / f"{test_name}.fdl"
        write_to_file(result.fdl, new_fdl_path)
        new_fdl, expected_error = self.load_fdl_with_validation(new_fdl_path)
        if expected_error:
            self.fail(f"New FDL schema validation failed at {new_fdl_path}:\n{expected_error}")

        # Generate mode: save result as expected and skip comparison
        if self.generate_result:
            expected_fdl_path.parent.mkdir(parents=True, exist_ok=True)
            write_to_file(new_fdl, expected_fdl_path)
            self.skipTest(f"Generated expected result at {expected_fdl_path}")

        # Verify expected file exists (only when NOT in generate mode)
        self.assertTrue(expected_fdl_path.exists(), f"Expected FDL file does not exist: {expected_fdl_path}")

        # Load expected results
        expected_fdl, expected_error = self.load_fdl_with_validation(expected_fdl_path)
        if expected_error:
            self.fail(f"Expected FDL schema validation failed at {expected_fdl_path}:\n{expected_error}")

        expected_context = self.get_component_from_fdl(expected_fdl, "context", label=template_label)
        self.assertIsNotNone(expected_context, f"Expected context {template_label} not found")

        expected_canvas = self.get_component_from_fdl(
            expected_fdl, "canvas", label=f"{template_label}: {context_label} {canvas_label}", context=expected_context
        )
        self.assertIsNotNone(expected_canvas, "Expected canvas not found")

        expected_fd = self.get_component_from_fdl(
            expected_fdl, "framing_decision", canvas=expected_canvas, framing_intent_id=framing_intent_id
        )
        self.assertIsNotNone(expected_fd, "Expected framing decision not found")

        # Extract actual context/canvas/fd from result using convenience accessors
        expected_canvas_id = new_canvas_id
        expected_fd_id = f"{expected_canvas_id}-{framing_intent_id}"

        actual_context = result.context
        self.assertIsNotNone(actual_context, f"Actual context '{template_label}' not found in result FDL")

        actual_canvas = result.canvas
        self.assertIsNotNone(actual_canvas, "Actual canvas not found in result FDL")

        actual_fd = result.framing_decision
        self.assertIsNotNone(actual_fd, "Actual framing decision not found in result FDL")

        self._fdl_comparator.compare_context(expected_context, actual_context)
        self._fdl_comparator.compare_canvas(expected_canvas, actual_canvas, expected_id=expected_canvas_id)
        self._fdl_comparator.compare_framing_decision(expected_fd, actual_fd, expected_id=expected_fd_id)

        # Verify canvas template
        expected_template = self.get_component_from_fdl(expected_fdl, "template", label=template_label)
        actual_template = self.get_component_from_fdl(result.fdl, "template", label=template_label)
        self.assertIsNotNone(expected_template, f"Expected template '{template_label}' not found in expected FDL")
        self.assertIsNotNone(actual_template, f"Actual template '{template_label}' not found in generated FDL")
        self._fdl_comparator.compare_canvas_template(expected_template, actual_template)

        # Store result on self for subclass hooks
        self._template_result = result
        self._template = template
        self._source_fdl_path = source_fdl_path
        self._template_fdl_path = template_fdl_path
        self._context_label = context_label
        self._canvas = canvas
        self._fd = fd
        self._framing_intent_id = framing_intent_id
