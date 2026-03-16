# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Source selector view for FDL Viewer.

Provides cascading dropdowns for selecting context/canvas/framing decisions.
"""

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class SourceSelectorView(QWidget):
    """
    Source selector with cascading dropdowns.

    Provides Context -> Canvas -> Framing Decision selection with
    automatic cascading when parent selections change.

    Parameters
    ----------
    parent : QWidget, optional
        Parent widget.

    Attributes
    ----------
    context_selected : Signal
        Emitted when a context is selected (label).
    canvas_selected : Signal
        Emitted when a canvas is selected (id).
    framing_selected : Signal
        Emitted when a framing decision is selected (id).
    """

    context_selected = Signal(str)
    canvas_selected = Signal(str)
    framing_selected = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Set up the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Group box
        group = QGroupBox("Source Selection")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(8)

        # Context selector
        context_layout = QHBoxLayout()
        context_label = QLabel("Context:")
        context_label.setMinimumWidth(80)
        self._context_combo = QComboBox()
        self._context_combo.setMinimumWidth(200)
        context_layout.addWidget(context_label)
        context_layout.addWidget(self._context_combo, 1)
        group_layout.addLayout(context_layout)

        # Canvas selector
        canvas_layout = QHBoxLayout()
        canvas_label = QLabel("Canvas:")
        canvas_label.setMinimumWidth(80)
        self._canvas_combo = QComboBox()
        self._canvas_combo.setMinimumWidth(200)
        canvas_layout.addWidget(canvas_label)
        canvas_layout.addWidget(self._canvas_combo, 1)
        group_layout.addLayout(canvas_layout)

        # Framing decision selector
        framing_layout = QHBoxLayout()
        framing_label = QLabel("Framing:")
        framing_label.setMinimumWidth(80)
        self._framing_combo = QComboBox()
        self._framing_combo.setMinimumWidth(200)
        framing_layout.addWidget(framing_label)
        framing_layout.addWidget(self._framing_combo, 1)
        group_layout.addLayout(framing_layout)

        # Info label
        self._info_label = QLabel("")
        self._info_label.setObjectName("secondaryLabel")
        self._info_label.setWordWrap(True)
        group_layout.addWidget(self._info_label)

        layout.addWidget(group)

    def _connect_signals(self) -> None:
        """Connect signals."""
        self._context_combo.currentTextChanged.connect(self._on_context_changed)
        self._canvas_combo.currentIndexChanged.connect(self._on_canvas_changed)
        self._framing_combo.currentIndexChanged.connect(self._on_framing_changed)

    @Slot(str)
    def _on_context_changed(self, text: str) -> None:
        """Handle context selection change."""
        if text:
            self.context_selected.emit(text)

    @Slot(int)
    def _on_canvas_changed(self, index: int) -> None:
        """Handle canvas selection change."""
        if index >= 0:
            canvas_id = self._canvas_combo.currentData()
            if canvas_id:
                self.canvas_selected.emit(canvas_id)

    @Slot(int)
    def _on_framing_changed(self, index: int) -> None:
        """Handle framing decision selection change."""
        if index >= 0:
            fd_id = self._framing_combo.currentData()
            if fd_id:
                self.framing_selected.emit(fd_id)

    @Slot(list)
    def set_contexts(self, labels: list[str]) -> None:
        """
        Set the available contexts.

        Parameters
        ----------
        labels : List[str]
            The list of context labels.
        """
        self._context_combo.blockSignals(True)
        self._context_combo.clear()
        self._context_combo.addItems(labels)
        self._context_combo.blockSignals(False)

        if labels:
            self._context_combo.setCurrentIndex(0)

    @Slot(list)
    def set_canvases(self, canvases: list[tuple[str, str]]) -> None:
        """
        Set the available canvases.

        Parameters
        ----------
        canvases : List[Tuple[str, str]]
            List of (canvas_id, label) tuples.
        """
        self._canvas_combo.blockSignals(True)
        self._canvas_combo.clear()
        for canvas_id, label in canvases:
            self._canvas_combo.addItem(label, canvas_id)
        self._canvas_combo.blockSignals(False)

        if canvases:
            self._canvas_combo.setCurrentIndex(0)

    @Slot(list)
    def set_framings(self, framings: list[tuple[str, str]]) -> None:
        """
        Set the available framing decisions.

        Parameters
        ----------
        framings : List[Tuple[str, str]]
            List of (fd_id, label) tuples.
        """
        self._framing_combo.blockSignals(True)
        self._framing_combo.clear()
        for fd_id, label in framings:
            self._framing_combo.addItem(label, fd_id)
        self._framing_combo.blockSignals(False)

        if framings:
            self._framing_combo.setCurrentIndex(0)

    def set_info(self, info: str) -> None:
        """
        Set the info label text.

        Parameters
        ----------
        info : str
            The info text to display.
        """
        self._info_label.setText(info)

    def get_selection(self) -> tuple[str, str, str]:
        """
        Get the current selection.

        Returns
        -------
        Tuple[str, str, str]
            (context_label, canvas_id, framing_id)
        """
        context = self._context_combo.currentText()
        canvas_id = self._canvas_combo.currentData() or ""
        fd_id = self._framing_combo.currentData() or ""
        return (context, canvas_id, fd_id)

    def set_enabled(self, enabled: bool) -> None:
        """
        Enable or disable all controls.

        Parameters
        ----------
        enabled : bool
            Whether to enable the controls.
        """
        self._context_combo.setEnabled(enabled)
        self._canvas_combo.setEnabled(enabled)
        self._framing_combo.setEnabled(enabled)
