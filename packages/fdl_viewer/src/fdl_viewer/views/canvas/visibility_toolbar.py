# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Visibility toolbar for FDL Viewer canvas.

Provides toggle buttons for showing/hiding canvas layers.
"""

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QWidget,
)

from fdl_viewer.models.app_state import AppState


class VisibilityToolbar(QWidget):
    """
    Compact toolbar with toggle buttons for layer visibility.

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
        self.setObjectName("visibilityToolbar")
        self.setMaximumHeight(32)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(4)

        # Grid toggle
        self._grid_btn = QPushButton("Grid")
        self._grid_btn.setObjectName("gridToggle")
        self._grid_btn.setCheckable(True)
        self._grid_btn.setChecked(True)
        layout.addWidget(self._grid_btn)

        # Canvas toggle
        self._canvas_btn = QPushButton("Canvas")
        self._canvas_btn.setObjectName("canvasToggle")
        self._canvas_btn.setCheckable(True)
        self._canvas_btn.setChecked(True)
        layout.addWidget(self._canvas_btn)

        # Effective toggle
        self._effective_btn = QPushButton("Effective")
        self._effective_btn.setObjectName("effectiveToggle")
        self._effective_btn.setCheckable(True)
        self._effective_btn.setChecked(True)
        layout.addWidget(self._effective_btn)

        # Framing toggle
        self._framing_btn = QPushButton("Framing")
        self._framing_btn.setObjectName("framingToggle")
        self._framing_btn.setCheckable(True)
        self._framing_btn.setChecked(True)
        layout.addWidget(self._framing_btn)

        # Protection toggle
        self._protection_btn = QPushButton("Protection")
        self._protection_btn.setObjectName("protectionToggle")
        self._protection_btn.setCheckable(True)
        self._protection_btn.setChecked(True)
        layout.addWidget(self._protection_btn)

        # Image toggle
        self._image_btn = QPushButton("Image")
        self._image_btn.setObjectName("imageToggle")
        self._image_btn.setCheckable(True)
        self._image_btn.setChecked(True)
        layout.addWidget(self._image_btn)

        # HUD toggle
        self._hud_btn = QPushButton("HUD")
        self._hud_btn.setObjectName("hudToggle")
        self._hud_btn.setCheckable(True)
        self._hud_btn.setChecked(False)  # Default OFF
        layout.addWidget(self._hud_btn)

        layout.addStretch()

    def _connect_signals(self) -> None:
        """Connect signals."""
        # Button signals
        self._grid_btn.toggled.connect(self._on_grid_toggled)
        self._canvas_btn.toggled.connect(self._on_canvas_toggled)
        self._effective_btn.toggled.connect(self._on_effective_toggled)
        self._framing_btn.toggled.connect(self._on_framing_toggled)
        self._protection_btn.toggled.connect(self._on_protection_toggled)
        self._image_btn.toggled.connect(self._on_image_toggled)
        self._hud_btn.toggled.connect(self._on_hud_toggled)

        # App state signals (for syncing if changed elsewhere)
        self._app_state.grid_visible_changed.connect(self._on_state_grid_changed)
        self._app_state.canvas_visible_changed.connect(self._on_state_canvas_changed)
        self._app_state.effective_visible_changed.connect(self._on_state_effective_changed)
        self._app_state.framing_visible_changed.connect(self._on_state_framing_changed)
        self._app_state.protection_visible_changed.connect(self._on_state_protection_changed)
        self._app_state.image_visible_changed.connect(self._on_state_image_changed)
        self._app_state.hud_visible_changed.connect(self._on_state_hud_changed)

    def _sync_from_state(self) -> None:
        """Sync button states from app state."""
        self._updating = True
        self._grid_btn.setChecked(self._app_state.grid_visible)
        self._canvas_btn.setChecked(self._app_state.canvas_visible)
        self._effective_btn.setChecked(self._app_state.effective_visible)
        self._framing_btn.setChecked(self._app_state.framing_visible)
        self._protection_btn.setChecked(self._app_state.protection_visible)
        self._image_btn.setChecked(self._app_state.image_underlay_visible)
        self._hud_btn.setChecked(self._app_state.hud_visible)
        self._updating = False

    # Button handlers
    @Slot(bool)
    def _on_grid_toggled(self, checked: bool) -> None:
        if not self._updating:
            self._app_state.set_grid_visible(checked)

    @Slot(bool)
    def _on_canvas_toggled(self, checked: bool) -> None:
        if not self._updating:
            self._app_state.set_canvas_visible(checked)

    @Slot(bool)
    def _on_effective_toggled(self, checked: bool) -> None:
        if not self._updating:
            self._app_state.set_effective_visible(checked)

    @Slot(bool)
    def _on_framing_toggled(self, checked: bool) -> None:
        if not self._updating:
            self._app_state.set_framing_visible(checked)

    @Slot(bool)
    def _on_protection_toggled(self, checked: bool) -> None:
        if not self._updating:
            self._app_state.set_protection_visible(checked)

    @Slot(bool)
    def _on_image_toggled(self, checked: bool) -> None:
        if not self._updating:
            self._app_state.set_image_underlay_visible(checked)

    # State change handlers
    @Slot(bool)
    def _on_state_grid_changed(self, visible: bool) -> None:
        self._updating = True
        self._grid_btn.setChecked(visible)
        self._updating = False

    @Slot(bool)
    def _on_state_canvas_changed(self, visible: bool) -> None:
        self._updating = True
        self._canvas_btn.setChecked(visible)
        self._updating = False

    @Slot(bool)
    def _on_state_effective_changed(self, visible: bool) -> None:
        self._updating = True
        self._effective_btn.setChecked(visible)
        self._updating = False

    @Slot(bool)
    def _on_state_framing_changed(self, visible: bool) -> None:
        self._updating = True
        self._framing_btn.setChecked(visible)
        self._updating = False

    @Slot(bool)
    def _on_state_protection_changed(self, visible: bool) -> None:
        self._updating = True
        self._protection_btn.setChecked(visible)
        self._updating = False

    @Slot(bool)
    def _on_state_image_changed(self, visible: bool) -> None:
        self._updating = True
        self._image_btn.setChecked(visible)
        self._updating = False

    @Slot(bool)
    def _on_hud_toggled(self, checked: bool) -> None:
        if not self._updating:
            self._app_state.set_hud_visible(checked)

    @Slot(bool)
    def _on_state_hud_changed(self, visible: bool) -> None:
        self._updating = True
        self._hud_btn.setChecked(visible)
        self._updating = False
