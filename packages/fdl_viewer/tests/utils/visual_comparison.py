# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Visual comparison utilities for FDL Viewer UI tests.

Extends ImageComparison with Qt-specific methods for comparing QPixmaps.
"""

import tempfile
from pathlib import Path

import OpenImageIO as Oiio
from fdl_imaging.testing import ImageComparison
from PySide6.QtGui import QPixmap


class VisualComparison(ImageComparison):
    """
    Qt-specific visual comparison utilities for UI tests.

    Extends ImageComparison with methods for working with QPixmaps,
    enabling comparison of Qt screenshots against baselines.

    Parameters
    ----------
    outputs_dir : Path, optional
        Directory to save diff images when comparisons fail.
    test_case : unittest.TestCase, optional
        If provided, uses TestCase methods for assertions.
    """

    @staticmethod
    def pixmap_to_imagebuf(pixmap: QPixmap) -> Oiio.ImageBuf:
        """
        Convert QPixmap to OIIO ImageBuf.

        Saves the pixmap to a temporary file and loads it with OIIO.

        Parameters
        ----------
        pixmap : QPixmap
            The Qt pixmap to convert.

        Returns
        -------
        Oiio.ImageBuf
            The loaded image buffer.
        """
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            pixmap.save(tmp.name)
            return Oiio.ImageBuf(tmp.name)

    def compare_pixmaps(
        self,
        expected_pixmap: QPixmap,
        actual_pixmap: QPixmap,
        fail_thresh: float | None = None,
        warn_thresh: float | None = None,
        allowed_failed_pixels: int | None = None,
    ) -> bool:
        """
        Compare two QPixmaps.

        Converts pixmaps to OIIO ImageBufs and compares them using
        the parent class's compare_buffers method.

        Parameters
        ----------
        expected_pixmap : QPixmap
            The expected (reference) pixmap.
        actual_pixmap : QPixmap
            The actual (test result) pixmap.
        fail_thresh : float, optional
            Threshold for considering a pixel as "failed".
        warn_thresh : float, optional
            Threshold for considering a pixel as "warning".
        allowed_failed_pixels : int, optional
            Number of pixels allowed to fail.

        Returns
        -------
        bool
            True if pixmaps match within tolerances.

        Raises
        ------
        AssertionError
            If the pixmaps don't match.
        """
        expected_buf = self.pixmap_to_imagebuf(expected_pixmap)
        actual_buf = self.pixmap_to_imagebuf(actual_pixmap)

        return self.compare_buffers(
            expected_buf=expected_buf,
            actual_buf=actual_buf,
            diff_ext=".png",
            fail_thresh=fail_thresh,
            warn_thresh=warn_thresh,
            allowed_failed_pixels=allowed_failed_pixels,
        )

    def save_pixmap(self, pixmap: QPixmap, path: Path) -> bool:
        """
        Save QPixmap to file.

        Parameters
        ----------
        pixmap : QPixmap
            The pixmap to save.
        path : Path
            The output path.

        Returns
        -------
        bool
            True if save was successful.
        """
        return pixmap.save(str(path))


def get_outputs_folder() -> Path:
    """
    Get the test outputs folder, creating it if it doesn't exist.

    Returns
    -------
    Path
        Path to the outputs folder.
    """
    output_path = Path(__file__).parent.parent / "outputs"
    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def get_baselines_folder() -> Path:
    """
    Get the baselines folder.

    Returns
    -------
    Path
        Path to the baselines folder.
    """
    return Path(__file__).parent.parent / "baselines"
