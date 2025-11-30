"""
Garage and Workshop Screen

Comprehensive component management interface where players can:
- View detailed component health
- Schedule repairs and replacements
- Track repair history
- Manage component inventory
- Monitor budget impact

Authors: Final Year Project - Computer Science
"""

import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QGridLayout, QMessageBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QComboBox, QSpinBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from gui.gui_component_health import ComponentHealthPanel, ComponentRepairButton


class GarageWorkshopScreen(QWidget):
    """
    Garage and Workshop management screen
    
    Allows players to view component health, schedule repairs,
    and manage the technical state of their race car.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.current_vehicle_id = None
        self.component_integration = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the garage UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Garage & Workshop")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #B9F2FF;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Back button
        back_btn = QPushButton("← Back to Career Hub")
        back_btn.clicked.connect(self.go_back)
        back_btn.setFixedWidth(200)
        header_layout.addWidget(back_btn)
        
        main_layout.addLayout(header_layout)
        
        # Main content area
        content_layout = QHBoxLayout()
        
        # Left side: Component health panel
        self.health_panel = ComponentHealthPanel(self)
        self.health_panel.setMinimumWidth(500)
        content_layout.addWidget(self.health_panel, 2)
        
        # Right side: Repair management
        repair_panel = self.create_repair_panel()
        content_layout.addWidget(repair_panel, 1)
        
        main_layout.addLayout(content_layout)
        
        # Bottom: Repair history
        history_group = self.create_history_panel()
        main_layout.addWidget(history_group)
        
        self.setLayout(main_layout)
    
    def create_repair_panel(self):
        """Create repair management panel"""
        panel = QGroupBox("Repair Management")
        panel.setStyleSheet("""
            QGroupBox {
                color: #B9F2FF;
                border: 2px solid #B9F2FF;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
                font-size: 12pt;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Quick repair section
        quick_repair_label = QLabel("Quick Repairs")
        quick_repair_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        quick_repair_label.setStyleSheet("color: #B9F2FF;")
        layout.addWidget(quick_repair_label)
        
        # Repair all button
        repair_all_btn = QPushButton("🔧 Repair All Components")
        repair_all_btn.clicked.connect(self.repair_all_components)
        repair_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        layout.addWidget(repair_all_btn)
        
        # Repair extent slider
        extent_layout = QHBoxLayout()
        extent_label = QLabel("Repair Extent:")
        extent_layout.addWidget(extent_label)
        
        self.repair_extent_spin = QSpinBox()
        self.repair_extent_spin.setMinimum(10)
        self.repair_extent_spin.setMaximum(100)
        self.repair_extent_spin.setValue(100)
        self.repair_extent_spin.setSuffix("%")
        self.repair_extent_spin.setStyleSheet("""
            QSpinBox {
                border: 2px solid #B9F2FF;
                border-radius: 3px;
                padding: 5px;
                background-color: #2A2D2E;
                color: #F5F5F5;
            }
        """)
        extent_layout.addWidget(self.repair_extent_spin)
        layout.addLayout(extent_layout)
        
        layout.addSpacing(20)
        
        # Estimated costs
        cost_label = QLabel("Estimated Costs")
        cost_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        cost_label.setStyleSheet("color: #B9F2FF;")
        layout.addWidget(cost_label)
        
        self.repair_cost_label = QLabel("Full Repair: $-- million")
        self.repair_cost_label.setStyleSheet("color: #F5F5F5; font-size: 10pt;")
        layout.addWidget(self.repair_cost_label)
        
        self.repair_time_label = QLabel("Time Required: -- hours")
        self.repair_time_label.setStyleSheet("color: #F5F5F5; font-size: 10pt;")
        layout.addWidget(self.repair_time_label)
        
        layout.addSpacing(20)
        
        # Individual component repairs
        individual_label = QLabel("Individual Components")
        individual_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        individual_label.setStyleSheet("color: #B9F2FF;")
        layout.addWidget(individual_label)
        
        # Component selector
        component_layout = QHBoxLayout()
        component_layout.addWidget(QLabel("Component:"))
        
        self.component_combo = QComboBox()
        self.component_combo.addItems([
            "Engine", "Hybrid Unit", "Drivetrain", "Gearbox",
            "Aerodynamics", "Tires", "Chassis", "Electronics",
            "Steering", "Safety"
        ])
        self.component_combo.setStyleSheet("""
            QComboBox {
                border: 2px solid #B9F2FF;
                border-radius: 3px;
                padding: 5px;
                background-color: #2A2D2E;
                color: #F5F5F5;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #B9F2FF;
            }
        """)
        component_layout.addWidget(self.component_combo)
        layout.addLayout(component_layout)
        
        # Repair selected component button
        repair_selected_btn = QPushButton("Repair Selected Component")
        repair_selected_btn.clicked.connect(self.repair_selected_component)
        layout.addWidget(repair_selected_btn)
        
        layout.addStretch()
        
        # Budget info
        budget_label = QLabel("Available Budget")
        budget_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        budget_label.setStyleSheet("color: #B9F2FF;")
        layout.addWidget(budget_label)
        
        self.budget_amount_label = QLabel("$-- million")
        self.budget_amount_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.budget_amount_label.setStyleSheet("color: #4CAF50;")
        layout.addWidget(self.budget_amount_label)
        
        panel.setLayout(layout)
        return panel
    
    def create_history_panel(self):
        """Create repair history panel"""
        panel = QGroupBox("Repair History")
        panel.setStyleSheet("""
            QGroupBox {
                color: #B9F2FF;
                border: 2px solid #B9F2FF;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
                font-size: 12pt;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels([
            "Components Repaired", "Cost ($M)", "Time (hours)", "Success"
        ])
        self.history_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.history_table.setSortingEnabled(True)
        
        # Style table
        self.history_table.setStyleSheet("""
            QTableWidget {
                background-color: #2A2D2E;
                border: 2px solid #B9F2FF;
                border-radius: 5px;
                gridline-color: #404040;
            }
            QTableWidget::item {
                color: #F5F5F5;
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #B9F2FF;
                color: #353839;
            }
            QHeaderView::section {
                background-color: #353839;
                color: #B9F2FF;
                padding: 5px;
                border: 1px solid #404040;
                font-weight: bold;
            }
        """)
        
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.history_table.setMaximumHeight(200)
        
        layout.addWidget(self.history_table)
        panel.setLayout(layout)
        return panel
    
    def set_vehicle(self, vehicle_id: int, component_integration):
        """
        Set the vehicle to display
        
        Args:
            vehicle_id: ID of the vehicle
            component_integration: ComponentIntegration instance
        """
        self.current_vehicle_id = vehicle_id
        self.component_integration = component_integration
        self.update_display()
    
    def update_display(self):
        """Update all displays with current vehicle data"""
        if not self.current_vehicle_id or not self.component_integration:
            return
        
        # Get component health data
        health_data = self.component_integration.get_component_health_ui(self.current_vehicle_id)
        
        if not health_data:
            QMessageBox.warning(self, "No Data", "No component data available for this vehicle.")
            return
        
        # Get performance multiplier
        race_car = self.component_integration.race_cars.get(self.current_vehicle_id)
        manager = self.component_integration.component_managers.get(self.current_vehicle_id)
        
        performance = 1.0
        if race_car and manager:
            performance = manager.get_performance_multiplier(race_car)
        
        # Update health panel
        self.health_panel.update_health(health_data, performance)
        
        # Update repair history
        self.update_repair_history()
        
        # Update budget (would need team data from parent)
        # For now, show placeholder
        if hasattr(self.parent_window, 'world') and self.parent_window.world.state:
            team_id = self.parent_window.world.state.player_profile.team_id
            team = self.parent_window.db.get_team(team_id)
            if team:
                budget = getattr(team, 'total_annual_budget', getattr(team, 'budget', 0))
                self.budget_amount_label.setText(f"${budget:.1f}M")
    
    def update_repair_history(self):
        """Update repair history table"""
        if not self.component_integration or not self.current_vehicle_id:
            return
        
        manager = self.component_integration.component_managers.get(self.current_vehicle_id)
        if not manager:
            return
        
        # Disable sorting while updating
        self.history_table.setSortingEnabled(False)
        
        # Clear table
        self.history_table.setRowCount(0)
        
        # Add repair history
        for repair in manager.repair_history:
            row = self.history_table.rowCount()
            self.history_table.insertRow(row)
            
            self.history_table.setItem(row, 0, QTableWidgetItem(", ".join(repair.components_repaired)))
            self.history_table.setItem(row, 1, QTableWidgetItem(f"${repair.cost:.2f}"))
            self.history_table.setItem(row, 2, QTableWidgetItem(f"{repair.time_minutes / 60:.1f}"))
            
            success_item = QTableWidgetItem("✓" if repair.success else "✗")
            if repair.success:
                success_item.setForeground(QColor("#4CAF50"))  # Green for success
            else:
                success_item.setForeground(QColor("#DD2D4A"))  # Red for failure
            self.history_table.setItem(row, 3, success_item)
        
        # Re-enable sorting
        self.history_table.setSortingEnabled(True)
        self.history_table.resizeColumnsToContents()
    
    def repair_all_components(self):
        """Repair all components to specified extent"""
        if not self.current_vehicle_id or not self.component_integration:
            return
        
        extent = self.repair_extent_spin.value() / 100.0
        
        # Confirm with user
        reply = QMessageBox.question(
            self,
            "Confirm Repair",
            f"Repair all components to {int(extent * 100)}% condition?\n\n"
            "This will cost money and time.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        race_car = self.component_integration.race_cars.get(self.current_vehicle_id)
        if not race_car:
            QMessageBox.warning(self, "Error", "Vehicle not found in component system.")
            return
        
        # Repair each major component
        components = ["engine", "drivetrain", "aerodynamics", "chassis", "electronics"]
        total_cost = 0
        total_time = 0
        
        for component in components:
            result = self.component_integration.schedule_component_repair(
                self.current_vehicle_id, component, extent
            )
            
            if result.get("success"):
                total_cost += result.get("cost_millions", 0)
                total_time += result.get("time_required_hours", 0)
        
        # Show result
        QMessageBox.information(
            self,
            "Repair Complete",
            f"All components repaired!\n\n"
            f"Total Cost: ${total_cost:.2f}M\n"
            f"Total Time: {total_time:.1f} hours ({total_time / 24:.1f} days)"
        )
        
        # Update display
        self.update_display()
    
    def repair_selected_component(self):
        """Repair the selected component"""
        if not self.current_vehicle_id or not self.component_integration:
            return
        
        component_map = {
            "Engine": "engine",
            "Hybrid Unit": "hybrid_unit",
            "Drivetrain": "drivetrain",
            "Gearbox": "gearbox",
            "Aerodynamics": "aerodynamics",
            "Tires": "tires",
            "Chassis": "chassis",
            "Electronics": "electronics",
            "Steering": "steering",
            "Safety": "safety"
        }
        
        selected = self.component_combo.currentText()
        component = component_map.get(selected, "engine")
        extent = self.repair_extent_spin.value() / 100.0
        
        result = self.component_integration.schedule_component_repair(
            self.current_vehicle_id, component, extent
        )
        
        if result.get("success"):
            QMessageBox.information(
                self,
                "Repair Complete",
                f"{selected} repaired to {int(extent * 100)}%!\n\n"
                f"Cost: ${result.get('cost_millions', 0):.2f}M\n"
                f"Time: {result.get('time_required_hours', 0):.1f} hours"
            )
            self.update_display()
        else:
            QMessageBox.warning(self, "Repair Failed", f"Could not repair {selected}")
    
    def go_back(self):
        """Return to career hub"""
        if self.parent_window:
            self.parent_window.show_career_hub()


__all__ = ['GarageWorkshopScreen']
