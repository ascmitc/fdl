# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Export controller for FDL Viewer.

Handles exporting FDL files and copying JSON to clipboard.
"""

from pathlib import Path

from fdl import FDL, write_to_file, write_to_string
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication

from fdl_viewer.models.fdl_model import FDLModel


class ExportController(QObject):
    """
    Controller for export operations.

    Handles exporting FDL to files and copying JSON to clipboard.

    Parameters
    ----------
    parent : QObject, optional
        Parent QObject for Qt ownership.

    Attributes
    ----------
    export_completed : Signal
        Emitted when export completes (path).
    copy_completed : Signal
        Emitted when copy to clipboard completes.
    error_occurred : Signal
        Emitted when an error occurs (message).
    """

    export_completed = Signal(str)  # path
    copy_completed = Signal()
    error_occurred = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        """
        Initialize the ExportController.

        Parameters
        ----------
        parent : QObject, optional
            Parent QObject for Qt ownership.
        """
        super().__init__(parent)

    def export_fdl(self, fdl: FDL, path: str) -> bool:
        """
        Export an FDL to a file.

        Parameters
        ----------
        fdl : FDL
            The FDL to export.
        path : str
            The output file path.

        Returns
        -------
        bool
            True if export was successful.
        """
        try:
            path = Path(path)
            if path.suffix.lower() != ".fdl":
                path = path.with_suffix(".fdl")

            write_to_file(fdl, path)
            self.export_completed.emit(str(path))
            return True

        except Exception as e:
            self.error_occurred.emit(f"Export failed: {e}")
            return False

    def export_from_model(self, model: FDLModel, path: str) -> bool:
        """
        Export an FDL from an FDLModel.

        Parameters
        ----------
        model : FDLModel
            The FDL model to export from.
        path : str
            The output file path.

        Returns
        -------
        bool
            True if export was successful.
        """
        if not model or not model.fdl:
            self.error_occurred.emit("No FDL to export")
            return False

        return self.export_fdl(model.fdl, path)

    def copy_to_clipboard(self, fdl: FDL) -> bool:
        """
        Copy FDL JSON to clipboard.

        Parameters
        ----------
        fdl : FDL
            The FDL to copy.

        Returns
        -------
        bool
            True if copy was successful.
        """
        try:
            json_str = write_to_string(fdl)

            clipboard = QApplication.clipboard()
            clipboard.setText(json_str)
            self.copy_completed.emit()
            return True

        except Exception as e:
            self.error_occurred.emit(f"Copy failed: {e}")
            return False

    def copy_from_model(self, model: FDLModel) -> bool:
        """
        Copy FDL JSON from an FDLModel to clipboard.

        Parameters
        ----------
        model : FDLModel
            The FDL model to copy from.

        Returns
        -------
        bool
            True if copy was successful.
        """
        if not model or not model.fdl:
            self.error_occurred.emit("No FDL to copy")
            return False

        return self.copy_to_clipboard(model.fdl)

    def get_json_string(self, fdl: FDL) -> str:
        """
        Get the JSON string for an FDL.

        Parameters
        ----------
        fdl : FDL
            The FDL to convert.

        Returns
        -------
        str
            The JSON string.
        """
        try:
            return write_to_string(fdl)
        except Exception:
            return ""

    def get_json_from_model(self, model: FDLModel) -> str:
        """
        Get the JSON string from an FDLModel.

        Parameters
        ----------
        model : FDLModel
            The FDL model.

        Returns
        -------
        str
            The JSON string, or empty string if model is invalid.
        """
        if not model or not model.fdl:
            return ""
        return self.get_json_string(model.fdl)
