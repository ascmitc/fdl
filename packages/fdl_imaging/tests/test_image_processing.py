# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Tests for the image processing module.
"""

import tempfile
from pathlib import Path

from fdl import read_from_file
from fdl.testing import BaseFDLTestCase
from OpenImageIO import ImageBuf

from fdl_imaging import (
    extract_framing_region,
    get_fdl_components,
    process_image_with_fdl,
)


class TestImageProcessing(BaseFDLTestCase):
    """Test cases for the image processing module."""

    def test_get_fdl_components(self):
        """Test that we can extract FDL components by ID."""
        fdl_path = self.get_resources_folder() / "Source_OCF" / "Source_FDLs" / "A_5184x4320_2_20percentSafe.fdl"
        fdl = read_from_file(fdl_path)

        context = self.get_component_from_fdl(fdl, "context", label="RED Monstro")
        canvas = self.get_component_from_fdl(fdl, "canvas", label="Open Gate RAW", context=context)
        fd = self.get_component_from_fdl(fdl, "framing_decision", label="1.78-1 Framing", canvas=canvas)

        # Test get_fdl_components function — resolve label to index
        context_index = next(i for i, c in enumerate(fdl.contexts) if c.label == "RED Monstro")
        resolved_context, resolved_canvas, resolved_fd = get_fdl_components(
            fdl,
            context_index=context_index,
            canvas_id=canvas.id,
            framing_decision_id=fd.id,
        )

        self.assertEqual(resolved_context.label, "RED Monstro")
        self.assertEqual(resolved_canvas.id, canvas.id)
        self.assertEqual(resolved_fd.id, fd.id)

    def test_get_fdl_components_invalid_context(self):
        """Test that invalid context index raises ValueError."""
        fdl_path = self.get_resources_folder() / "Source_OCF" / "Source_FDLs" / "A_5184x4320_2_20percentSafe.fdl"
        fdl = read_from_file(fdl_path)

        with self.assertRaises(ValueError) as cm:
            get_fdl_components(fdl, 999, "1", "1-1")
        self.assertIn("Context index", str(cm.exception))

    def test_process_image_with_fdl_tif(self):
        """Test processing a TIF image with FDL."""
        source_files_dir = self.get_resources_folder() / "Original_Source_Files"
        source_tif = source_files_dir / "D_8640x5760_1x_10PercentSafety-FramingChart.tif"
        source_fdl = source_files_dir / "D_8640x5760_1x_10PercentSafety-FramingChart.fdl"

        # Load FDL to get IDs
        fdl = read_from_file(source_fdl)
        context = fdl.contexts[0]
        canvas = context.canvases[0]
        fd = canvas.framing_decisions[0]

        # Create temp output
        with tempfile.NamedTemporaryFile(suffix=".tif", delete=False) as tmp:
            output_path = Path(tmp.name)

        try:
            result = process_image_with_fdl(
                input_path=source_tif,
                output_path=output_path,
                fdl=source_fdl,
                context_index=next(i for i, c in enumerate(fdl.contexts) if c.label == context.label),
                canvas_id=canvas.id,
                framing_decision_id=fd.id,
                use_protection=True,
                filter_name="triangle",
            )

            self.assertTrue(result)
            self.assertTrue(output_path.exists())

            # Verify output dimensions match protection dimensions
            output_buf = ImageBuf(str(output_path))
            self.assertFalse(output_buf.has_error)

            expected_width = int(fd.protection_dimensions.width)
            expected_height = int(fd.protection_dimensions.height)
            self.assertEqual(output_buf.spec().width, expected_width)
            self.assertEqual(output_buf.spec().height, expected_height)

        finally:
            if output_path.exists():
                output_path.unlink()

    def test_extract_framing_region(self):
        """Test extracting the framing decision region from an image."""
        source_files_dir = self.get_resources_folder() / "Original_Source_Files"
        source_tif = source_files_dir / "D_8640x5760_1x_10PercentSafety-FramingChart.tif"
        source_fdl = source_files_dir / "D_8640x5760_1x_10PercentSafety-FramingChart.fdl"

        # Load FDL to get IDs
        fdl = read_from_file(source_fdl)
        context = fdl.contexts[0]
        canvas = context.canvases[0]
        fd = canvas.framing_decisions[0]

        with tempfile.NamedTemporaryFile(suffix=".tif", delete=False) as tmp:
            output_path = Path(tmp.name)

        try:
            result = extract_framing_region(
                input_path=source_tif,
                output_path=output_path,
                fdl=source_fdl,
                context_index=next(i for i, c in enumerate(fdl.contexts) if c.label == context.label),
                canvas_id=canvas.id,
                framing_decision_id=fd.id,
                filter_name="triangle",
            )

            self.assertTrue(result)
            self.assertTrue(output_path.exists())

            # Verify output dimensions match framing decision dimensions
            output_buf = ImageBuf(str(output_path))
            self.assertFalse(output_buf.has_error)

            expected_width = int(fd.dimensions.width)
            expected_height = int(fd.dimensions.height)
            self.assertEqual(output_buf.spec().width, expected_width)
            self.assertEqual(output_buf.spec().height, expected_height)

        finally:
            if output_path.exists():
                output_path.unlink()

    def test_extract_framing_region_with_resize(self):
        """Test extracting and resizing the framing decision region."""
        source_files_dir = self.get_resources_folder() / "Original_Source_Files"
        source_tif = source_files_dir / "D_8640x5760_1x_10PercentSafety-FramingChart.tif"
        source_fdl = source_files_dir / "D_8640x5760_1x_10PercentSafety-FramingChart.fdl"

        # Load FDL to get IDs
        fdl = read_from_file(source_fdl)
        context = fdl.contexts[0]
        canvas = context.canvases[0]
        fd = canvas.framing_decisions[0]

        with tempfile.NamedTemporaryFile(suffix=".tif", delete=False) as tmp:
            output_path = Path(tmp.name)

        try:
            target_width = 1920
            target_height = 1080

            result = extract_framing_region(
                input_path=source_tif,
                output_path=output_path,
                fdl=source_fdl,
                context_index=next(i for i, c in enumerate(fdl.contexts) if c.label == context.label),
                canvas_id=canvas.id,
                framing_decision_id=fd.id,
                output_width=target_width,
                output_height=target_height,
                filter_name="triangle",
            )

            self.assertTrue(result)
            self.assertTrue(output_path.exists())

            # Verify output dimensions match requested size
            output_buf = ImageBuf(str(output_path))
            self.assertFalse(output_buf.has_error)
            self.assertEqual(output_buf.spec().width, target_width)
            self.assertEqual(output_buf.spec().height, target_height)

        finally:
            if output_path.exists():
                output_path.unlink()

    def test_dimension_mismatch_error(self):
        """Test that mismatched dimensions raise an error."""
        source_files_dir = self.get_resources_folder() / "Original_Source_Files"
        source_tif = source_files_dir / "D_8640x5760_1x_10PercentSafety-FramingChart.tif"

        # Use a different FDL with different canvas dimensions
        other_fdl_path = self.get_resources_folder() / "Source_OCF" / "Source_FDLs" / "A_5184x4320_2_20percentSafe.fdl"

        fdl = read_from_file(other_fdl_path)
        context = fdl.contexts[0]
        canvas = context.canvases[0]
        fd = canvas.framing_decisions[0]

        with tempfile.NamedTemporaryFile(suffix=".tif", delete=False) as tmp:
            output_path = Path(tmp.name)

        try:
            with self.assertRaises(ValueError) as cm:
                process_image_with_fdl(
                    input_path=source_tif,
                    output_path=output_path,
                    fdl=other_fdl_path,
                    context_index=next(i for i, c in enumerate(fdl.contexts) if c.label == context.label),
                    canvas_id=canvas.id,
                    framing_decision_id=fd.id,
                )
            self.assertIn("do not match canvas dimensions", str(cm.exception))
        finally:
            if output_path.exists():
                output_path.unlink()
