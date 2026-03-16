# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Application state management for FDL Viewer.

Provides a centralized singleton for managing application state with Qt signals
for reactive UI updates. Similar to Zustand/Redux pattern but using Qt signals.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, Signal

if TYPE_CHECKING:
    from fdl import CanvasTemplate, TemplateResult

    from fdl_viewer.models.fdl_model import FDLModel


class AppState(QObject):
    """
    Centralized application state with reactive signals.

    This singleton class manages all application state and emits signals
    when state changes, enabling reactive UI updates.

    Attributes
    ----------
    source_fdl_changed : Signal
        Emitted when the source FDL is loaded or changed.
    template_fdl_changed : Signal
        Emitted when the template FDL is loaded or changed.
    output_fdl_changed : Signal
        Emitted when the output FDL is generated.
    selection_changed : Signal
        Emitted when context/canvas/framing selection changes.
    template_modified_changed : Signal
        Emitted when template parameters are modified.
    active_tab_changed : Signal
        Emitted when the active tab changes.
    sidebar_collapsed_changed : Signal
        Emitted when sidebar collapse state changes.
    grid_visible_changed : Signal
        Emitted when grid visibility changes.
    image_opacity_changed : Signal
        Emitted when image underlay opacity changes.
    error_occurred : Signal
        Emitted when an error occurs.

    Examples
    --------
    >>> state = AppState.instance()
    >>> state.source_fdl_changed.connect(my_handler)
    >>> state.set_source_fdl(loaded_fdl)
    """

    _instance: AppState | None = None

    # FDL state signals
    source_fdl_changed = Signal(object)  # FDLModel or None
    template_fdl_changed = Signal(object)  # FDLModel or None
    output_fdl_changed = Signal(object)  # FDLModel or None

    # Selection signals
    selection_changed = Signal(str, str, str)  # context_label, canvas_id, framing_id
    template_modified_changed = Signal(bool)

    # UI state signals
    active_tab_changed = Signal(int)
    sidebar_collapsed_changed = Signal(bool)
    grid_visible_changed = Signal(bool)
    image_opacity_changed = Signal(float)

    # Layer visibility signals
    canvas_visible_changed = Signal(bool)
    effective_visible_changed = Signal(bool)
    framing_visible_changed = Signal(bool)
    protection_visible_changed = Signal(bool)
    image_visible_changed = Signal(bool)
    hud_visible_changed = Signal(bool)

    # Error handling
    error_occurred = Signal(str)

    # Transform results
    transform_result_changed = Signal(object)  # TemplateResult

    def __init__(self, parent: QObject | None = None) -> None:
        """
        Initialize the AppState.

        Parameters
        ----------
        parent : QObject, optional
            Parent QObject for Qt ownership.
        """
        super().__init__(parent)

        # FDL state
        self._source_fdl: FDLModel | None = None
        self._template_fdl: FDLModel | None = None
        self._output_fdl: FDLModel | None = None

        # Selection state
        self._selected_context: str = ""
        self._selected_canvas: str = ""
        self._selected_framing: str = ""

        # Template state
        self._template_modified: bool = False
        self._current_template: CanvasTemplate | None = None

        # UI state
        self._active_tab: int = 0
        self._sidebar_collapsed: bool = False
        self._grid_visible: bool = True
        self._image_opacity: float = 0.7

        # Layer visibility
        self._canvas_visible: bool = True
        self._effective_visible: bool = True
        self._framing_visible: bool = True
        self._protection_visible: bool = True
        self._image_underlay_visible: bool = True
        self._hud_visible: bool = False  # Default OFF

        # Transform results
        self._transform_result: TemplateResult | None = None

    @classmethod
    def instance(cls) -> AppState:
        """
        Get the singleton instance of AppState.

        Returns
        -------
        AppState
            The singleton AppState instance.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance. Useful for testing."""
        cls._instance = None

    # Source FDL
    @property
    def source_fdl(self) -> FDLModel | None:
        """Get the source FDL model."""
        return self._source_fdl

    def set_source_fdl(self, fdl_model: FDLModel | None) -> None:
        """
        Set the source FDL model.

        Parameters
        ----------
        fdl_model : FDLModel or None
            The FDL model to set as source.
        """
        self._source_fdl = fdl_model
        self.source_fdl_changed.emit(fdl_model)

    # Template FDL
    @property
    def template_fdl(self) -> FDLModel | None:
        """Get the template FDL model."""
        return self._template_fdl

    def set_template_fdl(self, fdl_model: FDLModel | None) -> None:
        """
        Set the template FDL model.

        Parameters
        ----------
        fdl_model : FDLModel or None
            The FDL model to set as template.
        """
        self._template_fdl = fdl_model
        self._template_modified = False
        self.template_fdl_changed.emit(fdl_model)
        self.template_modified_changed.emit(False)

    # Output FDL
    @property
    def output_fdl(self) -> FDLModel | None:
        """Get the output FDL model."""
        return self._output_fdl

    def set_output_fdl(self, fdl_model: FDLModel | None) -> None:
        """
        Set the output FDL model.

        Parameters
        ----------
        fdl_model : FDLModel or None
            The FDL model to set as output.
        """
        self._output_fdl = fdl_model
        self.output_fdl_changed.emit(fdl_model)

    # Selection
    @property
    def selected_context(self) -> str:
        """Get the selected context label."""
        return self._selected_context

    @property
    def selected_canvas(self) -> str:
        """Get the selected canvas ID."""
        return self._selected_canvas

    @property
    def selected_framing(self) -> str:
        """Get the selected framing decision ID."""
        return self._selected_framing

    def set_selection(self, context: str, canvas: str, framing: str) -> None:
        """
        Set the current selection.

        Parameters
        ----------
        context : str
            The context label.
        canvas : str
            The canvas ID.
        framing : str
            The framing decision ID.
        """
        self._selected_context = context
        self._selected_canvas = canvas
        self._selected_framing = framing
        self.selection_changed.emit(context, canvas, framing)

    # Template modification
    @property
    def template_modified(self) -> bool:
        """Check if template has been modified."""
        return self._template_modified

    def set_template_modified(self, modified: bool) -> None:
        """
        Set the template modified state.

        Parameters
        ----------
        modified : bool
            Whether the template has been modified.
        """
        self._template_modified = modified
        self.template_modified_changed.emit(modified)

    # Current template
    @property
    def current_template(self) -> CanvasTemplate | None:
        """Get the current canvas template."""
        return self._current_template

    def set_current_template(self, template: CanvasTemplate | None) -> None:
        """
        Set the current canvas template.

        Parameters
        ----------
        template : CanvasTemplate or None
            The template to use for transformations.
        """
        self._current_template = template

    # UI State
    @property
    def active_tab(self) -> int:
        """Get the active tab index."""
        return self._active_tab

    def set_active_tab(self, index: int) -> None:
        """
        Set the active tab index.

        Parameters
        ----------
        index : int
            The tab index (0-3).
        """
        self._active_tab = index
        self.active_tab_changed.emit(index)

    @property
    def sidebar_collapsed(self) -> bool:
        """Check if sidebar is collapsed."""
        return self._sidebar_collapsed

    def set_sidebar_collapsed(self, collapsed: bool) -> None:
        """
        Set the sidebar collapsed state.

        Parameters
        ----------
        collapsed : bool
            Whether the sidebar is collapsed.
        """
        self._sidebar_collapsed = collapsed
        self.sidebar_collapsed_changed.emit(collapsed)

    @property
    def grid_visible(self) -> bool:
        """Check if grid is visible."""
        return self._grid_visible

    def set_grid_visible(self, visible: bool) -> None:
        """
        Set the grid visibility.

        Parameters
        ----------
        visible : bool
            Whether the grid is visible.
        """
        self._grid_visible = visible
        self.grid_visible_changed.emit(visible)

    @property
    def image_opacity(self) -> float:
        """Get the image underlay opacity."""
        return self._image_opacity

    def set_image_opacity(self, opacity: float) -> None:
        """
        Set the image underlay opacity.

        Parameters
        ----------
        opacity : float
            The opacity value (0.0 to 1.0).
        """
        self._image_opacity = max(0.0, min(1.0, opacity))
        self.image_opacity_changed.emit(self._image_opacity)

    # Layer visibility
    @property
    def canvas_visible(self) -> bool:
        """Check if canvas layer is visible."""
        return self._canvas_visible

    def set_canvas_visible(self, visible: bool) -> None:
        """Set the canvas layer visibility."""
        self._canvas_visible = visible
        self.canvas_visible_changed.emit(visible)

    @property
    def effective_visible(self) -> bool:
        """Check if effective dimensions layer is visible."""
        return self._effective_visible

    def set_effective_visible(self, visible: bool) -> None:
        """Set the effective dimensions layer visibility."""
        self._effective_visible = visible
        self.effective_visible_changed.emit(visible)

    @property
    def framing_visible(self) -> bool:
        """Check if framing decision layer is visible."""
        return self._framing_visible

    def set_framing_visible(self, visible: bool) -> None:
        """Set the framing decision layer visibility."""
        self._framing_visible = visible
        self.framing_visible_changed.emit(visible)

    @property
    def protection_visible(self) -> bool:
        """Check if protection layer is visible."""
        return self._protection_visible

    def set_protection_visible(self, visible: bool) -> None:
        """Set the protection layer visibility."""
        self._protection_visible = visible
        self.protection_visible_changed.emit(visible)

    @property
    def image_underlay_visible(self) -> bool:
        """Check if image underlay is visible."""
        return self._image_underlay_visible

    def set_image_underlay_visible(self, visible: bool) -> None:
        """Set the image underlay visibility."""
        self._image_underlay_visible = visible
        self.image_visible_changed.emit(visible)

    @property
    def hud_visible(self) -> bool:
        """Check if HUD is visible."""
        return self._hud_visible

    def set_hud_visible(self, visible: bool) -> None:
        """Set the HUD visibility."""
        self._hud_visible = visible
        self.hud_visible_changed.emit(visible)

    # Transform results
    @property
    def transform_result(self) -> TemplateResult | None:
        """Get the last transformation result."""
        return self._transform_result

    def set_transform_result(self, result: TemplateResult | None) -> None:
        """
        Set the transformation result.

        Parameters
        ----------
        result : TemplateResult or None
            The transformation result.
        """
        self._transform_result = result
        self.transform_result_changed.emit(result)

    def emit_error(self, message: str) -> None:
        """
        Emit an error message.

        Parameters
        ----------
        message : str
            The error message.
        """
        self.error_occurred.emit(message)
