#!/usr/bin/env python3
"""
MacQ - Mac-Native Quantum Computing Software
Main Application Entry Point
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from macq.gui import MainWindow


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # macOS specific: use native menu bar
    # app.setAttribute(Qt.AA_DontUseNativeMenuBar, False)
    
    # Set application info
    app.setApplicationName("MacQ")
    app.setOrganizationName("MacQ Development Team")
    app.setApplicationVersion("1.0.0")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run event loop
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
