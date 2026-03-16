# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Transform controller for FDL Viewer.

Handles applying FDL template transformations.
"""

import uuid

from fdl import (
    FDL,
    CanvasTemplate,
    TemplateResult,
    find_by_id,
    find_by_label,
)
from PySide6.QtCore import QObject, Signal


class TransformController(QObject):
    """
    Controller for FDL template transformations.

    Wraps FDL template application with Qt signals for UI integration.

    Parameters
    ----------
    parent : QObject, optional
        Parent QObject for Qt ownership.

    Attributes
    ----------
    transform_started : Signal
        Emitted when transformation starts.
    transform_completed : Signal
        Emitted when transformation completes (result tuple).
    transform_failed : Signal
        Emitted when transformation fails (error message).

    Examples
    --------
    >>> controller = TransformController()
    >>> result = controller.apply_template(source_fdl, template, "Context", "1", "1-1")
    >>> if result:
    ...     new_canvas = result.canvas
    """

    transform_started = Signal()
    transform_completed = Signal(object)  # TemplateResult
    transform_failed = Signal(str)  # error message

    def __init__(self, parent: QObject | None = None) -> None:
        """
        Initialize the TransformController.

        Parameters
        ----------
        parent : QObject, optional
            Parent QObject for Qt ownership.
        """
        super().__init__(parent)

    def apply_template(
        self,
        source_fdl: FDL,
        template: CanvasTemplate,
        context_label: str,
        canvas_id: str,
        framing_decision_id: str,
        new_fd_name: str = "",
        context_creator: str = "FDL Viewer",
    ) -> TemplateResult | None:
        """
        Apply a canvas template to a source FDL.

        Parameters
        ----------
        source_fdl : FDL
            The source FDL to transform.
        template : CanvasTemplate
            The template to apply.
        context_label : str
            The label of the context to use.
        canvas_id : str
            The ID of the canvas to use.
        framing_decision_id : str
            The ID of the framing decision to use.
        new_fd_name : str, optional
            Name for the new framing decision.
        context_creator : str, optional
            Creator name for the new context.

        Returns
        -------
        TemplateResult or None
            The transformation result, or None if transformation failed.

        Raises
        ------
        ValueError
            If the context, canvas, or framing decision is not found.
        """
        self.transform_started.emit()

        try:
            # Find the source context
            context = find_by_label(source_fdl.contexts, context_label)
            if context is None:
                raise ValueError(f"Context not found: {context_label}")

            # Find the source canvas
            canvas = find_by_id(context.canvases, canvas_id)
            if canvas is None:
                raise ValueError(f"Canvas not found: {canvas_id}")

            # Find the framing decision
            framing = find_by_id(canvas.framing_decisions, framing_decision_id)
            if framing is None:
                raise ValueError(f"Framing decision not found: {framing_decision_id}")

            # Apply the template
            new_canvas_id = uuid.uuid4().hex[:30]
            result = template.apply(
                source_canvas=canvas,
                source_framing=framing,
                new_canvas_id=new_canvas_id,
                new_fd_name=new_fd_name,
                source_context_label=context.label,
                context_creator=context_creator,
            )

            self.transform_completed.emit(result)
            return result

        except Exception as e:
            error_msg = str(e)
            self.transform_failed.emit(error_msg)
            raise

    def validate_selection(
        self,
        source_fdl: FDL,
        context_label: str,
        canvas_id: str,
        framing_decision_id: str,
    ) -> tuple[bool, str]:
        """
        Validate that a selection exists in the source FDL.

        Parameters
        ----------
        source_fdl : FDL
            The source FDL.
        context_label : str
            The context label.
        canvas_id : str
            The canvas ID.
        framing_decision_id : str
            The framing decision ID.

        Returns
        -------
        tuple
            (is_valid, error_message)
        """
        if not source_fdl:
            return False, "No source FDL"

        context = find_by_label(source_fdl.contexts, context_label)
        if context is None:
            return False, f"Context not found: {context_label}"

        canvas = find_by_id(context.canvases, canvas_id)
        if canvas is None:
            return False, f"Canvas not found: {canvas_id}"

        framing = find_by_id(canvas.framing_decisions, framing_decision_id)
        if framing is None:
            return False, f"Framing decision not found: {framing_decision_id}"

        return True, ""
