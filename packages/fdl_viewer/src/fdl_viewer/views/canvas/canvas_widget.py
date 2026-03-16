# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Canvas widget for FDL Viewer.

Provides an interactive canvas with pan/zoom for visualizing FDL geometry.
"""

from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import QPointF, QRectF, QSize, Qt, Signal
from PySide6.QtGui import QMouseEvent, QPainter, QPixmap, QResizeEvent, QWheelEvent
from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsScene, QGraphicsView

from fdl_viewer.models.app_state import AppState
from fdl_viewer.models.fdl_model import FDLModel
from fdl_viewer.views.canvas.canvas_renderer import CanvasRenderer

if TYPE_CHECKING:
    from fdl import CanvasTemplate, PointFloat


class CanvasWidget(QGraphicsView):
    """
    Interactive canvas widget with pan/zoom support.

    Uses QGraphicsView/QGraphicsScene for efficient rendering of FDL geometry.
    Supports mouse wheel zoom (centered on cursor), middle-button pan,
    and double-click to fit.

    Parameters
    ----------
    parent : QWidget, optional
        Parent widget.

    Attributes
    ----------
    zoom_changed : Signal
        Emitted when zoom level changes (scale_factor).
    """

    zoom_changed = Signal(float)

    ZOOM_MIN = 0.05
    ZOOM_MAX = 10.0
    ZOOM_STEP = 1.15

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        self._renderer = CanvasRenderer()
        self._fdl_model: FDLModel | None = None
        self._is_source = True  # True for source view, False for output view

        self._panning = False
        self._pan_start = QPointF()
        self._scale = 1.0

        # Image underlay
        self._image_pixmap: QPixmap | None = None
        self._image_item: QGraphicsPixmapItem | None = None
        self._image_opacity: float = 0.7
        self._image_original_width: int = 0
        self._image_original_height: int = 0

        # HUD data (for output tab)
        self._source_model_for_hud: FDLModel | None = None
        self._template_for_hud: CanvasTemplate | None = None
        self._output_model_for_hud: FDLModel | None = None
        self._content_translation_for_hud: PointFloat | None = None
        self._scale_factor_for_hud: float | None = None

        self._setup_view()
        self._connect_signals()

    def _setup_view(self) -> None:
        """Configure view settings."""
        self.setRenderHint(QPainter.Antialiasing)
        # Note: SmoothPixmapTransform intentionally NOT set for pixel-perfect zoom
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.setDragMode(QGraphicsView.NoDrag)
        self.setBackgroundBrush(Qt.black)

    def _connect_signals(self) -> None:
        """Connect to app state signals."""
        app_state = AppState.instance()
        app_state.grid_visible_changed.connect(self._on_visibility_changed)
        app_state.image_opacity_changed.connect(self._on_image_opacity_changed)
        app_state.canvas_visible_changed.connect(self._on_visibility_changed)
        app_state.effective_visible_changed.connect(self._on_visibility_changed)
        app_state.framing_visible_changed.connect(self._on_visibility_changed)
        app_state.protection_visible_changed.connect(self._on_visibility_changed)
        app_state.image_visible_changed.connect(self._on_visibility_changed)
        app_state.hud_visible_changed.connect(self._on_visibility_changed)

    def set_fdl_model(self, model: FDLModel | None) -> None:
        """
        Set the FDL model to display.

        Parameters
        ----------
        model : FDLModel or None
            The FDL model to visualize.
        """
        self._fdl_model = model
        self.refresh()

    def set_is_source(self, is_source: bool) -> None:
        """
        Set whether this is a source or output view.

        Parameters
        ----------
        is_source : bool
            True for source view, False for output view.
        """
        self._is_source = is_source
        self.refresh()

    def refresh(self) -> None:
        """Refresh the canvas display."""
        self._scene.clear()
        self._image_item = None

        app_state = AppState.instance()
        canvas_rect = None

        if self._fdl_model is not None:
            canvas_rect = self._fdl_model.get_canvas_rect()

        # Draw image underlay first (behind everything) at native resolution at (0,0)
        if self._image_pixmap is not None and app_state.image_underlay_visible:
            self._draw_image_underlay()

        # Render FDL overlays if we have a model
        if self._fdl_model is not None:
            self._renderer.render(
                self._scene,
                self._fdl_model,
                show_grid=app_state.grid_visible,
                is_source=self._is_source,
                show_canvas=app_state.canvas_visible,
                show_effective=app_state.effective_visible,
                show_framing=app_state.framing_visible,
                show_protection=app_state.protection_visible,
                show_hud=app_state.hud_visible and not self._is_source,  # Only for output
                source_model=self._source_model_for_hud,
                template=self._template_for_hud,
                output_model=self._output_model_for_hud,
                content_translation=self._content_translation_for_hud,
                scale_factor=self._scale_factor_for_hud,
            )

        # Set scene rect based on canvas or image bounds
        scene_rect = None
        if canvas_rect is not None and isinstance(canvas_rect, QRectF):
            scene_rect = QRectF(canvas_rect)
            # If image is loaded, expand scene rect to include the full image at (0,0)
            if self._image_pixmap is not None:
                image_rect = QRectF(0, 0, self._image_pixmap.width(), self._image_pixmap.height())
                scene_rect = scene_rect.united(image_rect)
        elif self._image_pixmap is not None:
            # No canvas rect but we have an image - use image bounds at (0,0)
            scene_rect = QRectF(0, 0, self._image_pixmap.width(), self._image_pixmap.height())

        if scene_rect:
            padding = 100
            expanded = scene_rect.adjusted(-padding, -padding, padding, padding)
            self._scene.setSceneRect(expanded)

    def _draw_image_underlay(self) -> None:
        """
        Draw the image at native resolution at origin (0,0).

        The image is displayed at 1:1 pixel resolution. Both the image and FDL
        use (0,0) as the top-left origin, so FDL overlays align directly with
        image pixels. Qt's QGraphicsView handles zooming through view transforms.
        """
        if self._image_pixmap is None:
            return

        # Add pixmap at native resolution, positioned at origin (0,0)
        self._image_item = self._scene.addPixmap(self._image_pixmap)
        self._image_item.setTransformationMode(Qt.TransformationMode.FastTransformation)
        self._image_item.setPos(0, 0)  # Always at origin - same as FDL coordinate system
        self._image_item.setZValue(-10)
        self._image_item.setOpacity(self._image_opacity)

    def fit_in_view(self) -> None:
        """Fit the canvas content in the view."""
        fit_rect = None

        # Try to get canvas rect from FDL model (validate it's a real QRectF)
        if self._fdl_model is not None:
            canvas_rect = self._fdl_model.get_canvas_rect()
            if canvas_rect is not None and isinstance(canvas_rect, QRectF):
                fit_rect = canvas_rect

        # Fall back to image bounds if no valid canvas rect
        if fit_rect is None and self._image_pixmap is not None:
            fit_rect = QRectF(0, 0, self._image_pixmap.width(), self._image_pixmap.height())

        if fit_rect is not None:
            padding = 50
            expanded = fit_rect.adjusted(-padding, -padding, padding, padding)
            self.fitInView(expanded, Qt.KeepAspectRatio)
            self.zoom_changed.emit(self.transform().m11())

    def reset_zoom(self) -> None:
        """Reset zoom to 100%."""
        self.resetTransform()
        self.zoom_changed.emit(1.0)

    def zoom_in(self) -> None:
        """Zoom in by one step."""
        self._apply_zoom(self.ZOOM_STEP)

    def zoom_out(self) -> None:
        """Zoom out by one step."""
        self._apply_zoom(1.0 / self.ZOOM_STEP)

    def _apply_zoom(self, factor: float) -> None:
        """Apply a zoom factor."""
        current_scale = self.transform().m11()
        new_scale = current_scale * factor

        if self.ZOOM_MIN <= new_scale <= self.ZOOM_MAX:
            self.scale(factor, factor)
            self.zoom_changed.emit(new_scale)

    def get_zoom_level(self) -> float:
        """
        Get the current zoom level.

        Returns
        -------
        float
            The current scale factor.
        """
        return self.transform().m11()

    # Event handlers
    def wheelEvent(self, event: QWheelEvent) -> None:
        """Handle mouse wheel for zooming."""
        if event.angleDelta().y() > 0:
            self._apply_zoom(self.ZOOM_STEP)
        else:
            self._apply_zoom(1.0 / self.ZOOM_STEP)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press for panning (left or middle button)."""
        if event.button() in (Qt.LeftButton, Qt.MiddleButton):
            self._panning = True
            self._pan_start = event.position()
            self.setCursor(Qt.ClosedHandCursor)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle mouse move for panning."""
        if self._panning:
            delta = event.position() - self._pan_start
            self._pan_start = event.position()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - int(delta.x()))
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - int(delta.y()))
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handle mouse release to stop panning."""
        if event.button() in (Qt.LeftButton, Qt.MiddleButton):
            self._panning = False
            self.setCursor(Qt.ArrowCursor)
        else:
            super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """Handle double-click to fit in view."""
        if event.button() == Qt.LeftButton:
            self.fit_in_view()
        else:
            super().mouseDoubleClickEvent(event)

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Handle resize to maintain view."""
        super().resizeEvent(event)
        # Optionally fit on first show
        if not self._fdl_model:
            return

    def export_to_svg(self, output_path: str) -> bool:
        """
        Export the current scene to an SVG file.

        Uses Qt's QSvgGenerator to render the QGraphicsScene as a vector graphic.

        Parameters
        ----------
        output_path : str
            Path where the SVG file should be saved.

        Returns
        -------
        bool
            True if export succeeded, False otherwise.
        """
        try:
            from pathlib import Path

            from PySide6.QtSvg import QSvgGenerator

            scene_rect = self._scene.sceneRect()
            if scene_rect.isEmpty():
                return False

            generator = QSvgGenerator()
            generator.setFileName(output_path)
            generator.setSize(QSize(int(scene_rect.width()), int(scene_rect.height())))
            generator.setViewBox(scene_rect)
            generator.setTitle("FDL Viewer Scene Export")
            generator.setDescription("Exported from FDL Viewer")

            painter = QPainter(generator)
            self._scene.render(painter)
            painter.end()

            return Path(output_path).exists()
        except ImportError:
            # QSvgGenerator not available
            return False
        except Exception:
            return False

    def export_scene(self, output_path: str) -> bool:
        """
        Export the current scene to a file, choosing format by extension.

        SVG output uses QSvgGenerator (vector); PNG/JPG use QPixmap (raster).

        Parameters
        ----------
        output_path : str
            Path where the file should be saved. Extension determines format.

        Returns
        -------
        bool
            True if export succeeded, False otherwise.
        """
        from pathlib import Path

        ext = Path(output_path).suffix.lower()
        if ext == ".svg":
            return self.export_to_svg(output_path)
        else:
            # Raster fallback via grab()
            pixmap = self.grab()
            return pixmap.save(output_path)

    def _on_visibility_changed(self, visible: bool) -> None:
        """Handle any visibility change."""
        self.refresh()

    def _on_image_opacity_changed(self, opacity: float) -> None:
        """Handle image opacity change."""
        self._image_opacity = opacity
        if self._image_item is not None:
            self._image_item.setOpacity(opacity)

    def set_image(self, pixmap: QPixmap | None, original_width: int = 0, original_height: int = 0) -> None:
        """
        Set the image underlay.

        Parameters
        ----------
        pixmap : QPixmap or None
            The image pixmap, or None to clear.
        original_width : int, optional
            Original image width (for reference).
        original_height : int, optional
            Original image height (for reference).
        """
        self._image_pixmap = pixmap
        self._image_original_width = original_width
        self._image_original_height = original_height
        self.refresh()

    def clear_image(self) -> None:
        """Clear the image underlay."""
        self._image_pixmap = None
        self._image_item = None
        self._image_original_width = 0
        self._image_original_height = 0
        self.refresh()

    def has_image(self) -> bool:
        """
        Check if an image is loaded.

        Returns
        -------
        bool
            True if an image is loaded.
        """
        return self._image_pixmap is not None

    def validate_image_canvas_match(self) -> str | None:
        """
        Check if image dimensions match canvas dimensions.

        Both the image and FDL use (0,0) as top-left origin. For proper alignment,
        the source image must have the same resolution as the FDL canvas.

        Returns
        -------
        Optional[str]
            Error message if dimensions don't match, None if valid or not applicable.
        """
        if self._image_pixmap is None or self._fdl_model is None:
            return None

        canvas_rect = self._fdl_model.get_canvas_rect()
        if canvas_rect is None:
            return None

        img_w = self._image_pixmap.width()
        img_h = self._image_pixmap.height()
        canvas_w = int(canvas_rect.width())
        canvas_h = int(canvas_rect.height())

        if img_w != canvas_w or img_h != canvas_h:
            return f"Image size ({img_w}x{img_h}) does not match canvas size ({canvas_w}x{canvas_h})"
        return None

    def set_hud_data(
        self,
        source_model: FDLModel | None,
        template: Optional["CanvasTemplate"],
        output_model: FDLModel | None = None,
        content_translation: Optional["PointFloat"] = None,
        scale_factor: float | None = None,
    ) -> None:
        """
        Set the source model, template, and output data for HUD display.

        Parameters
        ----------
        source_model : FDLModel or None
            The original source FDL model.
        template : CanvasTemplate or None
            The template used for transformation.
        output_model : FDLModel or None
            The output FDL model from transformation.
        content_translation : PointFloat or None
            The content translation applied during transformation.
        scale_factor : float or None
            The scale factor applied during transformation.
        """
        self._source_model_for_hud = source_model
        self._template_for_hud = template
        self._output_model_for_hud = output_model
        self._content_translation_for_hud = content_translation
        self._scale_factor_for_hud = scale_factor
