# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Dimensions editor widget.

A reusable widget for editing width/height dimension pairs.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class DimensionsEditor(QWidget):
    """
    A widget for editing width/height dimension pairs.

    Supports both integer and floating-point dimensions.

    Parameters
    ----------
    parent : QWidget, optional
        Parent widget.
    use_float : bool, optional
        Whether to use float values (default False for integers).
    min_value : int or float, optional
        Minimum value (default 1).
    max_value : int or float, optional
        Maximum value (default 99999).
    label : str, optional
        Label text to show above inputs.

    Attributes
    ----------
    dimensions_changed : Signal
        Emitted when dimensions change (width, height).
    """

    dimensions_changed = Signal(object, object)  # width, height

    def __init__(
        self,
        parent: QWidget | None = None,
        use_float: bool = False,
        min_value: float = 1,
        max_value: float = 99999,
        label: str | None = None,
    ) -> None:
        super().__init__(parent)
        self._use_float = use_float
        self._min_value = min_value
        self._max_value = max_value
        self._label_text = label
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(4)

        # Optional label
        if self._label_text:
            label = QLabel(self._label_text)
            label.setObjectName("secondaryLabel")
            main_layout.addWidget(label)

        # Input row
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(8)

        # Width
        width_layout = QVBoxLayout()
        width_layout.setSpacing(2)
        width_label = QLabel("W")
        width_label.setObjectName("hintLabel")
        width_label.setAlignment(Qt.AlignCenter)
        width_layout.addWidget(width_label)

        if self._use_float:
            self._width_spin = QDoubleSpinBox()
            self._width_spin.setDecimals(2)
        else:
            self._width_spin = QSpinBox()

        self._width_spin.setRange(int(self._min_value), int(self._max_value))
        self._width_spin.valueChanged.connect(self._on_value_changed)
        width_layout.addWidget(self._width_spin)

        input_layout.addLayout(width_layout)

        # Separator
        sep = QLabel("\u00d7")  # multiplication sign
        sep.setObjectName("hintLabel")
        sep.setAlignment(Qt.AlignCenter)
        input_layout.addWidget(sep)

        # Height
        height_layout = QVBoxLayout()
        height_layout.setSpacing(2)
        height_label = QLabel("H")
        height_label.setObjectName("hintLabel")
        height_label.setAlignment(Qt.AlignCenter)
        height_layout.addWidget(height_label)

        if self._use_float:
            self._height_spin = QDoubleSpinBox()
            self._height_spin.setDecimals(2)
        else:
            self._height_spin = QSpinBox()

        self._height_spin.setRange(int(self._min_value), int(self._max_value))
        self._height_spin.valueChanged.connect(self._on_value_changed)
        height_layout.addWidget(self._height_spin)

        input_layout.addLayout(height_layout)

        main_layout.addLayout(input_layout)

    def _on_value_changed(self) -> None:
        """Handle value change."""
        self.dimensions_changed.emit(self.width(), self.height())

    def width(self) -> float:
        """
        Get the width value.

        Returns
        -------
        float or int
            The width.
        """
        return self._width_spin.value()

    def height(self) -> float:
        """
        Get the height value.

        Returns
        -------
        float or int
            The height.
        """
        return self._height_spin.value()

    def set_width(self, value: float) -> None:
        """
        Set the width value.

        Parameters
        ----------
        value : float or int
            The width.
        """
        self._width_spin.blockSignals(True)
        self._width_spin.setValue(int(value) if not self._use_float else value)
        self._width_spin.blockSignals(False)

    def set_height(self, value: float) -> None:
        """
        Set the height value.

        Parameters
        ----------
        value : float or int
            The height.
        """
        self._height_spin.blockSignals(True)
        self._height_spin.setValue(int(value) if not self._use_float else value)
        self._height_spin.blockSignals(False)

    def set_dimensions(self, width: float, height: float) -> None:
        """
        Set both dimensions.

        Parameters
        ----------
        width : float or int
            The width.
        height : float or int
            The height.
        """
        self._width_spin.blockSignals(True)
        self._height_spin.blockSignals(True)

        self._width_spin.setValue(int(width) if not self._use_float else width)
        self._height_spin.setValue(int(height) if not self._use_float else height)

        self._width_spin.blockSignals(False)
        self._height_spin.blockSignals(False)

    def dimensions(self) -> tuple[float, float]:
        """
        Get both dimensions.

        Returns
        -------
        tuple
            (width, height)
        """
        return (self.width(), self.height())

    def set_enabled(self, enabled: bool) -> None:
        """
        Enable/disable the inputs.

        Parameters
        ----------
        enabled : bool
            Whether inputs should be enabled.
        """
        self._width_spin.setEnabled(enabled)
        self._height_spin.setEnabled(enabled)
