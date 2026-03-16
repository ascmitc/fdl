# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Tests for the FDL Frameline Generator.

These tests verify the rendering functionality using sample FDL data.
"""

import tempfile
from pathlib import Path

import pytest

# Import FDL types for creating test data
from fdl import (
    FDL,
    DimensionsFloat,
    DimensionsInt,
    PointFloat,
)

# Import OIIO for testing
from OpenImageIO import FLOAT, ImageBuf, ImageSpec

from fdl_frameline_generator.colors import COLOR_CANVAS, hex_to_rgba
from fdl_frameline_generator.config import LayerVisibility, RenderConfig
from fdl_frameline_generator.primitives import (
    draw_circle,
    draw_crosshair,
    draw_ellipse,
    draw_filled_rect,
    draw_horizontal_line,
    draw_rect_outline,
    draw_vertical_line,
)
from fdl_frameline_generator.renderer import FramelineRenderer
from fdl_frameline_generator.text import (
    TextAlignment,
    render_anchor_label,
    render_dimension_label,
    render_text,
)

# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def sample_fdl() -> FDL:
    """Create a sample FDL for testing."""
    fdl = FDL(uuid="test-uuid", version_major=1, version_minor=0, fdl_creator="Test", default_framing_intent="TEST01")
    fdl.add_framing_intent(id="TEST01", label="1.78:1 Test", aspect_ratio=DimensionsInt(width=16, height=9), protection=0.1)
    ctx = fdl.add_context(label="Test Context", context_creator="Test")
    canvas = ctx.add_canvas(
        id="canvas1",
        label="Test Canvas",
        source_canvas_id="canvas1",
        dimensions=DimensionsInt(width=1920, height=1080),
        anamorphic_squeeze=1.0,
    )
    canvas.set_effective(dims=DimensionsInt(width=1800, height=1000), anchor=PointFloat(x=60, y=40))
    fd = canvas.add_framing_decision(
        id="canvas1-TEST01",
        label="Test Framing",
        framing_intent_id="TEST01",
        dimensions=DimensionsFloat(width=1600, height=900),
        anchor_point=PointFloat(x=160, y=90),
    )
    fd.set_protection(dims=DimensionsFloat(width=1700, height=950), anchor=PointFloat(x=110, y=65))
    return fdl


@pytest.fixture
def anamorphic_fdl() -> FDL:
    """Create an FDL with anamorphic squeeze for testing."""
    fdl = FDL(uuid="anamorphic-test-uuid", version_major=1, version_minor=0, fdl_creator="Test", default_framing_intent="ANAM01")
    fdl.add_framing_intent(id="ANAM01", label="2x Anamorphic", aspect_ratio=DimensionsInt(width=16, height=9), protection=0.088)
    ctx = fdl.add_context(label="Anamorphic Context", context_creator="Test")
    canvas = ctx.add_canvas(
        id="anam_canvas",
        label="Open Gate RAW",
        source_canvas_id="anam_canvas",
        dimensions=DimensionsInt(width=5184, height=4320),
        anamorphic_squeeze=2.0,
    )
    canvas.set_effective(dims=DimensionsInt(width=5184, height=4320), anchor=PointFloat(x=0, y=0))
    fd = canvas.add_framing_decision(
        id="anam_canvas-ANAM01",
        label="2x Anamorphic Framing",
        framing_intent_id="ANAM01",
        dimensions=DimensionsFloat(width=3072, height=3456),
        anchor_point=PointFloat(x=1056, y=432),
    )
    fd.set_protection(dims=DimensionsFloat(width=3840, height=4320), anchor=PointFloat(x=672, y=0))
    return fdl


@pytest.fixture
def test_image_buf() -> ImageBuf:
    """Create a test image buffer."""
    spec = ImageSpec(200, 200, 4, FLOAT)
    buf = ImageBuf(spec)
    return buf


# ============================================================================
# Color Tests
# ============================================================================


class TestColors:
    """Tests for color conversion functions."""

    def test_hex_to_rgba_with_hash(self):
        """Test hex to RGBA conversion with # prefix."""
        result = hex_to_rgba("#FF0000")
        assert result == (1.0, 0.0, 0.0, 1.0)

    def test_hex_to_rgba_without_hash(self):
        """Test hex to RGBA conversion without # prefix."""
        result = hex_to_rgba("00FF00")
        assert result == (0.0, 1.0, 0.0, 1.0)

    def test_hex_to_rgba_with_alpha(self):
        """Test hex to RGBA conversion with custom alpha."""
        result = hex_to_rgba("#0000FF", alpha=0.5)
        assert result == (0.0, 0.0, 1.0, 0.5)

    def test_hex_to_rgba_gray(self):
        """Test hex to RGBA conversion for gray."""
        result = hex_to_rgba("#808080")
        assert abs(result[0] - 0.502) < 0.01
        assert abs(result[1] - 0.502) < 0.01
        assert abs(result[2] - 0.502) < 0.01


