"""
Component Health Visualization Widgets

Displays real-time component health, wear, and damage for the garage/workshop UI.
Shows health bars, repair costs, and component status.

Authors: Final Year Project - Computer Science
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
    QPushButton, QGroupBox, QGridLayout, QScrollArea, QFrame,
    QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor


class ComponentHealthBar(QWidget):
    """Single component health bar with status indicator"""
    
    def __init__(self, component_name: str, health_percentage: int, 
                 status: str, color: str):
        super().__init__()
        self.component_name = component_name
        self.health_percentage = health_percentage
        self.status = status
        self.color = color
        self.init_ui()
    
    def init_ui(self):
        """Initialize the health bar UI"""
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Component name
        name_label = QLabel(self.component_name.replace('_', ' ').title())
        name_label.setMinimumWidth(150)
        name_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(name_label)
        
        # Health bar
        health_bar = QProgressBar()
        health_bar.setMinimum(0)
        health_bar.setMaximum(100)
        health_bar.setValue(self.health_percentage)
        health_bar.setTextVisible(True)
        health_bar.setFormat(f"{self.health_percentage}%")
        health_bar.setMinimumWidth(200)
        
        # Color based on health
        if self.color == "green":
            health_bar.setStyleSheet("""
                QProgressBar {
                    border: 2px solid #4CAF50;
                    border-radius: 5px;
                    text-align: center;
                    background-color: #2A2D2E;
                }
                QProgressBar::chunk {
                    background-color: #4CAF50;
                }
            """)
        elif self.color == "cyan":
            health_bar.setStyleSheet("""
                QProgressBar {
                    border: 2px solid #B9F2FF;
                    border-radius: 5px;
                    text-align: center;
                    background-color: #2A2D2E;
                }
                QProgressBar::chunk {
                    background-color: #B9F2FF;
                }
            """)
        elif self.color == "yellow":
            health_bar.setStyleSheet("""
                QProgressBar {
                    border: 2px solid #FFC107;
                    border-radius: 5px;
                    text-align: center;
                    background-color: #2A2D2E;
                }
                QProgressBar::chunk {
                    background-color: #FFC107;
                }
            """)
        elif self.color == "orange":
            health_bar.setStyleSheet("""
                QProgressBar {
                    border: 2px solid #FF9800;
                    border-radius: 5px;
                    text-align: center;
                    background-color: #2A2D2E;
                }
                QProgressBar::chunk {
                    background-color: #FF9800;
                }
            """)
        else:  # red
            health_bar.setStyleSheet("""
                QProgressBar {
                    border: 2px solid #DD2D4A;
                    border-radius: 5px;
                    text-align: center;
                    background-color: #2A2D2E;
                }
                QProgressBar::chunk {
                    background-color: #DD2D4A;
                }
            """)
        
        layout.addWidget(health_bar)
        
        # Status label
        status_label = QLabel(self.status)
        status_label.setMinimumWidth(100)
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_label.setFont(QFont("Arial", 9))
        
        if self.status == "Excellent":
            status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        elif self.status == "Good":
            status_label.setStyleSheet("color: #B9F2FF; font-weight: bold;")
        elif self.status == "Worn":
            status_label.setStyleSheet("color: #FFC107; font-weight: bold;")
        elif self.status == "Damaged":
            status_label.setStyleSheet("color: #FF9800; font-weight: bold;")
        else:  # Critical
            status_label.setStyleSheet("color: #DD2D4A; font-weight: bold;")
        
        layout.addWidget(status_label)
        
        self.setLayout(layout)


class ComponentHealthPanel(QWidget):
    """Panel showing all component health bars"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.component_data = {}
        self.init_ui()
    
    def init_ui(self):
        """Initialize the panel UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("Component Health Monitor")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #B9F2FF; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Scroll area for components
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: 2px solid #B9F2FF;
                border-radius: 5px;
                background-color: #2A2D2E;
            }
        """)
        
        # Container for health bars
        self.health_container = QWidget()
        self.health_layout = QVBoxLayout()
        self.health_layout.setSpacing(5)
        self.health_container.setLayout(self.health_layout)
        
        scroll.setWidget(self.health_container)
        layout.addWidget(scroll)
        
        # Overall health summary
        summary_group = QGroupBox("Overall Status")
        summary_group.setStyleSheet("""
            QGroupBox {
                color: #B9F2FF;
                border: 2px solid #B9F2FF;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        summary_layout = QGridLayout()
        
        self.overall_health_label = QLabel("Overall Health: --")
        self.overall_health_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        summary_layout.addWidget(self.overall_health_label, 0, 0)
        
        self.performance_label = QLabel("Performance Multiplier: --")
        self.performance_label.setFont(QFont("Arial", 11))
        summary_layout.addWidget(self.performance_label, 0, 1)
        
        self.needs_replacement_label = QLabel("Components Needing Replacement: --")
        self.needs_replacement_label.setFont(QFont("Arial", 11))
        summary_layout.addWidget(self.needs_replacement_label, 1, 0, 1, 2)
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        self.setLayout(layout)
    
    def update_health(self, health_data: dict, performance_multiplier: float = 1.0):
        """
        Update health display with new data
        
        Args:
            health_data: Dict from ComponentIntegration.get_component_health_ui()
            performance_multiplier: Current performance multiplier
        """
        # Clear existing health bars
        while self.health_layout.count():
            child = self.health_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Store data
        self.component_data = health_data
        
        # Add health bars for each component
        total_health = 0
        component_count = 0
        
        for component, data in health_data.items():
            if component == "needs_replacement":
                continue
            
            health_bar = ComponentHealthBar(
                component_name=component,
                health_percentage=data['percentage'],
                status=data['status'],
                color=data['color']
            )
            self.health_layout.addWidget(health_bar)
            
            total_health += data['percentage']
            component_count += 1
        
        # Add stretch to push everything to top
        self.health_layout.addStretch()
        
        # Update summary
        avg_health = total_health / component_count if component_count > 0 else 0
        self.overall_health_label.setText(f"Overall Health: {avg_health:.1f}%")
        
        if avg_health >= 80:
            self.overall_health_label.setStyleSheet("color: #4CAF50;")
        elif avg_health >= 60:
            self.overall_health_label.setStyleSheet("color: #B9F2FF;")
        elif avg_health >= 40:
            self.overall_health_label.setStyleSheet("color: #FFC107;")
        else:
            self.overall_health_label.setStyleSheet("color: #DD2D4A;")
        
        self.performance_label.setText(f"Performance Multiplier: {performance_multiplier:.3f}x")
        
        if performance_multiplier >= 0.95:
            self.performance_label.setStyleSheet("color: #4CAF50;")
        elif performance_multiplier >= 0.90:
            self.performance_label.setStyleSheet("color: #B9F2FF;")
        elif performance_multiplier >= 0.80:
            self.performance_label.setStyleSheet("color: #FFC107;")
        else:
            self.performance_label.setStyleSheet("color: #DD2D4A;")
        
        # Replacement needed
        needs_replacement = health_data.get("needs_replacement", [])
        if needs_replacement:
            replacement_text = f"Components Needing Replacement: {', '.join(needs_replacement)}"
            self.needs_replacement_label.setText(replacement_text)
            self.needs_replacement_label.setStyleSheet("color: #DD2D4A; font-weight: bold;")
        else:
            self.needs_replacement_label.setText("Components Needing Replacement: None")
            self.needs_replacement_label.setStyleSheet("color: #4CAF50;")


class ComponentRepairButton(QPushButton):
    """Repair button for individual component"""
    
    def __init__(self, component_name: str, repair_callback):
        super().__init__(f"Repair {component_name.replace('_', ' ').title()}")
        self.component_name = component_name
        self.repair_callback = repair_callback
        self.clicked.connect(self.on_repair_clicked)
        
        self.setStyleSheet("""
            QPushButton {
                background-color: #2A2D2E;
                color: #B9F2FF;
                border: 2px solid #B9F2FF;
                border-radius: 5px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #B9F2FF;
                color: #353839;
            }
        """)
    
    def on_repair_clicked(self):
        """Handle repair button click"""
        if self.repair_callback:
            self.repair_callback(self.component_name)


__all__ = ['ComponentHealthBar', 'ComponentHealthPanel', 'ComponentRepairButton']
