# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Pytest fixtures for FDL Viewer tests.
"""

from collections.abc import Generator
from pathlib import Path

import pytest

# Import scenario configuration from central testing module
from fdl.testing import (
    SCENARIO_CONFIGS,
    BaseFDLTestCase,
    ScenarioConfig,
    SourceVariant,
    get_scenario_paths,
    get_variant_by_letter,
)

# Import Qt application
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp() -> Generator[QApplication, None, None]:
    """
    Create a Qt application for the test session.

    Yields
    ------
    QApplication
        The Qt application instance.
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture(scope="class")
def main_window(qapp, app_state):
    """
    Create MainWindow instance for UI testing.

    Uses class scope to reuse window across tests in the same class,
    significantly improving test performance.

    Yields
    ------
    MainWindow
        The main window instance.
    """
    from fdl_viewer.views.main_window import MainWindow

    window = MainWindow()
    window.show()
    yield window
    window.close()


@pytest.fixture
def sample_files_dir() -> Path:
    """
    Get the path to sample FDL files.

    Returns
    -------
    Path
        Path to sample files directory.
    """
    return BaseFDLTestCase.get_resources_folder() / "Scenarios_For_Implementers"


@pytest.fixture
def source_files_dir(sample_files_dir: Path) -> Path:
    """
    Get the path to source FDL files.

    Source files are stored inside each scenario directory.
    We use Scen_1 as the canonical source for shared source files.

    Returns
    -------
    Path
        Path to source files directory.
    """
    # Sources are now in a shared folder at the FDL resources root
    fdl_resources = sample_files_dir.parent
    return fdl_resources / "Original_Source_Files"


@pytest.fixture
def sample_source_fdl_path(source_files_dir: Path) -> Path:
    """
    Get a sample source FDL file path.

    Returns
    -------
    Path
        Path to a sample source FDL file.
    """
    return source_files_dir / "B_4448x3096_1x_FramingChart.fdl"


@pytest.fixture
def scen1_dir(sample_files_dir: Path) -> Path:
    """
    Get the Scen_1 directory.

    Returns
    -------
    Path
        Path to Scen_1 directory.
    """
    return sample_files_dir / "Scen_1_FitDecision-into-UHD"


@pytest.fixture
def scen1_template_path(scen1_dir: Path) -> Path:
    """
    Get the Scen_1 template file path.

    Returns
    -------
    Path
        Path to Scen_1 template file.
    """
    return scen1_dir / "Scen_1_FitDecision-into-UHD-CANVAS-TEMPLATE.fdl"


@pytest.fixture
def scen1_expected_result_path(scen1_dir: Path) -> Path:
    """
    Get the Scen_1 expected result path.

    Returns
    -------
    Path
        Path to Scen_1 expected result file.
    """
    return scen1_dir / "Results" / "Scen1-RESULT-B_4448x3096_1x_FramingChart.fdl"


@pytest.fixture(scope="class")
def app_state():
    """
    Create AppState instance for testing.

    Uses class scope to reuse state across tests in the same class.
    State is reset between tests via reset_app_state fixture.

    Yields
    ------
    AppState
        The AppState instance.
    """
    from fdl_viewer.models.app_state import AppState

    # Reset singleton for testing
    AppState._instance = None
    state = AppState.instance()
    yield state
    # Clean up after all tests in class
    AppState._instance = None


