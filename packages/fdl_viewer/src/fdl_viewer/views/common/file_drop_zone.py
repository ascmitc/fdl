# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
File drop zone widget.

A reusable drag/drop area for loading files.
"""

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QMouseEvent
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class FileDropZone(QFrame):
    """
    A drag/drop zone for loading files.

    Supports filtering by file extensions, optional icon, and loaded state.

    Parameters
    ----------
    parent : QWidget, optional
        Parent widget.
    extensions : list of str, optional
        Allowed file extensions (e.g., ['.fdl', '.json']).
        If None, all files are accepted.
    title : str, optional
        Bold title text to display at the top.
    hint_text : str, optional
        Hint text shown below the title (e.g., "Drop file here or click to browse").
    icon : str, optional
        Icon/emoji to display. If None or empty, no icon is shown.
    show_extensions : bool, optional
        Whether to show the supported extensions. Default True.

    Attributes
    ----------
    file_dropped : Signal
        Emitted when a valid file is dropped (path as str).
    files_dropped : Signal
        Emitted when multiple files are dropped (list of paths).
    clicked : Signal
        Emitted when the drop zone is clicked.
    """

    file_dropped = Signal(str)
    files_dropped = Signal(list)
    clicked = Signal()

    def __init__(
        self,
        parent: QFrame | None = None,
        extensions: list[str] | None = None,
        title: str = "Drop File Here",
        hint_text: str = "Drop file here or click to browse",
        icon: str | None = None,
        show_extensions: bool = True,
    ) -> None:
        super().__init__(parent)
        self._extensions = extensions
        self._title = title
        self._hint_text = hint_text
        self._icon = icon
        self._show_extensions = show_extensions
        self._is_hovering = False
        self._is_loaded = False
        self._is_disabled = False
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the UI."""
        self.setObjectName("FileDropZone")
        self.setAcceptDrops(True)
        self.setMinimumHeight(80)
        self.setCursor(Qt.PointingHandCursor)
        self.setFrameShape(QFrame.NoFrame)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignCenter)

        # Apply border style to self
        self._update_style()

        # Icon (optional) - transparent to mouse events
        if self._icon:
            self._icon_label = QLabel(self._icon)
            self._icon_label.setObjectName("dropZoneIcon")
            self._icon_label.setAlignment(Qt.AlignCenter)
            self._icon_label.setAttribute(Qt.WA_TransparentForMouseEvents)
            layout.addWidget(self._icon_label)
        else:
            self._icon_label = None

        # Title - bold text, transparent to mouse events
        self._title_label = QLabel(self._title)
        self._title_label.setObjectName("dropZoneTitle")
        self._title_label.setAlignment(Qt.AlignCenter)
        self._title_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        layout.addWidget(self._title_label)

        # Hint/status text - transparent to mouse events
        self._hint_label = QLabel(self._hint_text)
        self._hint_label.setObjectName("dropZoneHint")
        self._hint_label.setAlignment(Qt.AlignCenter)
        self._hint_label.setWordWrap(True)
        self._hint_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        layout.addWidget(self._hint_label)

        # Extension hint (optional) - transparent to mouse events
        if self._show_extensions and self._extensions:
            ext_text = ", ".join(self._extensions)
            self._ext_label = QLabel(f"({ext_text})")
            self._ext_label.setObjectName("dropZoneExt")
            self._ext_label.setAlignment(Qt.AlignCenter)
            self._ext_label.setAttribute(Qt.WA_TransparentForMouseEvents)
            layout.addWidget(self._ext_label)
        else:
            self._ext_label = None

    def _update_style(self) -> None:
        """Update the style based on state using dynamic properties."""
        # Set dynamic properties for stylesheet selectors
        self.setProperty("loaded", self._is_loaded)
        self.setProperty("disabled", self._is_disabled)
        self.setProperty("hovering", self._is_hovering)

        # Repolish to apply stylesheet changes
        self.style().unpolish(self)
        self.style().polish(self)

    def _is_valid_file(self, path: str) -> bool:
        """
        Check if the file has a valid extension.

        Parameters
        ----------
        path : str
            The file path.

        Returns
        -------
        bool
            True if valid.
        """
        if not self._extensions:
            return True

        file_ext = Path(path).suffix.lower()
        return file_ext in [ext.lower() for ext in self._extensions]

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Handle drag enter."""
        if event.mimeData().hasUrls():
            # Check if any file has valid extension
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    if self._is_valid_file(url.toLocalFile()):
                        self._is_hovering = True
                        self._update_style()
                        event.acceptProposedAction()
                        return

        event.ignore()

    def dragLeaveEvent(self, event) -> None:
        """Handle drag leave."""
        self._is_hovering = False
        self._update_style()

    def dropEvent(self, event: QDropEvent) -> None:
        """Handle drop."""
        self._is_hovering = False
        self._update_style()

        valid_files = []
        for url in event.mimeData().urls():
            if url.isLocalFile():
                path = url.toLocalFile()
                if self._is_valid_file(path):
                    valid_files.append(path)

        if valid_files:
            event.acceptProposedAction()

            # Emit single file signal for first file
            self.file_dropped.emit(valid_files[0])

            # Emit multi-file signal
            if len(valid_files) > 1:
                self.files_dropped.emit(valid_files)
        else:
            event.ignore()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press to emit clicked signal."""
        if event.button() == Qt.LeftButton and not self._is_disabled:
            self.clicked.emit()
        super().mousePressEvent(event)

    def set_loaded(self, loaded: bool, filename: str = "") -> None:
        """
        Set the loaded state.

        Parameters
        ----------
        loaded : bool
            Whether a file is loaded.
        filename : str, optional
            The filename to display in the hint area.
        """
        self._is_loaded = loaded
        if loaded and filename:
            self._hint_label.setText(filename)
        else:
            self._hint_label.setText(self._hint_text)
        self._update_style()

    def set_disabled_state(self, disabled: bool) -> None:
        """
        Set the disabled state (grayed out).

        Parameters
        ----------
        disabled : bool
            Whether the drop zone should be disabled/grayed out.
        """
        self._is_disabled = disabled
        self.setAcceptDrops(not disabled)
        self._update_style()

    def set_hint_text(self, text: str) -> None:
        """
        Set the hint text.

        Parameters
        ----------
        text : str
            The new hint text.
        """
        self._hint_text = text
        if not self._is_loaded:
            self._hint_label.setText(text)

    def set_extensions(self, extensions: list[str] | None) -> None:
        """
        Set the allowed extensions.

        Parameters
        ----------
        extensions : list of str or None
            The allowed extensions.
        """
        self._extensions = extensions
