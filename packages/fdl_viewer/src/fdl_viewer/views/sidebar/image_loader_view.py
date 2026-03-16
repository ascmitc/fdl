# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Image loader view for FDL Viewer sidebar.

Provides controls for loading images and adjusting opacity.
"""

from pathlib import Path

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from fdl_viewer.controllers.image_controller import ImageController
from fdl_viewer.models.app_state import AppState
from fdl_viewer.views.common.file_drop_zone import FileDropZone


class ImageLoaderView(QWidget):
    """
    Widget for loading images and controlling opacity.

    Provides:
    - Drag/drop zone for image files
    - Browse button for file selection
    - Opacity slider
    - Clear button

    Parameters
    ----------
    parent : QWidget, optional
        Parent widget.

    Attributes
    ----------
    image_loaded : Signal
        Emitted when an image is loaded (QPixmap, width, height).
    image_cleared : Signal
        Emitted when the image is cleared.
    """

    image_loaded = Signal(object, int, int)  # QPixmap, width, height
    image_cleared = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._app_state = AppState.instance()
        self._image_controller = ImageController()
        self._current_path: str = ""
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Set up the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Group box
        group = QGroupBox("Image Underlay")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(8)

        # Drop zone
        extensions = list(self._image_controller.supported_formats)
        self._drop_zone = FileDropZone(
            extensions=extensions,
            title="Drop Image Here",
            hint_text="Drop file here or click to browse",
            icon="🖼️",
            show_extensions=True,
        )
        group_layout.addWidget(self._drop_zone)

        # File info label
        self._file_label = QLabel("No image loaded")
        self._file_label.setObjectName("secondaryLabel")
        self._file_label.setWordWrap(True)
        group_layout.addWidget(self._file_label)

        # Button row
        button_row = QHBoxLayout()
        button_row.setSpacing(8)

        self._browse_btn = QPushButton("Browse...")
        self._browse_btn.setMinimumWidth(90)
        self._browse_btn.setMinimumHeight(28)
        button_row.addWidget(self._browse_btn)

        button_row.addStretch()

        self._clear_btn = QPushButton("Clear")
        self._clear_btn.setMinimumWidth(70)
        self._clear_btn.setMinimumHeight(28)
        self._clear_btn.setEnabled(False)
        button_row.addWidget(self._clear_btn)

        group_layout.addLayout(button_row)

        # Opacity slider row
        opacity_row = QHBoxLayout()
        opacity_row.setSpacing(8)

        opacity_label = QLabel("Opacity:")
        opacity_label.setMinimumWidth(55)
        opacity_row.addWidget(opacity_label)

        self._opacity_slider = QSlider(Qt.Horizontal)
        self._opacity_slider.setRange(0, 100)
        self._opacity_slider.setValue(int(self._app_state.image_opacity * 100))
        self._opacity_slider.setTickPosition(QSlider.TicksBelow)
        self._opacity_slider.setTickInterval(10)
        self._opacity_slider.setMinimumHeight(25)
        opacity_row.addWidget(self._opacity_slider, 1)

        self._opacity_label = QLabel(f"{int(self._app_state.image_opacity * 100)}%")
        self._opacity_label.setMinimumWidth(40)
        self._opacity_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        opacity_row.addWidget(self._opacity_label)

        group_layout.addLayout(opacity_row)

        layout.addWidget(group)

    def _connect_signals(self) -> None:
        """Connect signals."""
        # Drop zone
        self._drop_zone.file_dropped.connect(self._on_file_dropped)
        self._drop_zone.clicked.connect(self._on_browse_clicked)

        # Buttons
        self._browse_btn.clicked.connect(self._on_browse_clicked)
        self._clear_btn.clicked.connect(self._on_clear_clicked)

        # Opacity slider
        self._opacity_slider.valueChanged.connect(self._on_opacity_changed)

        # Image controller
        self._image_controller.image_loaded.connect(self._on_image_loaded)
        self._image_controller.error_occurred.connect(self._on_error)

        # App state
        self._app_state.image_opacity_changed.connect(self._on_app_opacity_changed)

    @Slot(str)
    def _on_file_dropped(self, path: str) -> None:
        """Handle file dropped."""
        self._load_image(path)

    @Slot()
    def _on_browse_clicked(self) -> None:
        """Handle browse button click."""
        from fdl_viewer.utils.settings import Settings

        settings = Settings.instance()

        path, _ = QFileDialog.getOpenFileName(self, "Open Image", settings.get_last_directory(), self._image_controller.get_format_filter())

        if path:
            settings.set_last_directory(str(Path(path).parent))
            self._load_image(path)

    @Slot()
    def _on_clear_clicked(self) -> None:
        """Handle clear button click."""
        self._image_controller.clear()
        self._current_path = ""
        self._file_label.setText("No image loaded")
        self._clear_btn.setEnabled(False)
        self.image_cleared.emit()

    @Slot(int)
    def _on_opacity_changed(self, value: int) -> None:
        """Handle opacity slider change."""
        opacity = value / 100.0
        self._opacity_label.setText(f"{value}%")
        self._app_state.set_image_opacity(opacity)

    @Slot(float)
    def _on_app_opacity_changed(self, opacity: float) -> None:
        """Handle app state opacity change."""
        value = int(opacity * 100)
        self._opacity_slider.blockSignals(True)
        self._opacity_slider.setValue(value)
        self._opacity_slider.blockSignals(False)
        self._opacity_label.setText(f"{value}%")

    @Slot(object, int, int)
    def _on_image_loaded(self, pixmap, width: int, height: int) -> None:
        """Handle image loaded from controller."""
        path = self._image_controller.get_image_path()
        filename = Path(path).name if path else "Image"
        self._file_label.setText(f"{filename}\n({width} x {height})")
        self._clear_btn.setEnabled(True)
        self.image_loaded.emit(pixmap, width, height)

    @Slot(str)
    def _on_error(self, message: str) -> None:
        """Handle error from controller."""
        self._app_state.emit_error(message)

    def _load_image(self, path: str) -> None:
        """
        Load an image from path.

        Parameters
        ----------
        path : str
            Path to the image file.
        """
        self._current_path = path
        self._file_label.setText(f"Loading {Path(path).name}...")
        self._image_controller.load_image(path)

    def get_current_pixmap(self) -> object:
        """
        Get the currently loaded pixmap.

        Returns
        -------
        QPixmap or None
            The current pixmap.
        """
        return self._image_controller.get_current_pixmap()

    def get_current_path(self) -> str:
        """
        Get the path of the currently loaded image.

        Returns
        -------
        str
            The path to the current image, or empty string if none loaded.
        """
        return self._current_path
