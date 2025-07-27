"""
Tools system for drawing and editing
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional

# Try to import PySide6, fallback to dummy classes if not available
try:
    from PySide6.QtCore import Signal, QObject, QPoint
    from PySide6.QtGui import QPainter, QColor, QPen, QBrush
    PYSIDE6_AVAILABLE = True
    print("Successfully imported PySide6")
except ImportError as e:
    print(f"Warning: Could not import PySide6: {e}")
    print("Running with fallback tool implementations")
    print("To install PySide6: pip install PySide6")
    PYSIDE6_AVAILABLE = False
    
    # Create dummy classes for fallback
    class QObject:
        def __init__(self):
            pass
    
    class Signal:
        def __init__(self, *args):
            pass
    
    class QPoint:
        def __init__(self, x=0, y=0):
            self.x = lambda: x
            self.y = lambda: y
    
    class QPainter:
        def __init__(self, *args):
            pass
    
    class QColor:
        def __init__(self, *args):
            pass
    
    class QPen:
        def __init__(self, *args):
            pass
    
    class QBrush:
        def __init__(self, *args):
            pass

class Tool(QObject):
    """Base class for all tools"""
    
    # Signals
    tool_changed = Signal(str)
    
    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self.active = False
        self.properties = {}
        self.document = None
    
    @abstractmethod
    def mouse_press(self, pos: QPoint):
        """Handle mouse press event"""
        pass
    
    @abstractmethod
    def mouse_move(self, pos: QPoint):
        """Handle mouse move event"""
        pass
    
    @abstractmethod
    def mouse_release(self, pos: QPoint):
        """Handle mouse release event"""
        pass
    
    @abstractmethod
    def draw_preview(self, painter: QPainter, zoom: float):
        """Draw tool preview"""
        pass
    
    def set_property(self, name: str, value):
        """Set a tool property"""
        self.properties[name] = value
    
    def get_property(self, name: str, default=None):
        """Get a tool property"""
        return self.properties.get(name, default)
    
    def set_document(self, document):
        """Set the document for this tool"""
        self.document = document


class BrushTool(Tool):
    """Brush tool for drawing"""
    
    def __init__(self):
        super().__init__("Brush")
        self.stroke_points = []
        self.is_drawing = False
        
        # Default properties
        self.properties = {
            'size': 10.0,
            'opacity': 1.0,
            'color': (255, 0, 0, 255),  # Red
            'hardness': 0.5,
            'spacing': 0.25
        }
    
    def mouse_press(self, pos: QPoint):
        """Handle mouse press event"""
        self.is_drawing = True
        self.stroke_points = [pos]
        
        # Start stroke in document
        if self.document:
            # Convert QPoint to tuple for document
            point_tuple = (pos.x(), pos.y())
            self.document.draw_brush_stroke([point_tuple], 
                                          self.get_property('size'),
                                          self.get_property('opacity'),
                                          self.get_property('color'))
    
    def mouse_move(self, pos: QPoint):
        """Handle mouse move event"""
        if self.is_drawing:
            self.stroke_points.append(pos)
            
            # Draw stroke in document
            if self.document and len(self.stroke_points) >= 2:
                color = self.get_property('color')
                size = self.get_property('size')
                opacity = self.get_property('opacity')
                
                # Convert QPoints to tuples
                points = [(p.x(), p.y()) for p in self.stroke_points[-2:]]
                self.document.draw_brush_stroke(points, size, opacity, color)
    
    def mouse_release(self, pos: QPoint):
        """Handle mouse release event"""
        if self.is_drawing:
            self.is_drawing = False
            self.stroke_points = []
    
    def draw_preview(self, painter: QPainter, zoom: float):
        """Draw brush preview"""
        if not self.stroke_points:
            return
        
        # Set up pen for preview
        color = self.get_property('color')
        size = self.get_property('size') * zoom
        
        pen = QPen(QColor(color[0], color[1], color[2], color[3]))
        pen.setWidth(max(1, int(size)))
        pen.setCapStyle(QPen.RoundCap)
        pen.setJoinStyle(QPen.RoundJoin)
        painter.setPen(pen)
        
        # Draw preview lines
        for i in range(len(self.stroke_points) - 1):
            start = self.stroke_points[i]
            end = self.stroke_points[i + 1]
            painter.drawLine(start, end)


class EraserTool(Tool):
    """Eraser tool for erasing"""
    
    def __init__(self):
        super().__init__("Eraser")
        self.stroke_points = []
        self.is_erasing = False
        
        # Default properties
        self.properties = {
            'size': 20.0,
            'opacity': 1.0,
            'hardness': 0.5
        }
    
    def mouse_press(self, pos: QPoint):
        """Handle mouse press event"""
        self.is_erasing = True
        self.stroke_points = [pos]
        
        # Start erasing in document
        if self.document:
            point_tuple = (pos.x(), pos.y())
            self.document.erase_brush_stroke([point_tuple],
                                           self.get_property('size'),
                                           self.get_property('opacity'))
    
    def mouse_move(self, pos: QPoint):
        """Handle mouse move event"""
        if self.is_erasing:
            self.stroke_points.append(pos)
            
            # Erase stroke in document
            if self.document and len(self.stroke_points) >= 2:
                size = self.get_property('size')
                opacity = self.get_property('opacity')
                
                # Convert QPoints to tuples
                points = [(p.x(), p.y()) for p in self.stroke_points[-2:]]
                self.document.erase_brush_stroke(points, size, opacity)
    
    def mouse_release(self, pos: QPoint):
        """Handle mouse release event"""
        if self.is_erasing:
            self.is_erasing = False
            self.stroke_points = []
    
    def draw_preview(self, painter: QPainter, zoom: float):
        """Draw eraser preview"""
        if not self.stroke_points:
            return
        
        # Set up pen for preview (white with transparency)
        size = self.get_property('size') * zoom
        
        pen = QPen(QColor(255, 255, 255, 128))
        pen.setWidth(max(1, int(size)))
        pen.setCapStyle(QPen.RoundCap)
        pen.setJoinStyle(QPen.RoundJoin)
        painter.setPen(pen)
        
        # Draw preview lines
        for i in range(len(self.stroke_points) - 1):
            start = self.stroke_points[i]
            end = self.stroke_points[i + 1]
            painter.drawLine(start, end)


class SmudgeTool(Tool):
    """Smudge tool for blending colors"""
    
    def __init__(self):
        super().__init__("Smudge")
        self.stroke_points = []
        self.is_smudging = False
        
        # Default properties
        self.properties = {
            'size': 15.0,
            'opacity': 0.8,
            'strength': 0.5
        }
    
    def mouse_press(self, pos: QPoint):
        """Handle mouse press event"""
        self.is_smudging = True
        self.stroke_points = [pos]
        
        # Start smudge in document
        if self.document:
            params = {
                'strength': self.get_property('strength'),
                'size': self.get_property('size')
            }
            self.document.apply_filter('smudge', params)
    
    def mouse_move(self, pos: QPoint):
        """Handle mouse move event"""
        if self.is_smudging:
            self.stroke_points.append(pos)
            
            # Apply smudge in document
            if self.document and len(self.stroke_points) >= 2:
                params = {
                    'strength': self.get_property('strength'),
                    'size': self.get_property('size'),
                    'points': [(p.x(), p.y()) for p in self.stroke_points[-2:]]
                }
                self.document.apply_filter('smudge', params)
    
    def mouse_release(self, pos: QPoint):
        """Handle mouse release event"""
        if self.is_smudging:
            self.is_smudging = False
            self.stroke_points = []
    
    def draw_preview(self, painter: QPainter, zoom: float):
        """Draw smudge preview"""
        if not self.stroke_points:
            return
        
        # Set up pen for preview (blend color)
        size = self.get_property('size') * zoom
        
        pen = QPen(QColor(128, 128, 128, 128))
        pen.setWidth(max(1, int(size)))
        pen.setCapStyle(QPen.RoundCap)
        pen.setJoinStyle(QPen.RoundJoin)
        painter.setPen(pen)
        
        # Draw preview lines
        for i in range(len(self.stroke_points) - 1):
            start = self.stroke_points[i]
            end = self.stroke_points[i + 1]
            painter.drawLine(start, end)


class SelectionTool(Tool):
    """Selection tool for creating selections"""
    
    def __init__(self):
        super().__init__("Selection")
        self.start_pos = None
        self.end_pos = None
        self.is_selecting = False
        
        # Default properties
        self.properties = {
            'feather': 0,
            'mode': 'replace'  # replace, add, subtract, intersect
        }
    
    def mouse_press(self, pos: QPoint):
        """Handle mouse press event"""
        self.is_selecting = True
        self.start_pos = pos
        self.end_pos = pos
    
    def mouse_move(self, pos: QPoint):
        """Handle mouse move event"""
        if self.is_selecting:
            self.end_pos = pos
    
    def mouse_release(self, pos: QPoint):
        """Handle mouse release event"""
        if self.is_selecting:
            self.is_selecting = False
            self.end_pos = pos
            self._create_selection()
    
    def draw_preview(self, painter: QPainter, zoom: float):
        """Draw selection preview"""
        if not self.start_pos or not self.end_pos:
            return
        
        # Set up pen for selection rectangle
        pen = QPen(QColor(0, 120, 215, 255))  # Blue selection color
        pen.setWidth(2)
        pen.setStyle(QPen.DashLine)
        painter.setPen(pen)
        
        # Set up brush for selection fill
        brush = QBrush(QColor(0, 120, 215, 30))  # Semi-transparent blue
        painter.setBrush(brush)
        
        # Draw selection rectangle
        rect = self._get_selection_rect()
        painter.drawRect(rect)
    
    def _create_selection(self):
        """Create the selection"""
        if not self.start_pos or not self.end_pos:
            return
        
        # Get selection rectangle
        rect = self._get_selection_rect()
        
        # Apply selection to document
        if self.document:
            params = {
                'x': rect.x(),
                'y': rect.y(),
                'width': rect.width(),
                'height': rect.height(),
                'feather': self.get_property('feather'),
                'mode': self.get_property('mode')
            }
            self.document.apply_filter('selection', params)
    
    def _get_selection_rect(self):
        """Get the selection rectangle"""
        if not self.start_pos or not self.end_pos:
            return None
        
        # Convert QPoints to coordinates
        x1, y1 = self.start_pos.x(), self.start_pos.y()
        x2, y2 = self.end_pos.x(), self.end_pos.y()
        
        # Create rectangle
        from PySide6.QtCore import QRect
        return QRect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))


class ToolManager(QObject):
    """Manager for all tools"""
    
    # Signals
    tool_changed = Signal(object)
    color_changed = Signal(tuple)
    property_changed = Signal(str, object)
    
    def __init__(self):
        super().__init__()
        self.tools = {}
        self.current_tool = None
        self.current_color = (255, 0, 0, 255)  # Red
        
        self._create_tools()
        self._set_default_tool()
    
    def _create_tools(self):
        """Create all available tools"""
        self.tools['brush'] = BrushTool()
        self.tools['eraser'] = EraserTool()
        self.tools['smudge'] = SmudgeTool()
        self.tools['selection'] = SelectionTool()
    
    def _set_default_tool(self):
        """Set the default tool"""
        self.set_tool('brush')
    
    def set_tool(self, tool_name: str):
        """Set the current tool"""
        if tool_name in self.tools:
            self.current_tool = self.tools[tool_name]
            self.tool_changed.emit(self.current_tool)
    
    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """Get a specific tool"""
        return self.tools.get(tool_name)
    
    def get_current_tool(self) -> Optional[Tool]:
        """Get the current tool"""
        return self.current_tool
    
    def set_color(self, color: Tuple[int, int, int, int]):
        """Set the current color"""
        self.current_color = color
        self.color_changed.emit(color)
        
        # Update brush tool color
        brush_tool = self.tools.get('brush')
        if brush_tool:
            brush_tool.set_property('color', color)
    
    def get_color(self) -> Tuple[int, int, int, int]:
        """Get the current color"""
        return self.current_color
    
    def set_property(self, name: str, value):
        """Set a property on the current tool"""
        if self.current_tool:
            self.current_tool.set_property(name, value)
            self.property_changed.emit(name, value)
    
    def get_property(self, name: str, default=None):
        """Get a property from the current tool"""
        if self.current_tool:
            return self.current_tool.get_property(name, default)
        return default
    
    def set_document(self, document):
        """Set the document for all tools"""
        for tool in self.tools.values():
            tool.set_document(document) 