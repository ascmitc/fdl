# FDL Imaging

A Python library for FDL-based image processing built on
[OpenImageIO](https://github.com/AcademySoftwareFoundation/OpenImageIO).
Provides image cropping/extraction, template transformations, drawing
primitives, text rendering, and pixel-level image comparison.

This is a **library-only** package -- no CLI. It is used programmatically by
[fdl-frameline-generator](fdl_frameline_generator.md) and
[fdl-viewer](fdl_viewer.md).

## Install

```shell
pip install fdl-imaging
```

Requires OpenImageIO to be available on the system.

## Capabilities

- **Image extraction** -- crop images to framing decision or protection
  boundaries
- **Template transformation** -- apply FDL canvas template transformations to
  images (crop -> scale -> translate -> format)
- **Drawing primitives** -- render rectangles, circles, ellipses, crosshairs,
  grids, corner triangles, and edge arrows onto image buffers
- **Text rendering** -- dimension labels, anchor point labels, squeeze ratio
  labels with configurable alignment and anamorphic squeeze compensation
- **Image comparison** -- pixel-by-pixel regression testing with configurable
  tolerances, diff image generation, and detailed failure reporting

## Usage Examples

### Extract a framing region

```python
from fdl_imaging import extract_framing_region

extract_framing_region(
    input_path="source.tif",
    output_path="framed.tif",
    fdl="scene.fdl",
    context_id="Camera A",
    canvas_id="canvas_001",
    framing_decision_id="fd_001",
    resize_width=1920,
    resize_height=1080,
)
```

### Apply a template transformation

```python
from fdl_imaging import process_image_with_fdl_template

process_image_with_fdl_template(
    input_path="source.tif",
    output_path="transformed.tif",
    source_fdl="source.fdl",
    template_fdl="template.fdl",
    context_id="Camera A",
    canvas_id="canvas_001",
    framing_decision_id="fd_001",
    template_label="UHD Delivery",
)
```

### Draw on an image buffer

```python
import OpenImageIO as oiio
from fdl_imaging.drawing import draw_rect_outline, draw_crosshair, draw_grid
from fdl_imaging.text import render_dimension_label

buf = oiio.ImageBuf(oiio.ImageSpec(1920, 1080, 4, oiio.FLOAT))

draw_rect_outline(buf, x=100, y=50, w=1720, h=980,
                  color=(0.5, 0.5, 0.5, 1.0), line_width=2)
draw_crosshair(buf, cx=960, cy=540, size=40,
               color=(0.0, 0.8, 0.4, 1.0), line_width=1)
draw_grid(buf, spacing=100, color=(0.3, 0.3, 0.3, 0.5), line_width=1)
render_dimension_label(buf, "1920 x 1080", x=960, y=1060,
                       font_size=14, color=(1.0, 1.0, 1.0, 1.0))

buf.write("overlay.png")
```

## API Modules

| Module | Key exports | Purpose |
|--------|-------------|---------|
| `_processing` | `process_image_with_fdl()`, `extract_framing_region()`, `process_image_with_fdl_template()`, `transform_image_with_computed_values()`, `get_fdl_components()` | Core image processing operations |
| `drawing` | `draw_rect_outline()`, `draw_filled_rect()`, `draw_circle()`, `draw_ellipse()`, `draw_crosshair()`, `draw_grid()`, `draw_frame_region()`, `draw_corner_triangle()`, `draw_edge_arrow_inward()` | Geometric drawing primitives |
| `text` | `render_text()`, `render_text_bold()`, `render_dimension_label()`, `render_anchor_label()`, `render_squeeze_label()`, `get_text_size()` | Text rendering with alignment and squeeze compensation |
| `colors` | `RGBA`, `hex_to_rgba()`, `DEFAULT_DASH_PATTERN` | Color type and utilities |
| `testing` | `ImageComparison`, `BaseFDLImagingTestCase` | Pixel-level regression testing |

### Image Comparison for Testing

The `ImageComparison` class provides configurable pixel-level image comparison:

```python
from fdl_imaging.testing import ImageComparison

comparator = ImageComparison(
    fail_threshold=0.01,      # per-pixel difference threshold
    warn_threshold=0.005,
    allowed_failed_pixels=100, # tolerance for cross-platform text rendering
    outputs_dir="test_outputs", # save diff images here
)

result = comparator.compare("expected.tif", "actual.tif")
assert result.passed, result.message
```

## Package Relationships

```
fdl-viewer -------------+
                        +---> fdl-imaging ---> fdl (core)
fdl-frameline-generator +
```

`fdl-imaging` is the shared foundation: the frameline generator delegates all
drawing primitives and text rendering to it, and the viewer uses it for image
loading, processing, and visual QC comparison.

## Source

`packages/fdl_imaging/src/fdl_imaging/`
