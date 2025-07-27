"""
Layers panel for layer management
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, 
    QListWidgetItem, QSlider, QLabel, QComboBox, QCheckBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon

from ..core.document import Document

class LayersPanel(QWidget):
    """Panel for layer management"""
    
    # Signals
    layer_selected = Signal(int)
    
    def __init__(self, document: Document):
        super().__init__()
        self.document = document
        self.layer_items = []
        
        self.setup_ui()
        self.setup_connections()
        
        # Set panel properties
        self.setMaximumWidth(250)
        self.setMinimumWidth(200)
    
    def setup_ui(self):
        """Setup the UI layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("Layers")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # Layer list
        self.layer_list = QListWidget()
        self.layer_list.setAlternatingRowColors(True)
        layout.addWidget(self.layer_list)
        
        # Layer controls
        self.create_layer_controls()
        
        # Layer properties
        self.create_layer_properties()
    
    def create_layer_controls(self):
        """Create layer control buttons"""
        controls_layout = QHBoxLayout()
        
        # Add layer button
        add_button = QPushButton("+")
        add_button.setToolTip("Add Layer")
        add_button.setFixedSize(30, 30)
        add_button.clicked.connect(self.add_layer)
        controls_layout.addWidget(add_button)
        
        # Delete layer button
        delete_button = QPushButton("-")
        delete_button.setToolTip("Delete Layer")
        delete_button.setFixedSize(30, 30)
        delete_button.clicked.connect(self.delete_layer)
        controls_layout.addWidget(delete_button)
        
        # Move up button
        up_button = QPushButton("↑")
        up_button.setToolTip("Move Layer Up")
        up_button.setFixedSize(30, 30)
        up_button.clicked.connect(self.move_layer_up)
        controls_layout.addWidget(up_button)
        
        # Move down button
        down_button = QPushButton("↓")
        down_button.setToolTip("Move Layer Down")
        down_button.setFixedSize(30, 30)
        down_button.clicked.connect(self.move_layer_down)
        controls_layout.addWidget(down_button)
        
        controls_layout.addStretch()
        self.layout().addLayout(controls_layout)
    
    def create_layer_properties(self):
        """Create layer property controls"""
        # Opacity slider
        opacity_layout = QHBoxLayout()
        opacity_label = QLabel("Opacity:")
        opacity_label.setFixedWidth(50)
        opacity_layout.addWidget(opacity_label)
        
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.valueChanged.connect(self.on_opacity_changed)
        opacity_layout.addWidget(self.opacity_slider)
        
        self.opacity_value = QLabel("100%")
        self.opacity_value.setFixedWidth(40)
        opacity_layout.addWidget(self.opacity_value)
        
        self.layout().addLayout(opacity_layout)
        
        # Blend mode combo box
        blend_layout = QHBoxLayout()
        blend_label = QLabel("Blend:")
        blend_label.setFixedWidth(50)
        blend_layout.addWidget(blend_label)
        
        self.blend_mode_combo = QComboBox()
        self.blend_mode_combo.addItems(["Normal", "Multiply", "Screen", "Overlay", "Soft Light", "Hard Light"])
        self.blend_mode_combo.currentTextChanged.connect(self.on_blend_mode_changed)
        blend_layout.addWidget(self.blend_mode_combo)
        
        self.layout().addLayout(blend_layout)
        
        # Visibility checkbox
        self.visibility_checkbox = QCheckBox("Visible")
        self.visibility_checkbox.setChecked(True)
        self.visibility_checkbox.toggled.connect(self.on_visibility_changed)
        self.layout().addWidget(self.visibility_checkbox)
    
    def setup_connections(self):
        """Setup signal connections"""
        self.layer_list.currentRowChanged.connect(self.on_layer_selected)
    
    def update_layers(self):
        """Update the layer list"""
        self.layer_list.clear()
        self.layer_items = []
        
        if not self.document:
            return
        
        # Get layer names from document
        layer_names = self.document.get_layer_names()
        
        # Create list items
        for i, name in enumerate(layer_names):
            item = QListWidgetItem(name)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)  # Default to visible
            
            # Highlight active layer
            if i == self.document.get_active_layer_index():
                item.setBackground(Qt.lightGray)
            
            self.layer_list.addItem(item)
            self.layer_items.append(item)
        
        # Update layer properties
        self.update_layer_properties()
    
    def add_layer(self):
        """Add a new layer"""
        if self.document:
            layer_name = f"Layer {self.document.get_layer_count() + 1}"
            if self.document.add_layer(layer_name):
                self.update_layers()
    
    def delete_layer(self):
        """Delete the selected layer"""
        if self.document and self.layer_list.currentRow() >= 0:
            if self.document.delete_active_layer():
                self.update_layers()
    
    def move_layer_up(self):
        """Move the selected layer up"""
        current_row = self.layer_list.currentRow()
        if current_row > 0:
            # TODO: Implement layer reordering in document
            pass
    
    def move_layer_down(self):
        """Move the selected layer down"""
        current_row = self.layer_list.currentRow()
        if current_row < self.layer_list.count() - 1:
            # TODO: Implement layer reordering in document
            pass
    
    def on_layer_selected(self, row: int):
        """Handle layer selection"""
        if row >= 0 and self.document:
            self.document.set_active_layer(row)
            self.layer_selected.emit(row)
            self.update_layer_properties()
    
    def update_layer_properties(self):
        """Update layer property controls"""
        active_index = self.document.get_active_layer_index() if self.document else -1
        
        if active_index >= 0 and hasattr(self.document, 'layers') and active_index < len(self.document.layers):
            layer = self.document.layers[active_index]
            
            # Update opacity slider
            opacity = int(layer.opacity * 100)
            self.opacity_slider.setValue(opacity)
            self.opacity_value.setText(f"{opacity}%")
            
            # Update blend mode combo
            blend_mode = layer.blend_mode.capitalize()
            index = self.blend_mode_combo.findText(blend_mode)
            if index >= 0:
                self.blend_mode_combo.setCurrentIndex(index)
            
            # Update visibility checkbox
            self.visibility_checkbox.setChecked(layer.visible)
        else:
            # Disable controls if no layer is selected
            self.opacity_slider.setEnabled(False)
            self.blend_mode_combo.setEnabled(False)
            self.visibility_checkbox.setEnabled(False)
    
    def on_opacity_changed(self, value: int):
        """Handle opacity slider change"""
        active_index = self.document.get_active_layer_index() if self.document else -1
        
        if active_index >= 0 and hasattr(self.document, 'layers') and active_index < len(self.document.layers):
            layer = self.document.layers[active_index]
            layer.opacity = value / 100.0
            self.opacity_value.setText(f"{value}%")
    
    def on_blend_mode_changed(self, mode: str):
        """Handle blend mode change"""
        active_index = self.document.get_active_layer_index() if self.document else -1
        
        if active_index >= 0 and hasattr(self.document, 'layers') and active_index < len(self.document.layers):
            layer = self.document.layers[active_index]
            layer.blend_mode = mode.lower().replace(" ", "_")
    
    def on_visibility_changed(self, visible: bool):
        """Handle visibility checkbox change"""
        active_index = self.document.get_active_layer_index() if self.document else -1
        
        if active_index >= 0 and hasattr(self.document, 'layers') and active_index < len(self.document.layers):
            layer = self.document.layers[active_index]
            layer.visible = visible 