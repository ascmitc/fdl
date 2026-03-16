# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Custom error dialog for FDL Viewer.

Provides a scrollable, copyable error message display.
"""

from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)


class ErrorDialog(QDialog):
    """
    A custom error dialog with a scrollable text area for displaying
    long error messages.

    Parameters
    ----------
    title : str
        The dialog window title.
    summary : str
        A brief summary of the error shown at the top.
    details : str
        The full error details shown in the scrollable text area.
    parent : QWidget, optional
        Parent widget.
    """

    def __init__(
        self,
        title: str,
        summary: str,
        details: str,
        parent=None,
    ) -> None:
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setMinimumSize(600, 400)
        self.resize(700, 500)

        self._setup_ui(summary, details)

    def _setup_ui(self, summary: str, details: str) -> None:
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Summary label
        summary_label = QLabel(summary)
        summary_label.setObjectName("errorLabel")
        summary_label.setWordWrap(True)
        layout.addWidget(summary_label)

        # Details label
        details_label = QLabel("Error Details:")
        layout.addWidget(details_label)

        # Scrollable text area for error details
        self._text_edit = QTextEdit()
        self._text_edit.setObjectName("errorDetails")
        self._text_edit.setReadOnly(True)
        self._text_edit.setPlainText(details)
        layout.addWidget(self._text_edit, 1)

        # Button row
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # Copy button
        copy_button = QPushButton("Copy to Clipboard")
        copy_button.clicked.connect(self._copy_to_clipboard)
        button_layout.addWidget(copy_button)

        # Close button
        close_button = QPushButton("Close")
        close_button.setDefault(True)
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

    def _copy_to_clipboard(self) -> None:
        """Copy the error details to the clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(self._text_edit.toPlainText())

    @staticmethod
    def show_error(
        parent,
        title: str = "Error",
        summary: str = "An error occurred",
        details: str = "",
    ) -> None:
        """
        Convenience method to show an error dialog.

        Parameters
        ----------
        parent : QWidget
            Parent widget.
        title : str
            The dialog window title.
        summary : str
            A brief summary of the error.
        details : str
            The full error details.
        """
        dialog = ErrorDialog(title, summary, details, parent)
        dialog.exec()
