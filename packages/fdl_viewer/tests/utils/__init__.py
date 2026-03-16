# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Test utilities for FDL Viewer UI integration tests.

Provides helper classes for UI automation, visual comparison, FDL comparison,
image comparison, and scenario configuration.
"""

# Import from fdl packages
from fdl.testing import (
    SCENARIO_CONFIGS,
    FDLComparison,
    ScenarioConfig,
    SourceVariant,
    build_test_params,
    get_scenario_paths,
    get_scenario_test_id,
    get_variant_by_letter,
)
from fdl_imaging.testing import ImageComparison

from .ui_test_helper import UITestHelper
from .visual_comparison import VisualComparison

__all__ = [
    "SCENARIO_CONFIGS",
    "FDLComparison",
    "ImageComparison",
    "ScenarioConfig",
    "SourceVariant",
    "UITestHelper",
    "VisualComparison",
    "build_test_params",
    "get_scenario_paths",
    "get_scenario_test_id",
    "get_variant_by_letter",
]
