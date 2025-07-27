"""
Main application entry point for Next-Gen Paint
"""

import sys
import os
from pathlib import Path

# Add the C++ bindings to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "build"))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QSplitter
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QAction, QKeySequence

from .ui.main_window import MainWindow
from .core.document import Document
from .core.settings import Settings

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Next-Gen Paint")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Next-Gen Paint")
    
    # Load settings
    settings = Settings()
    
    # Create main window
    window = MainWindow()
    window.show()
    
    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 