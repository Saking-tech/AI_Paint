# NextGenPaint

A modern, high-performance digital painting application built with Python and C++.

## Features

- **High-Performance Canvas**: C++ core with Python bindings for fast image processing
- **Layer System**: Full layer management with blending modes and opacity control
- **Professional Tools**: Brush, Eraser, Selection, and more tools
- **File Support**: Open and save various image formats
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Fallback Mode**: Works without C++ bindings using pure Python/OpenCV

## Quick Start

### Prerequisites

- Python 3.10 or higher
- OpenCV (`pip install opencv-python`)
- NumPy (`pip install numpy`)

### Optional Dependencies

- **PySide6**: For full GUI support (`pip install PySide6`)
- **MSYS2**: For building C++ bindings (Windows)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd NextGenPaint
   ```

2. **Install Python dependencies**:
   ```bash
   pip install opencv-python numpy
   ```

3. **Run the application**:
   ```bash
   python src/python/ngpaint/main.py
   ```

## Project Structure

```
NextGenPaint/
├── src/
│   ├── cpp/                    # C++ core implementation
│   │   ├── include/            # Header files
│   │   ├── core/               # Core C++ classes
│   │   ├── plugins/            # C++ plugins
│   │   └── bindings/           # Python bindings
│   └── python/                 # Python application
│       └── ngpaint/
│           ├── core/           # Core Python modules
│           ├── gui/            # GUI components
│           └── plugins/        # Python plugins
├── build_msys2.py             # Build script for MSYS2
├── CMakeLists.txt             # CMake configuration
└── README.md                  # This file
```

## Building C++ Bindings (Optional)

For optimal performance, build the C++ bindings:

### Windows (MSYS2)

1. **Install MSYS2** from https://www.msys2.org/
2. **Install dependencies**:
   ```bash
   pacman -S mingw-w64-x86_64-gcc mingw-w64-x86_64-cmake mingw-w64-x86_64-opencv
   ```
3. **Build bindings**:
   ```bash
   python build_msys2.py
   ```

### Linux/macOS

1. **Install dependencies**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install build-essential cmake libopencv-dev
   
   # macOS
   brew install cmake opencv
   ```
2. **Build bindings**:
   ```bash
   mkdir build && cd build
   cmake ..
   make
   ```

## Usage

### Basic Operations

```python
from src.python.ngpaint.core import Document

# Create a new document
doc = Document()
doc.new_document(1920, 1080)

# Add a layer
doc.add_layer("My Layer")

# Draw on the active layer
doc.draw_brush_stroke([(100, 100), (200, 200)], size=10, opacity=1.0, color=(255, 0, 0, 255))

# Save the document
doc.save_document_as("my_painting.png")
```

### Tool System

```python
from src.python.ngpaint.core import BrushTool, EraserTool

# Create tools
brush = BrushTool()
eraser = EraserTool()

# Configure brush
brush.set_property('size', 20)
brush.set_property('color', (0, 255, 0, 255))
```

## Development

### Running Tests

```bash
python -c "import sys; sys.path.insert(0, 'src/python/ngpaint'); from core import Document; print('✓ All tests passed!')"
```

### Adding New Tools

1. Create a new tool class inheriting from `Tool`
2. Implement required methods: `mouse_press`, `mouse_move`, `mouse_release`, `draw_preview`
3. Register the tool in `ToolManager`

### Adding New Filters

1. Create a new filter function in C++ or Python
2. Add filter parameters to `FilterParams`
3. Register the filter in the appropriate system

## Troubleshooting

### Import Errors

If you see import errors:

1. **C++ bindings**: The application works in fallback mode without C++ bindings
2. **PySide6**: Install with `pip install PySide6` for full GUI
3. **OpenCV**: Install with `pip install opencv-python`

### Performance Issues

- **Use C++ bindings**: Build and use C++ bindings for better performance
- **Reduce canvas size**: Smaller canvases are faster to process
- **Limit undo steps**: Reduce `max_undo_steps` in settings

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenCV for image processing
- NumPy for numerical operations
- PySide6 for GUI framework
- MSYS2 for Windows build environment 