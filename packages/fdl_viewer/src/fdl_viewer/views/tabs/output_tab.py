# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Output tab for FDL Viewer.

Displays the output/transformed FDL canvas visualization.
"""

from typing import TYPE_CHECKING, Optional

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

if TYPE_CHECKING:
    from fdl import CanvasTemplate, PointFloat


class OutputTab(QWidget):
    """
    Output tab showing the transformed FDL canvas visualization.

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

        # Placeholder when no output
        self._placeholder = QWidget()
        placeholder_layout = QVBoxLayout(self._placeholder)
        placeholder_label = QLabel("No transformation result yet.\n\nLoad a source FDL, configure a template, and click TRANSFORM.")
        placeholder_label.setObjectName("placeholderLabel")
        placeholder_label.setAlignment(Qt.AlignCenter)
        placeholder_layout.addWidget(placeholder_label)
        layout.addWidget(self._placeholder)

        # Canvas widget (hidden initially)
        self._canvas_container = QWidget()
        canvas_layout = QVBoxLayout(self._canvas_container)
        canvas_layout.setContentsMargins(0, 0, 0, 0)
        canvas_layout.setSpacing(0)

        self._canvas = CanvasWidget()
        self._canvas.set_is_source(False)
        canvas_layout.addWidget(self._canvas, 1)

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

        # Separator
        controls_layout.addSpacing(20)

        # Visibility toolbar
        self._visibility_toolbar = VisibilityToolbar()
        controls_layout.addWidget(self._visibility_toolbar, 1)

        canvas_layout.addWidget(controls)

        self._canvas_container.hide()
        layout.addWidget(self._canvas_container)

    def _connect_signals(self) -> None:
        """Connect signals."""
        self._canvas.zoom_changed.connect(self._on_zoom_changed)

    def set_fdl_model(self, model: FDLModel | None) -> None:
        """
        Set the FDL model to display.

        Parameters
        ----------
        model : FDLModel or None
            The FDL model.
        """
        if model:
            self._placeholder.hide()
            self._canvas_container.show()
            self._canvas.set_fdl_model(model)
            from PySide6.QtCore import QTimer

            QTimer.singleShot(100, self._canvas.fit_in_view)
        else:
            self._placeholder.show()
            self._canvas_container.hide()
            self._canvas.set_fdl_model(None)

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

    def set_hud_data(
        self,
        source_model: FDLModel | None,
        template: Optional["CanvasTemplate"],
        output_model: FDLModel | None = None,
        content_translation: Optional["PointFloat"] = None,
        scale_factor: float | None = None,
    ) -> None:
        """
        Set the source model, template, and output data for HUD display.

        Parameters
        ----------
        source_model : FDLModel or None
            The original source FDL model.
        template : CanvasTemplate or None
            The template used for transformation.
        output_model : FDLModel or None
            The output FDL model from transformation.
        content_translation : PointFloat or None
            The content translation applied during transformation.
        scale_factor : float or None
            The scale factor applied during transformation.
        """
        self._canvas.set_hud_data(source_model, template, output_model, content_translation, scale_factor)
