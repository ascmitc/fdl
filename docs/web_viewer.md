# FDL Web Viewer (Example)

A React + Express example application that loads and visualises ASC FDL files
using the **Node.js / TypeScript bindings** and the native C addon.

!!! warning "Not production software"
    The web viewer exists to exercise and validate the Node.js bindings against
    the shared C core (`libfdl_core`). Its purpose is to demonstrate library
    portability across language runtimes -- the same FDL logic that runs in
    Python and C++ works identically through the Node.js native addon. The UI is
    minimal and intentionally simple.

## Prerequisites

- Python >= 3.10
- Node.js >= 20
- [uv](https://github.com/astral-sh/uv)

## Quick Start

From the repository root:

```shell
python examples/web_viewer/run.py
```

This single command will:

1. Set up the Python virtual environment (`uv sync`)
2. Build the Node.js native addon (via `scripts/build_node.py`)
3. Install npm dependencies
4. Launch the development servers

Once running:

- **Client:** http://localhost:5173 (Vite + React)
- **Server:** http://localhost:3001 (Express + native addon)

### Options

```
--setup-only   Run setup steps without launching the servers
--skip-build   Skip the native addon build step
--force-build  Force a rebuild of the native addon
```

### Manual Launch

If you have already run setup, you can start the servers directly:

```shell
cd examples/web_viewer
PYTHON_PATH=.venv/bin/python npm run dev
```

## Stack

| Layer  | Technology |
|--------|------------|
| Client | React, Vite, Tailwind CSS, Radix UI |
| Server | Express, TypeScript (tsx), `@asc-mitc/fdl` native addon |

## Source

`examples/web_viewer/`
