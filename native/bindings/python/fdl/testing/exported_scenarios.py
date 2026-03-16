# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Exported scenario configurations for FDL tests.

This module stores scenarios exported from the FDL Viewer UI.
These scenarios are automatically merged into SCENARIO_CONFIGS for pytest.

Usage:
    Scenarios are automatically added here when using the "Export Unit Test..."
    button in FDL Viewer. Each scenario captures a specific combination of
    source FDL, image, and template for debugging and regression testing.
"""

from fdl.testing.scenario_config import ScenarioConfig, SourceVariant  # noqa: F401

# Exported scenarios from FDL Viewer UI
# New scenarios will be auto-appended here
EXPORTED_SCENARIO_CONFIGS = {}
