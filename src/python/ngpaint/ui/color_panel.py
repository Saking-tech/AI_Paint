"""
Color panel for color selection
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPalette

class ColorPanel(QWidget):
    """Panel for color selection"""
    
    # Signals
    color_changed = Signal(tuple)
    
    def __init__(self):
        super().__init__()
        self.current_color = (255, 0, 0, 255)  # Red
        
        self.setup_ui()
        self.update_color_display()
        
        # Set panel properties
        self.setMaximumWidth(200)
        self.setMinimumWidth(200)
    
    def setup_ui(self):
        """Setup the UI layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("Color")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # Color display
        self.color_display = QPushButton()
        self.color_display.setFixedSize(80, 80)
        self.color_display.setStyleSheet("border: 2px solid #ccc; border-radius: 5px;")
        layout.addWidget(self.color_display, alignment=Qt.AlignCenter)
        
        # Color sliders
        self.create_color_slider("Red", 0, 255, 255, self.on_red_changed)
        self.create_color_slider("Green", 0, 255, 0, self.on_green_changed)
        self.create_color_slider("Blue", 0, 255, 0, self.on_blue_changed)
        self.create_color_slider("Alpha", 0, 255, 255, self.on_alpha_changed)
        
        # Preset colors
        self.create_preset_colors()
    
    def create_color_slider(self, name: str, min_val: int, max_val: int, default: int, callback):
        """Create a color slider"""
        layout = QHBoxLayout()
        
        label = QLabel(name)
        label.setFixedWidth(40)
        layout.addWidget(label)
        
        slider = QSlider(Qt.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(default)
        slider.valueChanged.connect(callback)
        layout.addWidget(slider)
        
        value_label = QLabel(str(default))
        value_label.setFixedWidth(30)
        value_label.setAlignment(Qt.AlignRight)
        layout.addWidget(value_label)
        
        self.layout().addLayout(layout)
        
        # Store references
        setattr(self, f"{name.lower()}_slider", slider)
        setattr(self, f"{name.lower()}_label", value_label)
    
    def create_preset_colors(self):
        """Create preset color buttons"""
        # Title for presets
        preset_title = QLabel("Presets")
        preset_title.setStyleSheet("font-weight: bold; font-size: 12px;")
        self.layout().addWidget(preset_title)
        
        # First row of presets
        layout1 = QHBoxLayout()
        preset_colors1 = [
            (255, 0, 0, 255),    # Red
            (0, 255, 0, 255),    # Green
            (0, 0, 255, 255),    # Blue
            (255, 255, 0, 255),  # Yellow
        ]
        
        for color in preset_colors1:
            button = QPushButton()
            button.setFixedSize(25, 25)
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgb({color[0]}, {color[1]}, {color[2]});
                    border: 1px solid #ccc;
                    border-radius: 3px;
                }}
                QPushButton:hover {{
                    border: 2px solid #0078d4;
                }}
            """)
            button.clicked.connect(lambda checked, c=color: self.set_color(c))
            layout1.addWidget(button)
        
        self.layout().addLayout(layout1)
        
        # Second row of presets
        layout2 = QHBoxLayout()
        preset_colors2 = [
            (255, 0, 255, 255),  # Magenta
            (0, 255, 255, 255),  # Cyan
            (0, 0, 0, 255),      # Black
            (255, 255, 255, 255) # White
        ]
        
        for color in preset_colors2:
            button = QPushButton()
            button.setFixedSize(25, 25)
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgb({color[0]}, {color[1]}, {color[2]});
                    border: 1px solid #ccc;
                    border-radius: 3px;
                }}
                QPushButton:hover {{
                    border: 2px solid #0078d4;
                }}
            """)
            button.clicked.connect(lambda checked, c=color: self.set_color(c))
            layout2.addWidget(button)
        
        self.layout().addLayout(layout2)
    
    def on_red_changed(self, value):
        """Handle red slider change"""
        self.current_color = (value, self.current_color[1], self.current_color[2], self.current_color[3])
        self.red_label.setText(str(value))
        self.update_color_display()
        self.color_changed.emit(self.current_color)
    
    def on_green_changed(self, value):
        """Handle green slider change"""
        self.current_color = (self.current_color[0], value, self.current_color[2], self.current_color[3])
        self.green_label.setText(str(value))
        self.update_color_display()
        self.color_changed.emit(self.current_color)
    
    def on_blue_changed(self, value):
        """Handle blue slider change"""
        self.current_color = (self.current_color[0], self.current_color[1], value, self.current_color[3])
        self.blue_label.setText(str(value))
        self.update_color_display()
        self.color_changed.emit(self.current_color)
    
    def on_alpha_changed(self, value):
        """Handle alpha slider change"""
        self.current_color = (self.current_color[0], self.current_color[1], self.current_color[2], value)
        self.alpha_label.setText(str(value))
        self.update_color_display()
        self.color_changed.emit(self.current_color)
    
    def set_color(self, color: tuple):
        """Set the current color"""
        self.current_color = color
        
        # Update sliders
        self.red_slider.setValue(color[0])
        self.green_slider.setValue(color[1])
        self.blue_slider.setValue(color[2])
        self.alpha_slider.setValue(color[3])
        
        # Update labels
        self.red_label.setText(str(color[0]))
        self.green_label.setText(str(color[1]))
        self.blue_label.setText(str(color[2]))
        self.alpha_label.setText(str(color[3]))
        
        self.update_color_display()
        self.color_changed.emit(self.current_color)
    
    def get_color(self) -> tuple:
        """Get the current color"""
        return self.current_color
    
    def update_color_display(self):
        """Update the color display button"""
        r, g, b, a = self.current_color
        alpha = a / 255.0
        
        # Create background with transparency
        style = f"""
            QPushButton {{
                background-color: rgba({r}, {g}, {b}, {alpha});
                border: 2px solid #ccc;
                border-radius: 5px;
            }}
        """
        self.color_display.setStyleSheet(style) 