# ============================================================================
# Primitive Drawing Tests
# ============================================================================


class TestPrimitives:
    """Tests for drawing primitive functions."""

    def test_draw_filled_rect(self, test_image_buf):
        """Test drawing a filled rectangle."""
        draw_filled_rect(test_image_buf, 10, 10, 50, 50, (1.0, 0.0, 0.0, 1.0))
        # Verify the buffer was modified (no error)
        assert not test_image_buf.has_error

    def test_draw_horizontal_line(self, test_image_buf):
        """Test drawing a horizontal line."""
        draw_horizontal_line(test_image_buf, 10, 100, 50, 2, (0.0, 1.0, 0.0, 1.0))
        assert not test_image_buf.has_error

    def test_draw_horizontal_line_dashed(self, test_image_buf):
        """Test drawing a dashed horizontal line."""
        draw_horizontal_line(test_image_buf, 10, 100, 50, 2, (0.0, 1.0, 0.0, 1.0), dashed=True, dash_pattern=(5, 3))
        assert not test_image_buf.has_error

    def test_draw_vertical_line(self, test_image_buf):
        """Test drawing a vertical line."""
        draw_vertical_line(test_image_buf, 50, 10, 100, 2, (0.0, 0.0, 1.0, 1.0))
        assert not test_image_buf.has_error

    def test_draw_vertical_line_dashed(self, test_image_buf):
        """Test drawing a dashed vertical line."""
        draw_vertical_line(test_image_buf, 50, 10, 100, 2, (0.0, 0.0, 1.0, 1.0), dashed=True)
        assert not test_image_buf.has_error

    def test_draw_rect_outline(self, test_image_buf):
        """Test drawing a rectangle outline."""
        draw_rect_outline(test_image_buf, 20, 20, 100, 80, 2, COLOR_CANVAS)
        assert not test_image_buf.has_error

    def test_draw_rect_outline_dashed(self, test_image_buf):
        """Test drawing a dashed rectangle outline."""
        draw_rect_outline(test_image_buf, 20, 20, 100, 80, 2, COLOR_CANVAS, dashed=True)
        assert not test_image_buf.has_error

    def test_draw_circle(self, test_image_buf):
        """Test drawing a circle outline."""
        draw_circle(test_image_buf, 100, 100, 40, 2, (1.0, 1.0, 0.0, 1.0))
        assert not test_image_buf.has_error

    def test_draw_circle_filled(self, test_image_buf):
        """Test drawing a filled circle."""
        draw_circle(test_image_buf, 100, 100, 30, 2, (1.0, 0.0, 1.0, 1.0), filled=True)
        assert not test_image_buf.has_error

    def test_draw_ellipse(self, test_image_buf):
        """Test drawing an ellipse outline."""
        draw_ellipse(test_image_buf, 100, 100, 60, 30, 2, (0.0, 1.0, 1.0, 1.0))
        assert not test_image_buf.has_error

    def test_draw_ellipse_filled(self, test_image_buf):
        """Test drawing a filled ellipse."""
        draw_ellipse(test_image_buf, 100, 100, 50, 25, 2, (1.0, 0.5, 0.0, 1.0), filled=True)
        assert not test_image_buf.has_error

    def test_draw_crosshair(self, test_image_buf):
        """Test drawing a crosshair."""
        draw_crosshair(test_image_buf, 100, 100, 20, 20, 1, (1.0, 1.0, 1.0, 0.5))
        assert not test_image_buf.has_error


