# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Image controller for FDL Viewer.

Handles loading and converting images for display using OpenImageIO.
"""

from pathlib import Path
from typing import ClassVar

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QImage, QPixmap

try:
    from OpenImageIO import ImageBuf, ImageBufAlgo, ImageSpec, TypeUInt8

    HAS_OIIO = True
except ImportError:
    HAS_OIIO = False


class ImageController(QObject):
    """
    Controller for loading and processing images.

    Uses OpenImageIO for professional format support (EXR, DPX, etc.)
    and converts to QImage/QPixmap for Qt display.

    Parameters
    ----------
    parent : QObject, optional
        Parent QObject for Qt ownership.

    Attributes
    ----------
    image_loaded : Signal
        Emitted when an image is loaded (QPixmap, width, height).
    error_occurred : Signal
        Emitted when an error occurs (error message).
    """

    image_loaded = Signal(object, int, int)  # QPixmap, width, height
    error_occurred = Signal(str)

    # Supported formats — raster via OIIO, plus SVG via Qt
    SUPPORTED_FORMATS: ClassVar[set[str]] = {".exr", ".png", ".tif", ".tiff", ".jpg", ".jpeg", ".dpx", ".svg"}

    def __init__(self, parent: QObject | None = None) -> None:
        """
        Initialize the ImageController.

        Parameters
        ----------
        parent : QObject, optional
            Parent QObject for Qt ownership.
        """
        super().__init__(parent)
        self._current_image: QImage | None = None
        self._current_pixmap: QPixmap | None = None
        self._image_path: str = ""
        self._original_width: int = 0
        self._original_height: int = 0

    @property
    def supported_formats(self) -> set:
        """Get the set of supported file extensions."""
        return set(self.SUPPORTED_FORMATS)

    def get_format_filter(self) -> str:
        """
        Get a file dialog filter string for supported formats.

        Returns
        -------
        str
            File dialog filter string.
        """
        all_exts = sorted(self.supported_formats)
        ext_str = " ".join(f"*{ext}" for ext in all_exts)

        filters = [
            f"Image Files ({ext_str})",
            "EXR Files (*.exr)",
            "PNG Files (*.png)",
            "TIFF Files (*.tif *.tiff)",
            "JPEG Files (*.jpg *.jpeg)",
            "DPX Files (*.dpx)",
            "SVG Files (*.svg)",
            "All Files (*)",
        ]

        return ";;".join(filters)

    def load_image(self, path: str) -> QPixmap | None:
        """
        Load an image at full resolution.

        SVG files are rendered via Qt's QSvgRenderer; all other formats use OIIO.

        Parameters
        ----------
        path : str
            Path to the image file.

        Returns
        -------
        QPixmap or None
            The loaded image as a pixmap, or None if loading failed.
        """
        path = Path(path)
        if not path.exists():
            self.error_occurred.emit(f"File not found: {path}")
            return None

        # SVG: render via Qt's SVG module
        if path.suffix.lower() == ".svg":
            return self._load_svg(str(path))

        if not HAS_OIIO:
            self.error_occurred.emit("OpenImageIO is required but not available")
            return None

        try:
            return self._load_with_oiio(str(path))
        except Exception as e:
            self.error_occurred.emit(f"Failed to load image: {e}")
            return None

    def _load_svg(self, path: str) -> QPixmap | None:
        """
        Load an SVG file by rendering it to a QPixmap via Qt.

        Parameters
        ----------
        path : str
            Path to the SVG file.

        Returns
        -------
        QPixmap or None
            The rendered SVG as a pixmap.
        """
        try:
            from PySide6.QtCore import Qt
            from PySide6.QtGui import QPainter
            from PySide6.QtSvg import QSvgRenderer

            renderer = QSvgRenderer(path)
            if not renderer.isValid():
                self.error_occurred.emit(f"Invalid SVG file: {path}")
                return None

            default_size = renderer.defaultSize()
            self._original_width = default_size.width()
            self._original_height = default_size.height()
            self._image_path = path

            pixmap = QPixmap(default_size)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()

            self._current_pixmap = pixmap
            self._current_image = pixmap.toImage()
            self.image_loaded.emit(pixmap, self._original_width, self._original_height)
            return pixmap
        except ImportError:
            self.error_occurred.emit("PySide6.QtSvg module is required for SVG support")
            return None
        except Exception as e:
            self.error_occurred.emit(f"Failed to load SVG: {e}")
            return None

    def _load_with_oiio(self, path: str) -> QPixmap | None:
        """
        Load using OpenImageIO with 8-bit conversion (no spatial downscaling).

        Handles EXR, DPX, and other professional formats.
        Applies gamma correction for linear colorspace images.

        Parameters
        ----------
        path : str
            Path to the image file.

        Returns
        -------
        QPixmap or None
            The loaded pixmap.
        """
        if not HAS_OIIO:
            return None

        buf = ImageBuf(path)
        if buf.has_error:
            self.error_occurred.emit(f"OIIO error: {buf.geterror()}")
            return None

        spec = buf.spec()
        self._original_width = spec.width
        self._original_height = spec.height
        self._image_path = path

        # NO DOWNSCALING - keep full resolution
        # Just convert to 8-bit RGBA for display

        display_spec = ImageSpec(spec.width, spec.height, 4, TypeUInt8)
        display_buf = ImageBuf(display_spec)

        # Apply gamma correction for linear colorspace (EXR, HDR)
        colorspace = spec.get_string_attribute("oiio:ColorSpace", "")
        is_linear = colorspace.lower() in ("linear", "scene_linear", "") and Path(path).suffix.lower() in (".exr", ".hdr")

        # Determine alpha channel: use source alpha if available (channel 3), otherwise fill with opaque (-1)
        alpha_channel = 3 if spec.nchannels >= 4 else -1

        if is_linear:
            gamma_buf = ImageBuf()
            ImageBufAlgo.pow(gamma_buf, buf, (1.0 / 2.2, 1.0 / 2.2, 1.0 / 2.2, 1.0))
            ImageBufAlgo.channels(display_buf, gamma_buf, (0, 1, 2, alpha_channel), newchannelnames=("R", "G", "B", "A"))
        else:
            if spec.nchannels >= 3:
                ImageBufAlgo.channels(display_buf, buf, (0, 1, 2, alpha_channel), newchannelnames=("R", "G", "B", "A"))
            else:
                # Grayscale - replicate to RGB
                ImageBufAlgo.channels(display_buf, buf, (0, 0, 0, -1), newchannelnames=("R", "G", "B", "A"))

        # Get pixel data
        width = display_buf.spec().width
        height = display_buf.spec().height
        pixels = display_buf.get_pixels(TypeUInt8)

        if pixels is None:
            self.error_occurred.emit("Failed to get pixel data from OIIO")
            return None

        # Fill alpha channel with opaque (255) if source didn't have alpha
        # channels() with -1 fills with 0 (transparent), so we fix it here
        if spec.nchannels < 4:
            pixels[:, :, 3] = 255

        image = QImage(
            pixels.tobytes(),
            width,
            height,
            width * 4,
            QImage.Format.Format_RGBA8888,
        ).copy()

        self._current_image = image
        self._current_pixmap = QPixmap.fromImage(image)
        self.image_loaded.emit(self._current_pixmap, self._original_width, self._original_height)
        return self._current_pixmap

    def get_current_pixmap(self) -> QPixmap | None:
        """
        Get the currently loaded pixmap.

        Returns
        -------
        QPixmap or None
            The current pixmap.
        """
        return self._current_pixmap

    def get_image_path(self) -> str:
        """
        Get the path of the currently loaded image.

        Returns
        -------
        str
            The image path.
        """
        return self._image_path

    def clear(self) -> None:
        """Clear the current image."""
        self._current_image = None
        self._current_pixmap = None
        self._image_path = ""
        self._original_width = 0
        self._original_height = 0
