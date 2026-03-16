# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
FDL Model wrapper for FDL Viewer.

Provides a Qt-aware wrapper around the FDL dataclass with signals for
reactive UI updates and computed properties for visualization.
"""

from fdl import (
    FDL,
    Canvas,
    CanvasTemplate,
    Context,
    FramingDecision,
    find_by_id,
    find_by_label,
)
from PySide6.QtCore import QObject, QPointF, QRectF, Signal


class FDLModel(QObject):
    """
    Qt-aware wrapper around fdl.FDL.

    Emits signals when FDL data changes, enabling reactive UI updates.
    Provides computed properties for visualization (bounding boxes, etc.).

    Parameters
    ----------
    fdl : FDL, optional
        The FDL dataclass to wrap.
    parent : QObject, optional
        Parent QObject for Qt ownership.

    Attributes
    ----------
    fdl_changed : Signal
        Emitted when the FDL data changes.
    context_changed : Signal
        Emitted when the selected context changes.
    canvas_changed : Signal
        Emitted when the selected canvas changes.
    framing_decision_changed : Signal
        Emitted when the selected framing decision changes.

    Examples
    --------
    >>> model = FDLModel(loaded_fdl)
    >>> model.fdl_changed.connect(on_fdl_changed)
    >>> model.set_selection("Context Label", "canvas_id", "fd_id")
    """

    # Signals
    fdl_changed = Signal()
    context_changed = Signal(str)
    canvas_changed = Signal(str)
    framing_decision_changed = Signal(str)

    def __init__(self, fdl: FDL | None = None, parent: QObject | None = None) -> None:
        """
        Initialize the FDLModel.

        Parameters
        ----------
        fdl : FDL, optional
            The FDL dataclass to wrap.
        parent : QObject, optional
            Parent QObject for Qt ownership.
        """
        super().__init__(parent)
        self._fdl: FDL | None = fdl
        self._file_path: str = ""
        self._selected_context_label: str = ""
        self._selected_canvas_id: str = ""
        self._selected_framing_id: str = ""

    @property
    def fdl(self) -> FDL | None:
        """
        Get the wrapped FDL dataclass.

        Returns
        -------
        FDL or None
            The FDL dataclass, or None if not set.
        """
        return self._fdl

    def set_fdl(self, fdl: FDL | None) -> None:
        """
        Set the FDL dataclass.

        Parameters
        ----------
        fdl : FDL or None
            The FDL dataclass to wrap.
        """
        self._fdl = fdl
        self._selected_context_label = ""
        self._selected_canvas_id = ""
        self._selected_framing_id = ""
        self.fdl_changed.emit()

    @property
    def file_path(self) -> str:
        """Get the file path of the loaded FDL."""
        return self._file_path

    def set_file_path(self, path: str) -> None:
        """
        Set the file path of the FDL.

        Parameters
        ----------
        path : str
            The file path.
        """
        self._file_path = path

    @property
    def is_valid(self) -> bool:
        """
        Check if the FDL is valid.

        Returns
        -------
        bool
            True if FDL is set and has contexts.
        """
        return self._fdl is not None and len(self._fdl.contexts) > 0

    # Context operations
    @property
    def contexts(self) -> list[Context]:
        """
        Get the list of contexts.

        Returns
        -------
        List[Context]
            The list of contexts, or empty list if FDL not set.
        """
        if self._fdl is None:
            return []
        return self._fdl.contexts

    @property
    def context_labels(self) -> list[str]:
        """
        Get the list of context labels.

        Returns
        -------
        List[str]
            The list of context labels.
        """
        return [ctx.label for ctx in self.contexts]

    @property
    def current_context(self) -> Context | None:
        """
        Get the currently selected context.

        Returns
        -------
        Context or None
            The selected context, or None if not selected.
        """
        if not self._selected_context_label or self._fdl is None:
            return None
        return find_by_label(self._fdl.contexts, self._selected_context_label)

    def set_context(self, label: str) -> None:
        """
        Set the selected context by label.

        Parameters
        ----------
        label : str
            The context label.
        """
        self._selected_context_label = label
        self._selected_canvas_id = ""
        self._selected_framing_id = ""
        self.context_changed.emit(label)

    # Canvas operations
    @property
    def canvases(self) -> list[Canvas]:
        """
        Get the list of canvases in the current context.

        Returns
        -------
        List[Canvas]
            The list of canvases, or empty list if no context selected.
        """
        context = self.current_context
        if context is None:
            return []
        return context.canvases

    @property
    def canvas_labels(self) -> list[str]:
        """
        Get the list of canvas labels/IDs.

        Returns
        -------
        List[str]
            The list of canvas labels (or IDs if no label).
        """
        return [cv.label or cv.id for cv in self.canvases]

    @property
    def current_canvas(self) -> Canvas | None:
        """
        Get the currently selected canvas.

        Returns
        -------
        Canvas or None
            The selected canvas, or None if not selected.
        """
        if not self._selected_canvas_id:
            return None
        context = self.current_context
        if context is None:
            return None
        return find_by_id(context.canvases, self._selected_canvas_id)

    def set_canvas(self, canvas_id: str) -> None:
        """
        Set the selected canvas by ID.

        Parameters
        ----------
        canvas_id : str
            The canvas ID.
        """
        self._selected_canvas_id = canvas_id
        self._selected_framing_id = ""
        self.canvas_changed.emit(canvas_id)

    def get_canvas_by_index(self, index: int) -> Canvas | None:
        """
        Get a canvas by index.

        Parameters
        ----------
        index : int
            The index of the canvas.

        Returns
        -------
        Canvas or None
            The canvas at the index, or None if out of bounds.
        """
        canvases = self.canvases
        if 0 <= index < len(canvases):
            return canvases[index]
        return None

    # Framing decision operations
    @property
    def framing_decisions(self) -> list[FramingDecision]:
        """
        Get the list of framing decisions in the current canvas.

        Returns
        -------
        List[FramingDecision]
            The list of framing decisions, or empty list if no canvas selected.
        """
        canvas = self.current_canvas
        if canvas is None:
            return []
        return canvas.framing_decisions

    @property
    def framing_labels(self) -> list[str]:
        """
        Get the list of framing decision labels/IDs.

        Returns
        -------
        List[str]
            The list of framing decision labels (or IDs if no label).
        """
        return [fd.label or fd.id for fd in self.framing_decisions]

    @property
    def current_framing_decision(self) -> FramingDecision | None:
        """
        Get the currently selected framing decision.

        Returns
        -------
        FramingDecision or None
            The selected framing decision, or None if not selected.
        """
        if not self._selected_framing_id:
            return None
        canvas = self.current_canvas
        if canvas is None:
            return None
        return find_by_id(canvas.framing_decisions, self._selected_framing_id)

    def set_framing_decision(self, fd_id: str) -> None:
        """
        Set the selected framing decision by ID.

        Parameters
        ----------
        fd_id : str
            The framing decision ID.
        """
        self._selected_framing_id = fd_id
        self.framing_decision_changed.emit(fd_id)

    def get_framing_by_index(self, index: int) -> FramingDecision | None:
        """
        Get a framing decision by index.

        Parameters
        ----------
        index : int
            The index of the framing decision.

        Returns
        -------
        FramingDecision or None
            The framing decision at the index, or None if out of bounds.
        """
        fds = self.framing_decisions
        if 0 <= index < len(fds):
            return fds[index]
        return None

    # Combined selection
    def set_selection(self, context_label: str, canvas_id: str, fd_id: str) -> None:
        """
        Set the complete selection.

        Parameters
        ----------
        context_label : str
            The context label.
        canvas_id : str
            The canvas ID.
        fd_id : str
            The framing decision ID.
        """
        self._selected_context_label = context_label
        self._selected_canvas_id = canvas_id
        self._selected_framing_id = fd_id
        self.context_changed.emit(context_label)
        self.canvas_changed.emit(canvas_id)
        self.framing_decision_changed.emit(fd_id)

    @property
    def selection_ids(self) -> tuple:
        """
        Get the current selection IDs.

        Returns
        -------
        tuple
            (context_label, canvas_id, framing_id)
        """
        return (self._selected_context_label, self._selected_canvas_id, self._selected_framing_id)

    # Canvas templates
    @property
    def canvas_templates(self) -> list[CanvasTemplate]:
        """
        Get the list of canvas templates.

        Returns
        -------
        List[CanvasTemplate]
            The list of canvas templates.
        """
        if self._fdl is None:
            return []
        return self._fdl.canvas_templates

    @property
    def template_labels(self) -> list[str]:
        """
        Get the list of template labels/IDs.

        Returns
        -------
        List[str]
            The list of template labels (or IDs if no label).
        """
        return [t.label or t.id for t in self.canvas_templates]

    def get_template_by_id(self, template_id: str) -> CanvasTemplate | None:
        """
        Get a canvas template by ID.

        Parameters
        ----------
        template_id : str
            The template ID.

        Returns
        -------
        CanvasTemplate or None
            The template, or None if not found.
        """
        return find_by_id(self.canvas_templates, template_id)

    def get_first_template(self) -> CanvasTemplate | None:
        """
        Get the first canvas template.

        Returns
        -------
        CanvasTemplate or None
            The first template, or None if none exist.
        """
        templates = self.canvas_templates
        if templates:
            return templates[0]
        return None

    # Visualization helpers
    def get_canvas_rect(self) -> QRectF | None:
        """Get the canvas bounding rectangle, or None if no canvas selected."""
        canvas = self.current_canvas
        if canvas is None:
            return None
        return QRectF(*canvas.get_rect())

    def get_effective_rect(self) -> QRectF | None:
        """Get the effective dimensions rectangle, or None if not defined."""
        canvas = self.current_canvas
        if canvas is None:
            return None
        rect = canvas.get_effective_rect()
        return QRectF(*rect) if rect is not None else None

    def get_framing_rect(self) -> QRectF | None:
        """Get the framing decision rectangle, or None if no framing selected."""
        fd = self.current_framing_decision
        if fd is None:
            return None
        return QRectF(*fd.get_rect())

    def get_protection_rect(self) -> QRectF | None:
        """Get the protection dimensions rectangle, or None if not defined."""
        fd = self.current_framing_decision
        if fd is None:
            return None
        rect = fd.get_protection_rect()
        return QRectF(*rect) if rect is not None else None

    def get_center_point(self) -> QPointF | None:
        """
        Get the center point of the framing decision.

        Returns
        -------
        QPointF or None
            The center point, or None if no framing selected.
        """
        rect = self.get_framing_rect()
        if rect is None:
            return None
        return rect.center()

    # Info display
    @property
    def version_string(self) -> str:
        """Get the FDL version as a string."""
        if self._fdl is None:
            return ""
        return f"{self._fdl.version.major}.{self._fdl.version.minor}"

    @property
    def uuid(self) -> str:
        """Get the FDL UUID."""
        if self._fdl is None:
            return ""
        return self._fdl.uuid

    @property
    def creator(self) -> str:
        """Get the FDL creator."""
        if self._fdl is None:
            return ""
        return self._fdl.fdl_creator

    def to_dict(self) -> dict:
        """
        Convert the FDL to a dictionary.

        Returns
        -------
        dict
            The FDL as a dictionary, or empty dict if not set.
        """
        if self._fdl is None:
            return {}
        return self._fdl.as_dict()
