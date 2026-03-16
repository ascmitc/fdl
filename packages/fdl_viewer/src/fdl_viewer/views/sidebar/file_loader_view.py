# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
File loader view for FDL Viewer.

Provides drag/drop zones for loading source and template FDL files.
"""

from pathlib import Path

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from fdl_viewer.models.template_presets import get_preset_names
from fdl_viewer.views.common.file_drop_zone import FileDropZone


class FileLoaderView(QWidget):
    """
    File loader view with drag/drop zones for source and template FDLs.

    Parameters
    ----------
    parent : QWidget, optional
        Parent widget.

    Attributes
    ----------
    source_file_dropped : Signal
        Emitted when a source file is dropped (path).
    template_file_dropped : Signal
        Emitted when a template file is dropped (path).
    preset_selected : Signal
        Emitted when a preset is selected (name).
    preset_mode_changed : Signal
        Emitted when preset mode is toggled (enabled).
    """

    source_file_dropped = Signal(str)
    template_file_dropped = Signal(str)
    preset_selected = Signal(str)
    preset_mode_changed = Signal(bool)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._last_directory = ""
        self._preset_mode = False
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Set up the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Header
        header = QLabel("Load FDL Files")
        header.setObjectName("headerLabel")
        layout.addWidget(header)

        # Source FDL drop zone
        self._source_zone = FileDropZone(
            extensions=[".fdl"],
            title="Source FDL",
            hint_text="Drop file here or click to browse",
            show_extensions=False,
        )
        layout.addWidget(self._source_zone)

        # Template FDL drop zone
        self._template_zone = FileDropZone(
            extensions=[".fdl"],
            title="Template FDL",
            hint_text="Drop file here or click to browse",
            show_extensions=False,
        )
        layout.addWidget(self._template_zone)

        # Preset selector (below Template FDL)
        preset_container = QWidget()
        preset_layout = QVBoxLayout(preset_container)
        preset_layout.setContentsMargins(0, 4, 0, 0)
        preset_layout.setSpacing(4)

        # Use preset checkbox
        self._use_preset_check = QCheckBox("Use Template Preset")
        preset_layout.addWidget(self._use_preset_check)

        # Preset combo
        self._preset_combo = QComboBox()
        self._preset_combo.addItems(get_preset_names())
        self._preset_combo.setEnabled(False)
        preset_layout.addWidget(self._preset_combo)

        layout.addWidget(preset_container)

    def _connect_signals(self) -> None:
        """Connect signals."""
        self._source_zone.file_dropped.connect(self._on_source_dropped)
        self._source_zone.clicked.connect(self._browse_source)

        self._template_zone.file_dropped.connect(self._on_template_dropped)
        self._template_zone.clicked.connect(self._browse_template)

        # Preset signals
        self._use_preset_check.toggled.connect(self._on_preset_mode_changed)
        self._preset_combo.currentTextChanged.connect(self._on_preset_selected)

    def _on_source_dropped(self, path: str) -> None:
        """Handle source file drop."""
        self._last_directory = str(Path(path).parent)
        self.source_file_dropped.emit(path)

    def _on_template_dropped(self, path: str) -> None:
        """Handle template file drop."""
        self._last_directory = str(Path(path).parent)
        self.template_file_dropped.emit(path)

    def _browse_source(self) -> None:
        """Open file dialog for source FDL."""
        path, _ = QFileDialog.getOpenFileName(self, "Open Source FDL", self._last_directory, "FDL Files (*.fdl);;All Files (*)")
        if path:
            self._on_source_dropped(path)

    def _browse_template(self) -> None:
        """Open file dialog for template FDL."""
        path, _ = QFileDialog.getOpenFileName(self, "Open Template FDL", self._last_directory, "FDL Files (*.fdl);;All Files (*)")
        if path:
            self._on_template_dropped(path)

    def set_source_loaded(self, loaded: bool, filename: str = "") -> None:
        """
        Set the source loaded state.

        Parameters
        ----------
        loaded : bool
            Whether a source is loaded.
        filename : str, optional
            The filename to display.
        """
        self._source_zone.set_loaded(loaded, filename)

    def set_template_loaded(self, loaded: bool, filename: str = "") -> None:
        """
        Set the template loaded state.

        Parameters
        ----------
        loaded : bool
            Whether a template is loaded.
        filename : str, optional
            The filename to display.
        """
        self._template_zone.set_loaded(loaded, filename)

    @Slot(bool)
    def _on_preset_mode_changed(self, enabled: bool) -> None:
        """Handle preset mode toggle."""
        self._preset_mode = enabled
        self._preset_combo.setEnabled(enabled)
        self._template_zone.set_disabled_state(enabled)
        self.preset_mode_changed.emit(enabled)

        # If enabling preset mode, immediately emit the current preset
        if enabled:
            self.preset_selected.emit(self._preset_combo.currentText())

    @Slot(str)
    def _on_preset_selected(self, name: str) -> None:
        """Handle preset selection."""
        # Only emit if preset mode is enabled
        if self._preset_mode:
            self.preset_selected.emit(name)

    def is_preset_mode(self) -> bool:
        """
        Check if preset mode is active.

        Returns
        -------
        bool
            True if using preset mode instead of FDL file.
        """
        return self._preset_mode
