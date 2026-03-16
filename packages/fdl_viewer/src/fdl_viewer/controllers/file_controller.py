# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
File controller for FDL Viewer.

Handles loading and saving FDL files.
"""

from pathlib import Path

from fdl import FDL, read_from_file, write_to_file
from PySide6.QtCore import QObject, Signal

from fdl_viewer.models.fdl_model import FDLModel


class FileController(QObject):
    """
    Controller for FDL file operations.

    Handles loading and saving FDL files using the fdl library functions.

    Parameters
    ----------
    parent : QObject, optional
        Parent QObject for Qt ownership.

    Attributes
    ----------
    file_loaded : Signal
        Emitted when a file is successfully loaded (path, FDLModel).
    file_saved : Signal
        Emitted when a file is successfully saved (path).
    error_occurred : Signal
        Emitted when an error occurs (message).

    Examples
    --------
    >>> controller = FileController()
    >>> model = controller.load_fdl("/path/to/file.fdl")
    >>> if model:
    ...     print(f"Loaded: {model.version_string}")
    """

    file_loaded = Signal(str, object)  # path, FDLModel
    file_saved = Signal(str)  # path
    error_occurred = Signal(str)  # error message

    def __init__(self, parent: QObject | None = None) -> None:
        """
        Initialize the FileController.

        Parameters
        ----------
        parent : QObject, optional
            Parent QObject for Qt ownership.
        """
        super().__init__(parent)

    def load_fdl(self, path: str) -> FDLModel | None:
        """
        Load an FDL file and return an FDLModel.

        Parameters
        ----------
        path : str
            Path to the FDL file.

        Returns
        -------
        FDLModel or None
            The loaded FDL model, or None if loading failed.

        Raises
        ------
        FileNotFoundError
            If the file does not exist.
        ValueError
            If the file is not a valid FDL file.
        """
        path = Path(path)

        if not path.exists():
            error = f"File not found: {path}"
            self.error_occurred.emit(error)
            raise FileNotFoundError(error)

        if path.suffix.lower() != ".fdl":
            error = f"Invalid file extension: {path.suffix}"
            self.error_occurred.emit(error)
            raise ValueError(error)

        try:
            fdl = read_from_file(path)
            model = FDLModel(fdl)
            model.set_file_path(str(path))
            self.file_loaded.emit(str(path), model)
            return model
        except Exception as e:
            error = f"Failed to load FDL: {e}"
            self.error_occurred.emit(error)
            raise

    def save_fdl(self, fdl: FDL, path: str) -> bool:
        """
        Save an FDL to a file.

        Parameters
        ----------
        fdl : FDL
            The FDL dataclass to save. Also accepts FDLModel (extracts .fdl).
        path : str
            Path to save the file.

        Returns
        -------
        bool
            True if save was successful.

        Raises
        ------
        ValueError
            If the FDL is invalid.
        IOError
            If the file cannot be written.
        """
        from fdl_viewer.models.fdl_model import FDLModel

        if isinstance(fdl, FDLModel):
            fdl = fdl.fdl

        path = Path(path)

        # Ensure .fdl extension
        if path.suffix.lower() != ".fdl":
            path = path.with_suffix(".fdl")

        try:
            write_to_file(fdl, path)
            self.file_saved.emit(str(path))
            return True
        except Exception as e:
            error = f"Failed to save FDL: {e}"
            self.error_occurred.emit(error)
            raise
