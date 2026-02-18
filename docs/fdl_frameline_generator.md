# Frameline Generator

Generates pixel-accurate frameline overlay images from ASC FDL files. Supports
raster output (EXR, PNG, TIFF, JPG, DPX) via OpenImageIO and vector output
(SVG) via a custom backend.

## Install

```shell
pip install fdl-frameline-generator
```

Requires [OpenImageIO](https://github.com/AcademySoftwareFoundation/OpenImageIO)
for raster formats. SVG output works without it.

## Example Output

A frameline overlay showing canvas (gray), effective (blue), protection (dashed
orange), and framing (green) layers with dimension labels, anchor points,
anamorphic squeeze reference circle, crosshair, ASC FDL logo, and metadata:

![Frameline overlay example](images/frameline_example.png)

## Quick Start

```shell
# Basic raster output (format from extension)
fdl-frameline input.fdl output.png

# SVG vector output with grid, no logo
fdl-frameline input.fdl output.svg --hide-logo --show-grid

# Select specific context/canvas/framing
fdl-frameline input.fdl output.exr --context "Camera A" --canvas abc123

# Add metadata overlay
fdl-frameline input.fdl output.png \
    --camera "ARRI Alexa Mini LF" \
    --show-name "My Show" \
    --dop "Jane Doe" \
    --sensor-mode "Open Gate"
```

## CLI Reference

### Required Arguments

| Argument | Description |
|----------|-------------|
| `input` | Path to the FDL file |
| `output` | Output image path (format auto-detected from extension) |

### FDL Selection

| Flag | Description | Default |
|------|-------------|---------|
| `--context LABEL` | Context to use | First context |
| `--canvas ID` | Canvas ID | First canvas |
| `--framing ID` | Framing decision ID | First framing decision |

### Layer Visibility

All layers are **shown by default** unless noted.

| Show | Hide | Layer |
|------|------|-------|
| `--show-canvas` | `--hide-canvas` | Canvas outline |
| `--show-effective` | `--hide-effective` | Effective dimensions |
| `--show-protection` | `--hide-protection` | Protection area |
| `--show-framing` | `--hide-framing` | Framing decision |
| `--show-squeeze-circle` | `--hide-squeeze-circle` | Anamorphic squeeze reference |
| `--show-labels` | `--hide-labels` | Dimension and anchor labels |
| `--show-crosshair` | `--hide-crosshair` | Center crosshair |
| `--show-grid` | | Grid overlay (default: **off**) |
| `--show-logo` | `--hide-logo` | ASC FDL logo |
| `--show-metadata` | `--hide-metadata` | Metadata overlay |

### Metadata Overlay

| Flag | Description |
|------|-------------|
| `--camera TEXT` | Camera make/model (e.g., "ARRI Alexa Mini LF") |
| `--show-name TEXT` | Show name |
| `--dop TEXT` | Director of Photography |
| `--sensor-mode TEXT` | Sensor mode (e.g., "4K", "Open Gate") |

### Styling

| Flag | Description | Default |
|------|-------------|---------|
| `--line-width INT` | Line width in pixels | varies by layer |
| `--font-size INT` | Font size in pixels | auto |
| `--font-path PATH` | Custom TrueType font file | system default |
| `--grid-spacing INT` | Grid line spacing | 100 |
| `--logo-path PATH` | Custom logo image | bundled ASC FDL logo |
| `--logo-scale FLOAT` | Logo scale factor | 0.333 |

### Colors

Pass hex color values (e.g., `#FF0000`):

| Flag | Default | Layer |
|------|---------|-------|
| `--color-canvas` | `#808080` | Canvas outline |
| `--color-effective` | `#0066CC` | Effective dimensions |
| `--color-protection` | `#FF9900` | Protection area |
| `--color-framing` | `#00CC66` | Framing decision |

## Output Formats

| Extension | Format | Backend |
|-----------|--------|---------|
| `.exr` | OpenEXR | OpenImageIO |
| `.png` | PNG | OpenImageIO |
| `.tif` / `.tiff` | TIFF | OpenImageIO |
| `.jpg` | JPEG | OpenImageIO |
| `.dpx` | DPX | OpenImageIO |
| `.svg` | SVG | Custom `SvgDocument` |

## Programmatic Usage

The renderer can be used directly from Python:

```python
from fdl_frameline_generator import FramelineRenderer, RenderConfig, LayerVisibility

config = RenderConfig(
    visibility=LayerVisibility(
        grid=True,
        squeeze_circle=True,
    ),
)

renderer = FramelineRenderer(config)

# From file path
renderer.render_from_fdl("input.fdl", "output.png")

# From FDL object
from fdl import read_from_file
fdl = read_from_file("input.fdl")
renderer.render_from_fdl_object(fdl, "output.exr")

# To SVG
svg_doc = renderer.render_to_svg(fdl)
svg_doc.write("output.svg")
```

## Architecture

| Module | Class / Purpose |
|--------|----------------|
| `renderer.py` | `FramelineRenderer` -- main rendering orchestrator |
| `config.py` | `RenderConfig`, `LayerVisibility` -- configuration dataclasses |
| `svg_backend.py` | `SvgDocument` -- vector SVG output backend |
| `colors.py` | Color constants and RGBA utilities |
| `cli.py` | `fdl-frameline` command-line interface |
| `primitives.py` | Re-exports drawing primitives from `fdl-imaging` |
| `text.py` | Re-exports text utilities from `fdl-imaging` |

The rendering pipeline:

1. Load FDL and select context/canvas/framing decision
2. Create an image buffer sized to the canvas dimensions
3. Render layers bottom-to-top: grid -> canvas -> effective -> protection -> framing
4. Add labels, crosshair, logo, and metadata
5. Write output in the requested format

Drawing primitives and text rendering are delegated to the
[fdl-imaging](fdl_imaging.md) package.

## Source

`packages/fdl_frameline_generator/src/fdl_frameline_generator/`
