# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Base test case for FDL imaging tests.

Extends BaseFDLTestCase with image processing and comparison capabilities.
"""

from pathlib import Path

from fdl import read_from_file
from fdl.testing.base import BaseFDLTestCase

from fdl_imaging import process_image_with_fdl_template
from fdl_imaging.testing.image_comparison import ImageComparison


class BaseFDLImagingTestCase(BaseFDLTestCase):
    """
    Test case with FDL + image processing capabilities.

    Extends BaseFDLTestCase with image comparison and processing.
    Subclass this for tests that need image processing but not Nuke.
    """

    def setUp(self):
        """Set up FDL and image comparators."""
        super().setUp()
        self._image_comparator = ImageComparison(
            outputs_dir=self.get_outputs_folder(),
            test_case=self,
        )

    def process_test_image(
        self,
        source_image: Path,
        source_fdl_path: Path,
        template_fdl_path: Path,
        template_id: str,
        context_label: str,
        canvas_id: str,
        framing_decision_id: str,
        test_name: str,
        expected_image_path: Path | None = None,
        filter_name: str = "triangle",
    ) -> Path:
        """
        Process a test image using OpenImageIO and FDL template transformations.

        Parameters
        ----------
        source_image : Path
            Path to the source image
        source_fdl_path : Path
            Path to the source FDL file
        template_fdl_path : Path
            Path to the template FDL file
        template_id : str
            ID of the template to apply
        context_label : str
            Label of the context to use
        canvas_id : str
            ID of the canvas to use
        framing_decision_id : str
            ID of the framing decision to use
        test_name : str
            Name of the test (used for output filename)
        expected_image_path : Path, optional
            Path to the expected result image.

        Returns
        -------
        Path
            Path to the generated output image
        """
        if expected_image_path is not None:
            output_ext = expected_image_path.suffix
        else:
            output_ext = source_image.suffix
        output_path = self.get_outputs_folder() / f"{test_name}_processed{output_ext}"

        # Resolve context label to index
        source_fdl = read_from_file(source_fdl_path)
        context_index = next(i for i, c in enumerate(source_fdl.contexts) if c.label == context_label)

        process_image_with_fdl_template(
            input_path=source_image,
            output_path=output_path,
            source_fdl=source_fdl,
            template_fdl=template_fdl_path,
            template_id=template_id,
            context_index=context_index,
            canvas_id=canvas_id,
            framing_decision_id=framing_decision_id,
            filter_name=filter_name,
        )

        return output_path

    def run_template_test(
        self,
        source_image: Path | None = None,
        expected_image_path: Path | None = None,
        input_dims: tuple[float, float] | None = None,
        **kwargs,
    ):
        """
        Run FDL template test with optional image processing.

        Calls super().run_template_test() for FDL validation, then
        processes and compares images if source_image is provided.
        """
        # Run the FDL-only test first
        super().run_template_test(**kwargs)

        # Process image if source exists
        if source_image is not None and source_image.exists():
            processed_image_path = self.process_test_image(
                source_image=source_image,
                source_fdl_path=self._source_fdl_path,
                template_fdl_path=self._template_fdl_path,
                template_id=self._template.id,
                context_label=self._context_label,
                canvas_id=self._canvas.id,
                framing_decision_id=self._fd.id,
                test_name=kwargs.get("test_name", "test"),
                expected_image_path=expected_image_path,
            )

            # Compare processed image with expected result
            if processed_image_path and expected_image_path is not None and expected_image_path.exists():
                self._image_comparator.compare_images(
                    expected_path=expected_image_path,
                    actual_path=processed_image_path,
                )
