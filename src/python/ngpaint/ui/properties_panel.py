"""
Properties panel for tool properties
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel, 
    QDoubleSpinBox, QSpinBox, QComboBox, QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt, Signal

class PropertiesPanel(QWidget):
    """Panel for tool properties"""
    
    # Signals
    property_changed = Signal(str, object)
    
    def __init__(self):
        super().__init__()
        self.current_tool = None
        
        self.setup_ui()
        
        # Set panel properties
        self.setMaximumWidth(200)
        self.setMinimumWidth(200)
    
    def setup_ui(self):
        """Setup the UI layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("Properties")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # Tool properties group
        self.tool_group = QGroupBox("Tool Properties")
        self.tool_layout = QFormLayout(self.tool_group)
        layout.addWidget(self.tool_group)
        
        # Create default properties
        self.create_brush_properties()
        
        layout.addStretch()
    
    def create_brush_properties(self):
        """Create brush tool properties"""
        # Size slider
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(1, 100)
        self.size_slider.setValue(10)
        self.size_slider.valueChanged.connect(lambda v: self.on_property_changed('size', v))
        
        self.size_spinbox = QSpinBox()
        self.size_spinbox.setRange(1, 100)
        self.size_spinbox.setValue(10)
        self.size_spinbox.valueChanged.connect(lambda v: self.on_property_changed('size', v))
        
        size_layout = QHBoxLayout()
        size_layout.addWidget(self.size_slider)
        size_layout.addWidget(self.size_spinbox)
        
        self.tool_layout.addRow("Size:", size_layout)
        
        # Opacity slider
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.valueChanged.connect(lambda v: self.on_property_changed('opacity', v / 100.0))
        
        self.opacity_spinbox = QDoubleSpinBox()
        self.opacity_spinbox.setRange(0.0, 1.0)
        self.opacity_spinbox.setSingleStep(0.1)
        self.opacity_spinbox.setValue(1.0)
        self.opacity_spinbox.valueChanged.connect(lambda v: self.on_property_changed('opacity', v))
        
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(self.opacity_spinbox)
        
        self.tool_layout.addRow("Opacity:", opacity_layout)
        
        # Hardness slider
        self.hardness_slider = QSlider(Qt.Horizontal)
        self.hardness_slider.setRange(0, 100)
        self.hardness_slider.setValue(50)
        self.hardness_slider.valueChanged.connect(lambda v: self.on_property_changed('hardness', v / 100.0))
        
        self.hardness_spinbox = QDoubleSpinBox()
        self.hardness_spinbox.setRange(0.0, 1.0)
        self.hardness_spinbox.setSingleStep(0.1)
        self.hardness_spinbox.setValue(0.5)
        self.hardness_spinbox.valueChanged.connect(lambda v: self.on_property_changed('hardness', v))
        
        hardness_layout = QHBoxLayout()
        hardness_layout.addWidget(self.hardness_slider)
        hardness_layout.addWidget(self.hardness_spinbox)
        
        self.tool_layout.addRow("Hardness:", hardness_layout)
        
        # Spacing slider
        self.spacing_slider = QSlider(Qt.Horizontal)
        self.spacing_slider.setRange(1, 100)
        self.spacing_slider.setValue(25)
        self.spacing_slider.valueChanged.connect(lambda v: self.on_property_changed('spacing', v / 100.0))
        
        self.spacing_spinbox = QDoubleSpinBox()
        self.spacing_spinbox.setRange(0.01, 1.0)
        self.spacing_spinbox.setSingleStep(0.01)
        self.spacing_spinbox.setValue(0.25)
        self.spacing_spinbox.valueChanged.connect(lambda v: self.on_property_changed('spacing', v))
        
        spacing_layout = QHBoxLayout()
        spacing_layout.addWidget(self.spacing_slider)
        spacing_layout.addWidget(self.spacing_spinbox)
        
        self.tool_layout.addRow("Spacing:", spacing_layout)
    
    def create_eraser_properties(self):
        """Create eraser tool properties"""
        # Clear existing properties
        while self.tool_layout.rowCount() > 0:
            self.tool_layout.removeRow(0)
        
        # Size slider
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(1, 100)
        self.size_slider.setValue(20)
        self.size_slider.valueChanged.connect(lambda v: self.on_property_changed('size', v))
        
        self.size_spinbox = QSpinBox()
        self.size_spinbox.setRange(1, 100)
        self.size_spinbox.setValue(20)
        self.size_spinbox.valueChanged.connect(lambda v: self.on_property_changed('size', v))
        
        size_layout = QHBoxLayout()
        size_layout.addWidget(self.size_slider)
        size_layout.addWidget(self.size_spinbox)
        
        self.tool_layout.addRow("Size:", size_layout)
        
        # Opacity slider
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.valueChanged.connect(lambda v: self.on_property_changed('opacity', v / 100.0))
        
        self.opacity_spinbox = QDoubleSpinBox()
        self.opacity_spinbox.setRange(0.0, 1.0)
        self.opacity_spinbox.setSingleStep(0.1)
        self.opacity_spinbox.setValue(1.0)
        self.opacity_spinbox.valueChanged.connect(lambda v: self.on_property_changed('opacity', v))
        
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(self.opacity_spinbox)
        
        self.tool_layout.addRow("Opacity:", opacity_layout)
        
        # Hardness slider
        self.hardness_slider = QSlider(Qt.Horizontal)
        self.hardness_slider.setRange(0, 100)
        self.hardness_slider.setValue(50)
        self.hardness_slider.valueChanged.connect(lambda v: self.on_property_changed('hardness', v / 100.0))
        
        self.hardness_spinbox = QDoubleSpinBox()
        self.hardness_spinbox.setRange(0.0, 1.0)
        self.hardness_spinbox.setSingleStep(0.1)
        self.hardness_spinbox.setValue(0.5)
        self.hardness_spinbox.valueChanged.connect(lambda v: self.on_property_changed('hardness', v))
        
        hardness_layout = QHBoxLayout()
        hardness_layout.addWidget(self.hardness_slider)
        hardness_layout.addWidget(self.hardness_spinbox)
        
        self.tool_layout.addRow("Hardness:", hardness_layout)
    
    def create_smudge_properties(self):
        """Create smudge tool properties"""
        # Clear existing properties
        while self.tool_layout.rowCount() > 0:
            self.tool_layout.removeRow(0)
        
        # Size slider
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(1, 100)
        self.size_slider.setValue(15)
        self.size_slider.valueChanged.connect(lambda v: self.on_property_changed('size', v))
        
        self.size_spinbox = QSpinBox()
        self.size_spinbox.setRange(1, 100)
        self.size_spinbox.setValue(15)
        self.size_spinbox.valueChanged.connect(lambda v: self.on_property_changed('size', v))
        
        size_layout = QHBoxLayout()
        size_layout.addWidget(self.size_slider)
        size_layout.addWidget(self.size_spinbox)
        
        self.tool_layout.addRow("Size:", size_layout)
        
        # Strength slider
        self.strength_slider = QSlider(Qt.Horizontal)
        self.strength_slider.setRange(0, 100)
        self.strength_slider.setValue(50)
        self.strength_slider.valueChanged.connect(lambda v: self.on_property_changed('strength', v / 100.0))
        
        self.strength_spinbox = QDoubleSpinBox()
        self.strength_spinbox.setRange(0.0, 1.0)
        self.strength_spinbox.setSingleStep(0.1)
        self.strength_spinbox.setValue(0.5)
        self.strength_spinbox.valueChanged.connect(lambda v: self.on_property_changed('strength', v))
        
        strength_layout = QHBoxLayout()
        strength_layout.addWidget(self.strength_slider)
        strength_layout.addWidget(self.strength_spinbox)
        
        self.tool_layout.addRow("Strength:", strength_layout)
        
        # Opacity slider
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(80)
        self.opacity_slider.valueChanged.connect(lambda v: self.on_property_changed('opacity', v / 100.0))
        
        self.opacity_spinbox = QDoubleSpinBox()
        self.opacity_spinbox.setRange(0.0, 1.0)
        self.opacity_spinbox.setSingleStep(0.1)
        self.opacity_spinbox.setValue(0.8)
        self.opacity_spinbox.valueChanged.connect(lambda v: self.on_property_changed('opacity', v))
        
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(self.opacity_spinbox)
        
        self.tool_layout.addRow("Opacity:", opacity_layout)
    
    def create_selection_properties(self):
        """Create selection tool properties"""
        # Clear existing properties
        while self.tool_layout.rowCount() > 0:
            self.tool_layout.removeRow(0)
        
        # Feather slider
        self.feather_slider = QSlider(Qt.Horizontal)
        self.feather_slider.setRange(0, 50)
        self.feather_slider.setValue(0)
        self.feather_slider.valueChanged.connect(lambda v: self.on_property_changed('feather', v))
        
        self.feather_spinbox = QSpinBox()
        self.feather_spinbox.setRange(0, 50)
        self.feather_spinbox.setValue(0)
        self.feather_spinbox.valueChanged.connect(lambda v: self.on_property_changed('feather', v))
        
        feather_layout = QHBoxLayout()
        feather_layout.addWidget(self.feather_slider)
        feather_layout.addWidget(self.feather_spinbox)
        
        self.tool_layout.addRow("Feather:", feather_layout)
        
        # Mode combo box
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Replace", "Add", "Subtract", "Intersect"])
        self.mode_combo.currentTextChanged.connect(lambda v: self.on_property_changed('mode', v.lower()))
        
        self.tool_layout.addRow("Mode:", self.mode_combo)
    
    def set_tool(self, tool):
        """Set the current tool and update properties"""
        self.current_tool = tool
        
        if tool is None:
            return
        
        tool_name = tool.name.lower()
        
        # Update properties based on tool type
        if "brush" in tool_name:
            self.create_brush_properties()
        elif "eraser" in tool_name:
            self.create_eraser_properties()
        elif "smudge" in tool_name:
            self.create_smudge_properties()
        elif "selection" in tool_name:
            self.create_selection_properties()
        
        # Update property values
        self.update_property_values()
    
    def update_property_values(self):
        """Update property values from current tool"""
        if not self.current_tool:
            return
        
        # Update size
        if hasattr(self, 'size_slider'):
            size = self.current_tool.get_property('size', 10)
            self.size_slider.setValue(int(size))
            if hasattr(self, 'size_spinbox'):
                self.size_spinbox.setValue(int(size))
        
        # Update opacity
        if hasattr(self, 'opacity_slider'):
            opacity = self.current_tool.get_property('opacity', 1.0)
            self.opacity_slider.setValue(int(opacity * 100))
            if hasattr(self, 'opacity_spinbox'):
                self.opacity_spinbox.setValue(opacity)
        
        # Update hardness
        if hasattr(self, 'hardness_slider'):
            hardness = self.current_tool.get_property('hardness', 0.5)
            self.hardness_slider.setValue(int(hardness * 100))
            if hasattr(self, 'hardness_spinbox'):
                self.hardness_spinbox.setValue(hardness)
        
        # Update spacing
        if hasattr(self, 'spacing_slider'):
            spacing = self.current_tool.get_property('spacing', 0.25)
            self.spacing_slider.setValue(int(spacing * 100))
            if hasattr(self, 'spacing_spinbox'):
                self.spacing_spinbox.setValue(spacing)
        
        # Update strength
        if hasattr(self, 'strength_slider'):
            strength = self.current_tool.get_property('strength', 0.5)
            self.strength_slider.setValue(int(strength * 100))
            if hasattr(self, 'strength_spinbox'):
                self.strength_spinbox.setValue(strength)
        
        # Update feather
        if hasattr(self, 'feather_slider'):
            feather = self.current_tool.get_property('feather', 0)
            self.feather_slider.setValue(feather)
            if hasattr(self, 'feather_spinbox'):
                self.feather_spinbox.setValue(feather)
        
        # Update mode
        if hasattr(self, 'mode_combo'):
            mode = self.current_tool.get_property('mode', 'replace')
            index = self.mode_combo.findText(mode.capitalize())
            if index >= 0:
                self.mode_combo.setCurrentIndex(index)
    
    def on_property_changed(self, name: str, value):
        """Handle property change"""
        if self.current_tool:
            self.current_tool.set_property(name, value)
            self.property_changed.emit(name, value) 