# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Visibility controls view for FDL Viewer.

Provides toggles for showing/hiding canvas layers.
"""

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QCheckBox,
    QGroupBox,
    QVBoxLayout,
    QWidget,
)

from fdl_viewer.models.app_state import AppState


class VisibilityView(QWidget):
    """
    View for toggling visibility of canvas layers.

    Provides checkboxes for:
    - Grid
    - Canvas outline
    - Effective dimensions
    - Framing decision
    - Protection area
    - Image underlay

    Parameters
    ----------
    parent : QWidget, optional
        Parent widget.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._app_state = AppState.instance()
        self._updating = False
        self._setup_ui()
        self._connect_signals()
        self._sync_from_state()

    def _setup_ui(self) -> None:
        """Set up the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Group box
        group = QGroupBox("Layer Visibility")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(4)

        # Grid toggle
        self._grid_check = QCheckBox("Grid")
        self._grid_check.setObjectName("gridCheckbox")
        self._grid_check.setChecked(True)
        group_layout.addWidget(self._grid_check)

        # Canvas toggle
        self._canvas_check = QCheckBox("Canvas")
        self._canvas_check.setObjectName("canvasCheckbox")
        self._canvas_check.setChecked(True)
        group_layout.addWidget(self._canvas_check)

        # Effective toggle
        self._effective_check = QCheckBox("Effective Dimensions")
        self._effective_check.setObjectName("effectiveCheckbox")
        self._effective_check.setChecked(True)
        group_layout.addWidget(self._effective_check)

        # Framing toggle
        self._framing_check = QCheckBox("Framing Decision")
        self._framing_check.setObjectName("framingCheckbox")
        self._framing_check.setChecked(True)
        group_layout.addWidget(self._framing_check)

        # Protection toggle
        self._protection_check = QCheckBox("Protection")
        self._protection_check.setObjectName("protectionCheckbox")
        self._protection_check.setChecked(True)
        group_layout.addWidget(self._protection_check)

        # Image toggle
        self._image_check = QCheckBox("Image Underlay")
        self._image_check.setObjectName("imageCheckbox")
        self._image_check.setChecked(True)
        group_layout.addWidget(self._image_check)

        # HUD toggle
        self._hud_check = QCheckBox("HUD Display")
        self._hud_check.setObjectName("hudCheckbox")
        self._hud_check.setChecked(False)  # Default OFF
        group_layout.addWidget(self._hud_check)

        layout.addWidget(group)

    def _connect_signals(self) -> None:
        """Connect signals."""
        # Checkbox signals
        self._grid_check.toggled.connect(self._on_grid_toggled)
        self._canvas_check.toggled.connect(self._on_canvas_toggled)
        self._effective_check.toggled.connect(self._on_effective_toggled)
        self._framing_check.toggled.connect(self._on_framing_toggled)
        self._protection_check.toggled.connect(self._on_protection_toggled)
        self._image_check.toggled.connect(self._on_image_toggled)
        self._hud_check.toggled.connect(self._on_hud_toggled)

        # App state signals (for syncing if changed elsewhere)
        self._app_state.grid_visible_changed.connect(self._on_state_grid_changed)
        self._app_state.canvas_visible_changed.connect(self._on_state_canvas_changed)
        self._app_state.effective_visible_changed.connect(self._on_state_effective_changed)
        self._app_state.framing_visible_changed.connect(self._on_state_framing_changed)
        self._app_state.protection_visible_changed.connect(self._on_state_protection_changed)
        self._app_state.image_visible_changed.connect(self._on_state_image_changed)
        self._app_state.hud_visible_changed.connect(self._on_state_hud_changed)

    def _sync_from_state(self) -> None:
        """Sync checkbox states from app state."""
        self._updating = True
        self._grid_check.setChecked(self._app_state.grid_visible)
        self._canvas_check.setChecked(self._app_state.canvas_visible)
        self._effective_check.setChecked(self._app_state.effective_visible)
        self._framing_check.setChecked(self._app_state.framing_visible)
        self._protection_check.setChecked(self._app_state.protection_visible)
        self._image_check.setChecked(self._app_state.image_underlay_visible)
        self._hud_check.setChecked(self._app_state.hud_visible)
        self._updating = False

    # Checkbox handlers
    @Slot(bool)
    def _on_grid_toggled(self, checked: bool) -> None:
        """Handle grid checkbox toggle."""
        if not self._updating:
            self._app_state.set_grid_visible(checked)

    @Slot(bool)
    def _on_canvas_toggled(self, checked: bool) -> None:
        """Handle canvas checkbox toggle."""
        if not self._updating:
            self._app_state.set_canvas_visible(checked)

    @Slot(bool)
    def _on_effective_toggled(self, checked: bool) -> None:
        """Handle effective checkbox toggle."""
        if not self._updating:
            self._app_state.set_effective_visible(checked)

    @Slot(bool)
    def _on_framing_toggled(self, checked: bool) -> None:
        """Handle framing checkbox toggle."""
        if not self._updating:
            self._app_state.set_framing_visible(checked)

    @Slot(bool)
    def _on_protection_toggled(self, checked: bool) -> None:
        """Handle protection checkbox toggle."""
        if not self._updating:
            self._app_state.set_protection_visible(checked)

    @Slot(bool)
    def _on_image_toggled(self, checked: bool) -> None:
        """Handle image checkbox toggle."""
        if not self._updating:
            self._app_state.set_image_underlay_visible(checked)

    # State change handlers (for syncing from external changes)
    @Slot(bool)
    def _on_state_grid_changed(self, visible: bool) -> None:
        """Sync grid checkbox from state."""
        self._updating = True
        self._grid_check.setChecked(visible)
        self._updating = False

    @Slot(bool)
    def _on_state_canvas_changed(self, visible: bool) -> None:
        """Sync canvas checkbox from state."""
        self._updating = True
        self._canvas_check.setChecked(visible)
        self._updating = False

    @Slot(bool)
    def _on_state_effective_changed(self, visible: bool) -> None:
        """Sync effective checkbox from state."""
        self._updating = True
        self._effective_check.setChecked(visible)
        self._updating = False

    @Slot(bool)
    def _on_state_framing_changed(self, visible: bool) -> None:
        """Sync framing checkbox from state."""
        self._updating = True
        self._framing_check.setChecked(visible)
        self._updating = False

    @Slot(bool)
    def _on_state_protection_changed(self, visible: bool) -> None:
        """Sync protection checkbox from state."""
        self._updating = True
        self._protection_check.setChecked(visible)
        self._updating = False

    @Slot(bool)
    def _on_state_image_changed(self, visible: bool) -> None:
        """Sync image checkbox from state."""
        self._updating = True
        self._image_check.setChecked(visible)
        self._updating = False

    @Slot(bool)
    def _on_hud_toggled(self, checked: bool) -> None:
        """Handle HUD checkbox toggle."""
        if not self._updating:
            self._app_state.set_hud_visible(checked)

    @Slot(bool)
    def _on_state_hud_changed(self, visible: bool) -> None:
        """Sync HUD checkbox from state."""
        self._updating = True
        self._hud_check.setChecked(visible)
        self._updating = False
