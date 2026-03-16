# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Recent files view for FDL Viewer.

Displays a list of recently opened files.
"""

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from fdl_viewer.models.recent_files import RecentFilesModel


class RecentFilesView(QWidget):
    """
    View for displaying recent files.

    Parameters
    ----------
    model : RecentFilesModel
        The recent files model.
    parent : QWidget, optional
        Parent widget.

    Attributes
    ----------
    file_selected : Signal
        Emitted when a file is selected (path, file_type).
    """

    file_selected = Signal(str, str)

    def __init__(self, model: RecentFilesModel, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._model = model
        self._setup_ui()
        self._connect_signals()
        self._refresh()

    def _setup_ui(self) -> None:
        """Set up the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Group box
        group = QGroupBox("Recent Files")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(4)

        # List widget
        self._list = QListWidget()
        self._list.setMaximumHeight(120)
        self._list.setAlternatingRowColors(True)
        group_layout.addWidget(self._list)

        # Clear button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self._clear_btn = QPushButton("Clear")
        self._clear_btn.setMaximumWidth(60)
        self._clear_btn.clicked.connect(self._on_clear)
        btn_layout.addWidget(self._clear_btn)
        group_layout.addLayout(btn_layout)

        layout.addWidget(group)

    def _connect_signals(self) -> None:
        """Connect signals."""
        self._model.files_changed.connect(self._refresh)
        self._list.itemDoubleClicked.connect(self._on_item_clicked)

    @Slot()
    def _refresh(self) -> None:
        """Refresh the list from the model."""
        self._list.clear()
        for recent in self._model.get_files():
            item = QListWidgetItem()
            # Show type indicator with filename
            type_label = "[S]" if recent.file_type == "source" else "[T]"
            item.setText(f"{type_label} {recent.filename}")
            item.setToolTip(f"{recent.path}\n\nType: {recent.file_type.title()}\nDouble-click to load as {recent.file_type}")
            item.setData(Qt.UserRole, recent.path)
            item.setData(Qt.UserRole + 1, recent.file_type)

            # Color code by type - green for source, cyan for template
            from PySide6.QtGui import QColor

            if recent.file_type == "source":
                item.setForeground(QColor(0, 204, 102))  # Green
            else:
                item.setForeground(QColor(0, 180, 255))  # Cyan/blue

            self._list.addItem(item)

        self._clear_btn.setEnabled(not self._model.is_empty)

    @Slot(QListWidgetItem)
    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        """Handle item click."""
        path = item.data(Qt.UserRole)
        file_type = item.data(Qt.UserRole + 1)
        if path:
            self.file_selected.emit(path, file_type)

    @Slot()
    def _on_clear(self) -> None:
        """Handle clear button click."""
        self._model.clear()
