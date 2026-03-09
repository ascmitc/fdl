# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
UI test helper for FDL Viewer integration tests.

Provides helper class for UI automation and interaction with the MainWindow.
"""

from pathlib import Path

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QImage, QPainter, QPixmap

from fdl_viewer.models.app_state import AppState
from fdl_viewer.views.main_window import MainWindow


class UITestHelper:
    """
    Helper class for UI-driven integration tests.

    Provides methods to interact with the MainWindow and its components,
    simulating user actions for testing purposes.

    Parameters
    ----------
    main_window : MainWindow
        The main window instance to test.
    qtbot : pytest_qt.QtBot
        The pytest-qt bot for waiting and interactions.
    """

    def __init__(self, main_window: MainWindow, qtbot) -> None:
        """
        Initialize the UITestHelper.

        Parameters
        ----------
        main_window : MainWindow
            The main window instance.
        qtbot : pytest_qt.QtBot
            The pytest-qt bot.
        """
        self.window = main_window
        self.qtbot = qtbot
        self.app_state = AppState.instance()

    def load_source_fdl(self, path: Path) -> None:
        """
        Load source FDL via MainWindow method (simulates UI load).

        Parameters
        ----------
        path : Path
            Path to the source FDL file.
        """
        self.window.load_source_fdl(str(path))
        self.qtbot.wait(7)  # Allow signals to propagate

    def load_template_fdl(self, path: Path) -> None:
        """
        Load template FDL via MainWindow method.

        Parameters
        ----------
        path : Path
            Path to the template FDL file.
        """
        self.window.load_template_fdl(str(path))
        self.qtbot.wait(7)

    def load_source_image(self, path: Path) -> None:
        """
        Load image via the sidebar's image loader.

        This uses the proper signal chain through the sidebar's ImageLoaderView,
        which triggers MainWindow._on_image_loaded and properly sets up
        the image display on all tabs.

        Parameters
        ----------
        path : Path
            Path to the image file.
        """
        # Use the sidebar's image loader which triggers proper signal chain
        self.window.sidebar._image_loader._load_image(str(path))
        self.qtbot.wait(7)  # Allow signals to propagate

    def select_context(self, index: int) -> None:
        """
        Select context in source selector dropdown by index.

        Parameters
        ----------
        index : int
            The index to select.
        """
        combo = self.window.sidebar._source_selector._context_combo
        combo.setCurrentIndex(index)
        self.qtbot.wait(4)

    def select_canvas(self, index: int) -> None:
        """
        Select canvas in source selector dropdown by index.

        Parameters
        ----------
        index : int
            The index to select.
        """
        combo = self.window.sidebar._source_selector._canvas_combo
        combo.setCurrentIndex(index)
        self.qtbot.wait(4)

    def select_framing_decision(self, index: int) -> None:
        """
        Select framing decision in source selector dropdown by index.

        Parameters
        ----------
        index : int
            The index to select.
        """
        combo = self.window.sidebar._source_selector._framing_combo
        combo.setCurrentIndex(index)
        self.qtbot.wait(4)

    def click_transform(self) -> None:
        """Click transform button and wait for completion."""
        self.window.sidebar._transform_button.click()
        self.qtbot.wait(35)  # Allow transformation to complete

    def switch_to_tab(self, tab_index: int) -> None:
        """
        Switch to specified tab.

        Parameters
        ----------
        tab_index : int
            Tab index: 0=Source, 1=Output, 2=Comparison, 3=Details.
        """
        self.window.tab_container.setCurrentIndex(tab_index)
        self.qtbot.wait(7)

    def capture_tab_screenshot(self, tab_index: int) -> QPixmap:
        """
        Capture screenshot of a specific tab's canvas.

        Parameters
        ----------
        tab_index : int
            Tab index: 0=Source, 1=Output, 2=Comparison, 3=Details.

        Returns
        -------
        QPixmap
            The captured screenshot.
        """
        self.switch_to_tab(tab_index)
        if tab_index == 0:  # Source
            return self.window.tab_container.source_tab.grab()
        elif tab_index == 1:  # Output
            return self.window.tab_container.output_tab.grab()
        elif tab_index == 2:  # Comparison
            return self.window.tab_container.comparison_tab.grab()
        elif tab_index == 3:  # Details
            return self.window.tab_container.details_tab.grab()
        return QPixmap()

    def capture_canvas_scene(self, canvas_widget) -> QPixmap:
        """
        Capture QGraphicsScene content directly (not widget grab).

        Uses scene.render() for pixel-perfect output independent of widget state.
        This provides more reliable output than widget.grab() for testing.

        Parameters
        ----------
        canvas_widget : CanvasView
            The canvas widget containing the QGraphicsScene.

        Returns
        -------
        QPixmap
            Rendered scene content as a pixmap.
        """
        scene = canvas_widget._scene
        scene_rect = scene.sceneRect()

        # Handle empty scene
        if scene_rect.isEmpty():
            return QPixmap()

        # Create QImage matching scene dimensions
        image = QImage(int(scene_rect.width()), int(scene_rect.height()), QImage.Format_ARGB32_Premultiplied)
        image.fill(Qt.black)  # Match canvas background

        # Render scene to image
        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        scene.render(painter, QRectF(image.rect()), scene_rect)
        painter.end()

        return QPixmap.fromImage(image)

    def capture_tab_scene(self, tab_index: int) -> QPixmap:
        """
        Capture scene content from a specific tab's canvas.

        Uses QGraphicsScene.render() for reliable output.

        Parameters
        ----------
        tab_index : int
            Tab index: 0=Source, 1=Output, 2=Comparison, 3=Details.

        Returns
        -------
        QPixmap
            Rendered scene content as a pixmap.
        """
        self.switch_to_tab(tab_index)
        if tab_index == 0:  # Source
            return self.capture_canvas_scene(self.window.tab_container.source_tab._canvas)
        elif tab_index == 1:  # Output
            return self.capture_canvas_scene(self.window.tab_container.output_tab._canvas)
        # Comparison tab has two canvases - capture whole tab for compound view
        elif tab_index == 2:
            return self.window.tab_container.comparison_tab.grab()
        # Details tab has text content - use grab
        elif tab_index == 3:
            return self.window.tab_container.details_tab.grab()
        return QPixmap()

    def capture_all_tabs(self) -> dict[str, QPixmap]:
        """
        Capture screenshots of all tabs.

        Returns
        -------
        Dict[str, QPixmap]
            Dictionary mapping tab names to screenshots.
        """
        return {
            "source": self.capture_tab_screenshot(0),
            "output": self.capture_tab_screenshot(1),
            "comparison": self.capture_tab_screenshot(2),
            "details": self.capture_tab_screenshot(3),
        }

    def save_pixmap_as_image(self, pixmap: QPixmap, path: Path) -> bool:
        """
        Save QPixmap to file.

        Parameters
        ----------
        pixmap : QPixmap
            The pixmap to save.
        path : Path
            The output path.

        Returns
        -------
        bool
            True if save was successful.
        """
        return pixmap.save(str(path))

    def export_fdl_programmatically(self, output_path: Path) -> bool:
        """
        Export FDL via controller (bypasses file dialog).

        Parameters
        ----------
        output_path : Path
            The output file path.

        Returns
        -------
        bool
            True if export was successful.
        """
        output_model = self.app_state.output_fdl
        if output_model and output_model.fdl:
            from fdl_viewer.controllers.file_controller import FileController

            controller = FileController()
            controller.save_fdl(output_model.fdl, str(output_path))
            return True
        return False

    def export_output_image_programmatically(self, output_path: Path, filter_name: str = "triangle") -> bool:
        """
        Export the transformed output image to the specified path.

        This bypasses the file dialog and directly exports the transformed
        image using MainWindow.export_output_image().

        Uses "triangle" (bilinear) filter by default in tests for
        deterministic cross-platform results.

        Parameters
        ----------
        output_path : Path
            Path where the output image should be saved.
        filter_name : str
            OIIO filter for resize operations. Default "triangle" for tests.

        Returns
        -------
        bool
            True if export was successful.
        """
        return self.window.export_output_image(str(output_path), filter_name=filter_name)

    def get_source_fdl_model(self):
        """
        Get the current source FDL model.

        Returns
        -------
        FDLModel or None
            The source FDL model.
        """
        return self.app_state.source_fdl

    def get_output_fdl_model(self):
        """
        Get the current output FDL model.

        Returns
        -------
        FDLModel or None
            The output FDL model.
        """
        return self.app_state.output_fdl

    def get_template_fdl_model(self):
        """
        Get the current template FDL model.

        Returns
        -------
        FDLModel or None
            The template FDL model.
        """
        return self.app_state.template_fdl

    def get_current_template(self):
        """
        Get the current canvas template.

        Returns
        -------
        CanvasTemplate or None
            The current canvas template.
        """
        return self.app_state.current_template

    def get_transform_result(self):
        """
        Get the last transformation result.

        Returns
        -------
        TemplateResult or None
            The transformation result.
        """
        return self.app_state.transform_result

    def is_transform_button_enabled(self) -> bool:
        """
        Check if the transform button is enabled.

        Returns
        -------
        bool
            True if the transform button is enabled.
        """
        return self.window.sidebar._transform_button.isEnabled()

    def get_status_bar_message(self) -> str:
        """
        Get the current status bar message.

        Returns
        -------
        str
            The status bar message.
        """
        return self.window._status_bar.currentMessage()
