# FDL Web Viewer (Example)

A React + Express example application that loads and visualises ASC FDL files
using the **Node.js / TypeScript bindings** and the native C addon.

> **This is not production software.** The web viewer exists to exercise and
> validate the Node.js bindings against the shared C core (`libfdl_core`). Its
> purpose is to demonstrate library portability across language runtimes -- the
> same FDL logic that runs in Python and C++ works identically through the
> Node.js native addon. The UI is minimal and intentionally simple.

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

The server depends on the repository's own Node binding (`native/bindings/node`), not
the published npm package, so it always runs the current core. Build it first with
`python scripts/build_node.py` (`run.py` does this for you).

## Tests

Both suites run every scenario that has a source image and a golden EXR, and use
`server/tests/scenario_inputs.json` (generated from the Python scenario config).

```shell
# FDL transform vs the committed Results FDLs (N-API binding)
npm test -w server

# Image bridge vs the golden EXRs (pixel-identical)
python -m pytest examples/web_viewer/server/tests -v
```

After changing the scenarios, regenerate the fixture with
`python examples/web_viewer/server/tests/scenario_inputs.py`.
