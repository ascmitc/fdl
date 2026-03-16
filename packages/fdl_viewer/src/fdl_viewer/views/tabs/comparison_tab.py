# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Comparison tab for FDL Viewer.

Provides side-by-side comparison of source and output FDLs.
"""

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from fdl_viewer.models.app_state import AppState
from fdl_viewer.models.fdl_model import FDLModel
from fdl_viewer.views.canvas.canvas_widget import CanvasWidget
from fdl_viewer.views.canvas.visibility_toolbar import VisibilityToolbar


class ComparisonTab(QWidget):
    """
    Comparison tab for side-by-side viewing of source and output.

    Provides:
    - Side-by-side mode with synchronized pan/zoom
    - Overlay mode (future)

    Parameters
    ----------
    parent : QWidget, optional
        Parent widget.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._app_state = AppState.instance()
        self._source_model: FDLModel | None = None
        self._output_model: FDLModel | None = None
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Set up the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Placeholder when no comparison available
        self._placeholder = QWidget()
        placeholder_layout = QVBoxLayout(self._placeholder)
        placeholder_label = QLabel("Load a source FDL and perform a transformation\nto compare source and output.")
        placeholder_label.setObjectName("placeholderLabel")
        placeholder_label.setAlignment(Qt.AlignCenter)
        placeholder_layout.addWidget(placeholder_label)
        layout.addWidget(self._placeholder)

        # Comparison container
        self._comparison_container = QWidget()
        comparison_layout = QVBoxLayout(self._comparison_container)
        comparison_layout.setContentsMargins(0, 0, 0, 0)
        comparison_layout.setSpacing(0)

        # Controls bar
        controls = QWidget()
        controls.setObjectName("controlsBar")
        controls.setMaximumHeight(40)
        controls_layout = QHBoxLayout(controls)
        controls_layout.setContentsMargins(8, 4, 8, 4)

        # Zoom controls
        self._zoom_out_btn = QPushButton("-")
        self._zoom_out_btn.setMaximumWidth(30)
        self._zoom_out_btn.clicked.connect(self._zoom_out_both)
        controls_layout.addWidget(self._zoom_out_btn)

        self._zoom_label = QLabel("100%")
        self._zoom_label.setMinimumWidth(50)
        self._zoom_label.setAlignment(Qt.AlignCenter)
        controls_layout.addWidget(self._zoom_label)

        self._zoom_in_btn = QPushButton("+")
        self._zoom_in_btn.setMaximumWidth(30)
        self._zoom_in_btn.clicked.connect(self._zoom_in_both)
        controls_layout.addWidget(self._zoom_in_btn)

        self._fit_btn = QPushButton("Fit")
        self._fit_btn.setMaximumWidth(40)
        self._fit_btn.clicked.connect(self._fit_both)
        controls_layout.addWidget(self._fit_btn)

        self._reset_btn = QPushButton("100%")
        self._reset_btn.setMaximumWidth(40)
        self._reset_btn.clicked.connect(self._reset_zoom_both)
        controls_layout.addWidget(self._reset_btn)

        # Separator
        controls_layout.addSpacing(20)

        # Visibility toolbar
        self._visibility_toolbar = VisibilityToolbar()
        controls_layout.addWidget(self._visibility_toolbar, 1)

        # Splitter with two canvases
        self._splitter = QSplitter(Qt.Horizontal)

        # Source panel
        source_panel = QWidget()
        source_layout = QVBoxLayout(source_panel)
        source_layout.setContentsMargins(0, 0, 0, 0)
        source_layout.setSpacing(0)

        source_header = QLabel("Source")
        source_header.setObjectName("sourceHeader")
        source_header.setAlignment(Qt.AlignCenter)
        source_layout.addWidget(source_header)

        self._source_canvas = CanvasWidget()
        self._source_canvas.set_is_source(True)
        source_layout.addWidget(self._source_canvas, 1)

        self._splitter.addWidget(source_panel)

        # Output panel
        output_panel = QWidget()
        output_layout = QVBoxLayout(output_panel)
        output_layout.setContentsMargins(0, 0, 0, 0)
        output_layout.setSpacing(0)

        output_header = QLabel("Output")
        output_header.setObjectName("outputHeader")
        output_header.setAlignment(Qt.AlignCenter)
        output_layout.addWidget(output_header)

        self._output_canvas = CanvasWidget()
        self._output_canvas.set_is_source(False)
        output_layout.addWidget(self._output_canvas, 1)

        self._splitter.addWidget(output_panel)

        # Add splitter first (takes up space), then controls at bottom
        comparison_layout.addWidget(self._splitter, 1)
        comparison_layout.addWidget(controls)

        self._comparison_container.hide()
        layout.addWidget(self._comparison_container)

    def _connect_signals(self) -> None:
        """Connect signals."""
        # Connect zoom signals from both canvases
        self._source_canvas.zoom_changed.connect(self._on_source_zoom_changed)
        self._output_canvas.zoom_changed.connect(self._on_output_zoom_changed)

    def set_source_model(self, model: FDLModel | None) -> None:
        """
        Set the source FDL model.

        Parameters
        ----------
        model : FDLModel or None
            The source model.
        """
        self._source_model = model
        self._source_canvas.set_fdl_model(model)
        self._update_visibility()

    def set_output_model(self, model: FDLModel | None) -> None:
        """
        Set the output FDL model.

        Parameters
        ----------
        model : FDLModel or None
            The output model.
        """
        self._output_model = model
        self._output_canvas.set_fdl_model(model)
        self._update_visibility()
        if model:
            from PySide6.QtCore import QTimer

            QTimer.singleShot(100, self._fit_both)

    def _update_visibility(self) -> None:
        """Update visibility based on loaded models."""
        if self._source_model and self._output_model:
            self._placeholder.hide()
            self._comparison_container.show()
            # Auto-fit both canvases when comparison becomes available
            from PySide6.QtCore import QTimer

            QTimer.singleShot(100, self._fit_both)
        else:
            self._placeholder.show()
            self._comparison_container.hide()

    @Slot()
    def _fit_both(self) -> None:
        """Fit both canvases."""
        self._source_canvas.fit_in_view()
        self._output_canvas.fit_in_view()

    @Slot()
    def _zoom_in_both(self) -> None:
        """Zoom in both canvases."""
        self._source_canvas.zoom_in()
        self._output_canvas.zoom_in()

    @Slot()
    def _zoom_out_both(self) -> None:
        """Zoom out both canvases."""
        self._source_canvas.zoom_out()
        self._output_canvas.zoom_out()

    @Slot()
    def _reset_zoom_both(self) -> None:
        """Reset zoom on both canvases to 100%."""
        self._source_canvas.reset_zoom()
        self._output_canvas.reset_zoom()

    @Slot(float)
    def _on_source_zoom_changed(self, scale: float) -> None:
        """Handle source canvas zoom change."""
        self._zoom_label.setText(f"{int(scale * 100)}%")

    @Slot(float)
    def _on_output_zoom_changed(self, scale: float) -> None:
        """Handle output canvas zoom change."""
        # Could sync or just ignore - using source canvas zoom for display
        pass

    def set_image(self, pixmap, width: int, height: int) -> None:
        """
        Set the image underlay on the source canvas only.

        Parameters
        ----------
        pixmap : QPixmap
            The image pixmap.
        width : int
            Original image width.
        height : int
            Original image height.
        """
        self._source_canvas.set_image(pixmap, width, height)

    def set_source_image(self, pixmap, width: int, height: int) -> None:
        """
        Set the image underlay on the source canvas.

        Parameters
        ----------
        pixmap : QPixmap
            The source image pixmap.
        width : int
            Original image width.
        height : int
            Original image height.
        """
        self._source_canvas.set_image(pixmap, width, height)

    def set_output_image(self, pixmap, width: int, height: int) -> None:
        """
        Set the image underlay on the output canvas.

        Parameters
        ----------
        pixmap : QPixmap
            The transformed output image pixmap.
        width : int
            Output image width.
        height : int
            Output image height.
        """
        self._output_canvas.set_image(pixmap, width, height)

    def clear_image(self) -> None:
        """Clear the image underlay from both canvases."""
        self._source_canvas.clear_image()
        self._output_canvas.clear_image()
