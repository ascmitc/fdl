# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Geometry utilities for FDL Viewer visualization.

Provides helper functions for converting FDL geometry to Qt graphics primitives.
"""

from fdl import (
    Canvas,
    DimensionsFloat,
    DimensionsInt,
    FramingDecision,
    PointFloat,
)
from PySide6.QtCore import QPointF, QRectF, QSizeF, Qt
from PySide6.QtGui import QBrush, QColor, QPen


class GeometryHelper:
    """
    Helper class for FDL geometry operations.

    Provides methods for converting FDL geometry to Qt graphics primitives
    and calculating visualization parameters.

    Examples
    --------
    >>> helper = GeometryHelper()
    >>> rect = helper.canvas_to_rect(canvas)
    >>> pen = helper.get_canvas_pen()
    """

    # Color constants (unified across source and output views)
    # Draw order (back to front): image → canvas → effective → protection → framing
    COLOR_CANVAS = QColor(128, 128, 128)  # Gray #808080
    COLOR_EFFECTIVE = QColor(0, 102, 204)  # Blue #0066CC
    COLOR_PROTECTION = QColor(255, 153, 0)  # Red/Orange #FF9900
    COLOR_FRAMING_SOURCE = QColor(0, 204, 102)  # Green #00CC66
    COLOR_FRAMING_OUTPUT = QColor(0, 204, 102)  # Green #00CC66 (same as source)
    COLOR_GRID = QColor(80, 80, 80)  # Dark gray
    COLOR_CROSSHAIR = QColor(255, 255, 255, 128)  # Semi-transparent white

    # Line widths
    LINE_WIDTH_CANVAS = 2.0
    LINE_WIDTH_EFFECTIVE = 1.5
    LINE_WIDTH_PROTECTION = 1.5
    LINE_WIDTH_FRAMING = 2.0
    LINE_WIDTH_GRID = 0.5

    # Default fill opacity for all geometry overlays
    FILL_OPACITY = 0.15

    # Grid spacing (in pixels)
    GRID_SPACING = 100

    @classmethod
    def canvas_to_rect(cls, canvas: Canvas) -> QRectF:
        """Convert canvas dimensions to QRectF."""
        return QRectF(*canvas.get_rect())

    @classmethod
    def effective_to_rect(cls, canvas: Canvas) -> QRectF | None:
        """Convert effective dimensions to QRectF, or None if not defined."""
        rect = canvas.get_effective_rect()
        return QRectF(*rect) if rect is not None else None

    @classmethod
    def framing_to_rect(cls, fd: FramingDecision) -> QRectF:
        """Convert framing decision to QRectF."""
        return QRectF(*fd.get_rect())

    @classmethod
    def protection_to_rect(cls, fd: FramingDecision) -> QRectF | None:
        """Convert protection dimensions to QRectF, or None if not defined."""
        rect = fd.get_protection_rect()
        return QRectF(*rect) if rect is not None else None

    @classmethod
    def get_center(cls, rect: QRectF) -> QPointF:
        """
        Get the center point of a rectangle.

        Parameters
        ----------
        rect : QRectF
            The rectangle.

        Returns
        -------
        QPointF
            The center point.
        """
        return rect.center()

    @classmethod
    def get_canvas_pen(cls) -> QPen:
        """
        Get the pen for drawing canvas outlines.

        Returns
        -------
        QPen
            The canvas outline pen.
        """
        pen = QPen(cls.COLOR_CANVAS)
        pen.setWidthF(cls.LINE_WIDTH_CANVAS)
        return pen

    @classmethod
    def get_effective_pen(cls) -> QPen:
        """
        Get the pen for drawing effective dimensions.

        Returns
        -------
        QPen
            The effective dimensions pen.
        """
        pen = QPen(cls.COLOR_EFFECTIVE)
        pen.setWidthF(cls.LINE_WIDTH_EFFECTIVE)
        return pen

    @classmethod
    def get_protection_pen(cls) -> QPen:
        """
        Get the pen for drawing protection dimensions (dashed).

        Returns
        -------
        QPen
            The protection dimensions pen (dashed style).
        """
        pen = QPen(cls.COLOR_PROTECTION)
        pen.setWidthF(cls.LINE_WIDTH_PROTECTION)
        pen.setStyle(Qt.DashLine)
        return pen

    @classmethod
    def get_framing_pen(cls, is_source: bool = True) -> QPen:
        """
        Get the pen for drawing framing decisions.

        Parameters
        ----------
        is_source : bool, optional
            True for source (green), False for output (blue).

        Returns
        -------
        QPen
            The framing decision pen.
        """
        color = cls.COLOR_FRAMING_SOURCE if is_source else cls.COLOR_FRAMING_OUTPUT
        pen = QPen(color)
        pen.setWidthF(cls.LINE_WIDTH_FRAMING)
        return pen

    @classmethod
    def get_grid_pen(cls) -> QPen:
        """
        Get the pen for drawing grid lines.

        Returns
        -------
        QPen
            The grid pen.
        """
        pen = QPen(cls.COLOR_GRID)
        pen.setWidthF(cls.LINE_WIDTH_GRID)
        return pen

    @classmethod
    def get_canvas_brush(cls, opacity: float | None = None) -> QBrush:
        """
        Get the brush for filling canvas areas.

        Parameters
        ----------
        opacity : float, optional
            Fill opacity (0.0 to 1.0). Defaults to FILL_OPACITY.

        Returns
        -------
        QBrush
            The canvas fill brush.
        """
        if opacity is None:
            opacity = cls.FILL_OPACITY
        color = QColor(cls.COLOR_CANVAS)
        color.setAlphaF(opacity)
        return QBrush(color)

    @classmethod
    def get_effective_brush(cls, opacity: float | None = None) -> QBrush:
        """
        Get the brush for filling effective dimension areas.

        Parameters
        ----------
        opacity : float, optional
            Fill opacity (0.0 to 1.0). Defaults to FILL_OPACITY.

        Returns
        -------
        QBrush
            The effective fill brush.
        """
        if opacity is None:
            opacity = cls.FILL_OPACITY
        color = QColor(cls.COLOR_EFFECTIVE)
        color.setAlphaF(opacity)
        return QBrush(color)

    @classmethod
    def get_protection_brush(cls, opacity: float | None = None) -> QBrush:
        """
        Get the brush for filling protection areas.

        Parameters
        ----------
        opacity : float, optional
            Fill opacity (0.0 to 1.0). Defaults to FILL_OPACITY.

        Returns
        -------
        QBrush
            The protection fill brush.
        """
        if opacity is None:
            opacity = cls.FILL_OPACITY
        color = QColor(cls.COLOR_PROTECTION)
        color.setAlphaF(opacity)
        return QBrush(color)

    @classmethod
    def get_framing_brush(cls, is_source: bool = True, opacity: float | None = None) -> QBrush:
        """
        Get the brush for filling framing areas.

        Parameters
        ----------
        is_source : bool, optional
            True for source (green), False for output (green, same as source).
        opacity : float, optional
            Fill opacity (0.0 to 1.0). Defaults to FILL_OPACITY.

        Returns
        -------
        QBrush
            The framing fill brush.
        """
        if opacity is None:
            opacity = cls.FILL_OPACITY
        base_color = cls.COLOR_FRAMING_SOURCE if is_source else cls.COLOR_FRAMING_OUTPUT
        color = QColor(base_color)  # Create a copy to avoid modifying the constant
        color.setAlphaF(opacity)
        return QBrush(color)

    @classmethod
    def calculate_fit_scale(cls, content_size: QSizeF, container_size: QSizeF, padding: float = 50.0) -> float:
        """
        Calculate scale factor to fit content within container.

        Parameters
        ----------
        content_size : QSizeF
            The size of the content to fit.
        container_size : QSizeF
            The size of the container.
        padding : float, optional
            Padding around the content.

        Returns
        -------
        float
            The scale factor.
        """
        if content_size.width() <= 0 or content_size.height() <= 0:
            return 1.0

        available_width = container_size.width() - 2 * padding
        available_height = container_size.height() - 2 * padding

        scale_x = available_width / content_size.width()
        scale_y = available_height / content_size.height()

        return min(scale_x, scale_y)

    @classmethod
    def dimensions_to_size(cls, dims: DimensionsInt | DimensionsFloat) -> QSizeF:
        """
        Convert FDL dimensions to QSizeF.

        Parameters
        ----------
        dims : DimensionsInt or DimensionsFloat
            The dimensions object.

        Returns
        -------
        QSizeF
            The size object.
        """
        return QSizeF(float(dims.width), float(dims.height))

    @classmethod
    def point_to_qpoint(cls, point: PointFloat) -> QPointF:
        """
        Convert FDL point to QPointF.

        Parameters
        ----------
        point : PointFloat
            The point object.

        Returns
        -------
        QPointF
            The Qt point object.
        """
        return QPointF(point.x, point.y)

    @classmethod
    def format_dimensions(cls, width: float, height: float) -> str:
        """Format dimensions as a string like '1920 x 1080'."""
        return DimensionsFloat(width=width, height=height).format()

    @classmethod
    def format_point(cls, x: float, y: float) -> str:
        """Format a point as a string like '(100, 200)'."""
        return PointFloat(x=x, y=y).format()
