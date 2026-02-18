# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Unit test export controller for FDL Viewer.

Handles exporting the current transformation as a unit test scenario.
"""

import re
import shutil
from pathlib import Path

from fdl import FDL, CanvasTemplate, write_to_file
from fdl.testing.base import BaseFDLTestCase
from fdl.testing.scenario_config import SCENARIO_CONFIGS
from PySide6.QtCore import QObject, Signal


class UnitTestExportController(QObject):
    """
    Controller for exporting unit test scenarios.

    Handles copying FDL files and images to the test resources directory
    and generating ScenarioConfig code for integration with pytest.

    Attributes
    ----------
    export_completed : Signal
        Emitted when export completes successfully (scenario_number, config_code).
    error_occurred : Signal
        Emitted when an error occurs (message).
    """

    export_completed = Signal(int, str)  # scenario_number, config_code
    error_occurred = Signal(str)

    # Base path for EdgeCases/exported (resolves via fdl package test resources)
    DEFAULT_EXPORT_BASE = BaseFDLTestCase.get_resources_folder() / "EdgeCases" / "exported"

    def __init__(self, parent: QObject | None = None) -> None:
        """
        Initialize the UnitTestExportController.

        Parameters
        ----------
        parent : QObject, optional
            Parent QObject for Qt ownership.
        """
        super().__init__(parent)

    def get_next_scenario_number(self) -> int:
        """
        Find the maximum existing scenario number and return the next one.

        Scans SCENARIO_CONFIGS and exported scenarios file to find the highest
        scenario number, then returns that + 1.

        Returns
        -------
        int
            The next available scenario number.
        """
        max_number = 0

        # Check existing SCENARIO_CONFIGS
        for num in SCENARIO_CONFIGS.keys():
            if num > max_number:
                max_number = num

        # Also check the exported_scenarios.py file for any manually added scenarios
        import fdl.testing.exported_scenarios as _exported_mod

        exported_scenarios_path = Path(_exported_mod.__file__)
        if exported_scenarios_path.exists():
            content = exported_scenarios_path.read_text(encoding="utf-8")
            # Find all scenario numbers in the file
            matches = re.findall(r"(\d+):\s*ScenarioConfig\(", content)
            for match in matches:
                num = int(match)
                if num > max_number:
                    max_number = num

        return max_number + 1

    def get_default_export_path(self) -> str:
        """
        Get the default export path for unit test files.

        Returns
        -------
        str
            Path to the EdgeCases/exported directory.
        """
        return str(self.DEFAULT_EXPORT_BASE)

    def export_unit_test(
        self,
        source_fdl: FDL,
        _source_fdl_path: str,
        template: CanvasTemplate,
        template_fdl: FDL,
        output_fdl: FDL,
        source_image_path: str | None,
        context_label: str,
        canvas_id: str,
        framing_id: str,
        input_dims: tuple[float, float],
        export_config: dict,
    ) -> bool:
        """
        Export the current transformation as a unit test scenario.

        Parameters
        ----------
        source_fdl : FDL
            The source FDL object.
        source_fdl_path : str
            Path to the original source FDL file.
        template : CanvasTemplate
            The template used for transformation.
        template_fdl : FDL
            The FDL containing the template.
        output_fdl : FDL
            The transformed output FDL.
        source_image_path : str, optional
            Path to the source image (if any).
        context_label : str
            The selected context label.
        canvas_id : str
            The selected canvas ID.
        framing_id : str
            The selected framing decision ID.
        input_dims : Tuple[float, float]
            Source image dimensions (width, height).
        export_config : dict
            Configuration from ExportUnitTestDialog.get_export_config().

        Returns
        -------
        bool
            True if export was successful.
        """
        try:
            scenario_number = export_config["scenario_number"]
            base_name = export_config["base_name"]
            export_path = Path(export_config["export_path"])
            include_image = export_config["include_image"]

            # Create directory structure
            source_dir = export_path / "source"
            templates_dir = export_path / "templates"
            results_dir = export_path / "Results"

            source_dir.mkdir(parents=True, exist_ok=True)
            templates_dir.mkdir(parents=True, exist_ok=True)
            results_dir.mkdir(parents=True, exist_ok=True)

            # Save source FDL
            source_fdl_dest = source_dir / f"{base_name}_source.fdl"
            write_to_file(source_fdl, source_fdl_dest)

            # Copy source image if requested
            if include_image and source_image_path:
                source_image_src = Path(source_image_path)
                if source_image_src.exists():
                    # Preserve original extension or default to .tiff
                    ext = source_image_src.suffix.lower()
                    if ext not in [".tif", ".tiff", ".exr", ".png", ".jpg", ".jpeg"]:
                        ext = ".tiff"
                    source_image_dest = source_dir / f"{base_name}_source{ext}"
                    shutil.copy2(source_image_src, source_image_dest)

            # Save template FDL
            template_fdl_dest = templates_dir / f"{base_name}_template.fdl"
            write_to_file(template_fdl, template_fdl_dest)

            # Save expected result FDL
            result_fdl_name = f"Scen{scenario_number}-RESULT-{base_name}.fdl"
            result_fdl_dest = results_dir / result_fdl_name
            write_to_file(output_fdl, result_fdl_dest)

            # Generate scenario config code
            config_code = self.generate_scenario_config_code(
                scenario_number=scenario_number,
                scenario_name=export_config["scenario_name"],
                base_name=base_name,
                context_label=context_label,
                canvas_label=canvas_id,
                framing_id=framing_id,
                input_dims=input_dims,
                template_label=template.label or template.id,
            )

            # Append to exported_scenarios.py
            self._append_to_exported_scenarios(scenario_number, config_code)

            self.export_completed.emit(scenario_number, config_code)
            return True

        except Exception as e:
            self.error_occurred.emit(f"Export failed: {e}")
            return False

    def generate_scenario_config_code(
        self,
        scenario_number: int,
        scenario_name: str,
        base_name: str,
        context_label: str,
        canvas_label: str,
        framing_id: str,
        input_dims: tuple[float, float],
        template_label: str,
    ) -> str:
        """
        Generate Python code for a ScenarioConfig entry.

        Parameters
        ----------
        scenario_number : int
            The scenario number.
        scenario_name : str
            Human-readable scenario name.
        base_name : str
            Base filename for exported files.
        context_label : str
            The context label.
        canvas_label : str
            The canvas label/ID.
        framing_id : str
            The framing decision ID.
        input_dims : Tuple[float, float]
            Input dimensions (width, height).
        template_label : str
            The template label.

        Returns
        -------
        str
            Python code for the ScenarioConfig entry.
        """
        input_w, input_h = input_dims

        code = f'''    {scenario_number}: ScenarioConfig(
        number={scenario_number},
        name="{scenario_name}",
        dir_name="EdgeCases/exported",
        template_filename="{base_name}_template.fdl",
        variants=[
            SourceVariant(
                letter="{base_name.upper()}",
                fdl_basename="{base_name}_source",
                input_dims=({input_w}, {input_h}),
                context_label="{context_label}",
                canvas_label="{canvas_label}",
                test_name_suffix="{scenario_name}",
            ),
        ],
        result_pattern="Scen{scenario_number}-RESULT-{{variant}}.fdl",
        context_label="{context_label}",
        canvas_label="{canvas_label}",
        template_label="{template_label}",
        framing_intent_id="{framing_id}",
        context_creator="Exported from FDL Viewer",
        custom_template_path="EdgeCases/exported/templates",
        custom_source_dir="EdgeCases/exported/source",
        custom_results_dir="EdgeCases/exported/Results",
    ),'''

        return code

    def _append_to_exported_scenarios(self, scenario_number: int, config_code: str) -> None:
        """
        Append a new scenario config to the exported_scenarios.py file.

        Parameters
        ----------
        scenario_number : int
            The scenario number.
        config_code : str
            The Python code for the scenario config.
        """
        import fdl.testing.exported_scenarios as _exported_mod

        exported_scenarios_path = Path(_exported_mod.__file__)

        if not exported_scenarios_path.exists():
            # File doesn't exist, will be created separately
            return

        content = exported_scenarios_path.read_text(encoding="utf-8")

        # Find the EXPORTED_SCENARIO_CONFIGS dict and insert before the closing brace
        # Pattern: find "EXPORTED_SCENARIO_CONFIGS = {" followed by content and "}"
        pattern = r"(EXPORTED_SCENARIO_CONFIGS\s*=\s*\{)(.*?)(\})"
        match = re.search(pattern, content, re.DOTALL)

        if match:
            prefix = match.group(1)
            existing_content = match.group(2)
            suffix = match.group(3)

            # Check if this scenario number already exists
            if f"    {scenario_number}:" in existing_content:
                # Already exists, don't add duplicate
                return

            # Add new config
            if existing_content.strip():
                # There's existing content, add after it
                new_content = f"{existing_content}\n{config_code}\n"
            else:
                # Empty dict, add the config
                new_content = f"\n{config_code}\n"

            new_file_content = content[: match.start()] + prefix + new_content + suffix + content[match.end() :]
            exported_scenarios_path.write_text(new_file_content, encoding="utf-8")
