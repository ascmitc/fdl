# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Settings management for FDL Viewer.

Provides a wrapper around QSettings for persistent application settings.
"""

from typing import Any, Optional

from PySide6.QtCore import QByteArray, QSettings


class Settings:
    """
    Wrapper around QSettings for FDL Viewer settings.

    Provides type-safe access to application settings with default values.

    Examples
    --------
    >>> settings = Settings()
    >>> settings.set_window_geometry(window.saveGeometry())
    >>> geometry = settings.get_window_geometry()
    """

    _instance: Optional["Settings"] = None

    # Setting keys
    WINDOW_GEOMETRY = "window/geometry"
    WINDOW_STATE = "window/state"
    SIDEBAR_WIDTH = "window/sidebar_width"
    SIDEBAR_COLLAPSED = "window/sidebar_collapsed"
    ACTIVE_TAB = "window/active_tab"
    GRID_VISIBLE = "canvas/grid_visible"
    IMAGE_OPACITY = "canvas/image_opacity"
    LAST_DIRECTORY = "files/last_directory"
    IMAGE_FILTER = "processing/image_filter"
    AUTO_PROCESS_IMAGE = "processing/auto_process"

    def __init__(self) -> None:
        """Initialize the Settings wrapper."""
        self._settings = QSettings("FDLViewer", "FDLViewer")

    @classmethod
    def instance(cls) -> "Settings":
        """
        Get the singleton instance of Settings.

        Returns
        -------
        Settings
            The singleton Settings instance.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _get(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        return self._settings.value(key, default)

    def _set(self, key: str, value: Any) -> None:
        """Set a setting value."""
        self._settings.setValue(key, value)
        self._settings.sync()

    # Window geometry
    def get_window_geometry(self) -> QByteArray | None:
        """
        Get the saved window geometry.

        Returns
        -------
        QByteArray or None
            The window geometry, or None if not saved.
        """
        value = self._get(self.WINDOW_GEOMETRY)
        if isinstance(value, QByteArray):
            return value
        return None

    def set_window_geometry(self, geometry: QByteArray) -> None:
        """
        Save the window geometry.

        Parameters
        ----------
        geometry : QByteArray
            The window geometry to save.
        """
        self._set(self.WINDOW_GEOMETRY, geometry)

    # Window state
    def get_window_state(self) -> QByteArray | None:
        """
        Get the saved window state.

        Returns
        -------
        QByteArray or None
            The window state, or None if not saved.
        """
        value = self._get(self.WINDOW_STATE)
        if isinstance(value, QByteArray):
            return value
        return None

    def set_window_state(self, state: QByteArray) -> None:
        """
        Save the window state.

        Parameters
        ----------
        state : QByteArray
            The window state to save.
        """
        self._set(self.WINDOW_STATE, state)

    # Sidebar width
    def get_sidebar_width(self) -> int:
        """
        Get the saved sidebar width.

        Returns
        -------
        int
            The sidebar width (default 400).
        """
        return int(self._get(self.SIDEBAR_WIDTH, 400))

    def set_sidebar_width(self, width: int) -> None:
        """
        Save the sidebar width.

        Parameters
        ----------
        width : int
            The sidebar width to save.
        """
        self._set(self.SIDEBAR_WIDTH, width)

    # Sidebar collapsed
    def get_sidebar_collapsed(self) -> bool:
        """
        Get the sidebar collapsed state.

        Returns
        -------
        bool
            True if sidebar is collapsed.
        """
        return self._get(self.SIDEBAR_COLLAPSED, False) == "true"

    def set_sidebar_collapsed(self, collapsed: bool) -> None:
        """
        Save the sidebar collapsed state.

        Parameters
        ----------
        collapsed : bool
            The collapsed state to save.
        """
        self._set(self.SIDEBAR_COLLAPSED, "true" if collapsed else "false")

    # Active tab
    def get_active_tab(self) -> int:
        """
        Get the last active tab index.

        Returns
        -------
        int
            The tab index (default 0).
        """
        return int(self._get(self.ACTIVE_TAB, 0))

    def set_active_tab(self, index: int) -> None:
        """
        Save the active tab index.

        Parameters
        ----------
        index : int
            The tab index to save.
        """
        self._set(self.ACTIVE_TAB, index)

    # Grid visible
    def get_grid_visible(self) -> bool:
        """
        Get the grid visibility setting.

        Returns
        -------
        bool
            True if grid is visible (default True).
        """
        return self._get(self.GRID_VISIBLE, "true") == "true"

    def set_grid_visible(self, visible: bool) -> None:
        """
        Save the grid visibility setting.

        Parameters
        ----------
        visible : bool
            The visibility state to save.
        """
        self._set(self.GRID_VISIBLE, "true" if visible else "false")

    # Image opacity
    def get_image_opacity(self) -> float:
        """
        Get the image underlay opacity.

        Returns
        -------
        float
            The opacity value (default 0.7).
        """
        return float(self._get(self.IMAGE_OPACITY, 0.7))

    def set_image_opacity(self, opacity: float) -> None:
        """
        Save the image underlay opacity.

        Parameters
        ----------
        opacity : float
            The opacity value to save (0.0 to 1.0).
        """
        self._set(self.IMAGE_OPACITY, opacity)

    # Last directory
    def get_last_directory(self) -> str:
        """
        Get the last used directory.

        Returns
        -------
        str
            The directory path (default empty string).
        """
        return str(self._get(self.LAST_DIRECTORY, ""))

    def set_last_directory(self, directory: str) -> None:
        """
        Save the last used directory.

        Parameters
        ----------
        directory : str
            The directory path to save.
        """
        self._set(self.LAST_DIRECTORY, directory)

    # Image filter
    def get_image_filter(self) -> str:
        """
        Get the image processing filter.

        Returns
        -------
        str
            The filter name (default 'lanczos3').
        """
        return str(self._get(self.IMAGE_FILTER, "lanczos3"))

    def set_image_filter(self, filter_name: str) -> None:
        """
        Save the image processing filter.

        Parameters
        ----------
        filter_name : str
            The filter name to save.
        """
        self._set(self.IMAGE_FILTER, filter_name)

    # Auto process image
    def get_auto_process_image(self) -> bool:
        """
        Get the auto-process image setting.

        Returns
        -------
        bool
            True if auto-process is enabled (default False).
        """
        return self._get(self.AUTO_PROCESS_IMAGE, "false") == "true"

    def set_auto_process_image(self, enabled: bool) -> None:
        """
        Save the auto-process image setting.

        Parameters
        ----------
        enabled : bool
            The enabled state to save.
        """
        self._set(self.AUTO_PROCESS_IMAGE, "true" if enabled else "false")
