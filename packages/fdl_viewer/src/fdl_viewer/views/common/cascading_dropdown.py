# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Cascading dropdown widget.

A reusable widget for cascading/dependent dropdown selections.
"""

from typing import Any

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class CascadingDropdown(QWidget):
    """
    A cascading dropdown where child options depend on parent selection.

    Parameters
    ----------
    parent : QWidget, optional
        Parent widget.
    label : str, optional
        Label text for the dropdown.

    Attributes
    ----------
    selection_changed : Signal
        Emitted when selection changes (selected_id, selected_data).
    """

    selection_changed = Signal(str, object)

    def __init__(
        self,
        parent: QWidget | None = None,
        label: str | None = None,
    ) -> None:
        super().__init__(parent)
        self._label_text = label
        self._items: list[dict[str, Any]] = []
        self._id_key = "id"
        self._label_key = "label"
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Optional label
        if self._label_text:
            label = QLabel(self._label_text)
            label.setObjectName("secondaryLabel")
            layout.addWidget(label)

        # Combo box (uses base QComboBox styles from stylesheet)
        self._combo = QComboBox()
        self._combo.currentIndexChanged.connect(self._on_index_changed)
        layout.addWidget(self._combo)

    def _on_index_changed(self, index: int) -> None:
        """Handle combo box selection change."""
        if index >= 0 and index < len(self._items):
            item = self._items[index]
            item_id = item.get(self._id_key, "")
            self.selection_changed.emit(item_id, item)

    def set_items(
        self,
        items: list[dict[str, Any]],
        id_key: str = "id",
        label_key: str = "label",
    ) -> None:
        """
        Set the items in the dropdown.

        Parameters
        ----------
        items : list of dict
            The items to populate.
        id_key : str, optional
            Key to use for item ID.
        label_key : str, optional
            Key to use for display label.
        """
        self._items = items
        self._id_key = id_key
        self._label_key = label_key

        self._combo.blockSignals(True)
        self._combo.clear()

        for item in items:
            label = item.get(label_key, item.get(id_key, ""))
            self._combo.addItem(str(label))

        self._combo.blockSignals(False)

        # Auto-select first item
        if items:
            self._combo.setCurrentIndex(0)
            self._on_index_changed(0)

    def clear(self) -> None:
        """Clear all items."""
        self._items = []
        self._combo.blockSignals(True)
        self._combo.clear()
        self._combo.blockSignals(False)

    def selected_id(self) -> str | None:
        """
        Get the selected item ID.

        Returns
        -------
        str or None
            The selected ID.
        """
        index = self._combo.currentIndex()
        if index >= 0 and index < len(self._items):
            return self._items[index].get(self._id_key)
        return None

    def selected_item(self) -> dict[str, Any] | None:
        """
        Get the selected item data.

        Returns
        -------
        dict or None
            The selected item.
        """
        index = self._combo.currentIndex()
        if index >= 0 and index < len(self._items):
            return self._items[index]
        return None

    def set_selected_id(self, item_id: str) -> bool:
        """
        Set the selection by ID.

        Parameters
        ----------
        item_id : str
            The ID to select.

        Returns
        -------
        bool
            True if found and selected.
        """
        for i, item in enumerate(self._items):
            if item.get(self._id_key) == item_id:
                self._combo.setCurrentIndex(i)
                return True
        return False

    def count(self) -> int:
        """
        Get the number of items.

        Returns
        -------
        int
            The item count.
        """
        return len(self._items)

    def set_enabled(self, enabled: bool) -> None:
        """
        Enable/disable the dropdown.

        Parameters
        ----------
        enabled : bool
            Whether to enable.
        """
        self._combo.setEnabled(enabled)

    def set_placeholder_text(self, text: str) -> None:
        """
        Set placeholder text when empty.

        Parameters
        ----------
        text : str
            The placeholder text.
        """
        self._combo.setPlaceholderText(text)
