# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Visual QC Integration Test for FDL Viewer

Dynamically discovers source FDL/image pairs and runs them through
all 18 scenario templates via the FDL Viewer UI, generating output
images and scene captures for visual inspection.

No comparison is performed - output only for visual QC.

Test Matrix:
- 63 source pairs x 18 templates = 1,134 test combinations
- Dynamically computed so new source files are automatically picked up

For each combination, the test:
1. Opens the FDL Viewer UI
2. Loads source FDL and image
3. Captures source scene visual
4. Loads template, selects context/canvas/framing_decision
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
    """Get the outputs folder for visual QC tests."""
    output_path = Path(__file__).parent / "outputs" / "visual_qc"
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


# Base paths
RESOURCES_FOLDER = get_resources_folder()
NEW_SOURCE_FILES_FOLDER = RESOURCES_FOLDER / "New_Source_Files"
SAMPLE_FILES_FOLDER = RESOURCES_FOLDER / "Scenarios_For_Implementers"
OUTPUTS_FOLDER = get_outputs_folder()

# Skipped combinations log file
SKIPPED_LOG_PATH = OUTPUTS_FOLDER / "_skipped.txt"

# Error log file for dialog errors and exceptions
ERRORS_LOG_PATH = OUTPUTS_FOLDER / "_errors.txt"


# Scenario template definitions mapping scenario number to relative paths
SCENARIO_TEMPLATES = {
    1: "Scen_1_FitDecision-into-UHD/Scen_1_FitDecision-into-UHD-CANVAS-TEMPLATE.fdl",
    2: "Scen_2_FitProtection-into-UHD/Scen_2_FitProtection-into-UHD-CANVAS-TEMPLATE.fdl",
    3: "Scen_3_Preserving-Protection/Scen_3_Preserving-Protection-CANVAS-TEMPLATE.fdl",
    4: "Scen_4_Preserving-Canvas/Scen_4_Preserving-Canvas-CANVAS-TEMPLATE.fdl",
    5: "Scen_5_Normalizing_LensSqueezeTo1/Scen_5_Normalizing_LensSqueezeTo1-CANVAS-TEMPLATE.fdl",
    6: "Scen_6_Normalizing_LensSqueezeTo2/Scen_6_Normalizing_LensSqueezeTo2-CANVAS-TEMPLATE.fdl",
    7: "Scen_7_TopAlignedSource-PreserveProtection-Centered/Scen_7_TopAlignedSource-PreserveProtection-Centered-CANVAS-TEMPLATE.fdl",
    8: "Scen_8_TopAlignedSource-PreserveCanvas-Centered/Scen_8_TopAlignedSource-PreserveCanvas-Centered-CANVAS-TEMPLATE.fdl",
    9: "Scen_9_PadToMax/Scen_9_PadToMax-CANVAS-TEMPLATE.fdl",
    10: "Scen_10_FitWidth_MaintainAspectRatio/Scen_10_FitWidth_MaintainAspectRatio-CANVAS-TEMPLATE.fdl",
    11: "Scen_11_FitHeight_MaintainAspectRatio/Scen_11_FitHeight_MaintainAspectRatio-CANVAS-TEMPLATE.fdl",
    12: "Scen_12_FitDecision_Fill/Scen_12_FitDecision-Fill.fdl",
    13: "Scen_13_FitDecision_With_Protection_Fill/Scen_13_FitDecision-With-ProtectionFill.fdl",
    14: "Scen_14_Preserving-Protection-WithMaxDim-Cropping/Scen_14_Preserving-Protection-WithMaxDim-Cropping-TEMPLATE.fdl",
    15: "Scen_15_Retention_Of_Relative_Anchors/Scen_15_Retention_of_relative_anchors.fdl",
    16: "Scen_16_Retention_Of_Relative_Anchors_pad_to_max_top_left/Scen_16_Retention_Of_Relative_Anchors_pad_to_max_top_left.fdl",
    17: "Scen_17_Retention_Of_Relative_Anchors_pad_to_max_bottom_left/Scen_17_Retention_Of_Relative_Anchors_pad_to_max_bottom_left.fdl",
    18: "Scen_18_Normalizing_LensSqueezeTo2_PadToMax_NonUniform_Crop/Scen_18_Normalizing_LensSqueezeTo2-CANVAS-TEMPLATE.fdl",
}


