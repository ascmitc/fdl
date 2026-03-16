# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Image comparison utilities for test suites.

Provides OIIO-based image comparison functionality that works both standalone
and with unittest.TestCase.
"""

import unittest
from pathlib import Path

import OpenImageIO as Oiio

# OIIO attribute name for bits per sample
OIIO_BITS_PER_SAMPLE = "oiio:BitsPerSample"


class ImageComparison:
    """
    Image comparison utilities using OpenImageIO.

    Provides methods to compare images pixel-by-pixel with configurable
    tolerances. Can be used standalone or integrated with unittest.TestCase.

    Parameters
    ----------
    outputs_dir : Path, optional
        Directory to save diff images when comparisons fail.
        If not provided, diff images won't be saved.
    test_case : unittest.TestCase, optional
        If provided, uses TestCase methods for assertions and naming.
    """

    # Default thresholds matching existing tests
    DEFAULT_FAIL_THRESHOLD = 1.0e-3
    DEFAULT_WARN_THRESHOLD = 1.0e-5
    DEFAULT_ALLOWED_FAILED_PIXELS = 0

    def __init__(
        self,
        outputs_dir: Path | None = None,
        test_case: unittest.TestCase | None = None,
    ):
        """
        Initialize the ImageComparison.

        Parameters
        ----------
        outputs_dir : Path, optional
            Directory to save diff images when comparisons fail.
        test_case : unittest.TestCase, optional
            If provided, uses TestCase methods for assertions.
        """
        self.outputs_dir = outputs_dir
        self.test_case = test_case

    def _fail(self, message: str) -> None:
        """Fail with message using TestCase if available, else raise AssertionError."""
        if self.test_case:
            self.test_case.fail(message)
        else:
            raise AssertionError(message)

    def _assertEqual(self, expected, actual, message: str) -> None:
        """Assert equality using TestCase if available, else plain assert."""
        if self.test_case:
            self.test_case.assertEqual(expected, actual, message)
        else:
            assert expected == actual, message

    def _get_test_name(self) -> str:
        """Get test name for diff file naming."""
        if self.test_case:
            return f"{self.test_case.__class__.__name__}_{self.test_case._testMethodName}"
        return "image_comparison"

    def compare_images(
        self,
        expected_path: Path | str,
        actual_path: Path | str,
        fail_thresh: float | None = None,
        warn_thresh: float | None = None,
        allowed_failed_pixels: int | None = None,
        strict_format: bool = False,
    ) -> bool:
        """
        Compare two image files.

        Parameters
        ----------
        expected_path : Path or str
            Path to the expected (reference) image.
        actual_path : Path or str
            Path to the actual (test result) image.
        fail_thresh : float, optional
            Threshold for considering a pixel comparison as failed.
        warn_thresh : float, optional
            Threshold for considering a pixel as "warning".
        allowed_failed_pixels : int, optional
            Number of pixels allowed to fail.
        strict_format : bool, optional
            If True, require format and bits-per-sample to match exactly.

        Returns
        -------
        bool
            True if images match within tolerances.

        Raises
        ------
        AssertionError
            If the images don't match.
        """
        expected_path = Path(expected_path)
        actual_path = Path(actual_path)

        expected_buf = Oiio.ImageBuf(str(expected_path))
        if expected_buf.has_error:
            self._fail(f"Failed to read expected image: {expected_buf.geterror()}")

        actual_buf = Oiio.ImageBuf(str(actual_path))
        if actual_buf.has_error:
            self._fail(f"Failed to read actual image: {actual_buf.geterror()}")

        return self.compare_buffers(
            expected_buf,
            actual_buf,
            diff_ext=expected_path.suffix,
            fail_thresh=fail_thresh,
            warn_thresh=warn_thresh,
            allowed_failed_pixels=allowed_failed_pixels,
            strict_format=strict_format,
        )

    def compare_buffers(
        self,
        expected_buf: Oiio.ImageBuf,
        actual_buf: Oiio.ImageBuf,
        diff_ext: str = ".png",
        fail_thresh: float | None = None,
        warn_thresh: float | None = None,
        allowed_failed_pixels: int | None = None,
        strict_format: bool = False,
    ) -> bool:
        """
        Compare two image buffers.

        This method compares:
        1. Image dimensions (width, height) - always required
        2. Number of channels - always required
        3. Image format (data type) - optional, controlled by strict_format
        4. Bits per sample - optional, controlled by strict_format
        5. Pixel values (within specified tolerances) - the main test

        If pixel comparison fails, a diff image is written to the outputs folder.

        Parameters
        ----------
        expected_buf : Oiio.ImageBuf
            The expected (reference) image buffer.
        actual_buf : Oiio.ImageBuf
            The actual (test result) image buffer.
        diff_ext : str
            File extension for diff output.
        fail_thresh : float, optional
            Threshold for considering a pixel comparison as failed.
        warn_thresh : float, optional
            Threshold for considering a pixel as "warning".
        allowed_failed_pixels : int, optional
            Number of pixels allowed to fail.
        strict_format : bool, optional
            If True, require format and bits-per-sample to match exactly.

        Returns
        -------
        bool
            True if images match within tolerances.

        Raises
        ------
        AssertionError
            If the images don't match.
        """
        if fail_thresh is None:
            fail_thresh = self.DEFAULT_FAIL_THRESHOLD
        if warn_thresh is None:
            warn_thresh = self.DEFAULT_WARN_THRESHOLD
        if allowed_failed_pixels is None:
            allowed_failed_pixels = self.DEFAULT_ALLOWED_FAILED_PIXELS

        expected_spec = expected_buf.spec()
        actual_spec = actual_buf.spec()

        # Build list of warnings for format differences
        format_warnings = []

        # Compare dimensions (always required)
        self._assertEqual(
            expected_spec.width,
            actual_spec.width,
            f"Image width mismatch: expected {expected_spec.width}, got {actual_spec.width}",
        )
        self._assertEqual(
            expected_spec.height,
            actual_spec.height,
            f"Image height mismatch: expected {expected_spec.height}, got {actual_spec.height}",
        )

        # Compare number of channels (always required)
        self._assertEqual(
            expected_spec.nchannels,
            actual_spec.nchannels,
            f"Channel count mismatch: expected {expected_spec.nchannels}, got {actual_spec.nchannels}",
        )

        # Compare format (data type)
        if expected_spec.format != actual_spec.format:
            msg = f"Image format mismatch: expected {expected_spec.format}, got {actual_spec.format}"
            if strict_format:
                self._fail(msg)
            else:
                format_warnings.append(msg)

        # Compare bits per sample
        expected_bps = expected_spec.get_int_attribute(OIIO_BITS_PER_SAMPLE, defaultval=0)
        actual_bps = actual_spec.get_int_attribute(OIIO_BITS_PER_SAMPLE, defaultval=0)
        if expected_bps != actual_bps:
            msg = f"Bits per sample mismatch: expected {expected_bps}, got {actual_bps}"
            if strict_format:
                self._fail(msg)
            else:
                format_warnings.append(msg)

        # Compare pixel values - this is the main test
        comp_results = Oiio.ImageBufAlgo.compare(expected_buf, actual_buf, fail_thresh, warn_thresh)

        if comp_results.nfail > allowed_failed_pixels:
            # Generate diff image if outputs_dir is set
            diff_path = None
            result_path = None

            if self.outputs_dir:
                self.outputs_dir.mkdir(parents=True, exist_ok=True)
                test_name = self._get_test_name()

                # Compute absolute difference image
                diff_buf = Oiio.ImageBufAlgo.absdiff(expected_buf, actual_buf)

                # Write diff image
                diff_filename = test_name.replace("test", "result_diff")
                diff_path = self.write_image(diff_buf, diff_filename, diff_ext, expected_bps)

                # Write actual result
                result_filename = test_name.replace("test", "result")
                result_path = self.write_image(actual_buf, result_filename, diff_ext, expected_bps)

            # Build detailed failure message
            failure_msg = (
                f"Image comparison failed\n"
                f"  Failed pixels: {comp_results.nfail} (allowed: {allowed_failed_pixels})\n"
                f"  Warning pixels: {comp_results.nwarn}\n"
                f"  Max error: {comp_results.maxerror:.6f}\n"
                f"  Mean error: {comp_results.meanerror:.6f}"
            )
            if diff_path:
                failure_msg += f"\n  Diff image: {diff_path}"
            if result_path:
                failure_msg += f"\n  Result image: {result_path}"
            if format_warnings:
                failure_msg += "\n  Format warnings:\n    " + "\n    ".join(format_warnings)

            self._fail(failure_msg)

        return True

    def write_image(
        self,
        image_buf: Oiio.ImageBuf,
        filename: str,
        ext: str,
        bits_per_sample: int = 0,
    ) -> Path:
        """
        Write an image buffer to the outputs directory.

        Parameters
        ----------
        image_buf : Oiio.ImageBuf
            The image buffer to write.
        filename : str
            Base filename (without extension).
        ext : str
            File extension (e.g., ".exr", ".tif").
        bits_per_sample : int, optional
            Bits per sample to set in the output. If 0, uses default.

        Returns
        -------
        Path
            Path to the written file.
        """
        if not self.outputs_dir:
            raise ValueError("outputs_dir not set")

        output_path = self.outputs_dir / f"{filename}{ext}"

        # Set bits per sample if specified
        if bits_per_sample > 0:
            spec = image_buf.spec()
            spec.attribute(OIIO_BITS_PER_SAMPLE, bits_per_sample)

        image_buf.write(str(output_path))
        return output_path