# ============================================================================
# Text Rendering Tests
# ============================================================================


class TestTextRendering:
    """Tests for text rendering functions."""

    def test_render_text(self, test_image_buf):
        """Test basic text rendering."""
        width, height = render_text(test_image_buf, "Hello", 10, 30, 16)
        assert width > 0
        assert height > 0
        assert not test_image_buf.has_error

    def test_render_text_centered(self, test_image_buf):
        """Test centered text rendering."""
        render_text(test_image_buf, "Centered", 100, 50, 14, alignment=TextAlignment.CENTER)
        assert not test_image_buf.has_error

    def test_render_dimension_label(self, test_image_buf):
        """Test dimension label rendering."""
        render_dimension_label(test_image_buf, 1920, 1080, 100, 100, 16)
        assert not test_image_buf.has_error

    def test_render_dimension_label_float(self, test_image_buf):
        """Test dimension label with float values."""
        render_dimension_label(test_image_buf, 1920.5, 1080.5, 100, 100, 16)
        assert not test_image_buf.has_error

    def test_render_anchor_label(self, test_image_buf):
        """Test anchor label rendering."""
        render_anchor_label(test_image_buf, 160, 90, 50, 50, 14)
        assert not test_image_buf.has_error


# ============================================================================
# Configuration Tests
# ============================================================================


class TestConfig:
    """Tests for configuration dataclasses."""

    def test_default_visibility(self):
        """Test default visibility settings."""
        vis = LayerVisibility()
        assert vis.canvas is True
        assert vis.effective is True
        assert vis.protection is True
        assert vis.framing is True
        assert vis.squeeze_circle is True
        assert vis.dimension_labels is True
        assert vis.anchor_labels is True
        assert vis.crosshair is True
        assert vis.grid is False

    def test_custom_visibility(self):
        """Test custom visibility settings."""
        vis = LayerVisibility(grid=True, protection=False)
        assert vis.grid is True
        assert vis.protection is False

    def test_default_config(self):
        """Test default render configuration."""
        config = RenderConfig()
        assert config.visibility is not None
        assert config.line_width_canvas == 3
        assert config.font_path is None

    def test_custom_config(self):
        """Test custom render configuration."""
        vis = LayerVisibility(grid=True)
        config = RenderConfig(
            visibility=vis,
            line_width_canvas=5,
            grid_spacing=50,
        )
        assert config.visibility.grid is True
        assert config.line_width_canvas == 5
        assert config.grid_spacing == 50


# ============================================================================
# Renderer Tests
# ============================================================================


