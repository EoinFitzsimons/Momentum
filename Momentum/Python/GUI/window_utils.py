"""Window management utilities for centered, properly-sized dialogs."""

from PyQt6.QtWidgets import (
    QWidget,
    QDialog,
    QVBoxLayout,
    QScrollArea,
    QTableWidget,
    QHeaderView,
)
from PyQt6.QtGui import QGuiApplication
from typing import Optional, Tuple, List


def get_screen_dimensions() -> Tuple[int, int]:
    """Get primary screen dimensions with fallback."""
    screen = QGuiApplication.primaryScreen()
    if screen is None:
        return 1920, 1080
    geometry = screen.geometry()
    return geometry.width(), geometry.height()


def center_dialog(dialog: QDialog, parent: Optional[QWidget] = None) -> None:
    """Center a dialog on the screen or parent window."""
    if parent:
        parent_geometry = parent.geometry()
        center_x = parent_geometry.center().x()
        center_y = parent_geometry.center().y()
    else:
        screen_w, screen_h = get_screen_dimensions()
        center_x = screen_w // 2
        center_y = screen_h // 2

    dialog_width = dialog.width()
    dialog_height = dialog.height()

    # Position dialog centered
    x = center_x - (dialog_width // 2)
    y = center_y - (dialog_height // 2)

    # Ensure dialog stays within screen bounds
    screen = QGuiApplication.primaryScreen()
    if screen is not None:
        screen_geometry = screen.geometry()
        if x < screen_geometry.left():
            x = screen_geometry.left()
        if y < screen_geometry.top():
            y = screen_geometry.top()
        if x + dialog_width > screen_geometry.right():
            x = screen_geometry.right() - dialog_width
        if y + dialog_height > screen_geometry.bottom():
            y = screen_geometry.bottom() - dialog_height

    dialog.move(int(x), int(y))


def calculate_responsive_size(
    ui_scale: int = 100,
    base_width: int = 900,
    base_height: int = 700,
    max_screen_percent: float = 0.85,
) -> Tuple[int, int]:
    """
    Calculate responsive dialog size based on screen and UI scale.

    Args:
        ui_scale: UI scale percentage (100, 125, 150)
        base_width: Base dialog width
        base_height: Base dialog height
        max_screen_percent: Maximum percent of screen to use

    Returns:
        Tuple of (width, height) for dialog sizing
    """
    screen_w, screen_h = get_screen_dimensions()
    
    # Scale by accessibility factor
    scale_factor = ui_scale / 100.0
    scaled_width = int(base_width * scale_factor)
    scaled_height = int(base_height * scale_factor)
    
    # Cap to screen percentage
    max_width = int(screen_w * max_screen_percent)
    max_height = int(screen_h * max_screen_percent)
    
    return min(scaled_width, max_width), min(scaled_height, max_height)


def setup_dialog_size_and_position(
    dialog: QDialog,
    parent: Optional[QWidget] = None,
    base_width: int = 900,
    base_height: int = 700,
    min_width: int = 600,
    min_height: int = 400,
    ui_scale: int = 100,
    max_screen_percent: float = 0.85,
) -> None:
    """
    Setup comprehensive dialog sizing and positioning.

    Args:
        dialog: Dialog to configure
        parent: Parent widget for centering
        base_width: Base dialog width
        base_height: Base dialog height
        min_width: Minimum dialog width
        min_height: Minimum dialog height
        ui_scale: UI scale percentage
        max_screen_percent: Maximum percent of screen to use
    """
    # Calculate responsive size
    width, height = calculate_responsive_size(ui_scale, base_width, base_height, max_screen_percent)
    
    # Ensure minimum sizes
    width = max(width, int(min_width * (ui_scale / 100.0)))
    height = max(height, int(min_height * (ui_scale / 100.0)))
    
    dialog.resize(width, height)
    dialog.setMinimumSize(int(min_width * (ui_scale / 100.0)), int(min_height * (ui_scale / 100.0)))
    
    # Center on parent or screen
    center_dialog(dialog, parent)


def configure_table_for_accessibility(
    table_widget: QTableWidget,
    ui_scale: int = 100,
    stretch_columns: Optional[List[int]] = None,
) -> None:
    """
    Configure table widget for accessibility at various UI scales.

    Args:
        table_widget: Table widget to configure
        ui_scale: UI scale percentage (100, 125, 150)
        stretch_columns: List of column indices to stretch to content
    """
    if stretch_columns is None:
        stretch_columns = []

    # Configure columns
    for col_idx in range(table_widget.columnCount()):
        if col_idx in stretch_columns:
            header = table_widget.horizontalHeader()
            if header is not None:
                header.setSectionResizeMode(col_idx, QHeaderView.ResizeMode.Stretch)
        else:
            header = table_widget.horizontalHeader()
            if header is not None:
                header.setSectionResizeMode(col_idx, QHeaderView.ResizeMode.ResizeToContents)

    # Set row height based on UI scale
    base_row_height = 30
    row_height = int(base_row_height * (ui_scale / 100.0))
    v_header = table_widget.verticalHeader()
    if v_header is not None:
        v_header.setDefaultSectionSize(row_height)

    # Set word wrap for better text display at larger scales
    table_widget.setWordWrap(True)
    table_widget.setAlternatingRowColors(True)

    # Style for better accessibility
    table_widget.setStyleSheet(
        f"""
        QTableWidget {{
            border: 1px solid rgba(185, 242, 255, 0.1);
            gridline-color: rgba(185, 242, 255, 0.1);
        }}
        QTableWidget::item {{
            padding: {int(8 * (ui_scale / 100.0))}px;
        }}
        QHeaderView::section {{
            background-color: rgba(185, 242, 255, 0.15);
            padding: {int(6 * (ui_scale / 100.0))}px;
            border: 1px solid rgba(185, 242, 255, 0.2);
        }}
    """
    )


def make_dialog_scrollable(
    dialog: QDialog,
    inner_widget: QWidget,
) -> None:
    """
    Wrap dialog content in a scroll area for text-scale overflow handling.

    Args:
        dialog: Dialog to make scrollable
        inner_widget: Inner widget content to wrap
    """
    scroll_area = QScrollArea(dialog)
    scroll_area.setWidgetResizable(True)
    scroll_area.setWidget(inner_widget)
    
    layout = QVBoxLayout(dialog)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(scroll_area)
    dialog.setLayout(layout)
