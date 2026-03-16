# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Template editor view for FDL Viewer.

Provides controls for editing canvas template parameters.
"""

from fdl import (
    CanvasTemplate,
    DimensionsInt,
    RoundStrategy,
)
from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from fdl_viewer.models.template_presets import (
    ALIGNMENT_HORIZONTAL_OPTIONS,
    ALIGNMENT_VERTICAL_OPTIONS,
    FIT_METHOD_OPTIONS,
    FIT_SOURCE_OPTIONS,
    PRESERVE_OPTIONS,
    ROUND_EVEN_OPTIONS,
    ROUND_MODE_OPTIONS,
)


class TemplateEditorView(QWidget):
    """
    Template editor with controls for all CanvasTemplate parameters.

    Parameters
    ----------
    parent : QWidget, optional
        Parent widget.

    Attributes
    ----------
    template_changed : Signal
        Emitted when template parameters change (CanvasTemplate).
    """

    template_changed = Signal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._template: CanvasTemplate | None = None
        self._updating = False
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Set up the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Header
        header = QLabel("Template Settings")
        header.setObjectName("headerLabel")
        layout.addWidget(header)

        # Target dimensions group
        dims_group = QGroupBox("Target Dimensions")
        dims_layout = QVBoxLayout(dims_group)

        # Width/Height
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Width:"))
        self._width_spin = QSpinBox()
        self._width_spin.setRange(1, 16384)
        self._width_spin.setValue(3840)
        size_layout.addWidget(self._width_spin)
        size_layout.addWidget(QLabel("Height:"))
        self._height_spin = QSpinBox()
        self._height_spin.setRange(1, 16384)
        self._height_spin.setValue(2160)
        size_layout.addWidget(self._height_spin)
        dims_layout.addLayout(size_layout)

        # Anamorphic squeeze
        squeeze_layout = QHBoxLayout()
        squeeze_layout.addWidget(QLabel("Anamorphic Squeeze:"))
        self._squeeze_spin = QDoubleSpinBox()
        self._squeeze_spin.setRange(0.1, 4.0)
        self._squeeze_spin.setValue(1.0)
        self._squeeze_spin.setSingleStep(0.1)
        squeeze_layout.addWidget(self._squeeze_spin)
        squeeze_layout.addStretch()
        dims_layout.addLayout(squeeze_layout)

        layout.addWidget(dims_group)

        # Fit settings group
        fit_group = QGroupBox("Fit Settings")
        fit_layout = QVBoxLayout(fit_group)

        # Fit source
        source_layout = QHBoxLayout()
        source_layout.addWidget(QLabel("Fit Source:"))
        self._fit_source_combo = QComboBox()
        for value, label in FIT_SOURCE_OPTIONS:
            self._fit_source_combo.addItem(label, value)
        source_layout.addWidget(self._fit_source_combo, 1)
        fit_layout.addLayout(source_layout)

        # Fit method
        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("Fit Method:"))
        self._fit_method_combo = QComboBox()
        for value, label in FIT_METHOD_OPTIONS:
            self._fit_method_combo.addItem(label, value)
        method_layout.addWidget(self._fit_method_combo, 1)
        fit_layout.addLayout(method_layout)

        layout.addWidget(fit_group)

        # Alignment group
        align_group = QGroupBox("Alignment")
        align_layout = QVBoxLayout(align_group)

        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel("Horizontal:"))
        self._align_h_combo = QComboBox()
        for value, label in ALIGNMENT_HORIZONTAL_OPTIONS:
            self._align_h_combo.addItem(label, value)
        self._align_h_combo.setCurrentIndex(1)  # center
        h_layout.addWidget(self._align_h_combo, 1)
        align_layout.addLayout(h_layout)

        v_layout = QHBoxLayout()
        v_layout.addWidget(QLabel("Vertical:"))
        self._align_v_combo = QComboBox()
        for value, label in ALIGNMENT_VERTICAL_OPTIONS:
            self._align_v_combo.addItem(label, value)
        self._align_v_combo.setCurrentIndex(1)  # center
        v_layout.addWidget(self._align_v_combo, 1)
        align_layout.addLayout(v_layout)

        layout.addWidget(align_group)

        # Preserve group
        preserve_group = QGroupBox("Preserve From Source")
        preserve_layout = QVBoxLayout(preserve_group)

        self._preserve_combo = QComboBox()
        for value, label in PRESERVE_OPTIONS:
            self._preserve_combo.addItem(label, value)
        preserve_layout.addWidget(self._preserve_combo)

        layout.addWidget(preserve_group)

        # Maximum dimensions group
        max_group = QGroupBox("Maximum Dimensions")
        max_layout = QVBoxLayout(max_group)

        self._max_enabled = QCheckBox("Enable Maximum Dimensions")
        max_layout.addWidget(self._max_enabled)

        max_size_layout = QHBoxLayout()
        max_size_layout.addWidget(QLabel("Max Width:"))
        self._max_width_spin = QSpinBox()
        self._max_width_spin.setRange(1, 16384)
        self._max_width_spin.setValue(3840)
        self._max_width_spin.setEnabled(False)
        max_size_layout.addWidget(self._max_width_spin)
        max_size_layout.addWidget(QLabel("Max Height:"))
        self._max_height_spin = QSpinBox()
        self._max_height_spin.setRange(1, 16384)
        self._max_height_spin.setValue(2160)
        self._max_height_spin.setEnabled(False)
        max_size_layout.addWidget(self._max_height_spin)
        max_layout.addLayout(max_size_layout)

        self._pad_to_max = QCheckBox("Pad to Maximum")
        self._pad_to_max.setEnabled(False)
        max_layout.addWidget(self._pad_to_max)

        layout.addWidget(max_group)

        # Rounding group
        round_group = QGroupBox("Rounding")
        round_layout = QHBoxLayout(round_group)

        round_layout.addWidget(QLabel("Even:"))
        self._round_even_combo = QComboBox()
        for value, label in ROUND_EVEN_OPTIONS:
            self._round_even_combo.addItem(label, value)
        self._round_even_combo.setCurrentIndex(1)  # even
        round_layout.addWidget(self._round_even_combo)

        round_layout.addWidget(QLabel("Mode:"))
        self._round_mode_combo = QComboBox()
        for value, label in ROUND_MODE_OPTIONS:
            self._round_mode_combo.addItem(label, value)
        round_layout.addWidget(self._round_mode_combo)

        layout.addWidget(round_group)

    def _connect_signals(self) -> None:
        """Connect signals."""
        self._width_spin.valueChanged.connect(self._on_value_changed)
        self._height_spin.valueChanged.connect(self._on_value_changed)
        self._squeeze_spin.valueChanged.connect(self._on_value_changed)
        self._fit_source_combo.currentIndexChanged.connect(self._on_value_changed)
        self._fit_method_combo.currentIndexChanged.connect(self._on_value_changed)
        self._align_h_combo.currentIndexChanged.connect(self._on_value_changed)
        self._align_v_combo.currentIndexChanged.connect(self._on_value_changed)
        self._preserve_combo.currentIndexChanged.connect(self._on_value_changed)
        self._max_enabled.toggled.connect(self._on_max_enabled_changed)
        self._max_width_spin.valueChanged.connect(self._on_value_changed)
        self._max_height_spin.valueChanged.connect(self._on_value_changed)
        self._pad_to_max.toggled.connect(self._on_value_changed)
        self._round_even_combo.currentIndexChanged.connect(self._on_value_changed)
        self._round_mode_combo.currentIndexChanged.connect(self._on_value_changed)

    @Slot()
    def _on_value_changed(self) -> None:
        """Handle value change in any field."""
        if self._updating:
            return

        template = self._build_template()
        if template:
            self.template_changed.emit(template)

    @Slot(bool)
    def _on_max_enabled_changed(self, enabled: bool) -> None:
        """Handle max dimensions checkbox."""
        self._max_width_spin.setEnabled(enabled)
        self._max_height_spin.setEnabled(enabled)
        self._pad_to_max.setEnabled(enabled)
        # When disabling max dimensions, also uncheck pad to max
        if not enabled:
            self._pad_to_max.setChecked(False)
        self._on_value_changed()

    def _build_template(self) -> CanvasTemplate | None:
        """Build a CanvasTemplate from current values."""
        max_dims = None
        if self._max_enabled.isChecked():
            max_dims = DimensionsInt(width=self._max_width_spin.value(), height=self._max_height_spin.value())

        return CanvasTemplate(
            id="custom_template",
            label="Custom Template",
            target_dimensions=DimensionsInt(width=self._width_spin.value(), height=self._height_spin.value()),
            target_anamorphic_squeeze=self._squeeze_spin.value(),
            fit_source=self._fit_source_combo.currentData(),
            fit_method=self._fit_method_combo.currentData(),
            alignment_method_horizontal=self._align_h_combo.currentData(),
            alignment_method_vertical=self._align_v_combo.currentData(),
            preserve_from_source_canvas=self._preserve_combo.currentData(),
            maximum_dimensions=max_dims,
            pad_to_maximum=self._pad_to_max.isChecked(),
            round=RoundStrategy(even=self._round_even_combo.currentData(), mode=self._round_mode_combo.currentData()),
        )

    @Slot(object)
    def set_template(self, template: CanvasTemplate) -> None:
        """
        Set the template values in the editor.

        Parameters
        ----------
        template : CanvasTemplate
            The template to display.
        """
        self._updating = True
        self._template = template

        self._width_spin.setValue(template.target_dimensions.width)
        self._height_spin.setValue(template.target_dimensions.height)
        self._squeeze_spin.setValue(template.target_anamorphic_squeeze)

        # Fit source
        for i in range(self._fit_source_combo.count()):
            if self._fit_source_combo.itemData(i) == template.fit_source:
                self._fit_source_combo.setCurrentIndex(i)
                break

        # Fit method
        for i in range(self._fit_method_combo.count()):
            if self._fit_method_combo.itemData(i) == template.fit_method:
                self._fit_method_combo.setCurrentIndex(i)
                break

        # Alignment
        for i in range(self._align_h_combo.count()):
            if self._align_h_combo.itemData(i) == template.alignment_method_horizontal:
                self._align_h_combo.setCurrentIndex(i)
                break

        for i in range(self._align_v_combo.count()):
            if self._align_v_combo.itemData(i) == template.alignment_method_vertical:
                self._align_v_combo.setCurrentIndex(i)
                break

        # Preserve
        for i in range(self._preserve_combo.count()):
            if self._preserve_combo.itemData(i) == template.preserve_from_source_canvas:
                self._preserve_combo.setCurrentIndex(i)
                break

        # Max dimensions
        has_max = template.maximum_dimensions is not None
        self._max_enabled.setChecked(has_max)
        self._max_width_spin.setEnabled(has_max)
        self._max_height_spin.setEnabled(has_max)
        self._pad_to_max.setEnabled(has_max)
        if has_max:
            self._max_width_spin.setValue(template.maximum_dimensions.width)
            self._max_height_spin.setValue(template.maximum_dimensions.height)
        self._pad_to_max.setChecked(template.pad_to_maximum)

        # Rounding
        for i in range(self._round_even_combo.count()):
            if self._round_even_combo.itemData(i) == template.round.even:
                self._round_even_combo.setCurrentIndex(i)
                break

        for i in range(self._round_mode_combo.count()):
            if self._round_mode_combo.itemData(i) == template.round.mode:
                self._round_mode_combo.setCurrentIndex(i)
                break

        self._updating = False
