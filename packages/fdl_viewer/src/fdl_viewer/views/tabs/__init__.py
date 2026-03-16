# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Tab widgets package for FDL Viewer.
"""

from fdl_viewer.views.tabs.comparison_tab import ComparisonTab
from fdl_viewer.views.tabs.details_tab import DetailsTab
from fdl_viewer.views.tabs.output_tab import OutputTab
from fdl_viewer.views.tabs.source_tab import SourceTab
from fdl_viewer.views.tabs.tab_container import TabContainer

__all__ = [
    "ComparisonTab",
    "DetailsTab",
    "OutputTab",
    "SourceTab",
    "TabContainer",
]
