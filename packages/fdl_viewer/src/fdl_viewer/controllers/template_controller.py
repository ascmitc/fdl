# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Template controller for FDL Viewer.

Handles template editing and preset management.
"""

from fdl import CanvasTemplate
from PySide6.QtCore import QObject, Signal

from fdl_viewer.models.app_state import AppState
from fdl_viewer.models.template_presets import (
    create_custom_template,
    get_preset,
    get_preset_names,
)


class TemplateController(QObject):
    """
    Controller for template editing and preset management.

    Provides methods for creating, editing, and applying template presets.

    Parameters
    ----------
    parent : QObject, optional
        Parent QObject for Qt ownership.

    Attributes
    ----------
    template_changed : Signal
        Emitted when the template is modified.
    preset_applied : Signal
        Emitted when a preset is applied (preset_name).
    """

    template_changed = Signal(object)  # CanvasTemplate
    preset_applied = Signal(str)  # preset name

    def __init__(self, parent: QObject | None = None) -> None:
        """
        Initialize the TemplateController.

        Parameters
        ----------
        parent : QObject, optional
            Parent QObject for Qt ownership.
        """
        super().__init__(parent)
        self._app_state = AppState.instance()
        self._current_template: CanvasTemplate | None = None
        self._original_template: CanvasTemplate | None = None

    @property
    def current_template(self) -> CanvasTemplate | None:
        """Get the current template."""
        return self._current_template

    def set_template(self, template: CanvasTemplate, from_user_edit: bool = False) -> None:
        """
        Set the current template.

        Parameters
        ----------
        template : CanvasTemplate
            The template to set.
        from_user_edit : bool, optional
            If True, this is a user edit and should mark the template as modified.
            If False, this is a new template being loaded and should reset modified state.
        """
        self._current_template = template
        if not from_user_edit:
            self._original_template = template
            self._app_state.set_template_modified(False)
        else:
            self._app_state.set_template_modified(True)
        self._app_state.set_current_template(template)
        self.template_changed.emit(template)

    def apply_preset(self, preset_name: str) -> CanvasTemplate | None:
        """
        Apply a preset template.

        Parameters
        ----------
        preset_name : str
            The name of the preset to apply.

        Returns
        -------
        CanvasTemplate or None
            The applied template, or None if preset not found.
        """
        template = get_preset(preset_name)
        if template:
            # If there's already an output, this is a modification that requires reprocessing
            has_output = self._app_state.output_fdl is not None
            self.set_template(template, from_user_edit=has_output)
            self.preset_applied.emit(preset_name)
            return template
        return None

    def get_preset_names(self) -> list[str]:
        """
        Get the list of available preset names.

        Returns
        -------
        List[str]
            The list of preset names.
        """
        return get_preset_names()

    def update_target_dimensions(self, width: int, height: int) -> None:
        """
        Update the target dimensions.

        Parameters
        ----------
        width : int
            The target width.
        height : int
            The target height.
        """
        if self._current_template is None:
            return

        from fdl import DimensionsInt, RoundStrategy

        t = self._current_template
        self._current_template = CanvasTemplate(
            id=t.id,
            label=t.label,
            target_dimensions=DimensionsInt(width=width, height=height),
            target_anamorphic_squeeze=t.target_anamorphic_squeeze,
            fit_source=t.fit_source,
            fit_method=t.fit_method,
            alignment_method_horizontal=t.alignment_method_horizontal,
            alignment_method_vertical=t.alignment_method_vertical,
            round=RoundStrategy(even=t.round.even, mode=t.round.mode),
            preserve_from_source_canvas=t.preserve_from_source_canvas,
            maximum_dimensions=t.maximum_dimensions,
            pad_to_maximum=t.pad_to_maximum,
        )
        self._app_state.set_current_template(self._current_template)
        self._app_state.set_template_modified(True)
        self.template_changed.emit(self._current_template)

    def create_custom(
        self,
        width: int,
        height: int,
        fit_source: str = "framing_decision.dimensions",
        fit_method: str = "fit_all",
    ) -> CanvasTemplate:
        """
        Create a new custom template.

        Parameters
        ----------
        width : int
            Target width.
        height : int
            Target height.
        fit_source : str, optional
            Fit source path.
        fit_method : str, optional
            Fit method.

        Returns
        -------
        CanvasTemplate
            The created template.
        """
        template = create_custom_template(
            width=width,
            height=height,
            fit_source=fit_source,
            fit_method=fit_method,
        )
        self.set_template(template)
        return template
