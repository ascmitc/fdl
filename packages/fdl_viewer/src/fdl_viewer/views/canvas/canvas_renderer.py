# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Canvas renderer for FDL Viewer.

Renders FDL geometry onto a QGraphicsScene.
"""

from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import QLineF, QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPen
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsScene, QGraphicsTextItem

from fdl_viewer.models.fdl_model import FDLModel
from fdl_viewer.utils.geometry import GeometryHelper

if TYPE_CHECKING:
    from fdl import CanvasTemplate, PointFloat


class CanvasRenderer:
    """
    Renders FDL geometry onto a QGraphicsScene.

    Draws canvas outline, effective dimensions, protection area,
    framing decision, grid overlay, and dimension labels.

    Draw order (back to front): grid → canvas → effective → protection → framing

    Color scheme (unified for source and output):
    - Canvas: gray (#808080), solid line, 15% fill
    - Effective: orange (#ff2f00), solid line, 15% fill
    - Protection: red/orange (#FF9900), dashed line, 15% fill
    - Framing: green (#00CC66), solid line, 15% fill

    Examples
    --------
    >>> renderer = CanvasRenderer()
    >>> renderer.render(scene, fdl_model, show_grid=True)
    """

    GRID_SPACING = 100

    def __init__(self) -> None:
        """Initialize the CanvasRenderer."""
        pass

    def render(
        self,
        scene: QGraphicsScene,
        model: FDLModel,
        show_grid: bool = True,
        is_source: bool = True,
        show_canvas: bool = True,
        show_effective: bool = True,
        show_framing: bool = True,
        show_protection: bool = True,
        show_hud: bool = False,
        source_model: FDLModel | None = None,
        template: Optional["CanvasTemplate"] = None,
        output_model: FDLModel | None = None,
        content_translation: Optional["PointFloat"] = None,
        scale_factor: float | None = None,
    ) -> None:
        """
        Render FDL geometry onto the scene.

        Parameters
        ----------
        scene : QGraphicsScene
            The scene to render onto.
        model : FDLModel
            The FDL model to visualize.
        show_grid : bool, optional
            Whether to show the grid overlay.
        is_source : bool, optional
            True for source view (green framing), False for output (blue).
        show_canvas : bool, optional
            Whether to show the canvas outline.
        show_effective : bool, optional
            Whether to show effective dimensions.
        show_framing : bool, optional
            Whether to show framing decision.
        show_protection : bool, optional
            Whether to show protection area.
        show_hud : bool, optional
            Whether to show the HUD overlay (output tab only).
        source_model : FDLModel, optional
            The original source FDL model for HUD display.
        template : CanvasTemplate, optional
            The template for HUD display.
        output_model : FDLModel, optional
            The output FDL model for HUD display.
        content_translation : PointFloat, optional
            The content translation for HUD display.
        scale_factor : float, optional
            The scale factor for HUD display.
        """
        if model is None:
            return

        canvas_rect = model.get_canvas_rect()
        # Validate canvas_rect is a real QRectF (not None or a mock object)
        if canvas_rect is None or not isinstance(canvas_rect, QRectF):
            return

        # Draw order (back to front): grid → canvas → effective → protection → framing

        # 1. Draw grid first (behind everything)
        if show_grid:
            self._draw_grid(scene, canvas_rect)

        # 2. Draw canvas (with fill)
        if show_canvas:
            self._draw_rect(scene, canvas_rect, GeometryHelper.get_canvas_pen(), brush=GeometryHelper.get_canvas_brush(), label="Canvas")

        # 3. Draw effective dimensions (with fill)
        if show_effective:
            effective_rect = model.get_effective_rect()
            if effective_rect:
                self._draw_rect(
                    scene, effective_rect, GeometryHelper.get_effective_pen(), brush=GeometryHelper.get_effective_brush(), label="Effective"
                )

        # 4. Draw protection area (with fill, dashed outline)
        if show_protection:
            protection_rect = model.get_protection_rect()
            if protection_rect:
                self._draw_rect(
                    scene,
                    protection_rect,
                    GeometryHelper.get_protection_pen(),
                    brush=GeometryHelper.get_protection_brush(),
                    label="Protection",
                )

        # 5. Draw framing decision (with fill, on top)
        if show_framing:
            framing_rect = model.get_framing_rect()
            if framing_rect:
                pen = GeometryHelper.get_framing_pen(is_source)
                brush = GeometryHelper.get_framing_brush(is_source)
                self._draw_rect(scene, framing_rect, pen, brush=brush, label="Framing")

                # Draw center crosshair
                self._draw_crosshair(scene, framing_rect.center())

        # Draw dimension and anchor labels
        self._draw_dimension_labels(scene, model, canvas_rect, show_canvas, show_effective, show_protection, show_framing)
        self._draw_anchor_labels(scene, model, show_effective, show_protection, show_framing)

        # 6. Draw HUD (only if enabled)
        if show_hud:
            framing_rect = model.get_framing_rect()
            if framing_rect:
                self._draw_hud(scene, framing_rect, source_model, template, output_model, content_translation, scale_factor)

    def _draw_grid(self, scene: QGraphicsScene, bounds: QRectF) -> None:
        """
        Draw a grid overlay.

        Parameters
        ----------
        scene : QGraphicsScene
            The scene to draw on.
        bounds : QRectF
            The bounds for the grid.
        """
        pen = GeometryHelper.get_grid_pen()

        # Vertical lines
        x = 0
        while x <= bounds.width():
            line = scene.addLine(QLineF(x, 0, x, bounds.height()), pen)
            line.setZValue(-1)
            x += self.GRID_SPACING

        # Horizontal lines
        y = 0
        while y <= bounds.height():
            line = scene.addLine(QLineF(0, y, bounds.width(), y), pen)
            line.setZValue(-1)
            y += self.GRID_SPACING

    def _draw_rect(self, scene: QGraphicsScene, rect: QRectF, pen: QPen, brush: QBrush | None = None, label: str = "") -> QGraphicsRectItem:
        """
        Draw a rectangle on the scene.

        Parameters
        ----------
        scene : QGraphicsScene
            The scene to draw on.
        rect : QRectF
            The rectangle to draw.
        pen : QPen
            The pen for the outline.
        brush : QBrush, optional
            The brush for filling.
        label : str, optional
            Label for the rectangle.

        Returns
        -------
        QGraphicsRectItem
            The created rectangle item.
        """
        item = scene.addRect(rect, pen, brush or QBrush(Qt.NoBrush))
        item.setZValue(1)
        return item

    def _draw_crosshair(self, scene: QGraphicsScene, center: QPointF, size: float = 20) -> None:
        """
        Draw a crosshair at a point.

        Parameters
        ----------
        scene : QGraphicsScene
            The scene to draw on.
        center : QPointF
            The center point.
        size : float, optional
            The size of the crosshair arms.
        """
        pen = QPen(GeometryHelper.COLOR_CROSSHAIR)
        pen.setWidthF(1.0)

        # Horizontal line
        scene.addLine(QLineF(center.x() - size, center.y(), center.x() + size, center.y()), pen)

        # Vertical line
        scene.addLine(QLineF(center.x(), center.y() - size, center.x(), center.y() + size), pen)

    def _draw_dimension_labels(
        self,
        scene: QGraphicsScene,
        model: FDLModel,
        canvas_rect: QRectF,
        show_canvas: bool = True,
        show_effective: bool = True,
        show_protection: bool = True,
        show_framing: bool = True,
    ) -> None:
        """
        Draw dimension labels on the canvas.

        Labels are 50% larger than base size and centered along the width
        of each geometry element.

        Parameters
        ----------
        scene : QGraphicsScene
            The scene to draw on.
        model : FDLModel
            The FDL model.
        canvas_rect : QRectF
            The canvas rectangle.
        show_canvas : bool, optional
            Whether to show canvas label.
        show_effective : bool, optional
            Whether to show effective label.
        show_protection : bool, optional
            Whether to show protection label.
        show_framing : bool, optional
            Whether to show framing label.
        """
        # 3x larger font (30pt instead of 10pt)
        font = QFont("Arial", 30)
        font.setBold(True)

        # Canvas dimensions (gray) - right aligned to avoid overlap
        if show_canvas:
            canvas = model.current_canvas
            if canvas:
                text = f"{int(canvas.dimensions.width)} x {int(canvas.dimensions.height)}"
                self._add_centered_label(scene, text, canvas_rect, font, GeometryHelper.COLOR_CANVAS, alignment="right")

        # Effective dimensions (blue) - left aligned to avoid overlap
        if show_effective:
            effective_rect = model.get_effective_rect()
            if effective_rect:
                canvas = model.current_canvas
                if canvas and canvas.effective_dimensions:
                    width = canvas.effective_dimensions.width
                    height = canvas.effective_dimensions.height
                    text = f"{int(width)} x {int(height)}"
                    self._add_centered_label(scene, text, effective_rect, font, GeometryHelper.COLOR_EFFECTIVE, alignment="left")

        # Protection dimensions (orange) - right aligned to avoid overlap with framing
        if show_protection:
            protection_rect = model.get_protection_rect()
            if protection_rect:
                fd = model.current_framing_decision
                if fd and fd.protection_dimensions:
                    width = fd.protection_dimensions.width
                    height = fd.protection_dimensions.height
                    text = f"{int(width)} x {int(height)}"
                    self._add_centered_label(scene, text, protection_rect, font, GeometryHelper.COLOR_PROTECTION, alignment="right")

        # Framing decision dimensions (green) - center aligned
        if show_framing:
            framing_rect = model.get_framing_rect()
            if framing_rect:
                fd = model.current_framing_decision
                if fd:
                    text = f"{int(fd.dimensions.width)} x {int(fd.dimensions.height)}"
                    self._add_centered_label(scene, text, framing_rect, font, GeometryHelper.COLOR_FRAMING_SOURCE, alignment="center")

    def _draw_anchor_labels(
        self, scene: QGraphicsScene, model: FDLModel, show_effective: bool = True, show_protection: bool = True, show_framing: bool = True
    ) -> None:
        """
        Draw anchor point labels on the canvas.

        Labels are offset vertically based on FDL hierarchy to avoid overlap:
        - Framing: no offset (most important)
        - Protection: 1x offset
        - Effective: 2x offset

        Parameters
        ----------
        scene : QGraphicsScene
            The scene to draw on.
        model : FDLModel
            The FDL model.
        show_effective : bool, optional
            Whether to show effective anchor.
        show_protection : bool, optional
            Whether to show protection anchor.
        show_framing : bool, optional
            Whether to show framing anchor.
        """
        # Smaller font for anchor labels
        font = QFont("Arial", 20)

        # Vertical offset step to avoid overlapping labels (approx text height + padding)
        offset_step = 30

        canvas = model.current_canvas
        fd = model.current_framing_decision

        # Effective anchor (blue) - double offset (third priority)
        if show_effective:
            effective_rect = model.get_effective_rect()
            if effective_rect and canvas and canvas.effective_anchor_point:
                x = canvas.effective_anchor_point.x
                y = canvas.effective_anchor_point.y
                text = f"({int(x)}, {int(y)})"
                self._add_anchor_label(
                    scene,
                    text,
                    effective_rect.topLeft(),
                    font,
                    GeometryHelper.COLOR_EFFECTIVE,
                    y_offset=-offset_step * 2,  # Negative to move further up
                )

        # Protection anchor (orange) - single offset (second priority)
        if show_protection:
            protection_rect = model.get_protection_rect()
            if protection_rect and fd:
                if fd.protection_anchor_point:
                    x = fd.protection_anchor_point.x
                    y = fd.protection_anchor_point.y
                else:
                    x = fd.anchor_point.x
                    y = fd.anchor_point.y
                text = f"({int(x)}, {int(y)})"
                self._add_anchor_label(
                    scene,
                    text,
                    protection_rect.topLeft(),
                    font,
                    GeometryHelper.COLOR_PROTECTION,
                    y_offset=-offset_step,  # Negative to move further up
                )

        # Framing decision anchor (green) - no offset (highest priority)
        if show_framing:
            framing_rect = model.get_framing_rect()
            if framing_rect and fd:
                x = fd.anchor_point.x
                y = fd.anchor_point.y
                text = f"({int(x)}, {int(y)})"
                self._add_anchor_label(
                    scene,
                    text,
                    framing_rect.topLeft(),
                    font,
                    GeometryHelper.COLOR_FRAMING_SOURCE,
                    y_offset=0,  # No offset, closest to anchor point
                )

    def _add_anchor_label(
        self, scene: QGraphicsScene, text: str, pos: QPointF, font: QFont, color: QColor, y_offset: float = 0
    ) -> QGraphicsTextItem:
        """
        Add an anchor point label at the top-left of a rectangle.

        Parameters
        ----------
        scene : QGraphicsScene
            The scene to draw on.
        text : str
            The label text.
        pos : QPointF
            The anchor position (top-left corner).
        font : QFont
            The font to use.
        color : QColor
            The text color.
        y_offset : float, optional
            Additional vertical offset to avoid overlapping labels.

        Returns
        -------
        QGraphicsTextItem
            The created text item.
        """
        item = scene.addText(text, font)
        item.setDefaultTextColor(color)
        item.setZValue(10)

        # Get the bounding rect of the text
        text_rect = item.boundingRect()

        # Position: above and slightly left of the anchor point, with optional offset
        x = pos.x() - 5
        y = pos.y() - text_rect.height() - 5 + y_offset

        item.setPos(x, y)
        return item

    def _add_label(self, scene: QGraphicsScene, text: str, pos: QPointF, font: QFont, color: QColor) -> QGraphicsTextItem:
        """
        Add a text label to the scene.

        Parameters
        ----------
        scene : QGraphicsScene
            The scene to draw on.
        text : str
            The label text.
        pos : QPointF
            The position.
        font : QFont
            The font to use.
        color : QColor
            The text color.

        Returns
        -------
        QGraphicsTextItem
            The created text item.
        """
        item = scene.addText(text, font)
        item.setPos(pos)
        item.setDefaultTextColor(color)
        item.setZValue(10)
        return item

    def _add_centered_label(
        self, scene: QGraphicsScene, text: str, rect: QRectF, font: QFont, color: QColor, offset_y: float = 10, alignment: str = "center"
    ) -> QGraphicsTextItem:
        """
        Add a text label along the bottom of a rectangle.

        Parameters
        ----------
        scene : QGraphicsScene
            The scene to draw on.
        text : str
            The label text.
        rect : QRectF
            The rectangle to position the label relative to.
        font : QFont
            The font to use.
        color : QColor
            The text color.
        offset_y : float, optional
            Vertical offset below the rectangle bottom.
        alignment : str, optional
            Horizontal alignment: "left", "center", or "right".

        Returns
        -------
        QGraphicsTextItem
            The created text item.
        """
        item = scene.addText(text, font)
        item.setDefaultTextColor(color)
        item.setZValue(10)

        # Get the bounding rect of the text to calculate offset
        text_rect = item.boundingRect()

        # Position: below rect bottom, with horizontal alignment
        y = rect.bottom() + offset_y

        if alignment == "left":
            x = rect.left()
        elif alignment == "right":
            x = rect.right() - text_rect.width()
        else:  # center
            x = rect.center().x() - text_rect.width() / 2

        item.setPos(x, y)
        return item

    def _draw_hud(
        self,
        scene: QGraphicsScene,
        framing_rect: QRectF,
        source_model: FDLModel | None,
        template: Optional["CanvasTemplate"],
        output_model: FDLModel | None = None,
        content_translation: Optional["PointFloat"] = None,
        scale_factor: float | None = None,
    ) -> None:
        """
        Draw the Heads Up Display showing source, output, and template info.

        Left column: Source FDL data (between framing center and left edge)
        Center column: Output FDL data (at framing center)
        Right column: Template data with transform results (between framing center and right edge)

        Parameters
        ----------
        scene : QGraphicsScene
            The scene to draw on.
        framing_rect : QRectF
            The framing decision rectangle for positioning.
        source_model : FDLModel or None
            The original source FDL model for left column.
        template : CanvasTemplate or None
            The template for right column.
        output_model : FDLModel or None
            The output FDL model for center column.
        content_translation : PointFloat or None
            The content translation for right column.
        scale_factor : float or None
            The scale factor for right column.
        """
        font = QFont("Arial", 42)  # 3x larger font
        color = QColor(255, 255, 255, 220)  # Semi-transparent white

        center_x = framing_rect.center().x()
        center_y = framing_rect.center().y()
        left_x = framing_rect.left()
        right_x = framing_rect.right()

        # Position three columns:
        # Left: midpoint between left edge and center (right-aligned text)
        # Center: at center (center-aligned text)
        # Right: midpoint between center and right edge (left-aligned text)
        left_col_x = (center_x + left_x) / 2
        center_col_x = center_x
        right_col_x = (center_x + right_x) / 2

        line_height = 66  # 3x larger line height

        # Build lines first to calculate vertical centering
        left_lines = self._build_source_hud_lines(source_model) if source_model else []
        center_lines = self._build_output_hud_lines(output_model) if output_model else []
        right_lines = self._build_template_hud_lines(template, content_translation, scale_factor) if template else []

        # Calculate base_y to center columns vertically within framing rect
        max_lines = max(len(left_lines), len(center_lines), len(right_lines))
        total_height = max_lines * line_height
        base_y = center_y - (total_height / 2)

        # Draw left column (Source FDL data)
        if left_lines:
            self._draw_hud_column(scene, left_lines, left_col_x, base_y, line_height, font, color, alignment="right")

        # Draw center column (Output FDL data)
        if center_lines:
            self._draw_hud_column(scene, center_lines, center_col_x, base_y, line_height, font, color, alignment="center")

        # Draw right column (Template data + transform results)
        if right_lines:
            self._draw_hud_column(scene, right_lines, right_col_x, base_y, line_height, font, color, alignment="left")

    def _build_source_hud_lines(self, model: FDLModel) -> list[tuple[str, str]]:
        """
        Build display lines for source FDL data.

        Only includes fields that are actually set (not None/default).

        Parameters
        ----------
        model : FDLModel
            The source FDL model.

        Returns
        -------
        List[Tuple[str, str]]
            List of (label, value) tuples to display.
        """
        lines: list[tuple[str, str]] = []
        canvas = model.current_canvas
        fd = model.current_framing_decision

        if canvas:
            # Canvas dimensions (always present)
            lines.append(("Canvas", f"{int(canvas.dimensions.width)} x {int(canvas.dimensions.height)}"))

            # Effective dimensions (optional)
            if canvas.effective_dimensions:
                lines.append(("Effective", f"{int(canvas.effective_dimensions.width)} x {int(canvas.effective_dimensions.height)}"))

            # Effective anchor point (optional)
            if canvas.effective_anchor_point:
                lines.append(("Eff. Anchor", f"({int(canvas.effective_anchor_point.x)}, {int(canvas.effective_anchor_point.y)})"))

        if fd:
            # Framing dimensions (always present)
            lines.append(("Framing", f"{int(fd.dimensions.width)} x {int(fd.dimensions.height)}"))

            # Framing anchor point (always present)
            lines.append(("Anchor", f"({int(fd.anchor_point.x)}, {int(fd.anchor_point.y)})"))

            # Protection dimensions (optional)
            if fd.protection_dimensions:
                lines.append(("Protection", f"{int(fd.protection_dimensions.width)} x {int(fd.protection_dimensions.height)}"))

            # Protection anchor point (optional)
            if fd.protection_anchor_point:
                lines.append(("Prot. Anchor", f"({int(fd.protection_anchor_point.x)}, {int(fd.protection_anchor_point.y)})"))

        return lines

    def _build_output_hud_lines(self, model: FDLModel) -> list[tuple[str, str]]:
        """
        Build display lines for output FDL data.

        Same fields as source, but from the output model.

        Parameters
        ----------
        model : FDLModel
            The output FDL model.

        Returns
        -------
        List[Tuple[str, str]]
            List of (label, value) tuples to display.
        """
        lines: list[tuple[str, str]] = []
        canvas = model.current_canvas
        fd = model.current_framing_decision

        if canvas:
            # Canvas dimensions (always present)
            lines.append(("Canvas", f"{int(canvas.dimensions.width)} x {int(canvas.dimensions.height)}"))

            # Effective dimensions (optional)
            if canvas.effective_dimensions:
                lines.append(("Effective", f"{int(canvas.effective_dimensions.width)} x {int(canvas.effective_dimensions.height)}"))

            # Effective anchor point (optional)
            if canvas.effective_anchor_point:
                lines.append(("Eff. Anchor", f"({int(canvas.effective_anchor_point.x)}, {int(canvas.effective_anchor_point.y)})"))

        if fd:
            # Framing dimensions (always present)
            lines.append(("Framing", f"{int(fd.dimensions.width)} x {int(fd.dimensions.height)}"))

            # Framing anchor point (always present)
            lines.append(("Anchor", f"({int(fd.anchor_point.x)}, {int(fd.anchor_point.y)})"))

            # Protection dimensions (optional)
            if fd.protection_dimensions:
                lines.append(("Protection", f"{int(fd.protection_dimensions.width)} x {int(fd.protection_dimensions.height)}"))

            # Protection anchor point (optional)
            if fd.protection_anchor_point:
                lines.append(("Prot. Anchor", f"({int(fd.protection_anchor_point.x)}, {int(fd.protection_anchor_point.y)})"))

        return lines

    def _build_template_hud_lines(
        self,
        template: "CanvasTemplate",
        content_translation: Optional["PointFloat"] = None,
        scale_factor: float | None = None,
    ) -> list[tuple[str, str]]:
        """
        Build display lines for template configuration and transform results.

        Only includes fields that are actually set (not None/default).

        Parameters
        ----------
        template : CanvasTemplate
            The template configuration.
        content_translation : PointFloat, optional
            The content translation from transformation.
        scale_factor : float, optional
            The scale factor from transformation.

        Returns
        -------
        List[Tuple[str, str]]
            List of (label, value) tuples to display.
        """
        lines: list[tuple[str, str]] = []

        # Target dimensions (always present)
        lines.append(("Target", f"{int(template.target_dimensions.width)} x {int(template.target_dimensions.height)}"))

        # Target anamorphic squeeze (show if not 1.0)
        if template.target_anamorphic_squeeze != 1.0:
            lines.append(("Squeeze", f"{template.target_anamorphic_squeeze:.2f}"))

        # Fit source (always present)
        fit_source_display = template.fit_source.replace("framing_decision.", "").replace("canvas.", "")
        lines.append(("Fit Source", fit_source_display))

        # Fit method (always present)
        lines.append(("Fit Method", template.fit_method))

        # Alignment methods (always show horizontal, vertical only if not "center")
        lines.append(("Align H", template.alignment_method_horizontal))
        if template.alignment_method_vertical != "center":
            lines.append(("Align V", template.alignment_method_vertical))

        # Preserve from source (show if set)
        if template.preserve_from_source_canvas:
            preserve_display = template.preserve_from_source_canvas.replace("framing_decision.", "").replace("canvas.", "")
            lines.append(("Preserve", preserve_display))

        # Maximum dimensions (optional)
        if template.maximum_dimensions:
            lines.append(("Max Dims", f"{int(template.maximum_dimensions.width)} x {int(template.maximum_dimensions.height)}"))

        # Pad to maximum (show if True)
        if template.pad_to_maximum:
            lines.append(("Pad to Max", "Yes"))

        # Transform results - scale factor
        if scale_factor is not None:
            lines.append(("Scale", f"{scale_factor:.4f}"))

        # Transform results - content translation
        if content_translation is not None:
            lines.append(("Translation", f"({content_translation.x:.1f}, {content_translation.y:.1f})"))

        return lines

    def _draw_hud_column(
        self,
        scene: QGraphicsScene,
        lines: list[tuple[str, str]],
        x: float,
        y: float,
        line_height: float,
        font: QFont,
        color: QColor,
        alignment: str = "left",
    ) -> None:
        """
        Draw a column of HUD text lines.

        Parameters
        ----------
        scene : QGraphicsScene
            The scene to draw on.
        lines : List[Tuple[str, str]]
            List of (label, value) tuples.
        x : float
            X position for the column.
        y : float
            Starting Y position.
        line_height : float
            Height between lines.
        font : QFont
            Font to use.
        color : QColor
            Text color.
        alignment : str
            "left", "center", or "right" alignment.
        """
        current_y = y
        for label, value in lines:
            text = f"{label}: {value}"
            item = scene.addText(text, font)
            item.setDefaultTextColor(color)
            item.setZValue(20)  # Above other labels

            text_rect = item.boundingRect()

            if alignment == "right":
                # Right-align: text ends at x
                item.setPos(x - text_rect.width(), current_y)
            elif alignment == "center":
                # Center-align: text centered on x
                item.setPos(x - text_rect.width() / 2, current_y)
            else:
                # Left-align: text starts at x
                item.setPos(x, current_y)

            current_y += line_height
