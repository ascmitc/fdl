# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Sidebar widget for FDL Viewer.

Contains file loading, source selection, and template editing components.
"""

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QFrame,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from fdl_viewer.controllers.selection_controller import SelectionController
from fdl_viewer.controllers.template_controller import TemplateController
from fdl_viewer.models.app_state import AppState
from fdl_viewer.models.fdl_model import FDLModel
from fdl_viewer.models.recent_files import RecentFilesModel
from fdl_viewer.views.sidebar.file_loader_view import FileLoaderView
from fdl_viewer.views.sidebar.image_loader_view import ImageLoaderView
from fdl_viewer.views.sidebar.recent_files_view import RecentFilesView
from fdl_viewer.views.sidebar.source_selector_view import SourceSelectorView
from fdl_viewer.views.sidebar.template_editor_view import TemplateEditorView


class SidebarWidget(QWidget):
    """
    Sidebar widget containing file loading and configuration controls.

    Contains:
    - Recent files list
    - File drop zones for source and template FDLs
    - Source selection (context/canvas/framing)
    - Template editor with presets

    Parameters
    ----------
    recent_files : RecentFilesModel, optional
        The recent files model.
    parent : QWidget, optional
        Parent widget.

    Attributes
    ----------
    source_file_dropped : Signal
        Emitted when a source FDL is dropped (path).
    template_file_dropped : Signal
        Emitted when a template FDL is dropped (path).
    transform_requested : Signal
        Emitted when transform button is clicked.
    """

    source_file_dropped = Signal(str)
    template_file_dropped = Signal(str)
    transform_requested = Signal()
    image_loaded = Signal(object, int, int)  # QPixmap, width, height
    image_cleared = Signal()

    def __init__(self, recent_files: RecentFilesModel | None = None, parent: QWidget | None = None) -> None:
        """
        Initialize the SidebarWidget.

        Parameters
        ----------
        recent_files : RecentFilesModel, optional
            The recent files model.
        parent : QWidget, optional
            Parent widget.
        """
        super().__init__(parent)

        self._app_state = AppState.instance()
        self._recent_files = recent_files or RecentFilesModel()
        self._selection_controller = SelectionController()
        self._template_controller = TemplateController()

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Set up the UI layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.NoFrame)

        # Create content widget
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(16)

        # Recent files
        self._recent_files_view = RecentFilesView(self._recent_files)
        content_layout.addWidget(self._recent_files_view)

        # File loader
        self._file_loader = FileLoaderView()
        content_layout.addWidget(self._file_loader)

        # Source selector
        self._source_selector = SourceSelectorView()
        content_layout.addWidget(self._source_selector)

        # Template editor
        self._template_editor = TemplateEditorView()
        content_layout.addWidget(self._template_editor)

        # Image loader
        self._image_loader = ImageLoaderView()
        content_layout.addWidget(self._image_loader)

        # Transform button
        self._transform_button = QPushButton("TRANSFORM")
        self._transform_button.setObjectName("transformButton")
        self._transform_button.setMinimumHeight(40)
        self._transform_button.setEnabled(False)
        content_layout.addWidget(self._transform_button)

        # Add stretch at bottom
        content_layout.addStretch()

        scroll.setWidget(content)
        layout.addWidget(scroll)

    def _connect_signals(self) -> None:
        """Connect signals to slots."""
        # App state
        self._app_state.source_fdl_changed.connect(self._on_source_fdl_changed)
        self._app_state.template_fdl_changed.connect(self._on_template_fdl_changed)
        self._app_state.selection_changed.connect(self._on_selection_changed)
        self._app_state.template_modified_changed.connect(self._on_template_modified_changed)
        self._app_state.output_fdl_changed.connect(self._on_output_fdl_changed)

        # File loader
        self._file_loader.source_file_dropped.connect(self.source_file_dropped)
        self._file_loader.template_file_dropped.connect(self.template_file_dropped)

        # Recent files
        self._recent_files_view.file_selected.connect(self._on_recent_file_selected)

        # Source selector
        self._source_selector.context_selected.connect(self._selection_controller.select_context)
        self._source_selector.canvas_selected.connect(self._selection_controller.select_canvas)
        self._source_selector.framing_selected.connect(self._selection_controller.select_framing)

        # Selection controller
        self._selection_controller.contexts_updated.connect(self._source_selector.set_contexts)
        self._selection_controller.canvases_updated.connect(self._source_selector.set_canvases)
        self._selection_controller.framings_updated.connect(self._source_selector.set_framings)

        # Preset mode from file loader
        self._file_loader.preset_selected.connect(self._template_controller.apply_preset)
        self._file_loader.preset_mode_changed.connect(self._on_preset_mode_changed)

        # Template editor
        self._template_editor.template_changed.connect(self._on_template_editor_changed)

        # Template controller
        self._template_controller.template_changed.connect(self._template_editor.set_template)

        # Image loader
        self._image_loader.image_loaded.connect(self.image_loaded)
        self._image_loader.image_cleared.connect(self.image_cleared)

        # Transform button
        self._transform_button.clicked.connect(self.transform_requested)

    @Slot(object)
    def _on_source_fdl_changed(self, fdl_model: FDLModel | None) -> None:
        """Handle source FDL change."""
        self._selection_controller.set_fdl_model(fdl_model)
        self._file_loader.set_source_loaded(fdl_model is not None)
        self._update_transform_button()

    @Slot(object)
    def _on_template_fdl_changed(self, fdl_model: FDLModel | None) -> None:
        """Handle template FDL change."""
        self._file_loader.set_template_loaded(fdl_model is not None)

        # Load first template from FDL if available (only if not in preset mode)
        if not self._file_loader.is_preset_mode():
            if fdl_model and fdl_model.fdl:
                template = fdl_model.get_first_template()
                if template:
                    self._template_controller.set_template(template)

        self._update_transform_button()

    @Slot(bool)
    def _on_preset_mode_changed(self, enabled: bool) -> None:
        """Handle preset mode toggle."""
        # When preset mode changes, update the transform button
        self._update_transform_button()

    @Slot(str, str, str)
    def _on_selection_changed(self, context: str, canvas: str, framing: str) -> None:
        """Handle selection change."""
        self._update_transform_button()

    @Slot(str, str)
    def _on_recent_file_selected(self, path: str, file_type: str) -> None:
        """Handle recent file selection."""
        if file_type == "source":
            self.source_file_dropped.emit(path)
        else:
            self.template_file_dropped.emit(path)

    @Slot(object)
    def _on_template_editor_changed(self, template) -> None:
        """Handle template editor changes (user edits)."""
        self._template_controller.set_template(template, from_user_edit=True)
        self._update_transform_button()

    @Slot(bool)
    def _on_template_modified_changed(self, modified: bool) -> None:
        """Handle template modified state change."""
        self._update_transform_button()

    @Slot(object)
    def _on_output_fdl_changed(self, fdl_model: FDLModel | None) -> None:
        """Handle output FDL change - reset template modified state."""
        # When a transform completes, mark template as not modified
        if fdl_model is not None:
            self._has_output = True
        self._update_transform_button()

    def _update_transform_button(self) -> None:
        """Update transform button enabled state and text."""
        source = self._app_state.source_fdl
        template = self._app_state.current_template
        context, canvas, framing = (
            self._app_state.selected_context,
            self._app_state.selected_canvas,
            self._app_state.selected_framing,
        )

        enabled = source is not None and template is not None and bool(context) and bool(canvas) and bool(framing)
        self._transform_button.setEnabled(enabled)

        # Update button text and style based on template modification state
        has_output = self._app_state.output_fdl is not None
        is_modified = self._app_state.template_modified

        if has_output and is_modified:
            self._transform_button.setText("REPROCESS && TRANSFORM")
            new_name = "reprocessButton"
        else:
            self._transform_button.setText("TRANSFORM")
            new_name = "transformButton"

        # Only update if object name changed (to avoid unnecessary repolishing)
        if self._transform_button.objectName() != new_name:
            self._transform_button.setObjectName(new_name)
            # Repolish to apply new stylesheet
            self._transform_button.style().unpolish(self._transform_button)
            self._transform_button.style().polish(self._transform_button)

    def get_image_path(self) -> str:
        """
        Get the path of the currently loaded image.

        Returns
        -------
        str
            The path to the current image, or empty string if none loaded.
        """
        return self._image_loader.get_current_path()