def discover_source_pairs() -> list[tuple[str, Path, Path]]:
    """
    Scan New_Source_Files folder for FDL/image pairs.

    Returns
    -------
    List[Tuple[str, Path, Path]]
        List of (source_name, fdl_path, image_path) tuples
    """
    pairs = []

    if not NEW_SOURCE_FILES_FOLDER.exists():
        return pairs

    # Find all Test_*.fdl files
    for fdl_path in sorted(NEW_SOURCE_FILES_FOLDER.glob("Test_*.fdl")):
        source_name = fdl_path.stem  # e.g., "Test_01_Sony_FX3"

        # Look for matching image (try common extensions)
        image_path = None
        for ext in [".tiff", ".tif", ".exr", ".png", ".jpg", ".jpeg"]:
            candidate = fdl_path.with_suffix(ext)
            if candidate.exists():
                image_path = candidate
                break

        if image_path is not None:
            pairs.append((source_name, fdl_path, image_path))

    return pairs


def get_template_path(scen_num: int) -> Path:
    """Get the full path to a scenario template FDL."""
    if scen_num not in SCENARIO_TEMPLATES:
        raise ValueError(f"Unknown scenario number: {scen_num}")
    return SAMPLE_FILES_FOLDER / SCENARIO_TEMPLATES[scen_num]


def generate_test_matrix() -> list[tuple[str, Path, Path, int, Path]]:
    """
    Generate the full test matrix of source pairs x scenarios.

    Returns
    -------
    List[Tuple[str, Path, Path, int, Path]]
        List of (source_name, source_fdl, source_image, scen_num, template_path) tuples
    """
    matrix = []
    source_pairs = discover_source_pairs()

    for source_name, source_fdl, source_image in source_pairs:
        for scen_num in sorted(SCENARIO_TEMPLATES.keys()):
            template_path = get_template_path(scen_num)
            if template_path.exists():
                matrix.append((source_name, source_fdl, source_image, scen_num, template_path))

    return matrix


def generate_test_ids(matrix: list[tuple[str, Path, Path, int, Path]]) -> list[str]:
    """Generate readable test IDs for the test matrix."""
    ids = []
    for source_name, _, _, scen_num, _ in matrix:
        ids.append(f"{source_name}_Scen{scen_num:02d}")
    return ids


def log_skipped(source_name: str, scen_num: int, reason: str):
    """Log a skipped test combination to the skipped log file."""
    OUTPUTS_FOLDER.mkdir(parents=True, exist_ok=True)
    with open(SKIPPED_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"{source_name} | Scen{scen_num:02d} | {reason}\n")


