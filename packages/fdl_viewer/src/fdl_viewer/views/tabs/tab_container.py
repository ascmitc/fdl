# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Tab container for FDL Viewer.

Contains the main tabbed interface with Source, Output, Comparison, and Details tabs.
"""

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QTabWidget, QWidget

from fdl_viewer.models.app_state import AppState
from fdl_viewer.views.tabs.comparison_tab import ComparisonTab
from fdl_viewer.views.tabs.details_tab import DetailsTab
from fdl_viewer.views.tabs.output_tab import OutputTab
from fdl_viewer.views.tabs.source_tab import SourceTab


class TabContainer(QTabWidget):
    """
    Container for the main content tabs.

    Contains:
    - Source: Visualization of source FDL
    - Output: Visualization of transformed output
    - Comparison: Side-by-side or slider comparison
    - Details: Transformation metrics and JSON export

    Parameters
    ----------
    parent : QWidget, optional
        Parent widget.

    Attributes
    ----------
    tab_changed : Signal
        Emitted when the active tab changes (index).
    """

    tab_changed = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._app_state = AppState.instance()
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Set up the tabs."""
        # Source tab
        self._source_tab = SourceTab()
        self.addTab(self._source_tab, "Source")

        # Output tab
        self._output_tab = OutputTab()
        self.addTab(self._output_tab, "Output")

        # Comparison tab
        self._comparison_tab = ComparisonTab()
        self.addTab(self._comparison_tab, "Comparison")

        # Details tab
        self._details_tab = DetailsTab()
        self.addTab(self._details_tab, "Details")

        # Tab styles come from base stylesheet (QTabWidget, QTabBar)

    def _connect_signals(self) -> None:
        """Connect signals."""
        self.currentChanged.connect(self._on_tab_changed)

        # App state
        self._app_state.source_fdl_changed.connect(self._on_source_changed)
        self._app_state.output_fdl_changed.connect(self._on_output_changed)

    @Slot(int)
    def _on_tab_changed(self, index: int) -> None:
        """Handle tab change."""
        self._app_state.set_active_tab(index)
        self.tab_changed.emit(index)

    @Slot(object)
    def _on_source_changed(self, model) -> None:
        """Handle source FDL change."""
        self._source_tab.set_fdl_model(model)
        self._comparison_tab.set_source_model(model)

    @Slot(object)
    def _on_output_changed(self, model) -> None:
        """Handle output FDL change."""
        self._output_tab.set_fdl_model(model)
        self._comparison_tab.set_output_model(model)
        self._details_tab.set_output_model(model)

    @property
    def source_tab(self) -> SourceTab:
        """Get the source tab."""
        return self._source_tab

    @property
    def output_tab(self) -> OutputTab:
        """Get the output tab."""
        return self._output_tab

    @property
    def comparison_tab(self) -> ComparisonTab:
        """Get the comparison tab."""
        return self._comparison_tab

    @property
    def details_tab(self) -> DetailsTab:
        """Get the details tab."""
        return self._details_tab
