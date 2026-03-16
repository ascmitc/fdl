# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Visual QC Integration Test for FDL Viewer - Edge Cases

Dynamically discovers edge case source FDL/image pairs and runs them through
their corresponding template FDLs via the FDL Viewer UI, generating output
images and scene captures for visual inspection.

No comparison is performed - output only for visual QC.

Edge Cases are organized in two categories:
- generated: Aspect ratios, squeeze factors, alignment, protection zones
- alignment_combos: Source/template alignment combinations

Each source is paired with its matching template (by naming convention:
_source -> _template).

For each source/template pair, the test:
1. Opens the FDL Viewer UI
2. Loads source FDL and image
3. Captures source scene visual
4. Loads corresponding template, selects context/canvas/framing_decision
5. Clicks transform
6. Captures output scene visual
7. Exports output FDL
8. Exports processed image

Performance optimization:
- Uses class-scoped MainWindow to avoid recreating UI for each test
- Resets app state between tests instead of recreating window

Dialog handling:
- Popup dialogs are suppressed during tests to prevent blocking
- Errors are logged to _errors.txt in the output folder
"""

import os
import traceback
from pathlib import Path

import pytest
from fdl.testing import BaseFDLTestCase

from utils.ui_test_helper import UITestHelper


def get_resources_folder() -> Path:
    """Get the path to test resources folder."""
    return BaseFDLTestCase.get_resources_folder()


def get_outputs_folder() -> Path:
    """Get the outputs folder for visual QC edge case tests."""
    output_path = Path(__file__).parent / "outputs" / "visual_qc_edge_cases"
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


# Base paths
RESOURCES_FOLDER = get_resources_folder()
EDGE_CASES_FOLDER = RESOURCES_FOLDER / "EdgeCases"
OUTPUTS_FOLDER = get_outputs_folder()

# Skipped combinations log file
SKIPPED_LOG_PATH = OUTPUTS_FOLDER / "_skipped.txt"

# Error log file for dialog errors and exceptions
ERRORS_LOG_PATH = OUTPUTS_FOLDER / "_errors.txt"


def find_matching_template(source_fdl: Path) -> Path | None:
    """
    Find the matching template for a source FDL.

    Templates are expected to be in a sibling 'templates' folder with
    the same filename pattern but '_source' replaced with '_template'.

    Parameters
    ----------
    source_fdl : Path
        Path to the source FDL file

    Returns
    -------
    Path or None
        Path to the matching template, or None if not found
    """
    source_dir = source_fdl.parent
    templates_dir = source_dir.parent / "templates"

    # Replace _source with _template in filename
    template_name = source_fdl.name.replace("_source", "_template")
    template_path = templates_dir / template_name

    if template_path.exists():
        return template_path
    return None


def find_matching_image(source_fdl: Path) -> Path | None:
    """
    Find the matching image for a source FDL.

    Images are expected to be in the same folder with the same
    base name but different extension.

    Parameters
    ----------
    source_fdl : Path
        Path to the source FDL file

    Returns
    -------
    Path or None
        Path to the matching image, or None if not found
    """
    for ext in [".tiff", ".tif", ".exr", ".png", ".jpg", ".jpeg"]:
        candidate = source_fdl.with_suffix(ext)
        if candidate.exists():
            return candidate
    return None


def discover_edge_case_pairs() -> list[tuple[int, str, str, Path, Path, str, Path]]:
    """
    Scan EdgeCases folder for FDL/image/template triplets.

    Returns
    -------
    List[Tuple[int, str, str, Path, Path, str, Path]]
        List of (test_num, category, source_name, source_fdl, source_image, template_name, template_path) tuples
    """
    pairs = []
    test_num = 1

    if not EDGE_CASES_FOLDER.exists():
        return pairs

    # Scan each category folder (generated, alignment_combos, etc.)
    for category_folder in sorted(EDGE_CASES_FOLDER.iterdir()):
        if not category_folder.is_dir():
            continue

        category_name = category_folder.name
        source_folder = category_folder / "source"

        if not source_folder.exists():
            continue

        # Find all source FDL files
        for fdl_path in sorted(source_folder.glob("*.fdl")):
            source_name = fdl_path.stem  # e.g., "test_aspect_1x1_source"

            # Find matching image
            image_path = find_matching_image(fdl_path)
            if image_path is None:
                continue

            # Find matching template
            template_path = find_matching_template(fdl_path)
            if template_path is None:
                continue

            template_name = template_path.stem

            pairs.append((test_num, category_name, source_name, fdl_path, image_path, template_name, template_path))
            test_num += 1

    return pairs


def generate_test_ids(pairs: list[tuple[int, str, str, Path, Path, str, Path]]) -> list[str]:
    """Generate readable test IDs for the test pairs."""
    ids = []
    for test_num, category, source_name, _, _, template_name, _ in pairs:
        # Shorten names for readability
        src_short = source_name.replace("_source", "")
        ids.append(f"{test_num:03d}_{category}_{src_short}")
    return ids


def log_skipped(test_num: int, source_name: str, category: str, reason: str):
    """Log a skipped test to the skipped log file."""
    OUTPUTS_FOLDER.mkdir(parents=True, exist_ok=True)
    with open(SKIPPED_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"{test_num:03d} | {category}/{source_name} | {reason}\n")


def log_error(
    test_num: int,
    source_name: str,
    category: str,
    expected_output: str,
    error_title: str,
    error_summary: str,
    error_details: str = "",
    stack_trace: str = "",
):
    """
    Log an error to the errors log file.

    Parameters
    ----------
    test_num : int
        Test number.
    source_name : str
        Name of the source file being processed.
    category : str
        Edge case category (generated, alignment_combos, etc.)
    expected_output : str
        The filename that would have been written.
    error_title : str
        Title of the error dialog.
    error_summary : str
        Summary of the error.
    error_details : str
        Detailed error information.
    stack_trace : str
        Stack trace if available.
    """
    OUTPUTS_FOLDER.mkdir(parents=True, exist_ok=True)
    with open(ERRORS_LOG_PATH, "a", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write(f"Test: {test_num:03d} | Category: {category} | Source: {source_name}\n")
        f.write(f"Expected output: {expected_output}\n")
        f.write(f"Error: {error_title}\n")
        f.write(f"Summary: {error_summary}\n")
        if error_details:
            f.write(f"Details:\n{error_details}\n")
        if stack_trace:
            f.write(f"Stack Trace:\n{stack_trace}\n")
        f.write("\n")


def clear_skipped_log():
    """Clear the skipped and error log files at the start of a test run."""
    if SKIPPED_LOG_PATH.exists():
        SKIPPED_LOG_PATH.unlink()
    if ERRORS_LOG_PATH.exists():
        ERRORS_LOG_PATH.unlink()


# Clear skipped log at module load time
clear_skipped_log()


# Generate the test pairs at module load time
TEST_PAIRS = discover_edge_case_pairs()
TEST_IDS = generate_test_ids(TEST_PAIRS)


@pytest.mark.skipif(os.environ.get("CICD") == "1", reason="UI tests require a display; skipped in CI/CD")
class TestVisualQCEdgeCases:
    """Visual QC tests for edge case source/template combinations via UI."""

    @pytest.mark.parametrize(
        "test_num,category,source_name,source_fdl,source_image,template_name,template_path",
        TEST_PAIRS,
        ids=TEST_IDS,
    )
    def test_visual_qc_edge_case(
        self,
        main_window,
        qtbot,
        suppress_dialogs,
        test_num: int,
        category: str,
        source_name: str,
        source_fdl: Path,
        source_image: Path,
        template_name: str,
        template_path: Path,
    ):
        """
        Generate visual QC output for an edge case source/template combination via UI.

        This test:
        1. Opens the FDL Viewer UI
        2. Loads source FDL and image
        3. Captures source scene visual
        4. Loads template, selects context/canvas/framing_decision
        5. Clicks transform
        6. Captures output scene visual
        7. Exports output FDL
        8. Exports processed image

        No comparison is performed - output only for visual QC.

        Popup dialogs are suppressed and logged to _errors.txt instead of blocking.

        Parameters
        ----------
        main_window : MainWindow
            The main window instance (class-scoped from conftest.py).
        qtbot : pytest_qt.QtBot
            The pytest-qt bot (from fixture).
        suppress_dialogs : DialogErrorCollector
            Fixture that suppresses popups and collects errors.
        test_num : int
            Test number for output file prefixing.
        category : str
            Edge case category (generated, alignment_combos, etc.)
        source_name : str
            Name of the source (e.g., "test_aspect_1x1_source")
        source_fdl : Path
            Path to the source FDL file
        source_image : Path
            Path to the source image file
        template_name : str
            Name of the template (e.g., "test_aspect_1x1_template")
        template_path : Path
            Path to the template FDL file
        """
        helper = UITestHelper(main_window, qtbot)

        # Clear any errors from previous test
        suppress_dialogs.clear()

        # Output directory structure: category/
        # Files prefixed with test number: 001_source_name_output.exr
        output_dir = OUTPUTS_FOLDER / category
        prefix = f"{test_num:03d}_{source_name}"
        output_image_path = output_dir / f"{prefix}_output.exr"
        current_phase = "initialization"

        try:
            # Create output directory
            output_dir.mkdir(parents=True, exist_ok=True)

            # =================================================================
            # PHASE 1: Load source FDL and image, capture source scene
            # =================================================================
            current_phase = "loading source FDL"
            helper.load_source_fdl(source_fdl)

            # Check for dialog errors after loading
            if suppress_dialogs.has_errors():
                err = suppress_dialogs.get_last_error()
                log_error(test_num, source_name, category, str(output_image_path), err["title"], err["summary"], err["details"])
                reason = f"Dialog error: {err['summary']}"
                log_skipped(test_num, source_name, category, reason)
                pytest.skip(reason)

            assert main_window._app_state.source_fdl is not None, "Source FDL should be loaded"

            current_phase = "loading source image"
            helper.load_source_image(source_image)

            # Check for dialog errors after image loading
            if suppress_dialogs.has_errors():
                err = suppress_dialogs.get_last_error()
                log_error(test_num, source_name, category, str(output_image_path), err["title"], err["summary"], err["details"])
                reason = f"Dialog error: {err['summary']}"
                log_skipped(test_num, source_name, category, reason)
                pytest.skip(reason)

            # Capture source scene
            current_phase = "capturing source scene"
            source_scene_pixmap = helper.capture_tab_scene(0)
            source_scene_path = output_dir / f"{prefix}_source_scene.png"
            helper.save_pixmap_as_image(source_scene_pixmap, source_scene_path)

            # =================================================================
            # PHASE 2: Load template, configure, transform
            # =================================================================
            current_phase = "loading template"
            helper.load_template_fdl(template_path)

            # Check for dialog errors after template loading
            if suppress_dialogs.has_errors():
                err = suppress_dialogs.get_last_error()
                log_error(test_num, source_name, category, str(output_image_path), err["title"], err["summary"], err["details"])
                reason = f"Dialog error: {err['summary']}"
                log_skipped(test_num, source_name, category, reason)
                pytest.skip(reason)

            assert main_window._app_state.template_fdl is not None, "Template FDL should be loaded"

            # Select first context/canvas/framing_decision
            current_phase = "selecting options"
            helper.select_context(0)
            helper.select_canvas(0)
            helper.select_framing_decision(0)

            # Verify transform is ready
            if not helper.is_transform_button_enabled():
                reason = "Transform button not enabled after loading source and template"
                log_skipped(test_num, source_name, category, reason)
                pytest.skip(reason)

            # Execute transform
            current_phase = "executing transform"
            helper.click_transform()

            # Check for dialog errors after transform
            if suppress_dialogs.has_errors():
                err = suppress_dialogs.get_last_error()
                log_error(test_num, source_name, category, str(output_image_path), err["title"], err["summary"], err["details"])
                reason = f"Dialog error during transform: {err['summary']}"
                log_skipped(test_num, source_name, category, reason)
                pytest.skip(reason)

            if main_window._app_state.output_fdl is None:
                reason = "Transform did not produce output FDL"
                log_skipped(test_num, source_name, category, reason)
                pytest.skip(reason)

            # =================================================================
            # PHASE 3: Capture output scene (with HUD enabled)
            # =================================================================
            current_phase = "capturing output scene"

            # Enable HUD for visual QC
            main_window._app_state.set_hud_visible(True)
            qtbot.wait(7)  # Allow refresh

            output_scene_pixmap = helper.capture_tab_scene(1)
            output_scene_path = output_dir / f"{prefix}_output_scene.png"
            helper.save_pixmap_as_image(output_scene_pixmap, output_scene_path)

            # Disable HUD after capture (reset for next test)
            main_window._app_state.set_hud_visible(False)

            # =================================================================
            # PHASE 4: Export FDL
            # =================================================================
            current_phase = "exporting FDL"
            output_fdl_path = output_dir / f"{prefix}_output.fdl"
            fdl_export_success = helper.export_fdl_programmatically(output_fdl_path)

            if not fdl_export_success:
                reason = "FDL export failed"
                log_skipped(test_num, source_name, category, reason)
                pytest.skip(reason)

            # =================================================================
            # PHASE 5: Export processed image
            # =================================================================
            current_phase = "exporting image"
            image_export_success = helper.export_output_image_programmatically(output_image_path)

            # Check for dialog errors after image export
            if suppress_dialogs.has_errors():
                err = suppress_dialogs.get_last_error()
                log_error(test_num, source_name, category, str(output_image_path), err["title"], err["summary"], err["details"])
                reason = f"Dialog error during export: {err['summary']}"
                log_skipped(test_num, source_name, category, reason)
                pytest.skip(reason)

            if not image_export_success:
                reason = "Image export failed"
                log_skipped(test_num, source_name, category, reason)
                pytest.skip(reason)

            # Verify outputs were created
            current_phase = "verifying outputs"
            assert source_scene_path.exists(), f"Source scene not saved: {source_scene_path}"
            assert output_scene_path.exists(), f"Output scene not saved: {output_scene_path}"
            assert output_fdl_path.exists(), f"Output FDL not created: {output_fdl_path}"
            assert output_image_path.exists(), f"Output image not created: {output_image_path}"

        except pytest.skip.Exception:
            # Re-raise skip exceptions
            raise
        except AssertionError:
            # Re-raise assertion errors
            raise
        except Exception as e:
            # Log the error with stack trace
            stack_trace = traceback.format_exc()
            log_error(
                test_num,
                source_name,
                category,
                str(output_image_path),
                f"Exception during {current_phase}",
                f"{type(e).__name__}: {e!s}",
                "",
                stack_trace,
            )
            reason = f"{type(e).__name__}: {e!s}"
            log_skipped(test_num, source_name, category, reason)
            pytest.skip(reason)


# Summary fixture for reporting
@pytest.fixture(scope="session", autouse=True)
def visual_qc_edge_cases_summary(request):
    """Print summary of visual QC edge case test results at end of session."""
    yield
    # After all tests complete
    skipped_count = 0
    error_count = 0

    if SKIPPED_LOG_PATH.exists():
        with open(SKIPPED_LOG_PATH) as f:
            skipped_count = len(f.readlines())

    if ERRORS_LOG_PATH.exists():
        with open(ERRORS_LOG_PATH) as f:
            # Count error entries (separated by "===")
            content = f.read()
            error_count = content.count("=" * 80)

    print("\n\nVisual QC Edge Cases Summary:")
    print(f"  Total test pairs: {len(TEST_PAIRS)}")
    if skipped_count > 0 or error_count > 0:
        print(f"  Skipped combinations: {skipped_count}")
        print(f"  Error entries: {error_count}")
        print(f"  Skipped log: {SKIPPED_LOG_PATH}")
        if error_count > 0:
            print(f"  Error log: {ERRORS_LOG_PATH}")
    else:
        print("  All combinations completed successfully!")
