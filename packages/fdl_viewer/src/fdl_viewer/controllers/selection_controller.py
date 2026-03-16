# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Selection controller for FDL Viewer.

Handles cascading selection logic for context/canvas/framing decisions.
"""

from PySide6.QtCore import QObject, Signal

from fdl_viewer.models.app_state import AppState
from fdl_viewer.models.fdl_model import FDLModel


class SelectionController(QObject):
    """
    Controller for cascading selection of context/canvas/framing decisions.

    Manages the selection state and provides methods for updating selections
    while maintaining cascade consistency.

    Parameters
    ----------
    parent : QObject, optional
        Parent QObject for Qt ownership.

    Attributes
    ----------
    contexts_updated : Signal
        Emitted when the list of contexts changes.
    canvases_updated : Signal
        Emitted when the list of canvases changes.
    framings_updated : Signal
        Emitted when the list of framing decisions changes.
    selection_complete : Signal
        Emitted when a complete selection is made (context, canvas, framing).
    """

    contexts_updated = Signal(list)  # List of context labels
    canvases_updated = Signal(list)  # List of (canvas_id, label) tuples
    framings_updated = Signal(list)  # List of (fd_id, label) tuples
    selection_complete = Signal(str, str, str)  # context_label, canvas_id, fd_id

    def __init__(self, parent: QObject | None = None) -> None:
        """
        Initialize the SelectionController.

        Parameters
        ----------
        parent : QObject, optional
            Parent QObject for Qt ownership.
        """
        super().__init__(parent)
        self._app_state = AppState.instance()
        self._fdl_model: FDLModel | None = None

    def set_fdl_model(self, model: FDLModel | None) -> None:
        """
        Set the FDL model to use for selections.

        Parameters
        ----------
        model : FDLModel or None
            The FDL model.
        """
        self._fdl_model = model
        self._update_contexts()

    def _update_contexts(self) -> None:
        """Update the list of available contexts."""
        if self._fdl_model is None or not self._fdl_model.is_valid:
            self.contexts_updated.emit([])
            return

        labels = self._fdl_model.context_labels
        self.contexts_updated.emit(labels)

        # Auto-select first if available
        if labels:
            self.select_context(labels[0])

    def select_context(self, label: str) -> None:
        """
        Select a context by label.

        Parameters
        ----------
        label : str
            The context label to select.
        """
        if self._fdl_model is None:
            return

        self._fdl_model.set_context(label)
        self._app_state.set_selection(label, "", "")
        self._update_canvases()

    def _update_canvases(self) -> None:
        """Update the list of available canvases for the selected context."""
        if self._fdl_model is None:
            self.canvases_updated.emit([])
            return

        canvases = self._fdl_model.canvases
        canvas_list = [(cv.id, cv.label or cv.id) for cv in canvases]
        self.canvases_updated.emit(canvas_list)

        # Auto-select first if available
        if canvas_list:
            self.select_canvas(canvas_list[0][0])

    def select_canvas(self, canvas_id: str) -> None:
        """
        Select a canvas by ID.

        Parameters
        ----------
        canvas_id : str
            The canvas ID to select.
        """
        if self._fdl_model is None:
            return

        self._fdl_model.set_canvas(canvas_id)
        context_label = self._fdl_model._selected_context_label
        self._app_state.set_selection(context_label, canvas_id, "")
        self._update_framings()

    def _update_framings(self) -> None:
        """Update the list of available framing decisions for the selected canvas."""
        if self._fdl_model is None:
            self.framings_updated.emit([])
            return

        framings = self._fdl_model.framing_decisions
        fd_list = [(fd.id, fd.label or fd.id) for fd in framings]
        self.framings_updated.emit(fd_list)

        # Auto-select first if available
        if fd_list:
            self.select_framing(fd_list[0][0])

    def select_framing(self, fd_id: str) -> None:
        """
        Select a framing decision by ID.

        Parameters
        ----------
        fd_id : str
            The framing decision ID to select.
        """
        if self._fdl_model is None:
            return

        self._fdl_model.set_framing_decision(fd_id)
        context_label = self._fdl_model._selected_context_label
        canvas_id = self._fdl_model._selected_canvas_id
        self._app_state.set_selection(context_label, canvas_id, fd_id)
        self.selection_complete.emit(context_label, canvas_id, fd_id)

    def get_current_selection(self) -> tuple[str, str, str]:
        """
        Get the current selection.

        Returns
        -------
        tuple
            (context_label, canvas_id, framing_id)
        """
        if self._fdl_model is None:
            return ("", "", "")
        return self._fdl_model.selection_ids

    def get_selected_context(self) -> object:
        """
        Get the currently selected context.

        Returns
        -------
        Context or None
            The selected context.
        """
        if self._fdl_model is None:
            return None
        return self._fdl_model.current_context

    def get_selected_canvas(self) -> object:
        """
        Get the currently selected canvas.

        Returns
        -------
        Canvas or None
            The selected canvas.
        """
        if self._fdl_model is None:
            return None
        return self._fdl_model.current_canvas
