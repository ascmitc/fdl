# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Main window for FDL Viewer application.

Provides the main application window with sidebar and tabbed content area.
"""

import tempfile
from pathlib import Path

from fdl_imaging import (
    get_fdl_components,
    transform_image_with_computed_values,
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QAction, QKeySequence, QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QStatusBar,
    QWidget,
)

from fdl_viewer import __version__
from fdl_viewer.controllers.file_controller import FileController
from fdl_viewer.controllers.transform_controller import TransformController
from fdl_viewer.controllers.unit_test_export_controller import UnitTestExportController
from fdl_viewer.models.app_state import AppState
from fdl_viewer.models.fdl_model import FDLModel
from fdl_viewer.models.recent_files import RecentFilesModel
from fdl_viewer.utils.settings import Settings
from fdl_viewer.views.common.error_dialog import ErrorDialog
from fdl_viewer.views.dialogs.export_unit_test_dialog import ExportUnitTestDialog
from fdl_viewer.views.sidebar.sidebar_widget import SidebarWidget
from fdl_viewer.views.tabs.tab_container import TabContainer


class MainWindow(QMainWindow):
    """
    Main application window for FDL Viewer.

    Contains a sidebar for file loading and configuration, and a tabbed
    content area for visualization and comparison.

    Parameters
    ----------
    parent : QWidget, optional
        Parent widget.

    Attributes
    ----------
    sidebar : SidebarWidget
        The sidebar widget containing file loaders and editors.
    tab_container : TabContainer
        The tabbed content area.
    """

    WINDOW_TITLE = "FDL Viewer"
    MIN_WIDTH = 1200
    MIN_HEIGHT = 800
    DEFAULT_SIDEBAR_WIDTH = 400

    def __init__(self, parent: QWidget | None = None) -> None:
        """
        Initialize the MainWindow.

        Parameters
        ----------
        parent : QWidget, optional
            Parent widget.
        """
        super().__init__(parent)

        # Initialize state and controllers
        self._app_state = AppState.instance()
        self._settings = Settings.instance()
        self._recent_files = RecentFilesModel()
        self._file_controller = FileController()
        self._transform_controller = TransformController()
        self._unit_test_export_controller = UnitTestExportController()

        # Store current source image for sharing between tabs
        self._current_image_pixmap = None
        self._current_image_width = 0
        self._current_image_height = 0
        self._current_image_path: str = ""

        # Store transformed output image
        self._output_image_pixmap = None
        self._output_image_path: str = ""

        # Setup UI
        self._setup_window()
        self._setup_menu()
        self._setup_central_widget()
        self._setup_status_bar()
        self._connect_signals()
        self._restore_state()

    def _setup_window(self) -> None:
        """Configure window properties."""
        self.setWindowTitle(f"{self.WINDOW_TITLE} v{__version__}")
        self.setMinimumSize(self.MIN_WIDTH, self.MIN_HEIGHT)

    def _setup_menu(self) -> None:
        """Set up the menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        # Open Source FDL
        open_source_action = QAction("Open Source FDL...", self)
        open_source_action.setShortcut(QKeySequence.Open)
        open_source_action.triggered.connect(self._on_open_source)
        file_menu.addAction(open_source_action)

        # Open Template FDL
        open_template_action = QAction("Open Template FDL...", self)
        open_template_action.setShortcut(QKeySequence("Ctrl+Shift+O"))
        open_template_action.triggered.connect(self._on_open_template)
        file_menu.addAction(open_template_action)

        file_menu.addSeparator()

        # Save Output FDL
        save_action = QAction("Save Output FDL...", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self._on_save_output)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        # Quit
        quit_action = QAction("Quit", self)
        quit_action.setShortcut(QKeySequence.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        # Toggle sidebar
        toggle_sidebar_action = QAction("Toggle Sidebar", self)
        toggle_sidebar_action.setShortcut(QKeySequence("Ctrl+Alt+S"))
        toggle_sidebar_action.triggered.connect(self._on_toggle_sidebar)
        view_menu.addAction(toggle_sidebar_action)

        # Toggle grid
        toggle_grid_action = QAction("Toggle Grid", self)
        toggle_grid_action.setShortcut(QKeySequence("Ctrl+G"))
        toggle_grid_action.triggered.connect(self._on_toggle_grid)
        view_menu.addAction(toggle_grid_action)

        view_menu.addSeparator()

        # Tab navigation
        for i, name in enumerate(["Source", "Output", "Comparison", "Details"]):
            tab_action = QAction(f"Show {name} Tab", self)
            tab_action.setShortcut(QKeySequence(f"Ctrl+{i + 1}"))
            tab_action.triggered.connect(lambda checked, idx=i: self._on_switch_tab(idx))
            view_menu.addAction(tab_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("About FDL Viewer", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

    def _setup_central_widget(self) -> None:
        """Set up the central widget with splitter layout."""
        # Create main splitter
        self._splitter = QSplitter(Qt.Horizontal)
        self._splitter.setHandleWidth(1)

        # Create sidebar
        self.sidebar = SidebarWidget(recent_files=self._recent_files, parent=self)

        # Create tab container
        self.tab_container = TabContainer(parent=self)

        # Add to splitter
        self._splitter.addWidget(self.sidebar)
        self._splitter.addWidget(self.tab_container)

        # Set initial sizes
        sidebar_width = self._settings.get_sidebar_width()
        self._splitter.setSizes([sidebar_width, self.MIN_WIDTH - sidebar_width])

        # Set stretch factors (sidebar fixed, tabs stretch)
        self._splitter.setStretchFactor(0, 0)
        self._splitter.setStretchFactor(1, 1)

        # Set as central widget
        self.setCentralWidget(self._splitter)

    def _setup_status_bar(self) -> None:
        """Set up the status bar."""
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._status_bar.showMessage("Ready")

    def _connect_signals(self) -> None:
        """Connect signals to slots."""
        # App state signals
        self._app_state.source_fdl_changed.connect(self._on_source_fdl_changed)
        self._app_state.template_fdl_changed.connect(self._on_template_fdl_changed)
        self._app_state.output_fdl_changed.connect(self._on_output_fdl_changed)
        self._app_state.error_occurred.connect(self._on_error)

        # Sidebar signals
        self.sidebar.source_file_dropped.connect(self.load_source_fdl)
        self.sidebar.template_file_dropped.connect(self.load_template_fdl)
        self.sidebar.transform_requested.connect(self._on_transform_requested)
        self.sidebar.image_loaded.connect(self._on_image_loaded)
        self.sidebar.image_cleared.connect(self._on_image_cleared)

        # Details tab signals
        self.tab_container.details_tab.export_image_requested.connect(self._on_export_image_requested)
        self.tab_container.details_tab.export_proxy_requested.connect(self._on_export_proxy_requested)
        self.tab_container.details_tab.export_unit_test_requested.connect(self._on_export_unit_test_requested)

        # Unit test export controller signals
        self._unit_test_export_controller.export_completed.connect(self._on_unit_test_export_completed)
        self._unit_test_export_controller.error_occurred.connect(self._on_error)

        # Splitter signals
        self._splitter.splitterMoved.connect(self._on_splitter_moved)

    def _restore_state(self) -> None:
        """Restore window state from settings."""
        # Restore geometry
        geometry = self._settings.get_window_geometry()
        if geometry:
            self.restoreGeometry(geometry)

        # Restore window state
        state = self._settings.get_window_state()
        if state:
            self.restoreState(state)

        # Always start on Source tab (index 0)
        self.tab_container.setCurrentIndex(0)

        # Restore grid visibility
        grid_visible = self._settings.get_grid_visible()
        self._app_state.set_grid_visible(grid_visible)

    def _save_state(self) -> None:
        """Save window state to settings."""
        self._settings.set_window_geometry(self.saveGeometry())
        self._settings.set_window_state(self.saveState())
        self._settings.set_sidebar_width(self._splitter.sizes()[0])
        self._settings.set_active_tab(self.tab_container.currentIndex())
        self._settings.set_grid_visible(self._app_state.grid_visible)

    def closeEvent(self, event) -> None:
        """Handle window close event."""
        self._save_state()
        super().closeEvent(event)

    # File operations
    def load_source_fdl(self, path: str) -> None:
        """
        Load a source FDL file.

        Parameters
        ----------
        path : str
            Path to the FDL file.
        """
        try:
            fdl_model = self._file_controller.load_fdl(path)
            if fdl_model:
                self._app_state.set_source_fdl(fdl_model)
                self._recent_files.add_file(path, "source")
                self._status_bar.showMessage(f"Loaded: {Path(path).name}")
        except Exception as e:
            self._show_error(f"Failed to load FDL: {e}")

    def load_template_fdl(self, path: str) -> None:
        """
        Load a template FDL file.

        Parameters
        ----------
        path : str
            Path to the FDL file.
        """
        try:
            fdl_model = self._file_controller.load_fdl(path)
            if fdl_model:
                self._app_state.set_template_fdl(fdl_model)
                self._recent_files.add_file(path, "template")
                self._status_bar.showMessage(f"Template loaded: {Path(path).name}")
        except Exception as e:
            self._show_error(f"Failed to load template: {e}")

    def save_output_fdl(self, path: str) -> None:
        """
        Save the output FDL file.

        Parameters
        ----------
        path : str
            Path to save the FDL file.
        """
        output_model = self._app_state.output_fdl
        if not output_model or not output_model.fdl:
            self._show_error("No output FDL to save")
            return

        try:
            self._file_controller.save_fdl(output_model.fdl, path)
            self._status_bar.showMessage(f"Saved: {Path(path).name}")
        except Exception as e:
            self._show_error(f"Failed to save FDL: {e}")

    # Slots
    @Slot()
    def _on_open_source(self) -> None:
        """Handle open source FDL action."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Source FDL", self._settings.get_last_directory(), "FDL Files (*.fdl);;All Files (*)"
        )
        if path:
            self._settings.set_last_directory(str(Path(path).parent))
            self.load_source_fdl(path)

    @Slot()
    def _on_open_template(self) -> None:
        """Handle open template FDL action."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Template FDL", self._settings.get_last_directory(), "FDL Files (*.fdl);;All Files (*)"
        )
        if path:
            self._settings.set_last_directory(str(Path(path).parent))
            self.load_template_fdl(path)

    @Slot()
    def _on_save_output(self) -> None:
        """Handle save output FDL action."""
        if not self._app_state.output_fdl:
            self._show_error("No output FDL to save")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Save Output FDL", self._settings.get_last_directory(), "FDL Files (*.fdl);;All Files (*)"
        )
        if path:
            if not path.endswith(".fdl"):
                path += ".fdl"
            self._settings.set_last_directory(str(Path(path).parent))
            self.save_output_fdl(path)

    @Slot()
    def _on_toggle_sidebar(self) -> None:
        """Toggle sidebar visibility."""
        sizes = self._splitter.sizes()
        if sizes[0] > 0:
            self._last_sidebar_width = sizes[0]
            self._splitter.setSizes([0, sizes[0] + sizes[1]])
            self._app_state.set_sidebar_collapsed(True)
        else:
            width = getattr(self, "_last_sidebar_width", self.DEFAULT_SIDEBAR_WIDTH)
            self._splitter.setSizes([width, sizes[1] - width])
            self._app_state.set_sidebar_collapsed(False)

    @Slot()
    def _on_toggle_grid(self) -> None:
        """Toggle grid visibility."""
        self._app_state.set_grid_visible(not self._app_state.grid_visible)

    @Slot(int)
    def _on_switch_tab(self, index: int) -> None:
        """Switch to a specific tab."""
        self.tab_container.setCurrentIndex(index)

    @Slot()
    def _on_about(self) -> None:
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About FDL Viewer",
            f"<h3>FDL Viewer v{__version__}</h3>"
            "<p>A PySide6 application for viewing and transforming "
            "Framing Decision List (FDL) files.</p>"
            "<p>FDL Viewer Application</p>",
        )

    @Slot(object)
    def _on_source_fdl_changed(self, fdl_model: FDLModel | None) -> None:
        """Handle source FDL change."""
        if fdl_model:
            self.setWindowTitle(f"{self.WINDOW_TITLE} - {Path(fdl_model.file_path).name}")
            # Clear existing source image - a new FDL means the old image is invalid
            # The user will need to load the corresponding image for this FDL
            self._on_image_cleared()
            # Update details tab with source model for comparison
            self.tab_container.details_tab.set_source_model(fdl_model)
            # Note: validation will happen when new image is loaded via _on_image_loaded()
        else:
            self.setWindowTitle(f"{self.WINDOW_TITLE} v{__version__}")
            self.tab_container.details_tab.set_source_model(None)

    @Slot(object)
    def _on_template_fdl_changed(self, fdl_model: FDLModel | None) -> None:
        """Handle template FDL change."""
        pass

    @Slot(object)
    def _on_output_fdl_changed(self, fdl_model: FDLModel | None) -> None:
        """Handle output FDL change."""
        if fdl_model:
            self._status_bar.showMessage("Transformation complete")
            # Update comparison tab with source image
            if self._current_image_pixmap is not None:
                self.tab_container.comparison_tab.set_image(
                    self._current_image_pixmap, self._current_image_width, self._current_image_height
                )
            # Enable unit test export button
            self.tab_container.details_tab.set_transform_available(True)
            # Switch to output tab
            self.tab_container.setCurrentIndex(1)
        else:
            # Disable unit test export button when no output
            self.tab_container.details_tab.set_transform_available(False)

    @Slot()
    def _on_transform_requested(self) -> None:
        """Handle transform request from sidebar."""
        source = self._app_state.source_fdl
        template = self._app_state.current_template

        if not source or not source.fdl:
            self._show_error("No source FDL loaded")
            return

        if not template:
            self._show_error("No template configured")
            return

        context_label, canvas_id, fd_id = (
            self._app_state.selected_context,
            self._app_state.selected_canvas,
            self._app_state.selected_framing,
        )

        if not context_label or not canvas_id or not fd_id:
            self._show_error("Please select a context, canvas, and framing decision")
            return

        try:
            result = self._transform_controller.apply_template(source.fdl, template, context_label, canvas_id, fd_id)

            if result:
                output_model = FDLModel(result.fdl)
                # Auto-select the output context/canvas/framing for visualization
                output_model.set_selection(result.context.label, result.canvas.id, result.framing_decision.id)
                self._app_state.set_output_fdl(output_model)
                self._app_state.set_transform_result(result)

                # Set HUD data for output tab (source, template, output, translation, scale)
                from fdl import ATTR_CONTENT_TRANSLATION, ATTR_SCALE_FACTOR, ATTR_SCALED_BOUNDING_BOX

                content_translation = result.canvas.get_custom_attr(ATTR_CONTENT_TRANSLATION)
                scale_factor = result.canvas.get_custom_attr(ATTR_SCALE_FACTOR)
                scaled_bounding_box = result.canvas.get_custom_attr(ATTR_SCALED_BOUNDING_BOX)
                self.tab_container.output_tab.set_hud_data(source, template, output_model, content_translation, scale_factor)

                # Transform and display output image if an image is loaded
                if self._current_image_path:
                    self._transform_and_display_output_image(
                        source.fdl,
                        context_label,
                        canvas_id,
                        fd_id,
                        template,
                        result.canvas,
                        scaled_bounding_box,
                        content_translation,
                    )

        except Exception as e:
            self._show_error(f"Transformation failed: {e}")

    @Slot(int, int)
    def _on_splitter_moved(self, pos: int, index: int) -> None:
        """Handle splitter movement."""
        sizes = self._splitter.sizes()
        self._app_state.set_sidebar_collapsed(sizes[0] == 0)

    @Slot(str)
    def _on_error(self, message: str) -> None:
        """Handle error from app state."""
        self._show_error(message)

    def _show_error(self, message: str) -> None:
        """Show an error message using the custom error dialog."""
        # Extract summary (first line) and details (rest)
        lines = message.split("\n", 1)
        summary = lines[0]
        details = message

        # Update status bar with summary
        self._status_bar.showMessage(f"Error: {summary[:100]}")

        # Show detailed error dialog
        ErrorDialog.show_error(
            self,
            title="Error",
            summary=summary,
            details=details,
        )

    def _transform_and_display_output_image(
        self,
        source_fdl,
        context_label: str,
        canvas_id: str,
        fd_id: str,
        template,
        new_canvas,
        scaled_bounding_box,
        content_translation,
    ) -> None:
        """
        Transform the loaded image and display on output tab.

        Parameters
        ----------
        source_fdl : FDL
            The source FDL object
        context_label : str
            The selected context label
        canvas_id : str
            The selected canvas ID
        fd_id : str
            The selected framing decision ID
        template : CanvasTemplate
            The template used for transformation
        new_canvas : Canvas
            The output canvas (from apply_fdl_template result)
        scaled_bounding_box : DimensionsFloat
            The scaled bounding box dimensions
        content_translation : Point
            The content translation offset
        """
        try:
            # Get source canvas and framing decision
            _context, source_canvas, source_framing = get_fdl_components(source_fdl, context_label, canvas_id, fd_id)

            # Create a temporary file for the output image
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                output_path = tmp_file.name

            # Transform the image
            transform_image_with_computed_values(
                input_path=self._current_image_path,
                output_path=output_path,
                source_canvas=source_canvas,
                source_framing=source_framing,
                template=template,
                new_canvas=new_canvas,
                scaled_bounding_box=scaled_bounding_box,
                content_translation=content_translation,
            )

            # Load the transformed image as QPixmap
            transformed_pixmap = QPixmap(output_path)
            if not transformed_pixmap.isNull():
                # Store the output image for export
                self._output_image_pixmap = transformed_pixmap
                self._output_image_path = output_path

                # Set the transformed image on the output tab
                self.tab_container.output_tab.set_image(
                    transformed_pixmap,
                    transformed_pixmap.width(),
                    transformed_pixmap.height(),
                )
                # Set the transformed image on the comparison tab's output canvas
                self.tab_container.comparison_tab.set_output_image(
                    transformed_pixmap,
                    transformed_pixmap.width(),
                    transformed_pixmap.height(),
                )
                self._status_bar.showMessage(f"Output image: {transformed_pixmap.width()}x{transformed_pixmap.height()}")
            else:
                self._status_bar.showMessage("Failed to load transformed image")

        except Exception as e:
            self._status_bar.showMessage(f"Image transform failed: {e}")

    @Slot(object, int, int)
    def _on_image_loaded(self, pixmap, width: int, height: int) -> None:
        """Handle image loaded from sidebar."""
        # Store for sharing between tabs
        self._current_image_pixmap = pixmap
        self._current_image_width = width
        self._current_image_height = height
        self._current_image_path = self.sidebar.get_image_path()

        # Validate image matches canvas size (blocking error if mismatch)
        self._validate_image_canvas_match()

        # If validation cleared the image, don't proceed
        if self._current_image_pixmap is None:
            return

        # Set on all tabs with canvases
        self.tab_container.source_tab.set_image(pixmap, width, height)
        self.tab_container.output_tab.set_image(pixmap, width, height)
        self.tab_container.comparison_tab.set_image(pixmap, width, height)

        # Enable export image button
        self.tab_container.details_tab.set_image_available(True)

        self._status_bar.showMessage(f"Image loaded: {width}x{height}")

    @Slot()
    def _on_image_cleared(self) -> None:
        """Handle image cleared from sidebar."""
        self._current_image_pixmap = None
        self._current_image_width = 0
        self._current_image_height = 0
        self._current_image_path = ""

        # Clear output image
        self._output_image_pixmap = None
        self._output_image_path = ""

        # Clear from all tabs
        self.tab_container.source_tab.clear_image()
        self.tab_container.output_tab.clear_image()
        self.tab_container.comparison_tab.clear_image()

        # Disable export image button
        self.tab_container.details_tab.set_image_available(False)

        self._status_bar.showMessage("Image cleared")

    def _validate_image_canvas_match(self) -> None:
        """
        Validate source image matches canvas dimensions.

        Both the image and FDL use (0,0) as top-left origin. For proper alignment,
        the source image must have the same resolution as the FDL canvas.
        If there's a mismatch, the image is cleared and an error is shown.
        """
        if self._current_image_pixmap is None:
            return

        source_fdl = self._app_state.source_fdl
        if source_fdl is None:
            return

        canvas_rect = source_fdl.get_canvas_rect()
        if canvas_rect is None:
            return

        img_w = self._current_image_width
        img_h = self._current_image_height
        canvas_w = int(canvas_rect.width())
        canvas_h = int(canvas_rect.height())

        if img_w != canvas_w or img_h != canvas_h:
            # Get detailed info for error message
            image_path = self._current_image_path if self._current_image_path else "Unknown"
            fdl_path = source_fdl.file_path if source_fdl.file_path else "Unknown"
            canvas_label = source_fdl.current_canvas.label if source_fdl.current_canvas else "Unknown"
            canvas_id = source_fdl.current_canvas.id if source_fdl.current_canvas else "Unknown"

            # BLOCKING ERROR: Clear the image and show error
            self._on_image_cleared()
            self._show_error(
                f"Source image size does not match canvas size.\n\n"
                f"Image: {image_path}\n"
                f"  Size: {img_w} x {img_h}\n\n"
                f"FDL: {fdl_path}\n"
                f"  Canvas: {canvas_label} (ID: {canvas_id})\n"
                f"  Size: {canvas_w} x {canvas_h}\n\n"
                "The source image must have the same resolution as the FDL canvas."
            )

    @Slot()
    def _on_export_image_requested(self) -> None:
        """Handle export image request from details tab."""
        if not self._current_image_path or self._app_state.transform_result is None:
            self._show_error("No transformed image to export. Please run a transform first.")
            return

        # Get original file info to suggest same format
        original_path = Path(self._current_image_path) if self._current_image_path else None
        original_ext = original_path.suffix.lower() if original_path else ".png"
        original_stem = original_path.stem if original_path else "output"

        # Build filter list — original format first, then the rest, SVG last
        format_filters = {
            ".exr": "EXR Files (*.exr)",
            ".png": "PNG Files (*.png)",
            ".tif": "TIFF Files (*.tif *.tiff)",
            ".tiff": "TIFF Files (*.tif *.tiff)",
            ".jpg": "JPEG Files (*.jpg *.jpeg)",
            ".jpeg": "JPEG Files (*.jpg *.jpeg)",
            ".dpx": "DPX Files (*.dpx)",
        }
        # Canonical order
        canonical_order = [
            "EXR Files (*.exr)",
            "PNG Files (*.png)",
            "TIFF Files (*.tif *.tiff)",
            "JPEG Files (*.jpg *.jpeg)",
            "DPX Files (*.dpx)",
        ]
        # Put original format first, then the rest
        first = format_filters.get(original_ext)
        filters = []
        if first:
            filters.append(first)
        for f in canonical_order:
            if f not in filters:
                filters.append(f)
        filters.append("SVG Files (*.svg)")
        filters.append("All Files (*)")

        # Suggest output filename with same extension
        suggested_name = f"{original_stem}_output{original_ext}"
        last_dir = self._settings.get_last_directory()
        suggested_path = str(Path(last_dir) / suggested_name) if last_dir else suggested_name

        path, _selected_filter = QFileDialog.getSaveFileName(self, "Export Image", suggested_path, ";;".join(filters))

        if path:
            self._settings.set_last_directory(str(Path(path).parent))

            # Ensure file has an extension - use original format as default
            supported_exts = [".exr", ".png", ".tif", ".tiff", ".jpg", ".jpeg", ".dpx", ".svg"]
            if not any(path.lower().endswith(ext) for ext in supported_exts):
                path += original_ext

            # Export using OIIO for proper format support
            if self.export_output_image(path):
                self._status_bar.showMessage(f"Image exported: {Path(path).name}")
                QMessageBox.information(self, "Export Complete", f"Image exported to:\n{path}")
            else:
                self._show_error(f"Failed to save image to: {path}")

    def export_output_image(self, output_path: str) -> bool:
        """
        Export the transformed output image to the specified path.

        For SVG output, exports the current QGraphicsScene as a vector graphic.
        For raster formats, re-runs the transform directly to the output path
        using OpenImageIO, bypassing the PNG temp file used for UI preview.
        This ensures EXR exports use the same code path (and half precision)
        as the core converter.

        Parameters
        ----------
        output_path : str
            Path where the image should be saved. Use .svg for vector output.

        Returns
        -------
        bool
            True if export succeeded, False otherwise.
        """
        ext = Path(output_path).suffix.lower()

        # SVG: export the scene as a vector graphic
        if ext == ".svg":
            output_canvas = self.tab_container.output_tab.canvas
            return output_canvas.export_to_svg(output_path)

        # Raster: use OIIO pipeline
        if not self._current_image_path:
            return False
        result = self._app_state.transform_result
        if result is None:
            return False
        try:
            source_fdl = self._app_state.source_fdl.fdl
            context_label = self._app_state.selected_context
            canvas_id = self._app_state.selected_canvas
            fd_id = self._app_state.selected_framing
            _context, source_canvas, source_framing = get_fdl_components(source_fdl, context_label, canvas_id, fd_id)
            template = self._app_state.current_template
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            from fdl import ATTR_CONTENT_TRANSLATION, ATTR_SCALED_BOUNDING_BOX

            transform_image_with_computed_values(
                input_path=self._current_image_path,
                output_path=output_path,
                source_canvas=source_canvas,
                source_framing=source_framing,
                template=template,
                new_canvas=result.canvas,
                scaled_bounding_box=result.canvas.get_custom_attr(ATTR_SCALED_BOUNDING_BOX),
                content_translation=result.canvas.get_custom_attr(ATTR_CONTENT_TRANSLATION),
            )
            return True
        except Exception:
            return False

    @Slot()
    def _on_export_proxy_requested(self) -> None:
        """Handle export proxy request from details tab (PNG/JPEG only)."""
        if self._output_image_pixmap is None:
            self._show_error("No transformed image to export. Please run a transform first.")
            return

        # Get original file info for suggested filename
        original_path = Path(self._current_image_path) if self._current_image_path else None
        original_stem = original_path.stem if original_path else "output"

        # Proxy exports are PNG or JPEG only
        filters = [
            "PNG Files (*.png)",
            "JPEG Files (*.jpg *.jpeg)",
            "All Files (*)",
        ]

        # Suggest output filename with _proxy suffix
        suggested_name = f"{original_stem}_proxy.png"
        last_dir = self._settings.get_last_directory()
        suggested_path = str(Path(last_dir) / suggested_name) if last_dir else suggested_name

        path, selected_filter = QFileDialog.getSaveFileName(self, "Export Proxy", suggested_path, ";;".join(filters))

        if path:
            self._settings.set_last_directory(str(Path(path).parent))

            # Determine format from selected filter or extension
            if not any(path.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg"]):
                # Default to PNG if no extension
                if "JPEG" in selected_filter:
                    path += ".jpg"
                else:
                    path += ".png"

            # Save the output pixmap (proxy uses QPixmap for PNG/JPEG)
            if self._output_image_pixmap.save(path):
                self._status_bar.showMessage(f"Proxy exported: {Path(path).name}")
                QMessageBox.information(self, "Export Complete", f"Proxy exported to:\n{path}")
            else:
                self._show_error(f"Failed to save proxy to: {path}")

    @Slot()
    def _on_export_unit_test_requested(self) -> None:
        """Handle export unit test request from details tab."""
        # Verify we have the necessary data
        source_fdl = self._app_state.source_fdl
        output_fdl = self._app_state.output_fdl
        template = self._app_state.current_template
        transform_result = self._app_state.transform_result

        if not source_fdl or not source_fdl.fdl:
            self._show_error("No source FDL loaded.")
            return

        if not output_fdl or not output_fdl.fdl:
            self._show_error("No transformation result. Please run a transform first.")
            return

        if not template:
            self._show_error("No template configured.")
            return

        if not transform_result:
            self._show_error("No transformation result available.")
            return

        # Get template FDL
        template_fdl_model = self._app_state.template_fdl
        if not template_fdl_model or not template_fdl_model.fdl:
            self._show_error("No template FDL available.")
            return

        # Get the next scenario number
        next_scenario = self._unit_test_export_controller.get_next_scenario_number()

        # Derive default name from source FDL filename
        default_name = ""
        if source_fdl.file_path:
            default_name = Path(source_fdl.file_path).stem

        # Get default export path
        default_export_path = self._unit_test_export_controller.get_default_export_path()

        # Show the export dialog
        dialog = ExportUnitTestDialog(
            parent=self,
            scenario_number=next_scenario,
            default_name=default_name,
            has_image=bool(self._current_image_path),
            default_export_path=default_export_path,
        )

        if dialog.exec() == ExportUnitTestDialog.Accepted:
            export_config = dialog.get_export_config()

            # Get selection info
            context_label = self._app_state.selected_context
            canvas_id = self._app_state.selected_canvas
            framing_id = self._app_state.selected_framing

            # Get input dimensions
            input_dims = (float(self._current_image_width), float(self._current_image_height))
            if input_dims == (0.0, 0.0) and source_fdl.current_canvas:
                # Fall back to canvas dimensions if no image
                input_dims = (
                    float(source_fdl.current_canvas.dimensions.width),
                    float(source_fdl.current_canvas.dimensions.height),
                )

            # Perform the export
            self._unit_test_export_controller.export_unit_test(
                source_fdl=source_fdl.fdl,
                source_fdl_path=source_fdl.file_path or "",
                template=template,
                template_fdl=template_fdl_model.fdl,
                output_fdl=output_fdl.fdl,
                source_image_path=self._current_image_path if export_config["include_image"] else None,
                context_label=context_label,
                canvas_id=canvas_id,
                framing_id=framing_id,
                input_dims=input_dims,
                export_config=export_config,
            )

    @Slot(int, str)
    def _on_unit_test_export_completed(self, scenario_number: int, config_code: str) -> None:
        """Handle successful unit test export."""
        self._status_bar.showMessage(f"Unit test scenario {scenario_number} exported successfully")
        QMessageBox.information(
            self,
            "Export Complete",
            f"Unit test scenario {scenario_number} exported successfully.\n\nThe scenario has been exported.\n\nRun 'pytest -v' to verify.",
        )
