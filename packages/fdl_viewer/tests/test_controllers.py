# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Unit tests for FDL Viewer controllers.
"""

import pytest
from PySide6.QtTest import QSignalSpy

from fdl_viewer.models.fdl_model import FDLModel


class TestFileController:
    """Tests for FileController."""

    def test_load_fdl_success(self, qapp, file_controller, sample_source_fdl_path):
        """Test loading an FDL file successfully."""
        if not sample_source_fdl_path.exists():
            pytest.skip("Sample file not found")

        spy = QSignalSpy(file_controller.file_loaded)

        model = file_controller.load_fdl(str(sample_source_fdl_path))

        assert spy.count() == 1
        assert model is not None
        assert model.fdl is not None

    def test_load_fdl_file_not_found(self, qapp, file_controller):
        """Test loading a non-existent file."""
        spy = QSignalSpy(file_controller.error_occurred)

        with pytest.raises(FileNotFoundError):
            file_controller.load_fdl("/nonexistent/path.fdl")

        assert spy.count() == 1

    def test_load_fdl_invalid_json(self, qapp, file_controller, tmp_path):
        """Test loading an invalid JSON file."""
        invalid_file = tmp_path / "invalid.fdl"
        invalid_file.write_text("not valid json", encoding="utf-8")

        spy = QSignalSpy(file_controller.error_occurred)

        with pytest.raises(Exception):
            file_controller.load_fdl(str(invalid_file))

        assert spy.count() == 1

    def test_save_fdl_success(self, qapp, file_controller, sample_source_fdl_path, tmp_path):
        """Test saving an FDL file."""
        if not sample_source_fdl_path.exists():
            pytest.skip("Sample file not found")

        from fdl import read_from_file

        fdl = read_from_file(sample_source_fdl_path)

        output_path = tmp_path / "output.fdl"
        spy = QSignalSpy(file_controller.file_saved)

        file_controller.save_fdl(fdl, str(output_path))

        assert spy.count() == 1
        assert output_path.exists()


class TestTransformController:
    """Tests for TransformController."""

    def test_validate_selection_missing_fdl(self, transform_controller):
        """Test validation fails with no FDL."""
        is_valid, error = transform_controller.validate_selection(None, "context1", "canvas1", "framing1")
        assert not is_valid
        assert "No source FDL" in error

    def test_validate_selection_missing_context(self, transform_controller, sample_source_fdl_path):
        """Test validation fails with missing context."""
        if not sample_source_fdl_path.exists():
            pytest.skip("Sample file not found")

        from fdl import read_from_file

        fdl = read_from_file(sample_source_fdl_path)

        is_valid, error = transform_controller.validate_selection(fdl, "nonexistent", "canvas1", "framing1")
        assert not is_valid
        assert "Context not found" in error

    def test_validate_selection_valid(self, transform_controller, sample_source_fdl_path):
        """Test validation passes with valid selections."""
        if not sample_source_fdl_path.exists():
            pytest.skip("Sample file not found")

        from fdl import read_from_file

        fdl = read_from_file(sample_source_fdl_path)

        # Get actual context/canvas/framing from the file
        context = fdl.contexts[0]
        canvas = context.canvases[0]
        framing = canvas.framing_decisions[0] if canvas.framing_decisions else None

        if not framing:
            pytest.skip("No framing decision in source")

        is_valid, error = transform_controller.validate_selection(fdl, context.label, canvas.id, framing.id)
        assert is_valid
        assert error == ""

    def test_apply_template_success(
        self,
        qapp,
        transform_controller,
        sample_source_fdl_path,
        scen1_template_path,
    ):
        """Test applying a template successfully."""
        if not sample_source_fdl_path.exists() or not scen1_template_path.exists():
            pytest.skip("Sample files not found")

        from fdl import read_from_file

        source_fdl = read_from_file(sample_source_fdl_path)
        template_fdl = read_from_file(scen1_template_path)

        # Get the template from the FDL
        template = template_fdl.canvas_templates[0] if template_fdl.canvas_templates else None
        if not template:
            pytest.skip("No template in template file")

        # Get context, canvas, framing from source
        context = source_fdl.contexts[0]
        canvas = context.canvases[0]
        framing = canvas.framing_decisions[0] if canvas.framing_decisions else None
        if not framing:
            pytest.skip("No framing decision in source")

        spy = QSignalSpy(transform_controller.transform_completed)

        transform_controller.apply_template(
            source_fdl=source_fdl,
            template=template,
            context_label=context.label,
            canvas_id=canvas.id,
            framing_decision_id=framing.id,
        )

        assert spy.count() == 1


class TestSelectionController:
    """Tests for SelectionController."""

    def test_set_fdl_model_updates_contexts(self, qapp, app_state, selection_controller, sample_source_fdl_path):
        """Test that setting FDL model triggers context updates."""
        if not sample_source_fdl_path.exists():
            pytest.skip("Sample file not found")

        from fdl import read_from_file

        fdl = read_from_file(sample_source_fdl_path)
        model = FDLModel(fdl)

        spy = QSignalSpy(selection_controller.contexts_updated)

        selection_controller.set_fdl_model(model)

        assert spy.count() >= 1

    def test_select_context(self, qapp, app_state, selection_controller, sample_source_fdl_path):
        """Test selecting a context."""
        if not sample_source_fdl_path.exists():
            pytest.skip("Sample file not found")

        from fdl import read_from_file

        fdl = read_from_file(sample_source_fdl_path)
        model = FDLModel(fdl)

        selection_controller.set_fdl_model(model)

        # Get a context label
        context_label = fdl.contexts[0].label
        selection_controller.select_context(context_label)

        # Should be able to get selected context
        selected = selection_controller.get_selected_context()
        assert selected is not None
        assert selected.label == context_label

    def test_select_canvas(self, qapp, app_state, selection_controller, sample_source_fdl_path):
        """Test selecting a canvas."""
        if not sample_source_fdl_path.exists():
            pytest.skip("Sample file not found")

        from fdl import read_from_file

        fdl = read_from_file(sample_source_fdl_path)
        model = FDLModel(fdl)

        selection_controller.set_fdl_model(model)

        # Select context first
        context = fdl.contexts[0]
        selection_controller.select_context(context.label)

        # Select canvas
        canvas = context.canvases[0]
        selection_controller.select_canvas(canvas.id)

        # Should be able to get selected canvas
        selected = selection_controller.get_selected_canvas()
        assert selected is not None
        assert selected.id == canvas.id

    def test_get_current_selection(self, qapp, app_state, selection_controller, sample_source_fdl_path):
        """Test getting the current selection tuple."""
        if not sample_source_fdl_path.exists():
            pytest.skip("Sample file not found")

        from fdl import read_from_file

        fdl = read_from_file(sample_source_fdl_path)
        model = FDLModel(fdl)

        selection_controller.set_fdl_model(model)

        # After setting model, selection should auto-cascade
        context_label, canvas_id, _framing_id = selection_controller.get_current_selection()

        # Should have at least context and canvas selected
        assert context_label != ""
        assert canvas_id != ""


class TestTemplateController:
    """Tests for TemplateController."""

    def test_apply_preset(self, qapp, template_controller):
        """Test applying a preset template."""
        template = template_controller.apply_preset("HD 1080p")

        assert template is not None
        assert template.target_dimensions.width == 1920
        assert template.target_dimensions.height == 1080

    def test_create_custom_template(self, qapp, template_controller):
        """Test creating a custom template."""
        template = template_controller.create_custom(
            width=2560,
            height=1440,
        )

        assert template is not None
        assert template.target_dimensions.width == 2560
        assert template.target_dimensions.height == 1440

    def test_create_custom_template_with_options(self, qapp, template_controller):
        """Test creating a custom template with options."""
        template = template_controller.create_custom(
            width=1920,
            height=1080,
            fit_source="framing_decision.dimensions",
            fit_method="width",
        )

        assert template is not None
        assert template.fit_source == "framing_decision.dimensions"
        assert template.fit_method == "width"

    def test_update_target_dimensions(self, qapp, template_controller):
        """Test updating template dimensions."""
        # First create a template
        template_controller.create_custom(
            width=1920,
            height=1080,
        )

        # Update dimensions
        template_controller.update_target_dimensions(3840, 2160)

        assert template_controller.current_template.target_dimensions.width == 3840
        assert template_controller.current_template.target_dimensions.height == 2160

    def test_get_preset_names(self, qapp, template_controller):
        """Test getting preset names."""
        names = template_controller.get_preset_names()

        assert "HD 1080p" in names
        assert "UHD 4K" in names