@pytest.fixture
def reset_app_state(app_state, main_window):
    """
    Reset app state and main window before each test to ensure clean state.

    This fixture must be explicitly requested by tests that need UI state reset.
    Tests using mock FDL models should NOT use this fixture as it causes UI
    signal handlers to process the mocks.
    """
    # Clear FDL state
    app_state._source_fdl = None
    app_state._template_fdl = None
    app_state._output_fdl = None

    # Clear selection state
    app_state._selected_context = ""
    app_state._selected_canvas = ""
    app_state._selected_framing = ""

    # Clear template state
    app_state._template_modified = False
    app_state._current_template = None

    # Clear transform results
    app_state._transform_result = None

    # Reset visibility settings to defaults
    app_state._grid_visible = True
    app_state._canvas_visible = True
    app_state._effective_visible = True
    app_state._framing_visible = True
    app_state._protection_visible = True
    app_state._image_underlay_visible = True
    app_state._hud_visible = False  # HUD defaults to OFF

    # Clear MainWindow image state (prevents cross-test contamination)
    main_window._current_image_pixmap = None
    main_window._current_image_width = 0
    main_window._current_image_height = 0
    main_window._current_image_path = ""
    main_window._output_image_pixmap = None
    main_window._output_image_path = ""

    # Clear canvas FDL models BEFORE clearing images
    # This prevents rendering mock FDL models during refresh() calls
    main_window.tab_container.source_tab._canvas.set_fdl_model(None)
    main_window.tab_container.output_tab._canvas.set_fdl_model(None)

    # Clear images from all tabs
    main_window.tab_container.source_tab.clear_image()
    main_window.tab_container.output_tab.clear_image()
    main_window.tab_container.comparison_tab.clear_image()

    yield


@pytest.fixture
def file_controller():
    """
    Create a FileController instance for testing.

    Returns
    -------
    FileController
        A FileController instance.
    """
    from fdl_viewer.controllers.file_controller import FileController

    return FileController()


@pytest.fixture
def transform_controller():
    """
    Create a TransformController instance for testing.

    Returns
    -------
    TransformController
        A TransformController instance.
    """
    from fdl_viewer.controllers.transform_controller import TransformController

    return TransformController()


@pytest.fixture
def selection_controller():
    """
    Create a SelectionController instance for testing.

    Returns
    -------
    SelectionController
        A SelectionController instance.
    """
    from fdl_viewer.controllers.selection_controller import SelectionController

    return SelectionController()


@pytest.fixture
def template_controller():
    """
    Create a TemplateController instance for testing.

    Returns
    -------
    TemplateController
        A TemplateController instance.
    """
    from fdl_viewer.controllers.template_controller import TemplateController

    return TemplateController()


@pytest.fixture
def scen1_paths(sample_files_dir: Path) -> dict[str, Path]:
    """
    Get paths for Scenario 1 test files.

    Returns
    -------
    Dict[str, Path]
        Dictionary with paths to source_files, results, and template.
    """
    scen_dir = sample_files_dir / "Scen_1_FitDecision-into-UHD"
    return {
        "source_files": scen_dir / "Source_Files",
        "results": scen_dir / "Results",
        "template": scen_dir / "Scen_1_FitDecision-into-UHD-CANVAS-TEMPLATE.fdl",
    }


@pytest.fixture
def scen1_source_b(scen1_paths: dict[str, Path]) -> dict[str, Path]:
    """
    Get source B files for Scen_1.

    Returns
    -------
    Dict[str, Path]
        Dictionary with paths to fdl and tif files.
    """
    source_dir = scen1_paths["source_files"]
    return {
        "fdl": source_dir / "B_4448x3096_1x_FramingChart.fdl",
        "tif": source_dir / "B_4448x3096_1x_FramingChart.tif",
    }


@pytest.fixture
def scen1_expected_b(scen1_paths: dict[str, Path]) -> dict[str, Path]:
    """
    Get expected results for source B in Scen_1.

    Returns
    -------
    Dict[str, Path]
        Dictionary with paths to expected fdl and exr files.
    """
    results_dir = scen1_paths["results"]
    return {
        "fdl": results_dir / "Scen1-RESULT-B_4448x3096_1x_FramingChart.fdl",
        "exr": results_dir / "Scen1-RESULT-B_4448x3096_1x_FramingChart.001001.exr",
    }


# =============================================================================
# Parameterized fixtures for Scenarios 1-17
# =============================================================================


@pytest.fixture
def scenario_config(request) -> ScenarioConfig:
    """
    Get scenario configuration from parameterized test.

    The test must be parameterized with (scen_num, variant_letter) tuples
    and use indirect=True for this fixture. Pytest unpacks the tuple,
    so request.param contains just the scenario number.

    Parameters
    ----------
    request : pytest.FixtureRequest
        Pytest request object containing the scenario number.

    Returns
    -------
    ScenarioConfig
        Configuration for the scenario.
    """
    scen_num = request.param
    return SCENARIO_CONFIGS[scen_num]


