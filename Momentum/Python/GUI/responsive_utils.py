"""
Responsive UI utilities for PyQt6 applications.

Provides helper functions for making UI elements scale properly to different screen sizes.
"""

from typing import Tuple, Optional
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QWidget, QSizePolicy


def get_responsive_size(
    width_percent: float = 0.7,
    height_percent: float = 0.7,
    max_width: Optional[int] = None,
    max_height: Optional[int] = None,
    min_width: int = 800,
    min_height: int = 600
) -> Tuple[int, int]:
    """
    Calculate responsive window dimensions based on screen size.
    
    Args:
        width_percent: Percentage of screen width to use (0.0-1.0)
        height_percent: Percentage of screen height to use (0.0-1.0)
        max_width: Maximum width in pixels (None for no limit)
        max_height: Maximum height in pixels (None for no limit)
        min_width: Minimum width in pixels
        min_height: Minimum height in pixels
    
    Returns:
        Tuple of (width, height) in pixels
    
    Example:
        >>> width, height = get_responsive_size(0.8, 0.8, max_width=1600)
        >>> self.resize(width, height)
    """
    screen = QGuiApplication.primaryScreen()
    if screen is None:
        # Fallback to minimums if no screen detected
        return (min_width, min_height)
    
    geometry = screen.geometry()
    
    # Calculate based on percentage
    calc_width = int(geometry.width() * width_percent)
    calc_height = int(geometry.height() * height_percent)
    
    # Apply maximum constraints
    if max_width is not None:
        calc_width = min(calc_width, max_width)
    if max_height is not None:
        calc_height = min(calc_height, max_height)
    
    # Apply minimum constraints
    calc_width = max(calc_width, min_width)
    calc_height = max(calc_height, min_height)
    
    return (calc_width, calc_height)


def make_widget_expanding(widget: QWidget, horizontal: bool = True, vertical: bool = True):
    """
    Set widget size policy to expand and fill available space.
    
    Args:
        widget: The widget to make expanding
        horizontal: Whether to expand horizontally
        vertical: Whether to expand vertically
    
    Example:
        >>> make_widget_expanding(my_table_widget)
        >>> make_widget_expanding(my_button, horizontal=True, vertical=False)
    """
    h_policy = QSizePolicy.Policy.Expanding if horizontal else QSizePolicy.Policy.Preferred
    v_policy = QSizePolicy.Policy.Expanding if vertical else QSizePolicy.Policy.Preferred
    widget.setSizePolicy(h_policy, v_policy)


def get_scaled_font_size(base_size: int, widget: QWidget) -> int:
    """
    Calculate scaled font size based on widget dimensions.
    
    Args:
        base_size: Base font size in points
        widget: Widget to base scaling on
    
    Returns:
        Scaled font size in points
    
    Example:
        >>> font_size = get_scaled_font_size(14, self)
        >>> font.setPointSize(font_size)
    """
    width = widget.width()
    
    # Scale factor based on width (assuming 1600px is "normal")
    if width >= 1600:
        scale = 1.0
    elif width >= 1200:
        scale = 0.9
    elif width >= 900:
        scale = 0.8
    else:
        scale = 0.7
    
    return max(8, int(base_size * scale))  # Minimum 8pt


def calculate_track_zoom(canvas_width: int, canvas_height: int) -> float:
    """
    Calculate appropriate zoom level for track visualization based on canvas size.
    
    Args:
        canvas_width: Width of the track canvas in pixels
        canvas_height: Height of the track canvas in pixels
    
    Returns:
        Zoom factor (smaller = more zoomed out)
    
    Example:
        >>> zoom = calculate_track_zoom(self.width(), self.height())
        >>> painter.scale(zoom, -zoom)
    """
    # Use smaller dimension as reference
    min_dimension = min(canvas_width, canvas_height)
    
    if min_dimension >= 1000:
        return 1.5  # Standard zoom for large displays
    elif min_dimension >= 800:
        return 1.2  # Slight zoom out for medium displays
    elif min_dimension >= 600:
        return 0.9  # More zoom out for smaller displays
    elif min_dimension >= 400:
        return 0.7  # Significant zoom out for narrow displays
    else:
        return 0.5  # Maximum zoom out for very small displays


def get_column_widths_responsive(total_width: int, column_ratios: list) -> list:
    """
    Calculate responsive column widths for tables based on available space.
    
    Args:
        total_width: Total available width in pixels
        column_ratios: List of relative widths (e.g., [1, 3, 1, 2] for 4 columns)
    
    Returns:
        List of column widths in pixels
    
    Example:
        >>> widths = get_column_widths_responsive(self.width(), [1, 4, 1, 2])
        >>> for i, width in enumerate(widths):
        ...     table.setColumnWidth(i, width)
    """
    total_ratio = sum(column_ratios)
    # Reserve some space for margins and scrollbars
    usable_width = total_width - 40
    
    return [int((usable_width * ratio) / total_ratio) for ratio in column_ratios]
