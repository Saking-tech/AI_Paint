"""
Document class for managing canvas and file operations
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Optional, List, Tuple
import json
from datetime import datetime

# Import C++ bindings
try:
    import sys
    import os
    # Add the current directory (ngpaint) to Python path to find the module
    current_dir = os.path.dirname(os.path.abspath(__file__))  # core/
    parent_dir = os.path.dirname(current_dir)  # ngpaint/
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    import ngp_core_python as ngp
    print("Successfully imported C++ bindings")
except ImportError as e:
    # Fallback for development
    print(f"Warning: Could not import C++ bindings: {e}")
    print("This may be due to:")
    print("1. Python version mismatch (C++ bindings compiled for Python 3.12, but running Python 3.10)")
    print("2. Missing OpenCV DLLs")
    print("3. C++ bindings not built yet")
    print("Running in fallback mode with numpy-based implementation")
    print("To fix: rebuild C++ bindings with current Python version using: python build_msys2.py")
    ngp = None

class Layer:
    """Simple layer implementation for fallback mode"""
    
    def __init__(self, name: str, width: int, height: int):
        self.name = name
        self.visible = True
        self.opacity = 1.0
        self.blend_mode = "normal"
        self.image = np.zeros((height, width, 4), dtype=np.uint8)
        self.image[:, :, 3] = 0  # Transparent by default

class Document:
    """Document class for managing canvas and file operations"""
    
    def __init__(self):
        self.canvas_core = None
        self.file_path = None
        self.width = 1920
        self.height = 1080
        self.active_layer_index = 0
        self.layers = []
        self.undo_stack = []
        self.redo_stack = []
        self.max_undo_steps = 50
        
        # Initialize canvas core if available
        if ngp:
            self.canvas_core = ngp.CanvasCore(self.width, self.height)
        else:
            # Fallback: create a simple layer system
            self._create_fallback_canvas()
    
    def new_document(self, width: int, height: int):
        """Create a new document"""
        self.width = width
        self.height = height
        self.file_path = None
        self.layers = []
        self.undo_stack = []
        self.redo_stack = []
        
        if self.canvas_core:
            self.canvas_core = ngp.CanvasCore(width, height)
        else:
            # Fallback: create a simple numpy array
            self._create_fallback_canvas()
    
    def open_document(self, file_path: str):
        """Open an existing document"""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Load image using OpenCV
        image = cv2.imread(str(file_path), cv2.IMREAD_UNCHANGED)
        if image is None:
            raise ValueError(f"Failed to load image: {file_path}")
        
        # Convert BGR to RGB
        if len(image.shape) == 3 and image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            # Add alpha channel
            alpha = np.full((image.shape[0], image.shape[1], 1), 255, dtype=np.uint8)
            image = np.concatenate([image, alpha], axis=2)
        elif len(image.shape) == 3 and image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)
        
        self.width = image.shape[1]
        self.height = image.shape[0]
        self.file_path = str(file_path)
        self.layers = []
        self.undo_stack = []
        self.redo_stack = []
        
        if self.canvas_core:
            # Create new canvas core with image dimensions
            self.canvas_core = ngp.CanvasCore(self.width, self.height)
            
            # Add a layer and load the image
            layer = self.canvas_core.add_layer("Background")
            self._load_image_to_layer(layer, image)
        else:
            # Fallback: store image in numpy array
            self._create_fallback_canvas(image)
    
    def save_document(self):
        """Save the current document"""
        if not self.file_path:
            raise ValueError("No file path set. Use save_document_as() instead.")
        
        self.save_document_as(self.file_path)
    
    def save_document_as(self, file_path: str):
        """Save the document to a specific path"""
        file_path = Path(file_path)
        
        # Get the composited image
        image = self.get_composited_image()
        if image is None:
            raise ValueError("No image data to save")
        
        # Convert RGB to BGR for OpenCV
        if len(image.shape) == 3 and image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        elif len(image.shape) == 3 and image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGRA)
        
        # Save the image
        success = cv2.imwrite(str(file_path), image)
        if not success:
            raise IOError(f"Failed to save image: {file_path}")
        
        self.file_path = str(file_path)
    
    def export_document(self, file_path: str):
        """Export the document (same as save for now)"""
        self.save_document_as(file_path)
    
    def add_layer(self, name: str) -> bool:
        """Add a new layer"""
        if self.canvas_core:
            layer = self.canvas_core.add_layer(name)
            return layer is not None
        else:
            # Fallback: create a new layer
            layer = Layer(name, self.width, self.height)
            self.layers.append(layer)
            self.active_layer_index = len(self.layers) - 1
            return True
    
    def delete_active_layer(self) -> bool:
        """Delete the active layer"""
        if self.canvas_core and self.active_layer_index >= 0:
            self.canvas_core.remove_layer(self.active_layer_index)
            return True
        elif self.layers and 0 <= self.active_layer_index < len(self.layers):
            # Fallback: remove layer from list
            del self.layers[self.active_layer_index]
            if self.active_layer_index >= len(self.layers):
                self.active_layer_index = max(0, len(self.layers) - 1)
            return True
        return False
    
    def set_active_layer(self, index: int):
        """Set the active layer"""
        if 0 <= index < self.get_layer_count():
            self.active_layer_index = index
    
    def get_layer_count(self) -> int:
        """Get the number of layers"""
        if self.canvas_core:
            return len(self.canvas_core.get_layers())
        return len(self.layers)
    
    def get_active_layer_index(self) -> int:
        """Get the active layer index"""
        return self.active_layer_index
    
    def get_layer_names(self) -> List[str]:
        """Get list of layer names"""
        if self.canvas_core:
            layers = self.canvas_core.get_layers()
            return [layer.name for layer in layers]
        else:
            return [layer.name for layer in self.layers]
    
    def get_composited_image(self) -> Optional[np.ndarray]:
        """Get the composited image from all layers"""
        if self.canvas_core:
            # Get composited image from C++ core
            cv_image = self.canvas_core.get_composited_image()
            if cv_image is not None:
                # Convert OpenCV Mat to numpy array
                return cv_image
        else:
            # Fallback: composite layers manually
            if not self.layers:
                return None
            
            # Start with the bottom layer
            result = self.layers[0].image.copy()
            
            # Blend remaining layers
            for layer in self.layers[1:]:
                if layer.visible and layer.opacity > 0:
                    result = self._blend_layers(result, layer.image, layer.opacity, layer.blend_mode)
            
            return result
        
        return None
    
    def _blend_layers(self, base: np.ndarray, overlay: np.ndarray, opacity: float, blend_mode: str) -> np.ndarray:
        """Blend two layers together"""
        if blend_mode == "normal":
            # Normal blend mode
            alpha = overlay[:, :, 3:4] / 255.0 * opacity
            result = base.copy()
            for c in range(3):  # RGB channels
                result[:, :, c] = (1 - alpha[:, :, 0]) * base[:, :, c] + alpha[:, :, 0] * overlay[:, :, c]
            return result
        else:
            # For now, just use normal blend
            return self._blend_layers(base, overlay, opacity, "normal")
    
    def undo(self) -> bool:
        """Undo the last action"""
        if self.canvas_core:
            if self.canvas_core.can_undo():
                self.canvas_core.undo()
                return True
        elif self.undo_stack:
            # Fallback: restore from undo stack
            state = self.undo_stack.pop()
            self.redo_stack.append(self._save_state())
            self._restore_state(state)
            return True
        return False
    
    def redo(self) -> bool:
        """Redo the last undone action"""
        if self.canvas_core:
            if self.canvas_core.can_redo():
                self.canvas_core.redo()
                return True
        elif self.redo_stack:
            # Fallback: restore from redo stack
            state = self.redo_stack.pop()
            self.undo_stack.append(self._save_state())
            self._restore_state(state)
            return True
        return False
    
    def can_undo(self) -> bool:
        """Check if undo is available"""
        if self.canvas_core:
            return self.canvas_core.can_undo()
        return len(self.undo_stack) > 0
    
    def can_redo(self) -> bool:
        """Check if redo is available"""
        if self.canvas_core:
            return self.canvas_core.can_redo()
        return len(self.redo_stack) > 0
    
    def apply_filter(self, filter_type: str, params: dict):
        """Apply a filter to the active layer"""
        if self.canvas_core and self.active_layer_index >= 0:
            self.canvas_core.apply_filter(self.active_layer_index, filter_type, params)
        elif 0 <= self.active_layer_index < len(self.layers):
            # Fallback: apply filter to numpy array
            self._save_undo_state()
            layer = self.layers[self.active_layer_index]
            
            if filter_type == "gaussian_blur":
                radius = params.get('radius', 5)
                layer.image = cv2.GaussianBlur(layer.image, (radius * 2 + 1, radius * 2 + 1), 0)
            elif filter_type == "unsharp_mask":
                radius = params.get('radius', 3)
                amount = params.get('amount', 1.0)
                threshold = params.get('threshold', 0)
                
                # Create blurred version
                blurred = cv2.GaussianBlur(layer.image, (radius * 2 + 1, radius * 2 + 1), 0)
                
                # Apply unsharp mask
                diff = layer.image.astype(np.float32) - blurred.astype(np.float32)
                mask = np.abs(diff) > threshold
                layer.image = np.clip(layer.image + diff * amount * mask, 0, 255).astype(np.uint8)
            elif filter_type == "brightness_contrast":
                brightness = params.get('brightness', 0)
                contrast = params.get('contrast', 0)
                
                # Apply brightness and contrast
                layer.image = cv2.convertScaleAbs(layer.image, alpha=1 + contrast/100, beta=brightness)
    
    def draw_brush_stroke(self, points: List[Tuple[int, int]], size: float, opacity: float, color: Tuple[int, int, int, int]):
        """Draw a brush stroke on the active layer"""
        if self.canvas_core and self.active_layer_index >= 0:
            # Convert color to C++ Pixel
            pixel = ngp.Pixel(color[0], color[1], color[2], color[3])
            self.canvas_core.draw_brush_stroke(self.active_layer_index, points, size, opacity, pixel)
        elif 0 <= self.active_layer_index < len(self.layers):
            # Fallback: draw on numpy array
            self._save_undo_state()
            layer = self.layers[self.active_layer_index]
            
            if len(points) < 2:
                return
            
            # Draw line segments
            for i in range(len(points) - 1):
                pt1 = points[i]
                pt2 = points[i + 1]
                
                # Draw line with thickness
                cv2.line(layer.image, pt1, pt2, color, thickness=max(1, int(size)), lineType=cv2.LINE_AA)
    
    def erase_brush_stroke(self, points: List[Tuple[int, int]], size: float, opacity: float):
        """Erase a brush stroke on the active layer"""
        if self.canvas_core and self.active_layer_index >= 0:
            self.canvas_core.erase_brush_stroke(self.active_layer_index, points, size, opacity)
        elif 0 <= self.active_layer_index < len(self.layers):
            # Fallback: erase on numpy array
            self._save_undo_state()
            layer = self.layers[self.active_layer_index]
            
            if len(points) < 2:
                return
            
            # Erase line segments (set alpha to 0)
            for i in range(len(points) - 1):
                pt1 = points[i]
                pt2 = points[i + 1]
                
                # Create mask for erasing
                mask = np.zeros((self.height, self.width), dtype=np.uint8)
                cv2.line(mask, pt1, pt2, 255, thickness=max(1, int(size)), lineType=cv2.LINE_AA)
                
                # Set alpha to 0 where mask is non-zero
                layer.image[mask > 0, 3] = 0
    
    def _save_undo_state(self):
        """Save current state for undo"""
        if len(self.undo_stack) >= self.max_undo_steps:
            self.undo_stack.pop(0)
        self.undo_stack.append(self._save_state())
        self.redo_stack.clear()  # Clear redo stack when new action is performed
    
    def _save_state(self) -> dict:
        """Save current document state"""
        state = {
            'layers': [],
            'active_layer_index': self.active_layer_index
        }
        
        for layer in self.layers:
            layer_state = {
                'name': layer.name,
                'visible': layer.visible,
                'opacity': layer.opacity,
                'blend_mode': layer.blend_mode,
                'image': layer.image.copy()
            }
            state['layers'].append(layer_state)
        
        return state
    
    def _restore_state(self, state: dict):
        """Restore document state"""
        self.layers = []
        for layer_state in state['layers']:
            layer = Layer(layer_state['name'], self.width, self.height)
            layer.visible = layer_state['visible']
            layer.opacity = layer_state['opacity']
            layer.blend_mode = layer_state['blend_mode']
            layer.image = layer_state['image'].copy()
            self.layers.append(layer)
        
        self.active_layer_index = state['active_layer_index']
    
    def _create_fallback_canvas(self, image: Optional[np.ndarray] = None):
        """Create a fallback canvas using numpy arrays"""
        if image is not None:
            # Create background layer with the image
            bg_layer = Layer("Background", self.width, self.height)
            bg_layer.image = image.copy()
            self.layers = [bg_layer]
        else:
            # Create a white canvas
            bg_layer = Layer("Background", self.width, self.height)
            bg_layer.image = np.ones((self.height, self.width, 4), dtype=np.uint8) * 255
            bg_layer.image[:, :, 3] = 255  # Alpha channel
            self.layers = [bg_layer]
        
        self.active_layer_index = 0
    
    def _load_image_to_layer(self, layer, image: np.ndarray):
        """Load an image into a layer"""
        if not ngp:
            return
        
        # Convert numpy array to C++ TileGrid
        tile_grid = layer.get_pixels()
        
        # For now, just fill with a solid color
        # In a real implementation, you would convert the numpy array to tiles
        pixel = ngp.Pixel(255, 255, 255, 255)
        tile_grid.fill(pixel) 