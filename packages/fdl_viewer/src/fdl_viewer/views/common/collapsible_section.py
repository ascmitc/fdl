# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Collapsible section widget.

A section with a header that can be expanded/collapsed.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class CollapsibleSection(QWidget):
    """
    A collapsible section with a clickable header.

    Parameters
    ----------
    title : str
        The section title.
    parent : QWidget, optional
        Parent widget.
    collapsed : bool, optional
        Initial collapsed state.

    Attributes
    ----------
    collapsed_changed : Signal
        Emitted when collapsed state changes (bool).
    """

    collapsed_changed = Signal(bool)

    def __init__(
        self,
        title: str,
        parent: QWidget | None = None,
        collapsed: bool = False,
    ) -> None:
        super().__init__(parent)
        self._title = title
        self._collapsed = collapsed
        self._content_widget: QWidget | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        self._header = QFrame()
        self._header.setObjectName("collapsibleHeader")
        self._header.setCursor(Qt.PointingHandCursor)
        self._header.mousePressEvent = self._on_header_clicked

        header_layout = QHBoxLayout(self._header)
        header_layout.setContentsMargins(8, 6, 8, 6)

        # Arrow indicator
        self._arrow = QLabel("▶")
        self._arrow.setObjectName("secondaryLabel")
        header_layout.addWidget(self._arrow)

        # Title
        self._title_label = QLabel(self._title)
        self._title_label.setObjectName("titleLabel")
        header_layout.addWidget(self._title_label)

        header_layout.addStretch()

        layout.addWidget(self._header)

        # Content container
        self._content_container = QWidget()
        self._content_layout = QVBoxLayout(self._content_container)
        self._content_layout.setContentsMargins(0, 4, 0, 0)
        self._content_layout.setSpacing(0)

        layout.addWidget(self._content_container)

        # Set initial state
        self._update_collapsed_state()

    def _on_header_clicked(self, event) -> None:
        """Handle header click."""
        self.set_collapsed(not self._collapsed)

    def _update_collapsed_state(self) -> None:
        """Update the visual state based on collapsed."""
        if self._collapsed:
            self._arrow.setText("▶")
            self._content_container.hide()
        else:
            self._arrow.setText("▼")
            self._content_container.show()

    def set_collapsed(self, collapsed: bool) -> None:
        """
        Set the collapsed state.

        Parameters
        ----------
        collapsed : bool
            Whether the section should be collapsed.
        """
        if self._collapsed != collapsed:
            self._collapsed = collapsed
            self._update_collapsed_state()
            self.collapsed_changed.emit(collapsed)

    def is_collapsed(self) -> bool:
        """
        Get the collapsed state.

        Returns
        -------
        bool
            True if collapsed.
        """
        return self._collapsed

    def set_content_widget(self, widget: QWidget) -> None:
        """
        Set the content widget.

        Parameters
        ----------
        widget : QWidget
            The widget to show in the content area.
        """
        # Remove old widget if any
        if self._content_widget:
            self._content_layout.removeWidget(self._content_widget)
            self._content_widget.setParent(None)

        self._content_widget = widget
        self._content_layout.addWidget(widget)

    def content_widget(self) -> QWidget | None:
        """
        Get the content widget.

        Returns
        -------
        QWidget or None
            The content widget.
        """
        return self._content_widget

    def set_title(self, title: str) -> None:
        """
        Set the section title.

        Parameters
        ----------
        title : str
            The new title.
        """
        self._title = title
        self._title_label.setText(title)

    def title(self) -> str:
        """
        Get the section title.

        Returns
        -------
        str
            The title.
        """
        return self._title