class TestRenderer:
    """Tests for the FramelineRenderer class."""

    def test_renderer_initialization(self):
        """Test renderer initialization."""
        renderer = FramelineRenderer()
        assert renderer.config is not None

    def test_renderer_with_custom_config(self):
        """Test renderer with custom configuration."""
        config = RenderConfig(line_width_canvas=5)
        renderer = FramelineRenderer(config)
        assert renderer.config.line_width_canvas == 5

    def test_render_to_buffer(self, sample_fdl):
        """Test rendering to buffer."""
        renderer = FramelineRenderer()
        buf = renderer.render_to_buffer(sample_fdl)

        assert buf is not None
        assert buf.spec().width == 1920
        assert buf.spec().height == 1080
        assert buf.spec().nchannels == 3

    def test_render_to_buffer_with_selection(self, sample_fdl):
        """Test rendering with explicit selection."""
        renderer = FramelineRenderer()
        buf = renderer.render_to_buffer(
            sample_fdl,
            context_label="Test Context",
            canvas_id="canvas1",
            framing_id="canvas1-TEST01",
        )

        assert buf is not None
        assert buf.spec().width == 1920

    def test_render_anamorphic(self, anamorphic_fdl):
        """Test rendering with anamorphic squeeze."""
        renderer = FramelineRenderer()
        buf = renderer.render_to_buffer(anamorphic_fdl)

        assert buf is not None
        assert buf.spec().width == 5184
        assert buf.spec().height == 4320

    def test_render_to_file_exr(self, sample_fdl):
        """Test rendering to EXR file."""
        renderer = FramelineRenderer()

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_output.exr"
            buf = renderer.render_to_buffer(sample_fdl)

            buf.write(str(output_path))
            assert output_path.exists()
            assert output_path.stat().st_size > 0

    def test_render_to_file_png(self, sample_fdl):
        """Test rendering to PNG file."""
        renderer = FramelineRenderer()

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_output.png"
            buf = renderer.render_to_buffer(sample_fdl)

            buf.write(str(output_path))
            assert output_path.exists()
            assert output_path.stat().st_size > 0

    def test_render_with_visibility_options(self, sample_fdl):
        """Test rendering with custom visibility."""
        config = RenderConfig(
            visibility=LayerVisibility(
                canvas=True,
                effective=False,
                protection=False,
                framing=True,
                grid=True,
            )
        )
        renderer = FramelineRenderer(config)
        buf = renderer.render_to_buffer(sample_fdl)

        assert buf is not None
        assert not buf.has_error

    def test_render_invalid_context(self, sample_fdl):
        """Test that invalid context raises error."""
        renderer = FramelineRenderer()

        with pytest.raises(ValueError, match="not found"):
            renderer.render_to_buffer(sample_fdl, context_label="Nonexistent")

    def test_render_invalid_canvas(self, sample_fdl):
        """Test that invalid canvas raises error."""
        renderer = FramelineRenderer()

        with pytest.raises(ValueError, match="not found"):
            renderer.render_to_buffer(
                sample_fdl,
                context_label="Test Context",
                canvas_id="nonexistent",
            )

    def test_render_invalid_framing(self, sample_fdl):
        """Test that invalid framing decision raises error."""
        renderer = FramelineRenderer()

        with pytest.raises(ValueError, match="not found"):
            renderer.render_to_buffer(
                sample_fdl,
                context_label="Test Context",
                canvas_id="canvas1",
                framing_id="nonexistent",
            )


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Integration tests for end-to-end rendering."""

    def test_full_render_pipeline(self, sample_fdl):
        """Test complete rendering pipeline."""
        config = RenderConfig(
            visibility=LayerVisibility(
                canvas=True,
                effective=True,
                protection=True,
                framing=True,
                squeeze_circle=True,
                dimension_labels=True,
                anchor_labels=True,
                crosshair=True,
                grid=True,
            ),
            line_width_canvas=3,
            line_width_framing=3,
            grid_spacing=100,
        )

        renderer = FramelineRenderer(config)
        buf = renderer.render_to_buffer(sample_fdl)

        assert buf is not None
        assert not buf.has_error
        assert buf.spec().width == 1920
        assert buf.spec().height == 1080

    def test_render_and_save(self, sample_fdl):
        """Test rendering and saving to multiple formats."""
        renderer = FramelineRenderer()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Test multiple output formats
            for ext in [".exr", ".png", ".tif", ".jpg", ".dpx", ".svg"]:
                output_path = Path(tmpdir) / f"test{ext}"
                success = renderer.render_from_fdl_object(sample_fdl, output_path)

                assert success
                assert output_path.exists()

    def test_render_to_svg_string(self, sample_fdl):
        """Test rendering to SVG string via render_to_svg."""
        renderer = FramelineRenderer()

        svg_str = renderer.render_to_svg(sample_fdl)

        assert svg_str is not None
        assert svg_str.startswith("<?xml")
        assert "<svg" in svg_str
        assert 'viewBox="0 0 1920 1080"' in svg_str
        # Should contain layer labels
        assert "Canvas" in svg_str

    def test_svg_output_is_valid_xml(self, sample_fdl):
        """Test that SVG output is well-formed XML."""
        import xml.etree.ElementTree as ET

        renderer = FramelineRenderer()
        svg_str = renderer.render_to_svg(sample_fdl)

        # Should parse without error
        root = ET.fromstring(svg_str)
        assert root.tag == "{http://www.w3.org/2000/svg}svg"

    def test_svg_file_output(self, sample_fdl):
        """Test writing SVG file via render_from_fdl_object."""
        renderer = FramelineRenderer()

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "output.svg"
            success = renderer.render_from_fdl_object(sample_fdl, output_path)

            assert success
            assert output_path.exists()
            content = output_path.read_text(encoding="utf-8")
            assert content.startswith("<?xml")
            assert "<svg" in content
