# Application Packages

Beyond the core `fdl` library, the project includes three application packages
in the `packages/` directory. Each is a standalone Python package within the
uv workspace.

```
fdl-viewer -------------+
                        +---> fdl-imaging ---> fdl (core)
fdl-frameline-generator +
```

## [Frameline Generator](fdl_frameline_generator.md)

Generates pixel-accurate frameline overlay images from FDL files. Supports
EXR, PNG, TIFF, SVG, and more.

```shell
pip install fdl-frameline-generator
fdl-frameline input.fdl output.png
```

## [FDL Imaging](fdl_imaging.md)

OpenImageIO-based image processing library for FDL workflows. Provides
cropping, extraction, template transformation, drawing primitives, and
pixel-level image comparison. Used by both the frameline generator and viewer.

```shell
pip install fdl-imaging
```

## [FDL Viewer](fdl_viewer.md)

PySide6 desktop application for visualizing and transforming FDL files
interactively. Displays source and output canvases with geometry overlays,
supports template application, image overlay, and side-by-side comparison.

```shell
pip install fdl-viewer
fdl-viewer
```

## Core CLI: fdl-validate

The core `fdl` package also provides a command-line validation tool:

```shell
fdl-validate scene.fdl              # validate a single file
fdl-validate *.fdl --strict         # validate multiple files
```

**Source:** `native/bindings/python/fdl/cli.py`
