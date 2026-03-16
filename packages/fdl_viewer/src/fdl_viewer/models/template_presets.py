# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Template presets for FDL Viewer.

Provides standard template presets for common output formats.
"""

from fdl import (
    CanvasTemplate,
    DimensionsInt,
    RoundStrategy,
)


def _create_preset(
    preset_id: str,
    label: str,
    width: int,
    height: int,
    fit_source: str = "framing_decision.dimensions",
    fit_method: str = "fit_all",
    alignment_horizontal: str = "center",
    alignment_vertical: str = "center",
    preserve_from_source_canvas: str | None = None,
    maximum_dimensions: DimensionsInt | None = None,
    pad_to_maximum: bool = False,
    round_even: str = "even",
    round_mode: str = "up",
    target_anamorphic_squeeze: float = 1.0,
) -> CanvasTemplate:
    """
    Create a preset CanvasTemplate.

    Parameters
    ----------
    preset_id : str
        The template ID.
    label : str
        The template label.
    width : int
        Target width.
    height : int
        Target height.
    fit_source : str, optional
        The fit source path.
    fit_method : str, optional
        The fit method.
    alignment_horizontal : str, optional
        Horizontal alignment.
    alignment_vertical : str, optional
        Vertical alignment.
    preserve_from_source_canvas : str, optional
        What to preserve from source.
    maximum_dimensions : DimensionsInt, optional
        Maximum dimensions for cropping.
    pad_to_maximum : bool, optional
        Whether to pad to maximum dimensions.
    round_even : str, optional
        Rounding even mode ('even' or 'whole').
    round_mode : str, optional
        Rounding direction ('up', 'down', or 'round').
    target_anamorphic_squeeze : float, optional
        Target anamorphic squeeze factor.

    Returns
    -------
    CanvasTemplate
        The created template preset.
    """
    return CanvasTemplate(
        id=preset_id,
        label=label,
        target_dimensions=DimensionsInt(width=width, height=height),
        target_anamorphic_squeeze=target_anamorphic_squeeze,
        fit_source=fit_source,
        fit_method=fit_method,
        alignment_method_horizontal=alignment_horizontal,
        alignment_method_vertical=alignment_vertical,
        preserve_from_source_canvas=preserve_from_source_canvas,
        maximum_dimensions=maximum_dimensions,
        pad_to_maximum=pad_to_maximum,
        round=RoundStrategy(even=round_even, mode=round_mode),
    )


# Standard presets
STANDARD_PRESETS: dict[str, CanvasTemplate] = {
    "HD 1080p": _create_preset(
        preset_id="preset_hd_1080p",
        label="HD 1080p",
        width=1920,
        height=1080,
    ),
    "UHD 4K": _create_preset(
        preset_id="preset_uhd_4k",
        label="UHD 4K",
        width=3840,
        height=2160,
    ),
    "DCI 2K": _create_preset(
        preset_id="preset_dci_2k",
        label="DCI 2K",
        width=2048,
        height=1080,
    ),
    "DCI 4K": _create_preset(
        preset_id="preset_dci_4k",
        label="DCI 4K",
        width=4096,
        height=2160,
    ),
    "DCI 2K Flat": _create_preset(
        preset_id="preset_dci_2k_flat",
        label="DCI 2K Flat",
        width=1998,
        height=1080,
    ),
    "DCI 4K Flat": _create_preset(
        preset_id="preset_dci_4k_flat",
        label="DCI 4K Flat",
        width=3996,
        height=2160,
    ),
    "DCI 2K Scope": _create_preset(
        preset_id="preset_dci_2k_scope",
        label="DCI 2K Scope",
        width=2048,
        height=858,
    ),
    "DCI 4K Scope": _create_preset(
        preset_id="preset_dci_4k_scope",
        label="DCI 4K Scope",
        width=4096,
        height=1716,
    ),
}


def get_preset(name: str) -> CanvasTemplate | None:
    """
    Get a preset template by name.

    Parameters
    ----------
    name : str
        The preset name.

    Returns
    -------
    CanvasTemplate or None
        The preset template, or None if not found.
    """
    return STANDARD_PRESETS.get(name)


def get_preset_names() -> list[str]:
    """
    Get the list of preset names.

    Returns
    -------
    List[str]
        The list of preset names.
    """
    return list(STANDARD_PRESETS.keys())


def create_custom_template(
    width: int,
    height: int,
    fit_source: str = "framing_decision.dimensions",
    fit_method: str = "fit_all",
    alignment_horizontal: str = "center",
    alignment_vertical: str = "center",
    preserve_from_source_canvas: str | None = None,
    max_width: int | None = None,
    max_height: int | None = None,
    pad_to_maximum: bool = False,
    round_even: str = "even",
    round_mode: str = "up",
    anamorphic_squeeze: float = 1.0,
) -> CanvasTemplate:
    """
    Create a custom canvas template.

    Parameters
    ----------
    width : int
        Target width.
    height : int
        Target height.
    fit_source : str, optional
        The fit source path.
    fit_method : str, optional
        The fit method ('fit_all', 'fill', 'width', 'height').
    alignment_horizontal : str, optional
        Horizontal alignment ('left', 'center', 'right').
    alignment_vertical : str, optional
        Vertical alignment ('top', 'center', 'bottom').
    preserve_from_source_canvas : str, optional
        What to preserve from source.
    max_width : int, optional
        Maximum width for cropping.
    max_height : int, optional
        Maximum height for cropping.
    pad_to_maximum : bool, optional
        Whether to pad to maximum dimensions.
    round_even : str, optional
        Rounding even mode ('even' or 'whole').
    round_mode : str, optional
        Rounding direction ('up', 'down', or 'round').
    anamorphic_squeeze : float, optional
        Target anamorphic squeeze factor.

    Returns
    -------
    CanvasTemplate
        The custom template.
    """
    max_dims = None
    if max_width is not None and max_height is not None:
        max_dims = DimensionsInt(width=max_width, height=max_height)

    return _create_preset(
        preset_id="custom_template",
        label="Custom Template",
        width=width,
        height=height,
        fit_source=fit_source,
        fit_method=fit_method,
        alignment_horizontal=alignment_horizontal,
        alignment_vertical=alignment_vertical,
        preserve_from_source_canvas=preserve_from_source_canvas,
        maximum_dimensions=max_dims,
        pad_to_maximum=pad_to_maximum,
        round_even=round_even,
        round_mode=round_mode,
        target_anamorphic_squeeze=anamorphic_squeeze,
    )


# Fit source options
FIT_SOURCE_OPTIONS = [
    ("framing_decision.dimensions", "Framing Decision"),
    ("framing_decision.protection_dimensions", "Protection Dimensions"),
    ("canvas.effective_dimensions", "Effective Canvas"),
    ("canvas.dimensions", "Full Canvas"),
]

# Fit method options
FIT_METHOD_OPTIONS = [
    ("fit_all", "Fit All (letterbox/pillarbox)"),
    ("fill", "Fill (may crop)"),
    ("width", "Fit Width"),
    ("height", "Fit Height"),
]

# Alignment options
ALIGNMENT_HORIZONTAL_OPTIONS = [
    ("left", "Left"),
    ("center", "Center"),
    ("right", "Right"),
]

ALIGNMENT_VERTICAL_OPTIONS = [
    ("top", "Top"),
    ("center", "Center"),
    ("bottom", "Bottom"),
]

# Preserve from source options
PRESERVE_OPTIONS = [
    (None, "None"),
    ("canvas.dimensions", "Canvas"),
    ("canvas.effective_dimensions", "Effective Canvas"),
    ("framing_decision.protection_dimensions", "Protection"),
    ("framing_decision.dimensions", "Framing Decision"),
]

# Rounding options
ROUND_EVEN_OPTIONS = [
    ("whole", "Whole Numbers"),
    ("even", "Even Numbers"),
]

ROUND_MODE_OPTIONS = [
    ("up", "Round Up"),
    ("down", "Round Down"),
    ("round", "Round Nearest"),
]
