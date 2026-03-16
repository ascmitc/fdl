# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Splash screen widget for FDL Viewer.

Displays the application logo and version on startup.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPainter
from PySide6.QtWidgets import QSplashScreen


class SplashScreen(QSplashScreen):
    """
    Custom splash screen that displays the application logo and version.

    Parameters
    ----------
    pixmap : QPixmap
        The pixmap to display on the splash screen.
    version_info : str
        The version string to display.
    """

    def __init__(self, pixmap, version_info, *args, **kwargs) -> None:
        """
        Initialize the splash screen.

        Parameters
        ----------
        pixmap : QPixmap
            The pixmap to display on the splash screen.
        version_info : str
            The version string to display.
        """
        super().__init__(pixmap, *args, **kwargs)
        self.version_info = version_info

    def drawContents(self, painter: QPainter) -> None:
        """
        Draw the contents of the splash screen.

        Parameters
        ----------
        painter : QPainter
            The painter object to draw with.
        """
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(Qt.white)
        painter.drawText(self.rect().adjusted(0, 0, -10, -10), Qt.AlignBottom | Qt.AlignRight, f"v{self.version_info}")
