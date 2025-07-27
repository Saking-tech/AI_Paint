"""
Filters panel for applying image effects and adjustments
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, 
    QPushButton, QComboBox, QSpinBox, QDoubleSpinBox,
    QGroupBox, QCheckBox, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont


class FiltersPanel(QWidget):
    """Panel for applying image filters and effects"""
    
    filter_applied = Signal(str, dict)  # filter_name, parameters
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_connections()
        
        # Preview timer for live updates
        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self.apply_preview_filter)
    
    def setup_ui(self):
        """Setup the filters panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Title
        title = QLabel("Filters & Effects")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Scroll area for filters
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        layout.addWidget(scroll_area)
        
        # Filters container
        filters_widget = QWidget()
        self.filters_layout = QVBoxLayout(filters_widget)
        self.filters_layout.setSpacing(12)
        scroll_area.setWidget(filters_widget)
        
        # Add filter sections
        self.add_blur_filters()
        self.add_sharpen_filters()
        self.add_adjustment_filters()
        self.add_artistic_filters()
        
        # Apply button
        self.apply_button = QPushButton("Apply Filter")
        self.apply_button.setEnabled(False)
        layout.addWidget(self.apply_button)
    
    def add_blur_filters(self):
        """Add blur filter controls"""
        group = QGroupBox("Blur")
        layout = QVBoxLayout(group)
        
        # Gaussian Blur
        gaussian_frame = QFrame()
        gaussian_frame.setFrameStyle(QFrame.StyledPanel)
        gaussian_layout = QVBoxLayout(gaussian_frame)
        
        gaussian_label = QLabel("Gaussian Blur")
        gaussian_layout.addWidget(gaussian_label)
        
        # Radius slider
        radius_layout = QHBoxLayout()
        radius_layout.addWidget(QLabel("Radius:"))
        self.gaussian_radius = QSlider(Qt.Horizontal)
        self.gaussian_radius.setRange(1, 50)
        self.gaussian_radius.setValue(5)
        radius_layout.addWidget(self.gaussian_radius)
        self.gaussian_radius_value = QSpinBox()
        self.gaussian_radius_value.setRange(1, 50)
        self.gaussian_radius_value.setValue(5)
        radius_layout.addWidget(self.gaussian_radius_value)
        gaussian_layout.addLayout(radius_layout)
        
        # Apply button
        self.gaussian_apply = QPushButton("Apply Gaussian Blur")
        gaussian_layout.addWidget(self.gaussian_apply)
        
        layout.addWidget(gaussian_frame)
        self.filters_layout.addWidget(group)
    
    def add_sharpen_filters(self):
        """Add sharpen filter controls"""
        group = QGroupBox("Sharpen")
        layout = QVBoxLayout(group)
        
        # Unsharp Mask
        unsharp_frame = QFrame()
        unsharp_frame.setFrameStyle(QFrame.StyledPanel)
        unsharp_layout = QVBoxLayout(unsharp_frame)
        
        unsharp_label = QLabel("Unsharp Mask")
        unsharp_layout.addWidget(unsharp_label)
        
        # Radius slider
        radius_layout = QHBoxLayout()
        radius_layout.addWidget(QLabel("Radius:"))
        self.unsharp_radius = QSlider(Qt.Horizontal)
        self.unsharp_radius.setRange(1, 20)
        self.unsharp_radius.setValue(3)
        radius_layout.addWidget(self.unsharp_radius)
        self.unsharp_radius_value = QSpinBox()
        self.unsharp_radius_value.setRange(1, 20)
        self.unsharp_radius_value.setValue(3)
        radius_layout.addWidget(self.unsharp_radius_value)
        unsharp_layout.addLayout(radius_layout)
        
        # Amount slider
        amount_layout = QHBoxLayout()
        amount_layout.addWidget(QLabel("Amount:"))
        self.unsharp_amount = QSlider(Qt.Horizontal)
        self.unsharp_amount.setRange(0, 200)
        self.unsharp_amount.setValue(100)
        amount_layout.addWidget(self.unsharp_amount)
        self.unsharp_amount_value = QSpinBox()
        self.unsharp_amount_value.setRange(0, 200)
        self.unsharp_amount_value.setValue(100)
        amount_layout.addWidget(self.unsharp_amount_value)
        unsharp_layout.addLayout(amount_layout)
        
        # Threshold slider
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Threshold:"))
        self.unsharp_threshold = QSlider(Qt.Horizontal)
        self.unsharp_threshold.setRange(0, 255)
        self.unsharp_threshold.setValue(0)
        threshold_layout.addWidget(self.unsharp_threshold)
        self.unsharp_threshold_value = QSpinBox()
        self.unsharp_threshold_value.setRange(0, 255)
        self.unsharp_threshold_value.setValue(0)
        threshold_layout.addWidget(self.unsharp_threshold_value)
        unsharp_layout.addLayout(threshold_layout)
        
        # Apply button
        self.unsharp_apply = QPushButton("Apply Unsharp Mask")
        unsharp_layout.addWidget(self.unsharp_apply)
        
        layout.addWidget(unsharp_frame)
        self.filters_layout.addWidget(group)
    
    def add_adjustment_filters(self):
        """Add adjustment filter controls"""
        group = QGroupBox("Adjustments")
        layout = QVBoxLayout(group)
        
        # Brightness/Contrast
        bc_frame = QFrame()
        bc_frame.setFrameStyle(QFrame.StyledPanel)
        bc_layout = QVBoxLayout(bc_frame)
        
        bc_label = QLabel("Brightness & Contrast")
        bc_layout.addWidget(bc_label)
        
        # Brightness slider
        brightness_layout = QHBoxLayout()
        brightness_layout.addWidget(QLabel("Brightness:"))
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(0)
        brightness_layout.addWidget(self.brightness_slider)
        self.brightness_value = QSpinBox()
        self.brightness_value.setRange(-100, 100)
        self.brightness_value.setValue(0)
        brightness_layout.addWidget(self.brightness_value)
        bc_layout.addLayout(brightness_layout)
        
        # Contrast slider
        contrast_layout = QHBoxLayout()
        contrast_layout.addWidget(QLabel("Contrast:"))
        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(-100, 100)
        self.contrast_slider.setValue(0)
        contrast_layout.addWidget(self.contrast_slider)
        self.contrast_value = QSpinBox()
        self.contrast_value.setRange(-100, 100)
        self.contrast_value.setValue(0)
        contrast_layout.addWidget(self.contrast_value)
        bc_layout.addLayout(contrast_layout)
        
        # Apply button
        self.bc_apply = QPushButton("Apply Brightness/Contrast")
        bc_layout.addWidget(self.bc_apply)
        
        layout.addWidget(bc_frame)
        self.filters_layout.addWidget(group)
    
    def add_artistic_filters(self):
        """Add artistic filter controls"""
        group = QGroupBox("Artistic")
        layout = QVBoxLayout(group)
        
        # Inpaint
        inpaint_frame = QFrame()
        inpaint_frame.setFrameStyle(QFrame.StyledPanel)
        inpaint_layout = QVBoxLayout(inpaint_frame)
        
        inpaint_label = QLabel("Inpaint (Object Removal)")
        inpaint_layout.addWidget(inpaint_label)
        
        # Method selection
        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("Method:"))
        self.inpaint_method = QComboBox()
        self.inpaint_method.addItems(["Telea", "NS"])
        method_layout.addWidget(self.inpaint_method)
        inpaint_layout.addLayout(method_layout)
        
        # Radius slider
        inpaint_radius_layout = QHBoxLayout()
        inpaint_radius_layout.addWidget(QLabel("Radius:"))
        self.inpaint_radius = QSlider(Qt.Horizontal)
        self.inpaint_radius.setRange(1, 20)
        self.inpaint_radius.setValue(3)
        inpaint_radius_layout.addWidget(self.inpaint_radius)
        self.inpaint_radius_value = QSpinBox()
        self.inpaint_radius_value.setRange(1, 20)
        self.inpaint_radius_value.setValue(3)
        inpaint_radius_layout.addWidget(self.inpaint_radius_value)
        inpaint_layout.addLayout(inpaint_radius_layout)
        
        # Apply button
        self.inpaint_apply = QPushButton("Apply Inpaint")
        inpaint_layout.addWidget(self.inpaint_apply)
        
        layout.addWidget(inpaint_frame)
        self.filters_layout.addWidget(group)
    
    def setup_connections(self):
        """Setup signal connections"""
        # Connect sliders to spinboxes
        self.gaussian_radius.valueChanged.connect(self.gaussian_radius_value.setValue)
        self.gaussian_radius_value.valueChanged.connect(self.gaussian_radius.setValue)
        
        self.unsharp_radius.valueChanged.connect(self.unsharp_radius_value.setValue)
        self.unsharp_radius_value.valueChanged.connect(self.unsharp_radius.setValue)
        
        self.unsharp_amount.valueChanged.connect(self.unsharp_amount_value.setValue)
        self.unsharp_amount_value.valueChanged.connect(self.unsharp_amount.setValue)
        
        self.unsharp_threshold.valueChanged.connect(self.unsharp_threshold_value.setValue)
        self.unsharp_threshold_value.valueChanged.connect(self.unsharp_threshold.setValue)
        
        self.brightness_slider.valueChanged.connect(self.brightness_value.setValue)
        self.brightness_value.valueChanged.connect(self.brightness_slider.setValue)
        
        self.contrast_slider.valueChanged.connect(self.contrast_value.setValue)
        self.contrast_value.valueChanged.connect(self.contrast_slider.setValue)
        
        self.inpaint_radius.valueChanged.connect(self.inpaint_radius_value.setValue)
        self.inpaint_radius_value.valueChanged.connect(self.inpaint_radius.setValue)
        
        # Connect apply buttons
        self.gaussian_apply.clicked.connect(self.apply_gaussian_blur)
        self.unsharp_apply.clicked.connect(self.apply_unsharp_mask)
        self.bc_apply.clicked.connect(self.apply_brightness_contrast)
        self.inpaint_apply.clicked.connect(self.apply_inpaint)
        
        # Connect sliders to preview timer
        sliders = [
            self.gaussian_radius, self.unsharp_radius, self.unsharp_amount,
            self.unsharp_threshold, self.brightness_slider, self.contrast_slider,
            self.inpaint_radius
        ]
        for slider in sliders:
            slider.valueChanged.connect(self.start_preview_timer)
    
    def start_preview_timer(self):
        """Start the preview timer for live updates"""
        self.preview_timer.start(300)  # 300ms delay
    
    def apply_preview_filter(self):
        """Apply filter for preview (non-destructive)"""
        # This would apply the filter to a preview layer
        # For now, just enable the apply button
        self.apply_button.setEnabled(True)
    
    def apply_gaussian_blur(self):
        """Apply Gaussian blur filter"""
        params = {
            'radius': self.gaussian_radius.value()
        }
        self.filter_applied.emit('gaussian_blur', params)
    
    def apply_unsharp_mask(self):
        """Apply unsharp mask filter"""
        params = {
            'radius': self.unsharp_radius.value(),
            'amount': self.unsharp_amount.value() / 100.0,
            'threshold': self.unsharp_threshold.value()
        }
        self.filter_applied.emit('unsharp_mask', params)
    
    def apply_brightness_contrast(self):
        """Apply brightness/contrast adjustment"""
        params = {
            'brightness': self.brightness_slider.value(),
            'contrast': self.contrast_slider.value()
        }
        self.filter_applied.emit('brightness_contrast', params)
    
    def apply_inpaint(self):
        """Apply inpaint filter"""
        params = {
            'method': self.inpaint_method.currentText().lower(),
            'radius': self.inpaint_radius.value()
        }
        self.filter_applied.emit('inpaint', params)
    
    def reset_all_filters(self):
        """Reset all filter controls to default values"""
        self.gaussian_radius.setValue(5)
        self.unsharp_radius.setValue(3)
        self.unsharp_amount.setValue(100)
        self.unsharp_threshold.setValue(0)
        self.brightness_slider.setValue(0)
        self.contrast_slider.setValue(0)
        self.inpaint_radius.setValue(3)
        self.inpaint_method.setCurrentIndex(0) 