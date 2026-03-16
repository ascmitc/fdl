# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Main entry point for FDL Viewer application.

This module initializes the Qt application and displays the main window.
"""

import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QApplication, QMessageBox

from fdl_viewer import __version__
from fdl_viewer.resources import get_icon_path, get_resource_path, load_stylesheet
from fdl_viewer.views.main_window import MainWindow
from fdl_viewer.views.splash_screen import SplashScreen


def setup_exception_handler() -> None:
    """
    Set up a global exception handler that logs errors to a file.
    """

    def exception_handler(exc_type, exc_value, exc_tb) -> None:
        """Handle uncaught exceptions by logging to file and showing dialog."""
        # Format the exception
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))

        # Log to file in user's home directory
        log_dir = Path.home()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"FDLViewer_crash_{timestamp}.log"

        try:
            with open(log_file, "w", encoding="utf-8") as f:
                f.write("FDL Viewer Crash Report\n")
                f.write(f"Version: {__version__}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write(f"\n{error_msg}")
            print(f"Crash log written to: {log_file}")
        except Exception:
            pass

        # Show error dialog
        app = QApplication.instance()
        if app:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("FDL Viewer Error")
            msg.setText("An unexpected error occurred.")
            msg.setDetailedText(error_msg)
            msg.setInformativeText(f"A crash log has been saved to:\n{log_file}")
            msg.exec()

        # Call the default handler
        sys.__excepthook__(exc_type, exc_value, exc_tb)

    sys.excepthook = exception_handler


def create_application() -> QApplication:
    """
    Create and configure the Qt application.

    Returns
    -------
    QApplication
        The configured Qt application instance.
    """
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QApplication(sys.argv)
    app.setApplicationName("FDL Viewer")
    app.setApplicationVersion(__version__)
    app.setOrganizationName("FDLViewer")
    app.setOrganizationDomain("fdlviewer.local")

    # Set application style
    app.setStyle("Fusion")

    # Load dark theme stylesheet
    stylesheet = load_stylesheet("dark_theme.qss")
    if stylesheet:
        app.setStyleSheet(stylesheet)

    # Set application icon
    icon_path = get_icon_path("fdl_viewer.ico")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    return app


def main(fdl_path: str | None = None) -> int:
    """
    Main entry point for the FDL Viewer application.

    Parameters
    ----------
    fdl_path : str, optional
        Path to an FDL file to open on startup.

    Returns
    -------
    int
        The application exit code.
    """
    # Set up exception handling
    setup_exception_handler()

    # Create application
    app = create_application()

    # Show splash screen
    splash = None
    splash_path = get_resource_path("ASCFDL_Logo.png")
    if splash_path.exists():
        splash_pixmap = QPixmap(str(splash_path))
        # Scale logo to 1/4 size (divide width and height by 2)
        scaled_pixmap = splash_pixmap.scaled(
            splash_pixmap.width() // 3,
            splash_pixmap.height() // 3,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        splash = SplashScreen(scaled_pixmap, __version__)
        splash.show()

        # Hold splash screen for 3 seconds
        time.sleep(3)

        # Close splash screen before showing main window
        splash.close()

    # Create and show main window
    window = MainWindow()
    window.show()

    # Load file if provided
    if fdl_path:
        window.load_source_fdl(fdl_path)
    elif len(sys.argv) > 1:
        # Check command line arguments
        arg = sys.argv[1]
        if arg.endswith(".fdl") and Path(arg).exists():
            window.load_source_fdl(arg)

    # Run event loop
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
