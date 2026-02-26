[# ASC Framing Decision List (FDL)

**Getting Started:**

_________________
INTRODUCTION:
ASC FDL’s are a set of instructions for how to view content in any application. The ASC FDL provides a mechanism to document framing decisions through all phases of a production's life cycle, from pre-visualization through post-production. The FDL can exist in the form of a sidecar JSON file, or embedded into another data structure like camera original files. Any time an application is rendering media to another department or person, an accompanying set of ASC FDL data should be created and delivered. Therefore any downstream applications are able to apply the intended frame.

_________________
1-SHEET:
This is the first [document](https://ascmitc.github.io/fdl/dev/docs/ASCFDL_One-Sheet-20210807.pdf) you should read.
This is a very brief introduction to what the FDL is and the problem it has set out to solve.



_________________
USER GUIDE:
This is a [document](https://ascmitc.github.io/fdl/dev/docs/ASCFDL_UserGuide_v2.0.PDF) intended for end users to better understand how the FDL could be used within their workflows.
This will also be a great reference for implementers to better understand the intention behind FDL usability.



_______________________________
GETTING ACCESS TO SAMPLE MEDIA
After you compile the code, an interface has been provided allowing you to view framing charts, configure settings and instantly view the expected outcome both visually and as the resulting FDL.  



_________________
SPECIFICATION:
This is the technical [specification](https://ascmitc.github.io/fdl/dev/Specification/ASCFDL_Specification_v2.0.pdf/) for implementers.



_____________________
IMPLIMENTATION GUIDE
For anyone looking to implement the ASCFDL into thier tooling, [a guide](https://ascmitc.github.io/fdl/dev/FDL_Template_Implementer_Guide/) has been created to offer helpful information. 



____________________________________________
CI AVAILABLE FOR MACOS, WINDOWS & LINUX 
Click on the CI/CD badge below to see per-platform results
[![CI/CD](https://github.com/ascmitc/fdl/actions/workflows/main.yml/badge.svg)](https://github.com/ascmitc/fdl/actions/workflows/main.yml)
[![Nightly Build](https://img.shields.io/badge/Nightly_Build-download-blue?logo=github)](https://nightly.link/ascmitc/fdl/workflows/main/main)
[![GitHub Actions](https://img.shields.io/badge/All_Runs-view-grey?logo=githubactions)](https://github.com/ascmitc/fdl/actions/workflows/main.yml)





## Repository Overview

This repository contains the ASC FDL reference implementation: a native C library with language bindings and Python application packages for working with Framing Decision List files.

### Directory Structure

```
.
├── native/                          # Native (C/C++) core and bindings
│   ├── core/                        # libfdl_core — shared C library
│   │   ├── include/fdl/             #   Public C ABI header (fdl_core.h)
│   │   ├── src/                     #   Implementation (parsing, validation, geometry, pipeline, templates)
│   │   └── tests/                   #   Catch2 C++ unit tests with JSON test vectors
│   ├── bindings/
│   │   ├── python/                  # fdl — Python ctypes bindings & facade
│   │   │   ├── fdl/                 #   FDL, Canvas, Context, FramingDecision, etc.
│   │   │   ├── fdl_ffi/             #   Low-level ctypes FFI loader and function declarations
│   │   │   └── tests/              #   Python unit tests (351 tests)
│   │   ├── cpp/fdl/                 # fdl.hpp — C++ RAII header-only wrapper
│   │   └── node/                    # Node.js bindings (placeholder)
│   ├── api/                         # OpenAPI spec (fdl_api.yaml)
│   └── tools/                       # Code generation and test vector extraction scripts
│
├── packages/                        # Python application packages
│   ├── fdl_imaging/                 # fdl-imaging — FDL-based image processing (OpenImageIO)
│   │   ├── src/fdl_imaging/         #   Image extraction, resizing, comparison utilities
│   │   └── tests/                   #   Image processing tests (6 tests)
│   ├── fdl_frameline_generator/     # fdl-frameline-generator — frameline overlay generation
│   │   ├── src/fdl_frameline_generator/  # EXR/PNG/TIFF/SVG frameline rendering
│   │   └── tests/                   #   Renderer + regression tests (157 tests)
│   └── fdl_viewer/                  # fdl-viewer — PySide6 desktop application
│       ├── src/fdl_viewer/          #   MVC architecture (models, views, controllers)
│       └── tests/                   #   UI, controller, model, and visual QC tests (130+ tests)
│
├── schema/                          # JSON Schema definitions (v0.1, v1.0, v2.0, v2.0.1)
├── resources/FDL/                   # Test resources
│   ├── Original_Source_Files/       #   Source FDL + TIFF image pairs
│   ├── Scenarios_For_Implementers/  #   30+ numbered scenarios with expected results
│   └── EdgeCases/                   #   Generated edge-case FDL files
├── docs/                            # Documentation (template logic, implementer guide)
├── Specification/                   # ASC FDL specification documents
└── pyproject.toml                   # uv workspace root
```

### Key Components

**`libfdl_core`** (`native/core/`) — The core engine, written in C++ and exposed via a C ABI. Handles FDL parsing, serialization (JSON), schema validation (Draft 2020-12 via jsoncons), geometry calculations, canvas resolution pipeline, and template application. Built with CMake.

**`fdl`** (`native/bindings/python/`) — Python package providing a high-level facade over `libfdl_core` via ctypes. Classes include `FDL`, `Canvas`, `Context`, `FramingIntent`, `FramingDecision`, and `CanvasTemplate`. Also provides rounding strategies, validation, and a `fdl-validate` CLI tool.

**`fdl-imaging`** (`packages/fdl_imaging/`) — Image processing utilities using OpenImageIO. Extracts framing regions from source images based on FDL geometry and produces output images matching target canvas dimensions.

**`fdl-frameline-generator`** (`packages/fdl_frameline_generator/`) — Generates frameline overlay images from FDL files. Supports EXR, PNG, TIFF (via OIIO), and SVG vector output. Includes a `fdl-frameline` CLI tool.

**`fdl-viewer`** (`packages/fdl_viewer/`) — A PySide6 desktop application for interactively viewing, transforming, and exporting FDL files. Supports source/output scene visualization with HUD overlays, template-based transforms, and image export. Built with an MVC architecture.

-----------------------------------------

## Developer Guide

### Prerequisites

- **Python** 3.10+
- **uv** (Python package manager) — [install instructions](https://docs.astral.sh/uv/getting-started/installation/)
- **CMake** 3.20+
- **C++ compiler** with C++17 support (Clang, GCC, or MSVC)
- **OpenImageIO** 2.4+ (required by `fdl-imaging` and `fdl-frameline-generator`)

### Clone the Repository

```bash
git clone https://github.com/ascmitc/fdl.git
cd fdl
```

### Code Generation

The Python bindings (FFI layer and facade classes) and the C++ RAII header are auto-generated from the IDL schema. Codegen must run before building or testing.

```bash
# Install codegen dependencies
uv pip install pyyaml jinja2 --system

# Run all codegen targets (python-ffi, python-facade, cpp-raii)
python scripts/run_codegen.py
```

This generates files into `native/bindings/python/fdl_ffi/`, `native/bindings/python/fdl/`, and `native/bindings/cpp/fdl/fdl.hpp`.

### Build the Native Library

The Python packages depend on `libfdl_core`, which must be compiled before running tests or using the Python bindings.

```bash
# Build and run C++ tests (recommended)
python scripts/build_native.py --run-tests

# Build without tests
python scripts/build_native.py --no-tests
```

Or manually with CMake:

```bash
cmake -S native/core -B native/core/build -DCMAKE_BUILD_TYPE=Release
cmake --build native/core/build --config Release -j$(nproc 2>/dev/null || sysctl -n hw.ncpu)
```

This produces `native/core/build/libfdl_core.dylib` (macOS), `libfdl_core.so` (Linux), or `fdl_core.dll` (Windows). The Python FFI loader finds it automatically at this path.

### Set Up the Python Environment

```bash
# Create the virtual environment and install all workspace packages + dev dependencies
uv sync --extra dev
```

This installs the full workspace (`fdl`, `fdl-imaging`, `fdl-frameline-generator`, `fdl-viewer`) in editable mode along with test dependencies (pytest, pytest-xdist, pytest-qt, pytest-cov, mktestdocs).

### Run the Tests

**C++ core tests (113 tests):**
```bash
python scripts/build_native.py --run-tests
# or: ctest --test-dir native/core/build --output-on-failure
```

**FDL core Python bindings (351 tests):**
```bash
uv run pytest native/bindings/python/tests/ -v -n auto -p no:pytest-qt
```

**FDL Imaging (6 tests):**
```bash
uv run pytest packages/fdl_imaging/tests/ -v -n auto -p no:pytest-qt
```

**FDL Frameline Generator (157 tests):**
```bash
uv run pytest packages/fdl_frameline_generator/tests/ -v -p no:pytest-qt
```

**FDL Viewer:**
```bash
# All viewer tests (can take a long time due to UI scenario matrix)
uv run pytest packages/fdl_viewer/tests/ -v

# Exclude slow visual QC tests
uv run pytest packages/fdl_viewer/tests/ -v \
    --ignore=packages/fdl_viewer/tests/test_visual_qc_matrix.py \
    --ignore=packages/fdl_viewer/tests/test_visual_qc_edge_cases.py
```

**Run everything (fast subset):**
```bash
uv run pytest native/bindings/python/tests/ packages/fdl_imaging/tests/ packages/fdl_frameline_generator/tests/ -v -n auto -p no:pytest-qt
```

### Linting

The project uses [ruff](https://docs.astral.sh/ruff/) for linting and formatting:

```bash
# Check for lint errors
uvx ruff check .

# Check formatting
uvx ruff format --check .

# Auto-format
uvx ruff format .
```

-----------------------------------------

## CI/CD

The GitHub Actions workflow (`.github/workflows/main.yml`) runs on every push, pull request, and nightly schedule across macOS, Windows, and Linux.

### Pipeline Overview

```
lint --> test (macOS, Windows, Linux) --> build_artifacts --> publish_release
```

| Job | Trigger | Description |
|-----|---------|-------------|
| **Lint** | All pushes/PRs | Runs `ruff check` and `ruff format --check` on Ubuntu |
| **Test** | After lint passes | Codegen, native build + C++ tests, Python tests (all 4 suites) on 3 platforms |
| **Build Artifacts** | Nightly, manual, or tag push | Builds platform-specific wheels (`fdl`, `fdl-imaging`, `fdl-frameline-generator`, `fdl-viewer`) and standalone FDL Viewer app (PyInstaller) |
| **Publish Release** | Tag push (`v*`) on main | Creates a GitHub Release and uploads all artifacts |

### Caching

Git LFS objects are cached per-OS to avoid re-downloading large test resources on every run. No build artifacts are cached.

### Test Parallelism

Non-viewer Python test suites run with `pytest-xdist` (`-n auto`) for parallel execution across all available CPU cores. Viewer tests run serially to avoid display conflicts.
](https://ascmitc.github.io/fdl/dev/FDL_Template_Implementer_Guide/)
