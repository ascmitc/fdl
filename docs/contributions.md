# Contributions

Contributions come in many forms -- reporting bugs, giving feedback, or submitting code.
Our goal is to provide a useful toolkit that suits the needs of its users.

## Architecture

For a full overview of how the project is structured, see the
[Architecture](architecture.md) doc. In short:

ASC FDL is built around a shared C core library (`libfdl_core`) with auto-generated
bindings for Python and C++. The code generation pipeline uses Jinja2 templates
driven by `fdl_api.yaml`.

- **Architecture overview**: [Architecture](architecture.md)
- **Code generation guide**: [Code Generation](codegen.md)
- **C ABI contract**: [C ABI Design](c_abi.md)
- **C/C++ API Reference**: [Doxygen docs on GitHub Pages](https://ascmitc.github.io/fdl/api/)
- **Python API Reference**: see the [FDL Classes](FDL Classes/fdl.md) section

## Common Tasks

| Task | Guide |
|------|-------|
| Add a field to an existing class | [Code Generation -> Add a Field](codegen.md#how-to-add-a-field-to-an-existing-class) |
| Add a new FDL class | [Code Generation -> Add a Class](codegen.md#how-to-add-a-new-class) |
| Write a new language binding | [C ABI Design](c_abi.md) |
| Understand the template pipeline | [Template Implementer Guide](FDL_Template_Implementer_Guide.md) |

## Naming Conventions

- The top-level document class is named **`FDL`**, not "Document". Client code
  reads as `FDL.parse(...)` or `fdl::FDL::parse(...)`.
- C ABI uses `fdl_doc_t` / `fdl_doc_*` -- `doc` is the internal handle name.
- Python facade: `FDL`. C++ RAII: `fdl::FDL`.

## Generated File Boundaries

Most files in `native/bindings/python/fdl/` and all of `fdl_ffi/` are
auto-generated and marked with:

```python
# AUTO-GENERATED from fdl_api.yaml -- DO NOT EDIT
```

**Do not edit these files by hand** -- your changes will be overwritten.

Hand-written files (safe to edit):

- `native/bindings/python/fdl/base.py` -- handle wrappers, collection protocol
- `native/bindings/python/fdl/cli.py` -- `fdl-validate` CLI

See [Code Generation](codegen.md#generated-vs-hand-written-files) for the full list.

## Package Management

ASC FDL uses [uv](https://docs.astral.sh/uv/) for Python package management.
The workspace root `pyproject.toml` defines four member packages.

!!! warning
    To regenerate `uv.lock`, always use `python scripts/uv_lock.py` (overrides
    the index URL to public PyPI). Never run `uv lock` directly.

## Running Tests

### Python

```shell
uv run pytest native/bindings/python/tests/ -v -n auto -p no:pytest-qt
```

### C++

```shell
python scripts/build_native.py --run-tests
```

This configures CMake, builds `libfdl_core`, and runs the Catch2 test suite.

## Linting

Run all lint checks locally with:

```shell
python scripts/lint.py
```

This mirrors the CI lint job and runs 5 checks:

1. **ruff-check** -- Python lint
2. **ruff-format** -- Python format check
3. **clang-format** -- C++ format check
4. **codegen-drift** -- verifies generated bindings match `fdl_api.yaml`
5. **clang-tidy** -- C++ static analysis

You can run a single step: `python scripts/lint.py --step ruff-check`

### Additional verification (beyond lint)

```shell
python scripts/build_native.py --run-tests                              # C++ tests
python scripts/check_abi_symbols.py                                     # ABI parity
uv run pytest native/bindings/python/tests/ -v -n auto -p no:pytest-qt # Python tests
```

## Regenerating Bindings

After modifying `fdl_api.yaml` or Jinja2 templates, regenerate all bindings:

```shell
python scripts/run_codegen.py
```

This runs all three targets (python-ffi, python-facade, cpp-raii) and formats
the output. To check for drift without committing:

```shell
python scripts/run_codegen.py --check
```

See [Code Generation](codegen.md) for details on the pipeline.

## Building Documentation

```shell
# Install docs dependencies
uv pip install -e ".[docs]"

# Build the docs (output in "site" folder)
mkdocs build

# Serve locally on localhost:8000
mkdocs serve
```

The C/C++ Doxygen documentation is built automatically by CI on push to the `dev` branch
and deployed to [GitHub Pages](https://ascmitc.github.io/fdl/api/).

## Schema Versions

The `schema/` directory contains JSON Schema definitions for each FDL
specification version:

| Directory | Spec Version |
|-----------|-------------|
| `schema/v0.1/` | Draft / prototype |
| `schema/v1.0/` | First release |
| `schema/v2.0/` | Canvas templates, custom attributes |
| `schema/v2.0.1/` | Current (bug fixes, clarifications) |

The C core validates documents against the appropriate schema version
using JSON Schema Draft 2020-12.

## Checklist For Contributions

### Fork the repo

Please fork the repo on GitHub and clone your fork locally.

`git clone git@github.com:<USERNAME>/fdl.git`

### Create a feature branch

Always work in a feature branch. ***Do not submit Pull Requests directly from "main".***

`git checkout -b my_feature_branch`

### Write code

Please try to follow the style of the project when writing code.
Use type hints and provide docstrings in your code.

### Write tests

All contributions should provide tests for new/updated behavior.
We use [pytest](https://docs.pytest.org/en/stable/) for Python and
[Catch2](https://github.com/catchorg/Catch2) for C++.

### Documentation

Please add/update relevant documentation. We use [mkdocs](https://www.mkdocs.org/) and
[mkdocstrings](https://mkdocstrings.github.io/).

!!! note
    All Python code blocks in the documentation are tested automatically,
    so make sure to write valid, self-contained examples.

### Submitting a Pull Request

Push your feature branch to your repo and open a Pull Request on GitHub.

`git push origin my_feature_branch`
