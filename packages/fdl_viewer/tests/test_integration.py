# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Integration tests for FDL Viewer.

Tests the end-to-end workflow using controllers.
Scenario-specific transformation tests are in test_ui_scenarios.py which provides
more comprehensive coverage with visual verification through the actual UI.
"""

import pytest


class TestEndToEndWorkflow:
    """
    End-to-end workflow tests.

    Tests the complete workflow from loading files to transformation.
    """

    def test_load_transform_save_workflow(
        self,
        qapp,
        file_controller,
        transform_controller,
        sample_source_fdl_path,
        scen1_template_path,
        tmp_path,
    ):
        """Test complete load-transform-save workflow."""
        if not sample_source_fdl_path.exists() or not scen1_template_path.exists():
            pytest.skip("Sample files not found")

        from PySide6.QtTest import QSignalSpy

        from fdl_viewer.models.fdl_model import FDLModel

        # Step 1: Load source FDL
        # file_loaded signal emits (path, FDLModel)
        load_spy = QSignalSpy(file_controller.file_loaded)
        file_controller.load_fdl(str(sample_source_fdl_path))
        assert load_spy.count() == 1
        source_model = load_spy.at(0)[1]  # Index 1 is FDLModel

        # Step 2: Load template FDL
        file_controller.load_fdl(str(scen1_template_path))
        assert load_spy.count() == 2
        template_model = load_spy.at(1)[1]  # Index 1 is FDLModel

        # Step 3: Get selections
        context = source_model.fdl.contexts[0]
        canvas = context.canvases[0]
        framing = canvas.framing_decisions[0]
        template = template_model.fdl.canvas_templates[0]

        # Step 4: Apply template
        transform_spy = QSignalSpy(transform_controller.transform_completed)
        transform_controller.apply_template(
            source_fdl=source_model.fdl,
            template=template,
            context_label=context.label,
            canvas_id=canvas.id,
            framing_decision_id=framing.id,
        )
        assert transform_spy.count() == 1
        result = transform_spy.at(0)[0]

        # Step 5: Create output model and save
        output_fdl = result.fdl
        output_model = FDLModel(output_fdl, None)

        output_path = tmp_path / "output.fdl"
        save_spy = QSignalSpy(file_controller.file_saved)
        file_controller.save_fdl(output_model, str(output_path))

        assert save_spy.count() == 1
        assert output_path.exists()

        # Step 6: Verify saved file can be loaded
        file_controller.load_fdl(str(output_path))
        assert load_spy.count() == 3
        reloaded_model = load_spy.at(2)[1]  # Index 1 is FDLModel
        assert reloaded_model.fdl is not None
