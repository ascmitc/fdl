# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Recent files model for FDL Viewer.

Manages a list of recently opened files with persistence.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QObject, QSettings, Signal


@dataclass
class RecentFile:
    """
    Represents a recently opened file.

    Attributes
    ----------
    path : str
        The file path.
    timestamp : str
        ISO format timestamp of when the file was opened.
    file_type : str
        The type of file ('source' or 'template').
    """

    path: str
    timestamp: str
    file_type: str = "source"

    @property
    def filename(self) -> str:
        """Get just the filename without path."""
        return Path(self.path).name

    @property
    def exists(self) -> bool:
        """Check if the file still exists."""
        return Path(self.path).exists()


class RecentFilesModel(QObject):
    """
    Model for managing recently opened files.

    Persists the list using QSettings and emits signals when the list changes.

    Parameters
    ----------
    max_files : int, optional
        Maximum number of recent files to keep (default 20).
    parent : QObject, optional
        Parent QObject for Qt ownership.

    Attributes
    ----------
    files_changed : Signal
        Emitted when the list of recent files changes.

    Examples
    --------
    >>> model = RecentFilesModel()
    >>> model.add_file("/path/to/file.fdl", "source")
    >>> recent = model.get_files()
    """

    files_changed = Signal()

    SETTINGS_KEY = "recent_files"
    DEFAULT_MAX_FILES = 20

    def __init__(self, max_files: int = DEFAULT_MAX_FILES, parent: QObject | None = None) -> None:
        """
        Initialize the RecentFilesModel.

        Parameters
        ----------
        max_files : int, optional
            Maximum number of recent files to keep.
        parent : QObject, optional
            Parent QObject for Qt ownership.
        """
        super().__init__(parent)
        self._max_files = max_files
        self._files: list[RecentFile] = []
        self._settings = QSettings("FDLViewer", "FDLViewer")
        self._load_from_settings()

    def _load_from_settings(self) -> None:
        """Load recent files from QSettings."""
        data = self._settings.value(self.SETTINGS_KEY, [])
        if data and isinstance(data, list):
            self._files = []
            for item in data:
                if isinstance(item, dict):
                    try:
                        self._files.append(
                            RecentFile(
                                path=item.get("path", ""), timestamp=item.get("timestamp", ""), file_type=item.get("file_type", "source")
                            )
                        )
                    except Exception:
                        pass
        # Filter out non-existent files
        self._files = [f for f in self._files if f.exists]

    def _save_to_settings(self) -> None:
        """Save recent files to QSettings."""
        data = [{"path": f.path, "timestamp": f.timestamp, "file_type": f.file_type} for f in self._files]
        self._settings.setValue(self.SETTINGS_KEY, data)
        self._settings.sync()

    def add_file(self, path: str, file_type: str = "source") -> None:
        """
        Add a file to the recent files list.

        Parameters
        ----------
        path : str
            The file path.
        file_type : str, optional
            The type of file ('source' or 'template').
        """
        # Normalize path
        path = str(Path(path).resolve())

        # Remove if already exists
        self._files = [f for f in self._files if f.path != path]

        # Add to beginning
        self._files.insert(0, RecentFile(path=path, timestamp=datetime.now().isoformat(), file_type=file_type))

        # Trim to max
        self._files = self._files[: self._max_files]

        self._save_to_settings()
        self.files_changed.emit()

    def remove_file(self, path: str) -> None:
        """
        Remove a file from the recent files list.

        Parameters
        ----------
        path : str
            The file path to remove.
        """
        path = str(Path(path).resolve())
        self._files = [f for f in self._files if f.path != path]
        self._save_to_settings()
        self.files_changed.emit()

    def clear(self) -> None:
        """Clear all recent files."""
        self._files = []
        self._save_to_settings()
        self.files_changed.emit()

    def get_files(self, file_type: str | None = None) -> list[RecentFile]:
        """
        Get the list of recent files.

        Parameters
        ----------
        file_type : str, optional
            Filter by file type ('source' or 'template').

        Returns
        -------
        List[RecentFile]
            The list of recent files.
        """
        if file_type is None:
            return list(self._files)
        return [f for f in self._files if f.file_type == file_type]

    def get_source_files(self) -> list[RecentFile]:
        """
        Get recent source files.

        Returns
        -------
        List[RecentFile]
            The list of recent source files.
        """
        return self.get_files("source")

    def get_template_files(self) -> list[RecentFile]:
        """
        Get recent template files.

        Returns
        -------
        List[RecentFile]
            The list of recent template files.
        """
        return self.get_files("template")

    @property
    def count(self) -> int:
        """Get the number of recent files."""
        return len(self._files)

    @property
    def is_empty(self) -> bool:
        """Check if the recent files list is empty."""
        return len(self._files) == 0
