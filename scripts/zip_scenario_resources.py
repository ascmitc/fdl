#!/usr/bin/env python3
"""Collect all Scenarios_For_Implementers test resources into a structured zip.

For each scenario/variant the zip contains a self-contained folder with the
template FDL, expected results, and the source files that drive that scenario:

    Scen_1_FitDecision-into-UHD/
        Scen_1_FitDecision-into-UHD-CANVAS-TEMPLATE.fdl
        Results/
            Scen1-RESULT-B_4448x3096_1x_FramingChart.fdl
            Scen1-RESULT-B_4448x3096_1x_FramingChart.001001.exr
            Scen1-RESULT-D_8640x5760_1x_10PercentSafety-FramingChart.fdl
            ...
        SourceFiles/
            B_4448x3096_1x_FramingChart.fdl
            B_4448x3096_1x_FramingChart.tif
            D_8640x5760_1x_10PercentSafety-FramingChart.fdl
            ...

The staging tree is assembled in a temporary directory before zipping so the
archive is clean and reproducible.

Usage:
    python scripts/zip_scenario_resources.py                        # default output
    python scripts/zip_scenario_resources.py -o my_resources.zip    # custom path
    python scripts/zip_scenario_resources.py --dry-run              # list files only
"""

import argparse
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

# Allow running standalone without installing the fdl package — just needs
# the pure-Python testing modules on sys.path.
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "native" / "bindings" / "python"))

from fdl.testing.scenario_config import (  # noqa: E402
    SCENARIO_CONFIGS,
    get_scenario_paths,
)

RESOURCES_DIR = REPO_ROOT / "resources" / "FDL"
SAMPLE_FILES_DIR = RESOURCES_DIR / "Scenarios_For_Implementers"


def stage_scenarios(staging_root: Path) -> list[tuple[Path, str]]:
    """Build a staged directory tree and return (src, arcname) pairs.

    Each scenario gets a folder named after its ``dir_name``.  Inside that
    folder the template FDL sits at the root, result files go under
    ``Results/``, and the source FDL + image go under ``SourceFiles/``.

    Returns a sorted list of (absolute_source_path, zip_arcname) tuples.
    """
    entries: list[tuple[Path, str]] = []

    for config in SCENARIO_CONFIGS.values():
        if config.is_error_test or not config.variants:
            continue

        scenario_dir = staging_root / config.dir_name
        results_dir = scenario_dir / "Results"
        source_files_dir = scenario_dir / "SourceFiles"

        results_dir.mkdir(parents=True, exist_ok=True)
        source_files_dir.mkdir(parents=True, exist_ok=True)

        # --- template (one per scenario, copy once) ---
        first_variant = config.variants[0]
        file_map = get_scenario_paths(SAMPLE_FILES_DIR, config, first_variant)
        template_src = file_map["template"]
        if template_src.exists():
            dst = scenario_dir / template_src.name
            if not dst.exists():
                shutil.copy2(template_src, dst)
                entries.append((dst, f"{config.dir_name}/{template_src.name}"))

        # --- per-variant: source files + results ---
        for variant in config.variants:
            file_map = get_scenario_paths(SAMPLE_FILES_DIR, config, variant)

            # Source FDL
            src_fdl = file_map["source_fdl"]
            if src_fdl.exists():
                dst = source_files_dir / src_fdl.name
                if not dst.exists():
                    shutil.copy2(src_fdl, dst)
                    entries.append((dst, f"{config.dir_name}/SourceFiles/{src_fdl.name}"))

            # Source image (TIF / TIFF)
            src_tif = file_map["source_tif"]
            if src_tif.exists():
                dst = source_files_dir / src_tif.name
                if not dst.exists():
                    shutil.copy2(src_tif, dst)
                    entries.append((dst, f"{config.dir_name}/SourceFiles/{src_tif.name}"))

            # Expected result FDL
            exp_fdl = file_map["expected_fdl"]
            if exp_fdl.exists():
                dst = results_dir / exp_fdl.name
                if not dst.exists():
                    shutil.copy2(exp_fdl, dst)
                    entries.append((dst, f"{config.dir_name}/Results/{exp_fdl.name}"))

            # Expected result EXR
            exp_exr = file_map["expected_exr"]
            if exp_exr.exists():
                dst = results_dir / exp_exr.name
                if not dst.exists():
                    shutil.copy2(exp_exr, dst)
                    entries.append((dst, f"{config.dir_name}/Results/{exp_exr.name}"))

    return sorted(entries, key=lambda e: e[1])


def create_zip(output_path: Path, entries: list[tuple[Path, str]]) -> int:
    """Write *entries* into a zip at *output_path*.  Returns file count."""
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for src, arcname in entries:
            zf.write(src, arcname=arcname)
    return len(entries)


def main() -> None:
    parser = argparse.ArgumentParser(description="Zip all Scenarios_For_Implementers test resources.")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("Scenarios_For_Implementers.zip"),
        help="Output zip file path (default: Scenarios_For_Implementers.zip)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List files that would be added without creating the zip.",
    )
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="fdl_scenario_zip_") as tmpdir:
        staging_root = Path(tmpdir)
        entries = stage_scenarios(staging_root)

        if not entries:
            print("No resource files found.", file=sys.stderr)
            sys.exit(1)

        if args.dry_run:
            print(f"Would add {len(entries)} files to {args.output}:\n")
            for _, arcname in entries:
                print(f"  {arcname}")
        else:
            count = create_zip(args.output, entries)
            size_mb = args.output.stat().st_size / (1024 * 1024)
            print(f"Created {args.output} with {count} files ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
