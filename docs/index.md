# ASC FDL

ASC FDL is a toolkit for parsing, validating, creating, and transforming
[Framing Decision List (FDL)](https://theasc.com/society/ascmitc/asc-framing-decision-list) files.
It is built around a shared C core library (`libfdl_core`) with idiomatic bindings for
**Python**, **TypeScript/Node.js**, and **C++**, and conforms to the official FDL
[specification](https://github.com/ascmitc/fdl/tree/main/Specification).

## How It Works

The C++ core compiles to a shared library exporting a stable C ABI. Language
bindings are **auto-generated** from a single IDL file (`fdl_api.yaml`) via a
Jinja2-based code generation pipeline. This ensures Python, TypeScript, and C++ stay in sync
with the C core and with each other. See [Architecture](architecture.md) for
the full picture.

## Install

### Python

```shell
pip install fdl
```

### TypeScript / Node.js

```shell
npm install fdl
```

### C++

The C++ bindings are a single header-only file wrapping the C ABI:

```cpp
#include "fdl/fdl.hpp"
```

Link against `libfdl_core` (built via CMake from `native/core/`).

## Features

| Feature                    | Python | TypeScript | C++ | Notes                                                |
|:---------------------------|:------:|:----------:|:---:|------------------------------------------------------|
| Parse & write FDL files    |   Y    |     Y      |  Y  |                                                      |
| Validate IDs & relations   |   Y    |     Y      |  Y  | Enforces unique IDs and valid cross-references       |
| JSON Schema validation     |   Y    |     Y      |  Y  |                                                      |
| Canvas templates           |   Y    |     Y      |  Y  | Apply templates to produce new canvases              |
| Rounding strategies        |   Y    |     Y      |  Y  | Global and per-dimension rounding control            |
| Custom attributes          |   Y    |     Y      |  Y  | Scalar + composite types (PointFloat, DimensionsFloat, DimensionsInt) |
| CLI tool                   |   Y    |            |     | `fdl-validate` for command-line validation           |

## Documentation

| Section | Description |
|---------|-------------|
| [Getting Started](getting_started.md) | Tutorials with Python, TypeScript, and C++ examples |
| [Architecture](architecture.md) | System design, layer diagram, ownership model |
| [Code Generation](codegen.md) | IDL pipeline, how to extend the data model |
| [C ABI Design](c_abi.md) | Native interface contract for binding authors |
| [Template Application](FDL_Apply_Template_Logic.md) | Algorithm overview and formula reference |
| [Template Implementer Guide](FDL_Template_Implementer_Guide.md) | Deep-dive with worked examples |
| [Application Packages](packages.md) | fdl-imaging, fdl-frameline-generator, fdl-viewer |
| [Contributing](contributions.md) | How to contribute, lint, test, and submit PRs |

## Examples

The `examples/` directory contains demonstration applications:

- **`examples/web_viewer/`** -- A React + Express web viewer that loads and visualises FDL
  files using the Node.js bindings. **This is a reference/demo application, not
  production software.** It is provided to illustrate how to integrate the FDL
  library into a web stack.

## API Reference

- **Python API** -- see the [FDL Classes](FDL Classes/fdl.md) section
- **C/C++ API** -- [Doxygen Reference](api/index.html) (auto-generated from source)
