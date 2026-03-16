# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Source tab for FDL Viewer.

Displays the source FDL canvas visualization.
"""

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from fdl_viewer.models.app_state import AppState
from fdl_viewer.models.fdl_model import FDLModel
from fdl_viewer.views.canvas.canvas_widget import CanvasWidget
from fdl_viewer.views.canvas.visibility_toolbar import VisibilityToolbar


class SourceTab(QWidget):
    """
    Source tab showing the source FDL canvas visualization.

    Contains the canvas widget with zoom controls and display options.

    Parameters
    ----------
    parent : QWidget, optional
        Parent widget.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._app_state = AppState.instance()
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Set up the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Canvas widget
        self._canvas = CanvasWidget()
        self._canvas.set_is_source(True)
        layout.addWidget(self._canvas, 1)

        # Controls bar
        controls = QWidget()
        controls.setObjectName("controlsBar")
        controls.setMaximumHeight(40)
        controls_layout = QHBoxLayout(controls)
        controls_layout.setContentsMargins(8, 4, 8, 4)

        # Zoom controls
        self._zoom_out_btn = QPushButton("-")
        self._zoom_out_btn.setMaximumWidth(30)
        self._zoom_out_btn.clicked.connect(self._canvas.zoom_out)
        controls_layout.addWidget(self._zoom_out_btn)

        self._zoom_label = QLabel("100%")
        self._zoom_label.setMinimumWidth(50)
        self._zoom_label.setAlignment(Qt.AlignCenter)
        controls_layout.addWidget(self._zoom_label)

        self._zoom_in_btn = QPushButton("+")
        self._zoom_in_btn.setMaximumWidth(30)
        self._zoom_in_btn.clicked.connect(self._canvas.zoom_in)
        controls_layout.addWidget(self._zoom_in_btn)

        self._fit_btn = QPushButton("Fit")
        self._fit_btn.setMaximumWidth(40)
        self._fit_btn.clicked.connect(self._canvas.fit_in_view)
        controls_layout.addWidget(self._fit_btn)

        self._reset_btn = QPushButton("100%")
        self._reset_btn.setMaximumWidth(40)
        self._reset_btn.clicked.connect(self._canvas.reset_zoom)
        controls_layout.addWidget(self._reset_btn)

        # Separator
        controls_layout.addSpacing(20)

        # Visibility toolbar
        self._visibility_toolbar = VisibilityToolbar()
        controls_layout.addWidget(self._visibility_toolbar, 1)

        layout.addWidget(controls)

    def _connect_signals(self) -> None:
        """Connect signals."""
        self._canvas.zoom_changed.connect(self._on_zoom_changed)
        # Refresh canvas when selection changes to ensure image displays correctly
        self._app_state.selection_changed.connect(self._on_selection_changed)

    @Slot(str, str, str)
    def _on_selection_changed(self, context: str, canvas: str, framing: str) -> None:
        """Handle selection change - refresh canvas to update display."""
        self._canvas.refresh()

    def set_fdl_model(self, model: FDLModel | None) -> None:
        """
        Set the FDL model to display.

        Parameters
        ----------
        model : FDLModel or None
            The FDL model.
        """
        self._canvas.set_fdl_model(model)
        if model:
            # Fit after a short delay to ensure layout is ready
            from PySide6.QtCore import QTimer

            QTimer.singleShot(100, self._canvas.fit_in_view)

    @Slot(float)
    def _on_zoom_changed(self, scale: float) -> None:
        """Handle zoom change."""
        self._zoom_label.setText(f"{int(scale * 100)}%")

    def set_image(self, pixmap, width: int, height: int) -> None:
        """
        Set the image underlay on the canvas.

        Parameters
        ----------
        pixmap : QPixmap
            The image pixmap.
        width : int
            Original image width.
        height : int
            Original image height.
        """
        self._canvas.set_image(pixmap, width, height)

    def clear_image(self) -> None:
        """Clear the image underlay."""
        self._canvas.clear_image()
