# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Unit tests for FDL Viewer views/widgets.

Uses pytest-qt for Qt widget testing.
"""

import pytest
from PySide6.QtTest import QSignalSpy

from fdl_viewer.views.common.cascading_dropdown import CascadingDropdown
from fdl_viewer.views.common.collapsible_section import CollapsibleSection
from fdl_viewer.views.common.dimensions_editor import DimensionsEditor
from fdl_viewer.views.common.file_drop_zone import FileDropZone


class TestCollapsibleSection:
    """Tests for CollapsibleSection widget."""

    def test_initial_state_expanded(self, qapp):
        """Test initial state is expanded by default."""
        section = CollapsibleSection("Test Section")
        assert not section.is_collapsed()

    def test_initial_state_collapsed(self, qapp):
        """Test initial state can be collapsed."""
        section = CollapsibleSection("Test Section", collapsed=True)
        assert section.is_collapsed()

    def test_toggle_collapsed(self, qapp):
        """Test toggling collapsed state."""
        section = CollapsibleSection("Test Section")
        spy = QSignalSpy(section.collapsed_changed)

        section.set_collapsed(True)

        assert section.is_collapsed()
        assert spy.count() == 1

    def test_set_title(self, qapp):
        """Test setting title."""
        section = CollapsibleSection("Initial Title")

        section.set_title("New Title")

        assert section.title() == "New Title"

    def test_set_content_widget(self, qapp):
        """Test setting content widget."""
        from PySide6.QtWidgets import QLabel

        section = CollapsibleSection("Test Section")
        label = QLabel("Content")

        section.set_content_widget(label)

        assert section.content_widget() is label


class TestDimensionsEditor:
    """Tests for DimensionsEditor widget."""

    def test_initial_values(self, qapp):
        """Test initial values."""
        editor = DimensionsEditor()
        assert editor.width() == 1
        assert editor.height() == 1

    def test_set_dimensions(self, qapp):
        """Test setting dimensions."""
        editor = DimensionsEditor()

        editor.set_dimensions(1920, 1080)

        assert editor.width() == 1920
        assert editor.height() == 1080

    def test_dimensions_changed_signal(self, qapp):
        """Test dimensions changed signal."""
        editor = DimensionsEditor()
        spy = QSignalSpy(editor.dimensions_changed)

        editor.set_dimensions(1920, 1080)
        # Trigger change by setting value directly (not blocked)
        editor._width_spin.setValue(1921)

        assert spy.count() >= 1

    def test_float_mode(self, qapp):
        """Test float mode."""
        editor = DimensionsEditor(use_float=True)

        editor.set_dimensions(1920.5, 1080.5)

        assert editor.width() == 1920.5
        assert editor.height() == 1080.5

    def test_dimensions_tuple(self, qapp):
        """Test getting dimensions as tuple."""
        editor = DimensionsEditor()
        editor.set_dimensions(1920, 1080)

        dims = editor.dimensions()

        assert dims == (1920, 1080)


class TestFileDropZone:
    """Tests for FileDropZone widget."""

    def test_accepts_drops(self, qapp):
        """Test that drop zone accepts drops."""
        zone = FileDropZone()
        assert zone.acceptDrops()

    def test_extension_filter(self, qapp):
        """Test extension filtering."""
        zone = FileDropZone(extensions=[".fdl", ".json"])

        assert zone._is_valid_file("/path/to/file.fdl")
        assert zone._is_valid_file("/path/to/file.json")
        assert not zone._is_valid_file("/path/to/file.txt")

    def test_no_extension_filter(self, qapp):
        """Test no extension filter accepts all."""
        zone = FileDropZone(extensions=None)

        assert zone._is_valid_file("/path/to/file.fdl")
        assert zone._is_valid_file("/path/to/file.txt")
        assert zone._is_valid_file("/path/to/file.anything")

    def test_set_hint_text(self, qapp):
        """Test setting hint text."""
        zone = FileDropZone(hint_text="Initial")

        zone.set_hint_text("New Hint")

        assert zone._hint_text == "New Hint"

    def test_initial_title(self, qapp):
        """Test initial title."""
        zone = FileDropZone(title="My Title")

        assert zone._title == "My Title"

    def test_initial_icon(self, qapp):
        """Test initial icon."""
        zone = FileDropZone(icon="📄")

        assert zone._icon == "📄"


class TestCascadingDropdown:
    """Tests for CascadingDropdown widget."""

    def test_set_items(self, qapp):
        """Test setting items."""
        dropdown = CascadingDropdown()
        items = [
            {"id": "1", "label": "Item 1"},
            {"id": "2", "label": "Item 2"},
            {"id": "3", "label": "Item 3"},
        ]

        dropdown.set_items(items)

        assert dropdown.count() == 3

    def test_selected_id(self, qapp):
        """Test getting selected ID."""
        dropdown = CascadingDropdown()
        items = [
            {"id": "1", "label": "Item 1"},
            {"id": "2", "label": "Item 2"},
        ]
        dropdown.set_items(items)

        # First item is auto-selected
        assert dropdown.selected_id() == "1"

    def test_set_selected_id(self, qapp):
        """Test setting selected ID."""
        dropdown = CascadingDropdown()
        items = [
            {"id": "1", "label": "Item 1"},
            {"id": "2", "label": "Item 2"},
        ]
        dropdown.set_items(items)

        result = dropdown.set_selected_id("2")

        assert result is True
        assert dropdown.selected_id() == "2"

    def test_set_selected_invalid_id(self, qapp):
        """Test setting invalid selected ID."""
        dropdown = CascadingDropdown()
        items = [
            {"id": "1", "label": "Item 1"},
        ]
        dropdown.set_items(items)

        result = dropdown.set_selected_id("invalid")

        assert result is False
        assert dropdown.selected_id() == "1"  # Unchanged

    def test_selected_item(self, qapp):
        """Test getting selected item."""
        dropdown = CascadingDropdown()
        items = [
            {"id": "1", "label": "Item 1", "extra": "data1"},
            {"id": "2", "label": "Item 2", "extra": "data2"},
        ]
        dropdown.set_items(items)

        item = dropdown.selected_item()

        assert item is not None
        assert item["id"] == "1"
        assert item["extra"] == "data1"

    def test_selection_changed_signal(self, qapp):
        """Test selection changed signal."""
        dropdown = CascadingDropdown()
        spy = QSignalSpy(dropdown.selection_changed)
        items = [
            {"id": "1", "label": "Item 1"},
            {"id": "2", "label": "Item 2"},
        ]

        dropdown.set_items(items)

        # Signal emitted on auto-select
        assert spy.count() >= 1

    def test_clear(self, qapp):
        """Test clearing items."""
        dropdown = CascadingDropdown()
        items = [{"id": "1", "label": "Item 1"}]
        dropdown.set_items(items)

        dropdown.clear()

        assert dropdown.count() == 0
        assert dropdown.selected_id() is None

    def test_custom_keys(self, qapp):
        """Test using custom ID and label keys."""
        dropdown = CascadingDropdown()
        items = [
            {"uuid": "abc", "name": "First"},
            {"uuid": "def", "name": "Second"},
        ]

        dropdown.set_items(items, id_key="uuid", label_key="name")

        assert dropdown.selected_id() == "abc"


class TestCanvasWidget:
    """Tests for CanvasWidget."""

    def test_creation(self, qapp):
        """Test widget creation."""
        from fdl_viewer.views.canvas.canvas_widget import CanvasWidget

        widget = CanvasWidget()

        assert widget is not None

    def test_set_is_source(self, qapp):
        """Test setting is_source flag."""
        from fdl_viewer.views.canvas.canvas_widget import CanvasWidget

        widget = CanvasWidget()

        widget.set_is_source(True)
        assert widget._is_source is True

        widget.set_is_source(False)
        assert widget._is_source is False

    def test_zoom_in(self, qapp):
        """Test zoom in."""
        from fdl_viewer.views.canvas.canvas_widget import CanvasWidget

        widget = CanvasWidget()
        initial_scale = widget.get_zoom_level()

        widget.zoom_in()

        assert widget.get_zoom_level() > initial_scale

    def test_zoom_out(self, qapp):
        """Test zoom out."""
        from fdl_viewer.views.canvas.canvas_widget import CanvasWidget

        widget = CanvasWidget()
        # Start zoomed in
        widget.zoom_in()
        widget.zoom_in()
        zoomed_scale = widget.get_zoom_level()

        widget.zoom_out()

        assert widget.get_zoom_level() < zoomed_scale

    def test_reset_zoom(self, qapp):
        """Test reset zoom."""
        from fdl_viewer.views.canvas.canvas_widget import CanvasWidget

        widget = CanvasWidget()
        widget.zoom_in()
        widget.zoom_in()

        widget.reset_zoom()

        assert widget.get_zoom_level() == 1.0

    def test_zoom_changed_signal(self, qapp):
        """Test zoom changed signal."""
        from fdl_viewer.views.canvas.canvas_widget import CanvasWidget

        widget = CanvasWidget()
        spy = QSignalSpy(widget.zoom_changed)

        widget.zoom_in()

        assert spy.count() == 1


class TestSourceSelectorView:
    """Tests for SourceSelectorView."""

    def test_creation(self, qapp, app_state):
        """Test widget creation."""
        from fdl_viewer.views.sidebar.source_selector_view import SourceSelectorView

        widget = SourceSelectorView()

        assert widget is not None

    def test_set_contexts(self, qapp, app_state, sample_source_fdl_path):
        """Test setting contexts on the view."""
        if not sample_source_fdl_path.exists():
            pytest.skip("Sample file not found")

        from fdl import read_from_file

        from fdl_viewer.views.sidebar.source_selector_view import SourceSelectorView

        fdl = read_from_file(sample_source_fdl_path)

        widget = SourceSelectorView()

        # Get context list as (index, display_label) tuples
        context_list = [(i, ctx.label or str(i)) for i, ctx in enumerate(fdl.contexts)]
        widget.set_contexts(context_list)

        # Should have contexts populated
        assert widget._context_combo.count() > 0
        assert widget._context_combo.count() == len(context_list)


class TestTemplateEditorView:
    """Tests for TemplateEditorView."""

    def test_creation(self, qapp, app_state):
        """Test widget creation."""
        from fdl_viewer.views.sidebar.template_editor_view import TemplateEditorView

        widget = TemplateEditorView()

        assert widget is not None

    def test_rounding_mode_combo_values(self, qapp, app_state):
        """Test all rounding mode options are present and selectable."""
        from fdl.constants import RoundingMode

        from fdl_viewer.views.sidebar.template_editor_view import TemplateEditorView

        widget = TemplateEditorView()

        assert widget._round_mode_combo.count() == 3
        assert widget._round_mode_combo.itemData(0) == RoundingMode.UP
        assert widget._round_mode_combo.itemData(1) == RoundingMode.DOWN
        assert widget._round_mode_combo.itemData(2) == RoundingMode.ROUND

    def test_rounding_even_combo_values(self, qapp, app_state):
        """Test all rounding even options are present and selectable."""
        from fdl.constants import RoundingEven

        from fdl_viewer.views.sidebar.template_editor_view import TemplateEditorView

        widget = TemplateEditorView()

        assert widget._round_even_combo.count() == 2
        assert widget._round_even_combo.itemData(0) == RoundingEven.WHOLE
        assert widget._round_even_combo.itemData(1) == RoundingEven.EVEN

    def test_set_template_rounding_round_trip(self, qapp, app_state):
        """Test that set_template correctly updates rounding combos and _build_template preserves values."""
        from fdl import CanvasTemplate, DimensionsInt, RoundStrategy
        from fdl.constants import RoundingEven, RoundingMode

        from fdl_viewer.views.sidebar.template_editor_view import TemplateEditorView

        widget = TemplateEditorView()

        template = CanvasTemplate(
            id="test",
            label="Test",
            target_dimensions=DimensionsInt(width=1920, height=1080),
            round=RoundStrategy(even=RoundingEven.WHOLE, mode=RoundingMode.DOWN),
        )
        widget.set_template(template)

        assert widget._round_even_combo.currentData() == RoundingEven.WHOLE
        assert widget._round_mode_combo.currentData() == RoundingMode.DOWN

        # Build template back and verify rounding survived
        built = widget._build_template()
        assert built.round.even == RoundingEven.WHOLE
        assert built.round.mode == RoundingMode.DOWN

    def test_rounding_mode_change_does_not_affect_even(self, qapp, app_state):
        """Changing mode combo must not alter the even combo."""
        from fdl import CanvasTemplate, DimensionsInt, RoundStrategy
        from fdl.constants import RoundingEven, RoundingMode

        from fdl_viewer.views.sidebar.template_editor_view import TemplateEditorView

        widget = TemplateEditorView()

        # Start with even=EVEN, mode=UP
        template = CanvasTemplate(
            id="test",
            label="Test",
            target_dimensions=DimensionsInt(width=1920, height=1080),
            round=RoundStrategy(even=RoundingEven.EVEN, mode=RoundingMode.UP),
        )
        widget.set_template(template)

        # Change mode to DOWN
        widget._round_mode_combo.setCurrentIndex(1)  # DOWN
        assert widget._round_mode_combo.currentData() == RoundingMode.DOWN
        # Even must remain EVEN
        assert widget._round_even_combo.currentData() == RoundingEven.EVEN

    def test_rounding_even_change_does_not_affect_mode(self, qapp, app_state):
        """Changing even combo must not alter the mode combo."""
        from fdl import CanvasTemplate, DimensionsInt, RoundStrategy
        from fdl.constants import RoundingEven, RoundingMode

        from fdl_viewer.views.sidebar.template_editor_view import TemplateEditorView

        widget = TemplateEditorView()

        # Start with even=EVEN, mode=DOWN
        template = CanvasTemplate(
            id="test",
            label="Test",
            target_dimensions=DimensionsInt(width=1920, height=1080),
            round=RoundStrategy(even=RoundingEven.EVEN, mode=RoundingMode.DOWN),
        )
        widget.set_template(template)

        # Change even to WHOLE
        widget._round_even_combo.setCurrentIndex(0)  # WHOLE
        assert widget._round_even_combo.currentData() == RoundingEven.WHOLE
        # Mode must remain DOWN
        assert widget._round_mode_combo.currentData() == RoundingMode.DOWN

    def test_dimension_controls(self, qapp, app_state):
        """Test dimension controls exist and work."""
        from fdl_viewer.views.sidebar.template_editor_view import TemplateEditorView

        widget = TemplateEditorView()

        # Set dimensions directly on the spin boxes
        widget._width_spin.setValue(1920)
        widget._height_spin.setValue(1080)

        # Dimensions should be set
        assert widget._width_spin.value() == 1920
        assert widget._height_spin.value() == 1080