@pytest.fixture
def variant_config(request, scenario_config: ScenarioConfig) -> SourceVariant:
    """
    Get variant configuration from parameterized test.

    The test must be parameterized with (scen_num, variant_letter) tuples
    and use indirect=True for this fixture. Pytest unpacks the tuple,
    so request.param contains just the variant letter.

    Parameters
    ----------
    request : pytest.FixtureRequest
        Pytest request object containing the variant letter.
    scenario_config : ScenarioConfig
        The scenario configuration.

    Returns
    -------
    SourceVariant
        Configuration for the variant.
    """
    letter = request.param
    variant = get_variant_by_letter(scenario_config, letter)
    if variant is None:
        raise ValueError(f"Variant '{letter}' not found in scenario {scenario_config.number}")
    return variant


@pytest.fixture
def scenario_paths(sample_files_dir: Path, scenario_config: ScenarioConfig, variant_config: SourceVariant) -> dict[str, Path]:
    """
    Get all file paths for the current scenario/variant.

    Parameters
    ----------
    sample_files_dir : Path
        Root path to Scenarios_For_Implementers.
    scenario_config : ScenarioConfig
        Scenario configuration.
    variant_config : SourceVariant
        Variant configuration.

    Returns
    -------
    Dict[str, Path]
        Dictionary with keys: template, source_fdl, source_tif, expected_fdl, expected_exr.
    """
    return get_scenario_paths(sample_files_dir, scenario_config, variant_config)


# =============================================================================
# Dialog suppression fixture for automated testing
# =============================================================================


class DialogErrorCollector:
    """
    Collects errors that would normally show in dialogs.

    Used during automated testing to prevent blocking popups
    and instead collect errors for logging.
    """

    def __init__(self):
        self.errors = []

    def add_error(self, title: str, summary: str, details: str = ""):
        """Record an error that would have been shown in a dialog."""
        self.errors.append(
            {
                "title": title,
                "summary": summary,
                "details": details,
            }
        )

    def clear(self):
        """Clear collected errors."""
        self.errors.clear()

    def has_errors(self) -> bool:
        """Check if any errors were collected."""
        return len(self.errors) > 0

    def get_last_error(self):
        """Get the most recent error, or None."""
        return self.errors[-1] if self.errors else None


@pytest.fixture
def suppress_dialogs(monkeypatch):
    """
    Suppress all popup dialogs during testing and collect errors instead.

    This fixture patches ErrorDialog.show_error and QMessageBox methods
    to prevent blocking modal dialogs during automated tests. Errors are
    collected and can be retrieved from the returned collector.

    Yields
    ------
    DialogErrorCollector
        Collector object containing any errors that would have been shown.
    """
    from PySide6.QtWidgets import QMessageBox

    collector = DialogErrorCollector()

    # Patch ErrorDialog.show_error
    def mock_show_error(parent, title="Error", summary="An error occurred", details=""):
        collector.add_error(title, summary, details)

    monkeypatch.setattr("fdl_viewer.views.common.error_dialog.ErrorDialog.show_error", mock_show_error)

    # Also patch it on the main_window import path
    monkeypatch.setattr("fdl_viewer.views.main_window.ErrorDialog.show_error", mock_show_error)

    # Patch QMessageBox static methods to not block
    def mock_message_box(parent, title, message):
        collector.add_error(title, message, "")
        return QMessageBox.StandardButton.Ok

    def mock_critical(parent, title, message):
        collector.add_error(f"CRITICAL: {title}", message, "")
        return QMessageBox.StandardButton.Ok

    def mock_information(parent, title, message):
        # Information dialogs are not errors, just log them
        return QMessageBox.StandardButton.Ok

    def mock_about(parent, title, message):
        return None

    monkeypatch.setattr(QMessageBox, "critical", mock_critical)
    monkeypatch.setattr(QMessageBox, "information", mock_information)
    monkeypatch.setattr(QMessageBox, "about", mock_about)
    monkeypatch.setattr(QMessageBox, "warning", mock_message_box)

    yield collector
