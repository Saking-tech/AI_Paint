"""
Tools panel for selecting drawing tools
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QButtonGroup
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap

from ..core.tools import ToolManager

class ToolsPanel(QWidget):
    """Panel for selecting drawing tools"""
    
    def __init__(self, tool_manager: ToolManager):
        super().__init__()
        self.tool_manager = tool_manager
        self.button_group = QButtonGroup()
        
        self.setup_ui()
        self.setup_connections()
        
        # Set panel properties
        self.setMaximumWidth(60)
        self.setMinimumWidth(60)
    
    def setup_ui(self):
        """Setup the UI layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)
        
        # Create tool buttons
        self.create_tool_button("brush", "🖌️", "Brush Tool (B)")
        self.create_tool_button("eraser", "🧽", "Eraser Tool (E)")
        self.create_tool_button("smudge", "👆", "Smudge Tool (S)")
        self.create_tool_button("selection", "⬜", "Selection Tool (M)")
        
        # Add stretch to push buttons to top
        layout.addStretch()
    
    def create_tool_button(self, tool_name: str, icon_text: str, tooltip: str):
        """Create a tool button"""
        button = QPushButton(icon_text)
        button.setToolTip(tooltip)
        button.setCheckable(True)
        button.setFixedSize(50, 50)
        button.setProperty("tool_name", tool_name)
        
        # Style the button
        button.setStyleSheet("""
            QPushButton {
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #f0f0f0;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:checked {
                background-color: #0078d4;
                color: white;
                border-color: #005a9e;
            }
        """)
        
        self.button_group.addButton(button)
        self.layout().addWidget(button)
        
        # Set brush as default
        if tool_name == "brush":
            button.setChecked(True)
    
    def setup_connections(self):
        """Setup signal connections"""
        self.button_group.buttonClicked.connect(self.on_tool_selected)
    
    def on_tool_selected(self, button):
        """Handle tool selection"""
        tool_name = button.property("tool_name")
        self.tool_manager.set_tool(tool_name) 