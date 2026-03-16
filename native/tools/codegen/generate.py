# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Code generator: reads fdl_api.yaml and dispatches to language-specific generators.

Usage:
    python -m codegen.generate --target python-facade    # idiomatic classes
    python -m codegen.generate --target python-models    # Pydantic models
    python -m codegen.generate --target cpp-raii         # C++ RAII header
    python -m codegen.generate --target node-addon       # Node.js addon
    python -m codegen.generate --target node-facade      # Node.js facade
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .fdl_idl import parse_idl


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate bindings from fdl_api.yaml")
    parser.add_argument("--idl", type=Path, help="Path to fdl_api.yaml")
    parser.add_argument(
        "--target",
        choices=["python-facade", "python-models", "cpp-raii", "node-addon", "node-facade"],
        default="python-facade",
    )
    parser.add_argument("--schema", type=Path, help="Path to JSON Schema (for python-models)")
    parser.add_argument("--output", type=Path, help="Output directory")
    args = parser.parse_args()

    # Default paths relative to repository layout
    repo_root = Path(__file__).parent.parent.parent  # native/tools/codegen -> native/
    idl_path = args.idl or (repo_root / "api" / "fdl_api.yaml")

    if not idl_path.exists():
        print(f"IDL file not found: {idl_path}", file=sys.stderr)
        sys.exit(1)

    header_path = repo_root / "core" / "include" / "fdl" / "fdl_core.h"
    idl = parse_idl(idl_path, header_path=header_path)

    if args.target == "python-facade":
        from . import python_gen

        output_dir = args.output or (repo_root / "bindings" / "python" / "fdl")
        python_gen.generate_facade(idl, output_dir)
    elif args.target == "cpp-raii":
        from . import cpp_gen

        output_dir = args.output or (repo_root / "bindings" / "cpp" / "fdl")
        cpp_gen.generate_raii(idl, output_dir)
    elif args.target == "node-addon":
        from . import node_gen

        output_dir = args.output or (repo_root / "bindings" / "node" / "src" / "addon")
        node_gen.generate_addon(idl, output_dir)
    elif args.target == "python-models":
        from . import python_gen

        schema_path = args.schema or (repo_root.parent / "schema" / "v2.0.1" / "ascfdl.schema.json")
        output_dir = args.output or (repo_root / "bindings" / "python" / "fdl" / "models")
        python_gen.generate_models(schema_path, output_dir)
    elif args.target == "node-facade":
        from . import node_gen

        output_dir = args.output or (repo_root / "bindings" / "node" / "src")
        node_gen.generate_facade(idl, output_dir)


if __name__ == "__main__":
    main()
