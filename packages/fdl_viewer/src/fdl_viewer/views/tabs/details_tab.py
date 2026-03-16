# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Details tab for FDL Viewer.

Displays transformation metrics and provides JSON export functionality.
"""

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from fdl_viewer.controllers.export_controller import ExportController
from fdl_viewer.models.app_state import AppState
from fdl_viewer.models.fdl_model import FDLModel


class DetailsTab(QWidget):
    """
    Details tab showing transformation metrics and JSON export.

    Displays:
    - Transformation parameters
    - Output dimensions and anchor points
    - Full JSON preview
    - Export buttons

    Parameters
    ----------
    parent : QWidget, optional
        Parent widget.

    Attributes
    ----------
    export_image_requested : Signal
        Emitted when image export is requested (same format as source).
    export_proxy_requested : Signal
        Emitted when proxy export is requested (PNG/JPEG).
    export_unit_test_requested : Signal
        Emitted when unit test export is requested.
    """

    export_image_requested = Signal()
    export_proxy_requested = Signal()
    export_unit_test_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._app_state = AppState.instance()
        self._export_controller = ExportController()
        self._source_model: FDLModel | None = None
        self._output_model: FDLModel | None = None
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Set up the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Placeholder when no output
        self._placeholder = QLabel("No transformation result to display.\n\nPerform a transformation to see details.")
        self._placeholder.setObjectName("placeholderLabel")
        self._placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._placeholder)

        # Details container
        self._details_container = QWidget()
        details_layout = QVBoxLayout(self._details_container)
        details_layout.setContentsMargins(0, 0, 0, 0)

        # Splitter for metrics and JSON
        splitter = QSplitter(Qt.Vertical)

        # Metrics panel
        metrics_widget = QWidget()
        metrics_layout = QVBoxLayout(metrics_widget)
        metrics_layout.setContentsMargins(0, 0, 0, 0)

        # Comparison group - Source vs Output
        compare_group = QGroupBox("Source vs Output Comparison")
        compare_grid = QGridLayout(compare_group)
        compare_grid.setSpacing(8)

        # Header row
        source_header = QLabel("Source")
        source_header.setObjectName("headerLabel")
        source_header.setProperty("sourceColor", True)
        source_header.setAlignment(Qt.AlignCenter)
        output_header = QLabel("Output")
        output_header.setObjectName("headerLabel")
        output_header.setProperty("outputColor", True)
        output_header.setAlignment(Qt.AlignCenter)

        compare_grid.addWidget(QLabel(""), 0, 0)
        compare_grid.addWidget(source_header, 0, 1)
        compare_grid.addWidget(output_header, 0, 2)

        row = 1

        # Context ID row
        compare_grid.addWidget(QLabel("Context ID:"), row, 0)
        self._source_context_id = QLabel("-")
        self._source_context_id.setProperty("sourceColor", True)
        compare_grid.addWidget(self._source_context_id, row, 1)
        self._output_context_id = QLabel("-")
        self._output_context_id.setProperty("outputColor", True)
        compare_grid.addWidget(self._output_context_id, row, 2)
        row += 1

        # Canvas ID row
        compare_grid.addWidget(QLabel("Canvas ID:"), row, 0)
        self._source_canvas_id = QLabel("-")
        self._source_canvas_id.setProperty("sourceColor", True)
        compare_grid.addWidget(self._source_canvas_id, row, 1)
        self._output_canvas_id = QLabel("-")
        self._output_canvas_id.setProperty("outputColor", True)
        compare_grid.addWidget(self._output_canvas_id, row, 2)
        row += 1

        # Canvas Dimensions row
        compare_grid.addWidget(QLabel("Canvas Dims:"), row, 0)
        self._source_canvas_dims = QLabel("-")
        self._source_canvas_dims.setProperty("sourceColor", True)
        compare_grid.addWidget(self._source_canvas_dims, row, 1)
        self._output_canvas_dims = QLabel("-")
        self._output_canvas_dims.setProperty("outputColor", True)
        compare_grid.addWidget(self._output_canvas_dims, row, 2)
        row += 1

        # Effective Dimensions row
        compare_grid.addWidget(QLabel("Effective Dims:"), row, 0)
        self._source_effective_dims = QLabel("-")
        self._source_effective_dims.setProperty("sourceColor", True)
        compare_grid.addWidget(self._source_effective_dims, row, 1)
        self._output_effective_dims = QLabel("-")
        self._output_effective_dims.setProperty("outputColor", True)
        compare_grid.addWidget(self._output_effective_dims, row, 2)
        row += 1

        # Effective Anchor row
        compare_grid.addWidget(QLabel("Effective Anchor:"), row, 0)
        self._source_effective_anchor = QLabel("-")
        self._source_effective_anchor.setProperty("sourceColor", True)
        compare_grid.addWidget(self._source_effective_anchor, row, 1)
        self._output_effective_anchor = QLabel("-")
        self._output_effective_anchor.setProperty("outputColor", True)
        compare_grid.addWidget(self._output_effective_anchor, row, 2)
        row += 1

        # Framing Decision ID row
        compare_grid.addWidget(QLabel("Framing ID:"), row, 0)
        self._source_framing_id = QLabel("-")
        self._source_framing_id.setProperty("sourceColor", True)
        compare_grid.addWidget(self._source_framing_id, row, 1)
        self._output_framing_id = QLabel("-")
        self._output_framing_id.setProperty("outputColor", True)
        compare_grid.addWidget(self._output_framing_id, row, 2)
        row += 1

        # Framing Dimensions row
        compare_grid.addWidget(QLabel("Framing Dims:"), row, 0)
        self._source_framing_dims = QLabel("-")
        self._source_framing_dims.setProperty("sourceColor", True)
        compare_grid.addWidget(self._source_framing_dims, row, 1)
        self._output_framing_dims = QLabel("-")
        self._output_framing_dims.setProperty("outputColor", True)
        compare_grid.addWidget(self._output_framing_dims, row, 2)
        row += 1

        # Framing Anchor row
        compare_grid.addWidget(QLabel("Framing Anchor:"), row, 0)
        self._source_framing_anchor = QLabel("-")
        self._source_framing_anchor.setProperty("sourceColor", True)
        compare_grid.addWidget(self._source_framing_anchor, row, 1)
        self._output_framing_anchor = QLabel("-")
        self._output_framing_anchor.setProperty("outputColor", True)
        compare_grid.addWidget(self._output_framing_anchor, row, 2)
        row += 1

        # Protection Dimensions row
        compare_grid.addWidget(QLabel("Protection Dims:"), row, 0)
        self._source_protection_dims = QLabel("-")
        self._source_protection_dims.setProperty("sourceColor", True)
        compare_grid.addWidget(self._source_protection_dims, row, 1)
        self._output_protection_dims = QLabel("-")
        self._output_protection_dims.setProperty("outputColor", True)
        compare_grid.addWidget(self._output_protection_dims, row, 2)
        row += 1

        # Protection Anchor row
        compare_grid.addWidget(QLabel("Protection Anchor:"), row, 0)
        self._source_protection_anchor = QLabel("-")
        self._source_protection_anchor.setProperty("sourceColor", True)
        compare_grid.addWidget(self._source_protection_anchor, row, 1)
        self._output_protection_anchor = QLabel("-")
        self._output_protection_anchor.setProperty("outputColor", True)
        compare_grid.addWidget(self._output_protection_anchor, row, 2)

        # Set column stretch
        compare_grid.setColumnStretch(0, 1)
        compare_grid.setColumnStretch(1, 2)
        compare_grid.setColumnStretch(2, 2)

        metrics_layout.addWidget(compare_group)

        # Transform info group
        transform_group = QGroupBox("Transformation Info")
        transform_form = QFormLayout(transform_group)

        self._scale_label = QLabel("-")
        transform_form.addRow("Scale Factor:", self._scale_label)

        self._template_label = QLabel("-")
        transform_form.addRow("Template:", self._template_label)

        metrics_layout.addWidget(transform_group)

        splitter.addWidget(metrics_widget)

        # JSON preview panel
        json_widget = QWidget()
        json_layout = QVBoxLayout(json_widget)
        json_layout.setContentsMargins(0, 0, 0, 0)

        json_header = QHBoxLayout()
        json_header.addWidget(QLabel("JSON Preview"))
        json_header.addStretch()

        self._copy_btn = QPushButton("Copy to Clipboard")
        self._copy_btn.clicked.connect(self._on_copy_clicked)
        json_header.addWidget(self._copy_btn)

        self._export_btn = QPushButton("Export FDL...")
        self._export_btn.clicked.connect(self._on_export_clicked)
        json_header.addWidget(self._export_btn)

        self._export_image_btn = QPushButton("Export Image...")
        self._export_image_btn.clicked.connect(self._on_export_image_clicked)
        self._export_image_btn.setEnabled(False)
        json_header.addWidget(self._export_image_btn)

        self._export_proxy_btn = QPushButton("Export Proxy...")
        self._export_proxy_btn.clicked.connect(self._on_export_proxy_clicked)
        self._export_proxy_btn.setEnabled(False)
        json_header.addWidget(self._export_proxy_btn)

        self._export_unit_test_btn = QPushButton("Export Unit Test...")
        self._export_unit_test_btn.clicked.connect(self._on_export_unit_test_clicked)
        self._export_unit_test_btn.setEnabled(False)
        self._export_unit_test_btn.setToolTip("Export current transformation as a unit test scenario")
        json_header.addWidget(self._export_unit_test_btn)

        json_layout.addLayout(json_header)

        self._json_preview = QTextEdit()
        self._json_preview.setObjectName("jsonPreview")
        self._json_preview.setReadOnly(True)
        json_layout.addWidget(self._json_preview)

        splitter.addWidget(json_widget)

        # Set initial sizes
        splitter.setSizes([200, 400])

        details_layout.addWidget(splitter)

        self._details_container.hide()
        layout.addWidget(self._details_container)

    def _connect_signals(self) -> None:
        """Connect signals."""
        self._app_state.transform_result_changed.connect(self._on_transform_result)
        self._export_controller.copy_completed.connect(self._on_copy_completed)
        self._export_controller.export_completed.connect(self._on_export_completed)
        self._export_controller.error_occurred.connect(self._on_error)

    def set_source_model(self, model: FDLModel | None) -> None:
        """
        Set the source FDL model.

        Parameters
        ----------
        model : FDLModel or None
            The source model.
        """
        self._source_model = model
        self._update_display()

    def set_output_model(self, model: FDLModel | None) -> None:
        """
        Set the output FDL model.

        Parameters
        ----------
        model : FDLModel or None
            The output model.
        """
        self._output_model = model
        self._update_display()

    def _update_display(self) -> None:
        """Update the display based on current models."""
        if not self._output_model or not self._output_model.fdl:
            self._placeholder.show()
            self._details_container.hide()
            return

        self._placeholder.hide()
        self._details_container.show()

        # Update source column
        self._update_source_display()

        # Update output column
        self._update_output_display()

        # Template info
        if self._output_model.canvas_templates:
            template = self._output_model.canvas_templates[0]
            self._template_label.setText(template.label or template.id)

        # JSON preview
        json_str = self._export_controller.get_json_from_model(self._output_model)
        self._json_preview.setPlainText(json_str)

    def _update_source_display(self) -> None:
        """Update source column in comparison table."""
        # Reset all fields
        self._source_context_id.setText("-")
        self._source_canvas_id.setText("-")
        self._source_canvas_dims.setText("-")
        self._source_effective_dims.setText("-")
        self._source_effective_anchor.setText("-")
        self._source_framing_id.setText("-")
        self._source_framing_dims.setText("-")
        self._source_framing_anchor.setText("-")
        self._source_protection_dims.setText("-")
        self._source_protection_anchor.setText("-")

        if not self._source_model or not self._source_model.fdl:
            return

        model = self._source_model
        if model.contexts:
            context = model.contexts[0]
            self._source_context_id.setText(context.label or "-")

            if context.canvases:
                canvas = context.canvases[0]
                self._source_canvas_id.setText(canvas.id or "-")
                self._source_canvas_dims.setText(f"{canvas.dimensions.width} x {canvas.dimensions.height}")

                if canvas.effective_dimensions:
                    self._source_effective_dims.setText(f"{canvas.effective_dimensions.width} x {canvas.effective_dimensions.height}")
                if canvas.effective_anchor_point:
                    self._source_effective_anchor.setText(f"({canvas.effective_anchor_point.x:.2f}, {canvas.effective_anchor_point.y:.2f})")

                if canvas.framing_decisions:
                    fd = canvas.framing_decisions[0]
                    self._source_framing_id.setText(fd.id or "-")
                    self._source_framing_dims.setText(f"{fd.dimensions.width:.2f} x {fd.dimensions.height:.2f}")
                    self._source_framing_anchor.setText(f"({fd.anchor_point.x:.2f}, {fd.anchor_point.y:.2f})")

                    if fd.protection_dimensions:
                        self._source_protection_dims.setText(
                            f"{fd.protection_dimensions.width:.2f} x {fd.protection_dimensions.height:.2f}"
                        )
                    if fd.protection_anchor_point:
                        self._source_protection_anchor.setText(f"({fd.protection_anchor_point.x:.2f}, {fd.protection_anchor_point.y:.2f})")
                    elif fd.protection_dimensions:
                        # Use framing anchor if protection anchor not specified
                        self._source_protection_anchor.setText(f"({fd.anchor_point.x:.2f}, {fd.anchor_point.y:.2f})")

    def _update_output_display(self) -> None:
        """Update output column in comparison table."""
        # Reset all fields
        self._output_context_id.setText("-")
        self._output_canvas_id.setText("-")
        self._output_canvas_dims.setText("-")
        self._output_effective_dims.setText("-")
        self._output_effective_anchor.setText("-")
        self._output_framing_id.setText("-")
        self._output_framing_dims.setText("-")
        self._output_framing_anchor.setText("-")
        self._output_protection_dims.setText("-")
        self._output_protection_anchor.setText("-")

        model = self._output_model
        if not model or not model.contexts:
            return

        context = model.contexts[0]
        self._output_context_id.setText(context.label or "-")

        if context.canvases and len(context.canvases) > 1:
            canvas = context.canvases[1]  # Output canvas is second
            self._output_canvas_id.setText(canvas.id or "-")
            self._output_canvas_dims.setText(f"{canvas.dimensions.width} x {canvas.dimensions.height}")

            if canvas.effective_dimensions:
                self._output_effective_dims.setText(f"{canvas.effective_dimensions.width} x {canvas.effective_dimensions.height}")
            if canvas.effective_anchor_point:
                self._output_effective_anchor.setText(f"({canvas.effective_anchor_point.x:.2f}, {canvas.effective_anchor_point.y:.2f})")

            if canvas.framing_decisions:
                fd = canvas.framing_decisions[0]
                self._output_framing_id.setText(fd.id or "-")
                self._output_framing_dims.setText(f"{fd.dimensions.width:.2f} x {fd.dimensions.height:.2f}")
                self._output_framing_anchor.setText(f"({fd.anchor_point.x:.2f}, {fd.anchor_point.y:.2f})")

                if fd.protection_dimensions:
                    self._output_protection_dims.setText(f"{fd.protection_dimensions.width:.2f} x {fd.protection_dimensions.height:.2f}")
                if fd.protection_anchor_point:
                    self._output_protection_anchor.setText(f"({fd.protection_anchor_point.x:.2f}, {fd.protection_anchor_point.y:.2f})")
                elif fd.protection_dimensions:
                    # Use framing anchor if protection anchor not specified
                    self._output_protection_anchor.setText(f"({fd.anchor_point.x:.2f}, {fd.anchor_point.y:.2f})")

    @Slot(object)
    def _on_transform_result(self, result) -> None:
        """Handle transform result."""
        if result:
            from fdl import ATTR_SCALED_BOUNDING_BOX

            sbb = result.canvas.get_custom_attr(ATTR_SCALED_BOUNDING_BOX)
            if sbb:
                self._scale_label.setText(f"{sbb.width:.4f} x {sbb.height:.4f}")

    @Slot()
    def _on_copy_clicked(self) -> None:
        """Handle copy button click."""
        if self._output_model:
            self._export_controller.copy_from_model(self._output_model)

    @Slot()
    def _on_export_clicked(self) -> None:
        """Handle export button click."""
        if not self._output_model:
            return

        path, _ = QFileDialog.getSaveFileName(self, "Export FDL", "", "FDL Files (*.fdl);;All Files (*)")
        if path:
            self._export_controller.export_from_model(self._output_model, path)

    @Slot()
    def _on_copy_completed(self) -> None:
        """Handle copy completed."""
        QMessageBox.information(self, "Copied", "JSON copied to clipboard.")

    @Slot(str)
    def _on_export_completed(self, path: str) -> None:
        """Handle export completed."""
        QMessageBox.information(self, "Exported", f"FDL exported to:\n{path}")

    @Slot(str)
    def _on_error(self, message: str) -> None:
        """Handle error."""
        QMessageBox.critical(self, "Error", message)

    @Slot()
    def _on_export_image_clicked(self) -> None:
        """Handle export image button click."""
        self.export_image_requested.emit()

    @Slot()
    def _on_export_proxy_clicked(self) -> None:
        """Handle export proxy button click."""
        self.export_proxy_requested.emit()

    @Slot()
    def _on_export_unit_test_clicked(self) -> None:
        """Handle export unit test button click."""
        self.export_unit_test_requested.emit()

    def set_image_available(self, available: bool) -> None:
        """
        Set whether an image is available for export.

        Parameters
        ----------
        available : bool
            True if an image is loaded.
        """
        self._export_image_btn.setEnabled(available)
        self._export_proxy_btn.setEnabled(available)

    def set_transform_available(self, available: bool) -> None:
        """
        Set whether a transform result is available for export.

        Parameters
        ----------
        available : bool
            True if a transformation has been performed.
        """
        self._export_unit_test_btn.setEnabled(available)
