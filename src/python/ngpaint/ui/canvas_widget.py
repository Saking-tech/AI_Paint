"""
Canvas widget for drawing and interaction
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QSizePolicy
from PySide6.QtCore import Qt, Signal, QPoint, QRect
from PySide6.QtGui import QPainter, QPixmap, QColor, QPen, QBrush, QMouseEvent, QWheelEvent, QImage
import cv2
import numpy as np

from ..core.document import Document
from ..core.tools import Tool

class CanvasWidget(QWidget):
    """Canvas widget for drawing and interaction"""
    
    # Signals
    mouse_pressed = Signal(QPoint)
    mouse_moved = Signal(QPoint)
    mouse_released = Signal(QPoint)
    zoom_changed = Signal(float)
    
    def __init__(self, document: Document):
        super().__init__()
        self.document = document
        self.current_tool = None
        self.zoom = 1.0
        self.pan_offset = QPoint(0, 0)
        self.is_panning = False
        self.last_mouse_pos = QPoint()
        
        self.setup_ui()
        self.setup_canvas()
        
        # Set widget properties
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)
        self.setMinimumSize(400, 300)
    
    def setup_ui(self):
        """Setup the UI layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area for canvas
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create canvas widget
        self.canvas = Canvas(self.document)
        self.scroll_area.setWidget(self.canvas)
        
        layout.addWidget(self.scroll_area)
    
    def setup_canvas(self):
        """Setup the canvas"""
        self.canvas.set_zoom(self.zoom)
        self.canvas.set_pan_offset(self.pan_offset)
    
    def set_tool(self, tool: Tool):
        """Set the current tool"""
        self.current_tool = tool
        self.canvas.set_tool(tool)
    
    def update_canvas(self):
        """Update the canvas display"""
        self.canvas.update()
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events"""
        if event.button() == Qt.LeftButton:
            if event.modifiers() & Qt.ControlModifier:
                # Start panning
                self.is_panning = True
                self.last_mouse_pos = event.pos()
                self.setCursor(Qt.ClosedHandCursor)
            else:
                # Tool interaction
                canvas_pos = self.map_to_canvas(event.pos())
                self.mouse_pressed.emit(canvas_pos)
                if self.current_tool:
                    self.current_tool.mouse_press(canvas_pos)
        elif event.button() == Qt.MiddleButton:
            # Start panning
            self.is_panning = True
            self.last_mouse_pos = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move events"""
        if self.is_panning:
            # Handle panning
            delta = event.pos() - self.last_mouse_pos
            self.pan_offset += delta
            self.canvas.set_pan_offset(self.pan_offset)
            self.last_mouse_pos = event.pos()
        else:
            # Tool interaction
            canvas_pos = self.map_to_canvas(event.pos())
            self.mouse_moved.emit(canvas_pos)
            if self.current_tool:
                self.current_tool.mouse_move(canvas_pos)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release events"""
        if event.button() in [Qt.LeftButton, Qt.MiddleButton]:
            if self.is_panning:
                # Stop panning
                self.is_panning = False
                self.setCursor(Qt.ArrowCursor)
            else:
                # Tool interaction
                canvas_pos = self.map_to_canvas(event.pos())
                self.mouse_released.emit(canvas_pos)
                if self.current_tool:
                    self.current_tool.mouse_release(canvas_pos)
    
    def wheelEvent(self, event: QWheelEvent):
        """Handle wheel events for zooming"""
        if event.modifiers() & Qt.ControlModifier:
            # Zoom
            delta = event.angleDelta().y()
            zoom_factor = 1.1 if delta > 0 else 0.9
            self.zoom *= zoom_factor
            self.zoom = max(0.1, min(10.0, self.zoom))
            
            self.canvas.set_zoom(self.zoom)
            self.zoom_changed.emit(self.zoom)
            
            event.accept()
        else:
            # Scroll
            super().wheelEvent(event)
    
    def map_to_canvas(self, widget_pos: QPoint) -> QPoint:
        """Map widget coordinates to canvas coordinates"""
        canvas_pos = self.canvas.mapFrom(self, widget_pos)
        return canvas_pos - self.pan_offset


class Canvas(QWidget):
    """Inner canvas widget for drawing"""
    
    def __init__(self, document: Document):
        super().__init__()
        self.document = document
        self.current_tool = None
        self.zoom = 1.0
        self.pan_offset = QPoint(0, 0)
        
        # Set widget properties
        self.setMinimumSize(800, 600)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    
    def set_tool(self, tool):
        """Set the current tool"""
        self.current_tool = tool
    
    def set_zoom(self, zoom: float):
        """Set the zoom level"""
        self.zoom = zoom
        self.update_size()
        self.update()
    
    def set_pan_offset(self, offset: QPoint):
        """Set the pan offset"""
        self.pan_offset = offset
        self.update()
    
    def update_size(self):
        """Update the canvas size based on document and zoom"""
        if self.document:
            width = int(self.document.width * self.zoom)
            height = int(self.document.height * self.zoom)
            self.setMinimumSize(width, height)
            self.resize(width, height)
    
    def paintEvent(self, event):
        """Paint the canvas"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Apply zoom and pan transformations
        painter.translate(self.pan_offset)
        painter.scale(self.zoom, self.zoom)
        
        # Draw checkerboard background
        self.draw_checkerboard(painter)
        
        # Draw document content
        if self.document:
            self.draw_document(painter)
        
        # Draw tool preview
        if self.current_tool:
            # Reset transformations for tool preview
            painter.resetTransform()
            painter.translate(self.pan_offset)
            painter.scale(self.zoom, self.zoom)
            self.current_tool.draw_preview(painter, self.zoom)
    
    def draw_checkerboard(self, painter: QPainter):
        """Draw checkerboard background"""
        size = 20
        color1 = QColor(200, 200, 200)
        color2 = QColor(255, 255, 255)
        
        # Calculate visible area
        visible_rect = painter.viewport()
        start_x = max(0, visible_rect.x() // size * size)
        start_y = max(0, visible_rect.y() // size * size)
        end_x = min(self.document.width, (visible_rect.x() + visible_rect.width()) // size * size + size)
        end_y = min(self.document.height, (visible_rect.y() + visible_rect.height()) // size * size + size)
        
        for y in range(start_y, end_y, size):
            for x in range(start_x, end_x, size):
                color = color1 if (x // size + y // size) % 2 == 0 else color2
                painter.fillRect(x, y, size, size, color)
    
    def draw_document(self, painter: QPainter):
        """Draw the document content"""
        if not self.document:
            return
        
        # Get the composited image from the document
        image = self.document.get_composited_image()
        if image is None:
            return
        
        # Convert to QPixmap and draw
        pixmap = self.image_to_pixmap(image)
        painter.drawPixmap(0, 0, pixmap)
    
    def image_to_pixmap(self, image: np.ndarray) -> QPixmap:
        """Convert OpenCV image to QPixmap"""
        if image is None:
            # Create a transparent pixmap
            pixmap = QPixmap(self.document.width, self.document.height)
            pixmap.fill(QColor(255, 255, 255, 0))
            return pixmap
        
        # Ensure image is in the right format
        if len(image.shape) == 3:
            height, width, channels = image.shape
            if channels == 3:
                # Convert BGR to RGB
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                format = QImage.Format_RGB888
            elif channels == 4:
                # Convert BGRA to RGBA
                image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)
                format = QImage.Format_RGBA8888
            else:
                # Unknown format, create transparent pixmap
                pixmap = QPixmap(self.document.width, self.document.height)
                pixmap.fill(QColor(255, 255, 255, 0))
                return pixmap
        else:
            # Grayscale image
            height, width = image.shape
            format = QImage.Format_Grayscale8
        
        # Create QImage from numpy array
        qimage = QImage(image.data, width, height, image.strides[0], format)
        
        # Convert to QPixmap
        return QPixmap.fromImage(qimage) 