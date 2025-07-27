"""
Main window for Next-Gen Paint application
"""

from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QSplitter, 
    QToolBar, QStatusBar, QMenuBar, QMenu, QFileDialog, QMessageBox,
    QDockWidget, QTabWidget, QSlider, QLabel, QComboBox, QSpinBox,
    QDoubleSpinBox, QCheckBox, QPushButton, QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt, QTimer, Signal, QSize, QPoint
from PySide6.QtGui import QIcon, QAction, QKeySequence, QPixmap, QPainter, QColor

from .canvas_widget import CanvasWidget
from .layers_panel import LayersPanel
from .tools_panel import ToolsPanel
from .properties_panel import PropertiesPanel
from .color_panel import ColorPanel
from .filters_panel import FiltersPanel
from ..core.document import Document
from ..core.tools import ToolManager
from ..core.settings import Settings

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.document = Document()
        self.tool_manager = ToolManager()
        self.settings = Settings()
        
        self.setup_ui()
        self.setup_menus()
        self.setup_toolbars()
        self.setup_status_bar()
        self.setup_docks()
        self.setup_connections()
        
        # Set window properties
        self.setWindowTitle("Next-Gen Paint")
        self.setMinimumSize(1200, 800)
        self.resize(1600, 1000)
        
        # Create a new document
        self.new_document()
    
    def setup_ui(self):
        """Setup the main UI layout"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel (tools and properties)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tools panel
        self.tools_panel = ToolsPanel(self.tool_manager)
        left_layout.addWidget(self.tools_panel)
        
        # Properties panel
        self.properties_panel = PropertiesPanel()
        left_layout.addWidget(self.properties_panel)
        
        # Color panel
        self.color_panel = ColorPanel()
        left_layout.addWidget(self.color_panel)
        
        splitter.addWidget(left_panel)
        splitter.setStretchFactor(0, 0)
        
        # Canvas area
        self.canvas_widget = CanvasWidget(self.document)
        splitter.addWidget(self.canvas_widget)
        splitter.setStretchFactor(1, 1)
        
        # Right panel (layers and filters)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Layers panel
        self.layers_panel = LayersPanel(self.document)
        right_layout.addWidget(self.layers_panel)
        
        # Filters panel
        self.filters_panel = FiltersPanel()
        right_layout.addWidget(self.filters_panel)
        
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(2, 0)
        
        # Set splitter sizes
        splitter.setSizes([200, 800, 200])
    
    def setup_menus(self):
        """Setup the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("&New", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.new_document)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Open...", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_document)
        file_menu.addAction(open_action)
        
        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_document)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_as_action.triggered.connect(self.save_document_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("&Export...", self)
        export_action.triggered.connect(self.export_document)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence.Undo)
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence.Redo)
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("Cu&t", self)
        cut_action.setShortcut(QKeySequence.Cut)
        cut_action.triggered.connect(self.cut)
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("&Copy", self)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self.copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("&Paste", self)
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self.paste)
        edit_menu.addAction(paste_action)
        
        # Layer menu
        layer_menu = menubar.addMenu("&Layer")
        
        new_layer_action = QAction("&New Layer", self)
        new_layer_action.setShortcut(QKeySequence("Ctrl+Shift+N"))
        new_layer_action.triggered.connect(self.new_layer)
        layer_menu.addAction(new_layer_action)
        
        delete_layer_action = QAction("&Delete Layer", self)
        delete_layer_action.setShortcut(QKeySequence("Delete"))
        delete_layer_action.triggered.connect(self.delete_layer)
        layer_menu.addAction(delete_layer_action)
        
        # Filter menu
        filter_menu = menubar.addMenu("&Filter")
        
        blur_action = QAction("&Blur", self)
        blur_action.triggered.connect(self.apply_blur)
        filter_menu.addAction(blur_action)
        
        sharpen_action = QAction("&Sharpen", self)
        sharpen_action.triggered.connect(self.apply_sharpen)
        filter_menu.addAction(sharpen_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_toolbars(self):
        """Setup toolbars"""
        # Main toolbar
        main_toolbar = self.addToolBar("Main")
        main_toolbar.setMovable(False)
        
        # File actions
        main_toolbar.addAction(self.findChild(QAction, "New"))
        main_toolbar.addAction(self.findChild(QAction, "Open"))
        main_toolbar.addAction(self.findChild(QAction, "Save"))
        
        main_toolbar.addSeparator()
        
        # Edit actions
        main_toolbar.addAction(self.findChild(QAction, "Undo"))
        main_toolbar.addAction(self.findChild(QAction, "Redo"))
        
        main_toolbar.addSeparator()
        
        # Layer actions
        main_toolbar.addAction(self.findChild(QAction, "New Layer"))
    
    def setup_status_bar(self):
        """Setup the status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Add status labels
        self.zoom_label = QLabel("100%")
        self.status_bar.addPermanentWidget(self.zoom_label)
        
        self.position_label = QLabel("0, 0")
        self.status_bar.addPermanentWidget(self.position_label)
        
        self.status_bar.showMessage("Ready")
    
    def setup_docks(self):
        """Setup dockable widgets"""
        # History dock
        history_dock = QDockWidget("History", self)
        history_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, history_dock)
        
        # Navigator dock
        navigator_dock = QDockWidget("Navigator", self)
        navigator_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, navigator_dock)
    
    def setup_connections(self):
        """Setup signal connections"""
        # Connect tool manager to canvas and document
        self.tool_manager.tool_changed.connect(self.canvas_widget.set_tool)
        self.tool_manager.set_document(self.document)
        
        # Connect color panel to tool manager
        self.color_panel.color_changed.connect(self.tool_manager.set_color)
        
        # Connect properties panel to tool manager
        self.properties_panel.property_changed.connect(self.tool_manager.set_property)
        
        # Connect tool manager to properties panel
        self.tool_manager.tool_changed.connect(self.properties_panel.set_tool)
        
        # Connect layers panel to document
        self.layers_panel.layer_selected.connect(self.document.set_active_layer)
        
        # Connect filters panel to document
        self.filters_panel.filter_applied.connect(self.document.apply_filter)
        
        # Connect canvas mouse events to tool manager
        self.canvas_widget.mouse_pressed.connect(self._handle_mouse_press)
        self.canvas_widget.mouse_moved.connect(self._handle_mouse_move)
        self.canvas_widget.mouse_released.connect(self._handle_mouse_release)
    
    def _handle_mouse_press(self, pos: QPoint):
        """Handle mouse press from canvas"""
        if self.tool_manager.get_current_tool():
            self.tool_manager.get_current_tool().mouse_press(pos)
            self.canvas_widget.update_canvas()
    
    def _handle_mouse_move(self, pos: QPoint):
        """Handle mouse move from canvas"""
        if self.tool_manager.get_current_tool():
            self.tool_manager.get_current_tool().mouse_move(pos)
            self.canvas_widget.update_canvas()
    
    def _handle_mouse_release(self, pos: QPoint):
        """Handle mouse release from canvas"""
        if self.tool_manager.get_current_tool():
            self.tool_manager.get_current_tool().mouse_release(pos)
            self.canvas_widget.update_canvas()
    
    def new_document(self):
        """Create a new document"""
        self.document.new_document(1920, 1080)
        self.canvas_widget.update_canvas()
        self.layers_panel.update_layers()
        self.status_bar.showMessage("New document created")
    
    def open_document(self):
        """Open an existing document"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Document", "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff);;All Files (*)"
        )
        
        if file_path:
            try:
                self.document.open_document(file_path)
                self.canvas_widget.update_canvas()
                self.layers_panel.update_layers()
                self.status_bar.showMessage(f"Opened {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open document: {e}")
    
    def save_document(self):
        """Save the current document"""
        if not self.document.file_path:
            return self.save_document_as()
        
        try:
            self.document.save_document()
            self.status_bar.showMessage(f"Saved {self.document.file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save document: {e}")
    
    def save_document_as(self):
        """Save the document with a new name"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Document", "", 
            "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)"
        )
        
        if file_path:
            try:
                self.document.save_document_as(file_path)
                self.status_bar.showMessage(f"Saved {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save document: {e}")
    
    def export_document(self):
        """Export the document"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Document", "", 
            "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)"
        )
        
        if file_path:
            try:
                self.document.export_document(file_path)
                self.status_bar.showMessage(f"Exported {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export document: {e}")
    
    def undo(self):
        """Undo the last action"""
        if self.document.undo():
            self.canvas_widget.update_canvas()
            self.status_bar.showMessage("Undo")
    
    def redo(self):
        """Redo the last undone action"""
        if self.document.redo():
            self.canvas_widget.update_canvas()
            self.status_bar.showMessage("Redo")
    
    def cut(self):
        """Cut selection to clipboard"""
        # TODO: Implement cut functionality
        pass
    
    def copy(self):
        """Copy selection to clipboard"""
        # TODO: Implement copy functionality
        pass
    
    def paste(self):
        """Paste from clipboard"""
        # TODO: Implement paste functionality
        pass
    
    def new_layer(self):
        """Create a new layer"""
        self.document.add_layer("New Layer")
        self.layers_panel.update_layers()
        self.status_bar.showMessage("New layer created")
    
    def delete_layer(self):
        """Delete the current layer"""
        if self.document.delete_active_layer():
            self.layers_panel.update_layers()
            self.canvas_widget.update_canvas()
            self.status_bar.showMessage("Layer deleted")
    
    def apply_blur(self):
        """Apply blur filter"""
        # TODO: Implement blur filter dialog
        pass
    
    def apply_sharpen(self):
        """Apply sharpen filter"""
        # TODO: Implement sharpen filter dialog
        pass
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self, "About Next-Gen Paint",
            "Next-Gen Paint v1.0.0\n\n"
            "A modern, extensible paint application\n"
            "Built with PyQt6 and C++"
        )
    
    def closeEvent(self, event):
        """Handle window close event"""
        # TODO: Check for unsaved changes
        event.accept() 