# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Unit tests for FDL Viewer models.
"""

from unittest.mock import MagicMock

import pytest
from PySide6.QtTest import QSignalSpy

from fdl_viewer.models.app_state import AppState
from fdl_viewer.models.fdl_model import FDLModel
from fdl_viewer.models.recent_files import RecentFilesModel
from fdl_viewer.models.template_presets import (
    STANDARD_PRESETS,
    get_preset,
    get_preset_names,
)


class TestAppState:
    """Tests for AppState singleton."""

    def test_singleton_instance(self, app_state):
        """Test that AppState is a singleton."""
        state1 = AppState.instance()
        state2 = AppState.instance()
        assert state1 is state2

    def test_initial_state(self, app_state):
        """Test initial state values."""
        assert app_state.source_fdl is None
        assert app_state.template_fdl is None
        assert app_state.output_fdl is None
        # Selection values default to empty string, not None
        assert app_state.selected_context == ""
        assert app_state.selected_canvas == ""
        assert app_state.selected_framing == ""
        assert app_state.active_tab == 0
        assert app_state.grid_visible is True

    def test_set_source_fdl_emits_signal(self, qapp, app_state):
        """Test that setting source FDL emits signal."""
        spy = QSignalSpy(app_state.source_fdl_changed)
        mock_model = MagicMock(spec=FDLModel)

        app_state.set_source_fdl(mock_model)

        assert spy.count() == 1
        assert app_state.source_fdl is mock_model

    def test_set_template_fdl_emits_signal(self, qapp, app_state):
        """Test that setting template FDL emits signal."""
        spy = QSignalSpy(app_state.template_fdl_changed)
        mock_model = MagicMock(spec=FDLModel)

        app_state.set_template_fdl(mock_model)

        assert spy.count() == 1
        assert app_state.template_fdl is mock_model

    def test_set_output_fdl_emits_signal(self, qapp, app_state):
        """Test that setting output FDL emits signal."""
        spy = QSignalSpy(app_state.output_fdl_changed)
        mock_model = MagicMock(spec=FDLModel)

        app_state.set_output_fdl(mock_model)

        assert spy.count() == 1
        assert app_state.output_fdl is mock_model

    def test_set_selection_emits_signal(self, qapp, app_state):
        """Test that setting selection emits signal."""
        spy = QSignalSpy(app_state.selection_changed)

        app_state.set_selection("context1", "canvas1", "framing1")

        assert spy.count() == 1
        assert app_state.selected_context == "context1"
        assert app_state.selected_canvas == "canvas1"
        assert app_state.selected_framing == "framing1"

    def test_set_active_tab_emits_signal(self, qapp, app_state):
        """Test that setting active tab emits signal."""
        spy = QSignalSpy(app_state.active_tab_changed)

        app_state.set_active_tab(2)

        assert spy.count() == 1
        assert app_state.active_tab == 2

    def test_set_grid_visible_emits_signal(self, qapp, app_state):
        """Test that setting grid visibility emits signal."""
        spy = QSignalSpy(app_state.grid_visible_changed)

        app_state.set_grid_visible(False)

        assert spy.count() == 1
        assert app_state.grid_visible is False

    def test_reset_state(self, qapp, app_state):
        """Test resetting state via reset_instance."""
        mock_model = MagicMock(spec=FDLModel)
        app_state.set_source_fdl(mock_model)
        app_state.set_selection("ctx", "canvas", "framing")

        # Reset instance creates a fresh state
        AppState.reset_instance()
        new_state = AppState.instance()

        assert new_state.source_fdl is None
        assert new_state.template_fdl is None
        assert new_state.output_fdl is None
        assert new_state.selected_context == ""


class TestFDLModel:
    """Tests for FDLModel wrapper."""

    def test_create_empty_model(self):
        """Test creating an empty model."""
        model = FDLModel()
        assert model.fdl is None
        assert model.file_path == ""

    def test_create_model_with_fdl(self, sample_source_fdl_path):
        """Test creating a model from FDL file."""
        if not sample_source_fdl_path.exists():
            pytest.skip("Sample file not found")

        from fdl import read_from_file

        fdl = read_from_file(sample_source_fdl_path)
        model = FDLModel(fdl)
        model.set_file_path(str(sample_source_fdl_path))

        assert model.fdl is fdl
        assert model.file_path == str(sample_source_fdl_path)

    def test_contexts_property(self, sample_source_fdl_path):
        """Test contexts property."""
        if not sample_source_fdl_path.exists():
            pytest.skip("Sample file not found")

        from fdl import read_from_file

        fdl = read_from_file(sample_source_fdl_path)
        model = FDLModel(fdl)

        assert model.contexts is not None
        assert len(model.contexts) > 0

    def test_canvas_templates_property(self, scen1_template_path):
        """Test canvas_templates property."""
        if not scen1_template_path.exists():
            pytest.skip("Sample file not found")

        from fdl import read_from_file

        fdl = read_from_file(scen1_template_path)
        model = FDLModel(fdl)

        # Template files should have canvas_templates
        assert model.canvas_templates is not None


class TestRecentFilesModel:
    """Tests for RecentFilesModel."""

    def test_add_file(self, qapp, tmp_path):
        """Test adding a file to recent files."""
        # Create a real file to add (RecentFilesModel filters non-existent files)
        test_file = tmp_path / "file.fdl"
        test_file.write_text("{}", encoding="utf-8")

        model = RecentFilesModel(max_files=5)
        model.clear()

        model.add_file(str(test_file))

        files = model.get_files()
        assert len(files) == 1
        assert files[0].path == str(test_file.resolve())

    def test_max_files_limit(self, qapp, tmp_path):
        """Test that max files limit is respected."""
        # Create real files
        for i in range(5):
            (tmp_path / f"file{i}.fdl").write_text("{}", encoding="utf-8")

        model = RecentFilesModel(max_files=3)
        model.clear()

        for i in range(5):
            model.add_file(str(tmp_path / f"file{i}.fdl"))

        files = model.get_files()
        assert len(files) == 3

    def test_duplicate_moves_to_top(self, qapp, tmp_path):
        """Test that adding a duplicate moves it to top."""
        # Create real files
        file1 = tmp_path / "file1.fdl"
        file2 = tmp_path / "file2.fdl"
        file1.write_text("{}", encoding="utf-8")
        file2.write_text("{}", encoding="utf-8")

        model = RecentFilesModel(max_files=5)
        model.clear()

        model.add_file(str(file1))
        model.add_file(str(file2))
        model.add_file(str(file1))

        files = model.get_files()
        assert files[0].path == str(file1.resolve())
        assert len(files) == 2

    def test_clear(self, qapp, tmp_path):
        """Test clearing recent files."""
        test_file = tmp_path / "file.fdl"
        test_file.write_text("{}", encoding="utf-8")

        model = RecentFilesModel(max_files=5)
        model.add_file(str(test_file))

        model.clear()

        assert len(model.get_files()) == 0


class TestTemplatePresets:
    """Tests for template presets."""

    def test_presets_defined(self):
        """Test that presets are defined."""
        assert len(STANDARD_PRESETS) > 0
        assert "HD 1080p" in STANDARD_PRESETS
        assert "UHD 4K" in STANDARD_PRESETS
        assert "DCI 2K" in STANDARD_PRESETS
        assert "DCI 4K" in STANDARD_PRESETS

    def test_hd_1080p_dimensions(self):
        """Test HD 1080p preset dimensions."""
        preset = STANDARD_PRESETS["HD 1080p"]
        assert preset.target_dimensions.width == 1920
        assert preset.target_dimensions.height == 1080

    def test_uhd_4k_dimensions(self):
        """Test UHD 4K preset dimensions."""
        preset = STANDARD_PRESETS["UHD 4K"]
        assert preset.target_dimensions.width == 3840
        assert preset.target_dimensions.height == 2160

    def test_dci_2k_dimensions(self):
        """Test DCI 2K preset dimensions."""
        preset = STANDARD_PRESETS["DCI 2K"]
        assert preset.target_dimensions.width == 2048
        assert preset.target_dimensions.height == 1080

    def test_dci_4k_dimensions(self):
        """Test DCI 4K preset dimensions."""
        preset = STANDARD_PRESETS["DCI 4K"]
        assert preset.target_dimensions.width == 4096
        assert preset.target_dimensions.height == 2160

    def test_get_preset(self):
        """Test getting a preset by name."""
        preset = get_preset("HD 1080p")
        assert preset is not None
        assert preset.target_dimensions.width == 1920

    def test_get_preset_names(self):
        """Test getting preset names."""
        names = get_preset_names()
        assert "HD 1080p" in names
        assert "UHD 4K" in names
        assert "DCI 2K" in names
        assert "DCI 4K" in names

    def test_get_invalid_preset(self):
        """Test getting invalid preset returns None."""
        preset = get_preset("Invalid Preset")
        assert preset is None
