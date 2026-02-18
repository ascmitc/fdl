# FDL Viewer

A PySide6 desktop application for visualizing, analyzing, and transforming
ASC FDL (Framing Decision List) files interactively.

## Install & Launch

```shell
pip install fdl-viewer

fdl-viewer                     # launch empty
fdl-viewer path/to/scene.fdl   # launch with file pre-loaded
```

Requires [PySide6](https://doc.qt.io/qtforpython-6/) and
[OpenImageIO](https://github.com/AcademySoftwareFoundation/OpenImageIO).

## Screenshots

### Source Tab

Displays the source canvas with layered geometry overlays -- canvas outline,
effective dimensions, protection area, and framing decision. Reference images
can be loaded as a background layer.

![Source tab showing layered geometry](images/viewer_source.png)

### Output Tab

Shows the result of applying a canvas template. The HUD displays source
dimensions, output dimensions, and template parameters (fit method, alignment,
scale factor, translation).

![Output tab with HUD overlay](images/viewer_output.png)

### Comparison View

Side-by-side or slider-based comparison of source and output transformations,
useful for verifying template results.

![Comparison view](images/viewer_comparison.png)

### Anamorphic Example

Source and output for a RED EPIC with 2x anamorphic squeeze. The elliptical
reference circle indicates the squeeze ratio.

![Anamorphic source (RED EPIC)](images/viewer_anamorphic_source.png)

![Anamorphic output with pad-to-maximum](images/viewer_anamorphic_output.png)

## Features

- **Canvas geometry visualization** -- nested rectangles for canvas, effective,
  protection, and framing layers with labeled dimensions and anchor points
- **Template application** -- select a canvas template and apply it to a source
  canvas/framing decision; view the result immediately
- **Image overlay** -- load EXR, PNG, TIFF, JPG, or DPX reference images as a
  background layer with adjustable opacity
- **Side-by-side comparison** -- source and output tabs with a slider-based
  comparison mode
- **Unit test export** -- capture the current source/template/output combination
  as a pytest scenario for regression testing
- **Layer visibility controls** -- toggle individual layers on/off via sidebar
  checkboxes or the toolbar
- **Details tab** -- transformation metrics, JSON export, and clipboard copy

## Layer Colors

| Layer | Color | Description |
|-------|-------|-------------|
| Canvas | Gray | Full sensor / recording area |
| Effective | Orange | Effective (active) image area |
| Protection | Orange-red (dashed) | Safety / action-safe zone |
| Framing | Green | Framing decision area |

## Architecture

The viewer follows a **Model-View-Controller** pattern with reactive state
management via Qt signals.

### Models

| Class | File | Purpose |
|-------|------|---------|
| `AppState` | `models/app_state.py` | Singleton state with ~20 Qt signals for reactive UI updates |
| `FDLModel` | `models/fdl_model.py` | Qt-aware FDL wrapper with computed geometry properties |
| `RecentFilesModel` | `models/recent_files.py` | Recently opened file tracking |
| `TemplatePresetsModel` | `models/template_presets.py` | Template preset management |

### Controllers

Seven controllers handle business logic:

| Controller | Purpose |
|------------|---------|
| `FileController` | FDL file load/save |
| `ImageController` | Image loading and format conversion via OpenImageIO |
| `TransformController` | Template application logic |
| `SelectionController` | Cascading context/canvas/framing selection |
| `TemplateController` | Template selection and preset handling |
| `ExportController` | FDL export and JSON clipboard operations |
| `UnitTestExportController` | Test case generation for regression testing |

### Views

29 view components organized by area:

- **Main window** -- `MainWindow` with menu bar and status bar
- **Sidebar** -- file loader (drag-drop), source selector (cascading dropdowns),
  template editor, visibility toggles
- **Tabs** -- source, output, comparison, details
- **Canvas** -- `CanvasRenderer` (geometry drawing engine), `CanvasWidget`
  (interactive QGraphicsView), visibility toolbar
- **Dialogs** -- export unit test dialog, error dialog
- **Common** -- collapsible sections, dimension editors, file drop zones

## Building a Standalone App

The viewer can be packaged as a standalone desktop application using PyInstaller:

```shell
cd packages/fdl_viewer
./build.sh
```

The PyInstaller spec file (`FDL Viewer.spec`) is included in the package root.

## Source

`packages/fdl_viewer/src/fdl_viewer/`
