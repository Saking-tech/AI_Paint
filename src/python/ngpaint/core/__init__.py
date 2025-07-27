"""
Core module for NextGenPaint
"""

from .document import Document
from .tools import Tool, BrushTool, EraserTool, SelectionTool
from .settings import Settings

__all__ = ['Document', 'Tool', 'BrushTool', 'EraserTool', 'SelectionTool', 'Settings'] 