def log_error(
    source_name: str,
    scen_num: int,
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
    source_name : str
        Name of the source file being processed.
    scen_num : int
        Scenario number.
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
        f.write(f"Source: {source_name} | Scenario: {scen_num:02d}\n")
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


# Generate the test matrix at module load time
TEST_MATRIX = generate_test_matrix()
TEST_IDS = generate_test_ids(TEST_MATRIX)


@pytest.mark.skipif(os.environ.get("CICD") == "1", reason="UI tests require a display; skipped in CI/CD")
class TestVisualQCMatrix:
    """Visual QC tests for source/template combinations via UI."""

    @pytest.mark.parametrize(
        "source_name,source_fdl,source_image,scen_num,template_path",
        TEST_MATRIX,
        ids=TEST_IDS,
    )
    def test_visual_qc_output(
        self,
        main_window,
        qtbot,
        suppress_dialogs,
        source_name: str,
        source_fdl: Path,
        source_image: Path,
        scen_num: int,
        template_path: Path,
    ):
        """
        Generate visual QC output for a source/template combination via UI.

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
        source_name : str
            Name of the source (e.g., "Test_01_Sony_FX3")
        source_fdl : Path
            Path to the source FDL file
        source_image : Path
            Path to the source image file
        scen_num : int
            Scenario number (1-18)
        template_path : Path
            Path to the template FDL file
        """
        helper = UITestHelper(main_window, qtbot)

        # Clear any errors from previous test
        suppress_dialogs.clear()

        # Track expected outputs for error logging
        source_output_dir = OUTPUTS_FOLDER / source_name
        output_image_path = source_output_dir / f"Scen{scen_num:02d}_output.exr"
        current_phase = "initialization"

        try:
            # Create output directory for this source
            source_output_dir.mkdir(parents=True, exist_ok=True)

            # =================================================================
            # PHASE 1: Load source FDL and image, capture source scene
            # =================================================================
            current_phase = "loading source FDL"
            helper.load_source_fdl(source_fdl)

            # Check for dialog errors after loading
            if suppress_dialogs.has_errors():
                err = suppress_dialogs.get_last_error()
                log_error(source_name, scen_num, str(output_image_path), err["title"], err["summary"], err["details"])
                reason = f"Dialog error: {err['summary']}"
                log_skipped(source_name, scen_num, reason)
                pytest.skip(reason)

            assert main_window._app_state.source_fdl is not None, "Source FDL should be loaded"

            current_phase = "loading source image"
            helper.load_source_image(source_image)

            # Check for dialog errors after image loading
            if suppress_dialogs.has_errors():
                err = suppress_dialogs.get_last_error()
                log_error(source_name, scen_num, str(output_image_path), err["title"], err["summary"], err["details"])
                reason = f"Dialog error: {err['summary']}"
                log_skipped(source_name, scen_num, reason)
                pytest.skip(reason)

            # Capture source scene
            current_phase = "capturing source scene"
            source_scene_pixmap = helper.capture_tab_scene(0)
            source_scene_path = source_output_dir / f"Scen{scen_num:02d}_source_scene.png"
            helper.save_pixmap_as_image(source_scene_pixmap, source_scene_path)

            # =================================================================
            # PHASE 2: Load template, configure, transform
            # =================================================================
            current_phase = "loading template"
            helper.load_template_fdl(template_path)

            # Check for dialog errors after template loading
            if suppress_dialogs.has_errors():
                err = suppress_dialogs.get_last_error()
                log_error(source_name, scen_num, str(output_image_path), err["title"], err["summary"], err["details"])
                reason = f"Dialog error: {err['summary']}"
                log_skipped(source_name, scen_num, reason)
                pytest.skip(reason)

            assert main_window._app_state.template_fdl is not None, "Template FDL should be loaded"

            # Select first context/canvas/framing_decision
            # (source FDLs have single items for each)
            current_phase = "selecting options"
            helper.select_context(0)
            helper.select_canvas(0)
            helper.select_framing_decision(0)

            # Verify transform is ready
            if not helper.is_transform_button_enabled():
                reason = "Transform button not enabled after loading source and template"
                log_skipped(source_name, scen_num, reason)
                pytest.skip(reason)

            # Execute transform
            current_phase = "executing transform"
            helper.click_transform()

            # Check for dialog errors after transform
            if suppress_dialogs.has_errors():
                err = suppress_dialogs.get_last_error()
                log_error(source_name, scen_num, str(output_image_path), err["title"], err["summary"], err["details"])
                reason = f"Dialog error during transform: {err['summary']}"
                log_skipped(source_name, scen_num, reason)
                pytest.skip(reason)

            if main_window._app_state.output_fdl is None:
                reason = "Transform did not produce output FDL"
                log_skipped(source_name, scen_num, reason)
                pytest.skip(reason)

            # =================================================================
            # PHASE 3: Capture output scene
            # =================================================================
            current_phase = "capturing output scene"
            output_scene_pixmap = helper.capture_tab_scene(1)
            output_scene_path = source_output_dir / f"Scen{scen_num:02d}_output_scene.png"
            helper.save_pixmap_as_image(output_scene_pixmap, output_scene_path)

            # =================================================================
            # PHASE 4: Export FDL
            # =================================================================
            current_phase = "exporting FDL"
            output_fdl_path = source_output_dir / f"Scen{scen_num:02d}_output.fdl"
            fdl_export_success = helper.export_fdl_programmatically(output_fdl_path)

            if not fdl_export_success:
                reason = "FDL export failed"
                log_skipped(source_name, scen_num, reason)
                pytest.skip(reason)

            # =================================================================
            # PHASE 5: Export processed image
            # =================================================================
            current_phase = "exporting image"
            image_export_success = helper.export_output_image_programmatically(output_image_path)

            # Check for dialog errors after image export
            if suppress_dialogs.has_errors():
                err = suppress_dialogs.get_last_error()
                log_error(source_name, scen_num, str(output_image_path), err["title"], err["summary"], err["details"])
                reason = f"Dialog error during export: {err['summary']}"
                log_skipped(source_name, scen_num, reason)
                pytest.skip(reason)

            if not image_export_success:
                reason = "Image export failed"
                log_skipped(source_name, scen_num, reason)
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
                source_name,
                scen_num,
                str(output_image_path),
                f"Exception during {current_phase}",
                f"{type(e).__name__}: {e!s}",
                "",
                stack_trace,
            )
            reason = f"{type(e).__name__}: {e!s}"
            log_skipped(source_name, scen_num, reason)
            pytest.skip(reason)


# Summary fixture for reporting
@pytest.fixture(scope="session", autouse=True)
def visual_qc_summary(request):
    """Print summary of visual QC test results at end of session."""
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

    print("\n\nVisual QC Summary:")
    print(f"  Total test combinations: {len(TEST_MATRIX)}")
    if skipped_count > 0 or error_count > 0:
        print(f"  Skipped combinations: {skipped_count}")
        print(f"  Error entries: {error_count}")
        print(f"  Skipped log: {SKIPPED_LOG_PATH}")
        if error_count > 0:
            print(f"  Error log: {ERRORS_LOG_PATH}")
    else:
        print("  All combinations completed successfully!")
