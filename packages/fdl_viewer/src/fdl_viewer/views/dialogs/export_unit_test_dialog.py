# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Export Unit Test dialog for FDL Viewer.

Allows users to export the current transformation as a unit test scenario.
"""

import re
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)


class ExportUnitTestDialog(QDialog):
    """
    Dialog for exporting the current transformation as a unit test scenario.

    Parameters
    ----------
    parent : QWidget, optional
        Parent widget.
    scenario_number : int
        The next available scenario number.
    default_name : str, optional
        Default scenario name derived from source FDL filename.
    has_image : bool
        Whether a source image is loaded.
    default_export_path : str, optional
        Default path for exporting files.
    """

    def __init__(
        self,
        parent=None,
        scenario_number: int = 32,
        default_name: str = "",
        has_image: bool = False,
        default_export_path: str = "",
    ) -> None:
        super().__init__(parent)
        self._scenario_number = scenario_number
        self._default_name = default_name
        self._has_image = has_image
        self._default_export_path = default_export_path

        self.setWindowTitle("Export Unit Test")
        self.setMinimumWidth(500)
        self.setModal(True)

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Info label
        info_label = QLabel(f"Export current transformation as unit test scenario #{self._scenario_number}.")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Scenario configuration group
        config_group = QGroupBox("Scenario Configuration")
        config_layout = QFormLayout(config_group)

        # Scenario number (read-only)
        self._scenario_number_label = QLabel(str(self._scenario_number))
        config_layout.addRow("Scenario Number:", self._scenario_number_label)

        # Scenario name
        self._name_edit = QLineEdit()
        self._name_edit.setText(self._sanitize_name(self._default_name))
        self._name_edit.setPlaceholderText("e.g., custom_framing_test")
        self._name_edit.textChanged.connect(self._update_preview)
        config_layout.addRow("Scenario Name:", self._name_edit)

        # Include source image checkbox
        self._include_image_checkbox = QCheckBox("Include source image (TIFF)")
        self._include_image_checkbox.setChecked(self._has_image)
        self._include_image_checkbox.setEnabled(self._has_image)
        if not self._has_image:
            self._include_image_checkbox.setToolTip("No source image loaded")
        config_layout.addRow("", self._include_image_checkbox)

        layout.addWidget(config_group)

        # Export location group
        location_group = QGroupBox("Export Location")
        location_layout = QVBoxLayout(location_group)

        path_layout = QHBoxLayout()
        self._path_edit = QLineEdit()
        self._path_edit.setText(self._default_export_path)
        self._path_edit.textChanged.connect(self._update_preview)
        path_layout.addWidget(self._path_edit)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._on_browse)
        path_layout.addWidget(browse_btn)
        location_layout.addLayout(path_layout)

        layout.addWidget(location_group)

        # File preview group
        preview_group = QGroupBox("Files to be Created")
        preview_layout = QVBoxLayout(preview_group)

        self._preview_label = QLabel()
        self._preview_label.setWordWrap(True)
        self._preview_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        preview_layout.addWidget(self._preview_label)

        layout.addWidget(preview_group)

        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Initial preview update
        self._update_preview()

    def _sanitize_name(self, name: str) -> str:
        """
        Sanitize a name for use in filenames.

        Parameters
        ----------
        name : str
            The name to sanitize.

        Returns
        -------
        str
            Sanitized name with only alphanumeric and underscore characters.
        """
        if not name:
            return ""
        # Remove file extension if present
        name = Path(name).stem
        # Replace non-alphanumeric chars with underscore
        name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
        # Remove consecutive underscores
        name = re.sub(r"_+", "_", name)
        # Remove leading/trailing underscores
        name = name.strip("_")
        return name.lower()

    def _update_preview(self) -> None:
        """Update the file preview based on current settings."""
        name = self._name_edit.text().strip()
        if not name:
            name = "unnamed"

        base_name = f"export_{self._scenario_number:03d}_{name}"
        export_path = Path(self._path_edit.text()) if self._path_edit.text() else Path(".")

        files = [
            f"source/{base_name}_source.fdl",
            f"templates/{base_name}_template.fdl",
            f"Results/Scen{self._scenario_number}-RESULT-{base_name}.fdl",
        ]

        if self._include_image_checkbox.isChecked():
            files.insert(1, f"source/{base_name}_source.tiff")

        preview_text = f"Base path: {export_path}\n\n"
        preview_text += "\n".join(f"  - {f}" for f in files)

        self._preview_label.setText(preview_text)

    def _on_browse(self) -> None:
        """Handle browse button click."""
        path = QFileDialog.getExistingDirectory(
            self,
            "Select Export Directory",
            self._path_edit.text() or str(Path.home()),
        )
        if path:
            self._path_edit.setText(path)

    @property
    def scenario_number(self) -> int:
        """Get the scenario number."""
        return self._scenario_number

    @property
    def scenario_name(self) -> str:
        """Get the scenario name."""
        return self._name_edit.text().strip() or "unnamed"

    @property
    def include_image(self) -> bool:
        """Check if source image should be included."""
        return self._include_image_checkbox.isChecked()

    @property
    def export_path(self) -> str:
        """Get the export path."""
        return self._path_edit.text().strip()

    def get_export_config(self) -> dict:
        """
        Get the complete export configuration.

        Returns
        -------
        dict
            Dictionary with export configuration:
            - scenario_number: int
            - scenario_name: str
            - include_image: bool
            - export_path: str
            - base_name: str
        """
        name = self.scenario_name
        return {
            "scenario_number": self._scenario_number,
            "scenario_name": name,
            "include_image": self.include_image,
            "export_path": self.export_path,
            "base_name": f"export_{self._scenario_number:03d}_{name}",
        }
