"""
Engine Component Models

Comprehensive engine and powertrain system modeling for racing simulation.
Includes internal combustion engines, hybrid systems, and electric powertrains.

Authors: Final Year Project - Computer Science
"""

from dataclasses import dataclass, field
from typing import Optional, Dict
from .enums import (
    AspirationType, FuelSystem, FuelType, EngineConfiguration,
    HybridSystemType, EnergyStorageType, ERSMode
)


@dataclass
class EngineComponent:
    """
    Internal Combustion Engine Model
    
    Represents the complete engine assembly with all internal components
    and degradation simulation for realistic wear modeling.
    """
    # Core specifications
    displacement: float                    # Engine displacement in liters
    cylinders: int                         # Number of cylinders
    configuration: EngineConfiguration     # Engine layout (V8, Inline-4, etc.)
    aspiration: AspirationType            # Aspiration method
    fuel_system: FuelSystem               # Fuel delivery system
    fuel_type: FuelType                   # Fuel type used
    
    # Performance characteristics
    max_power_bhp: float = 500.0          # Maximum power output (BHP)
    max_power_rpm: int = 8000             # RPM at max power
    max_torque_nm: float = 600.0          # Maximum torque (Nm)
    max_torque_rpm: int = 6000            # RPM at max torque
    redline_rpm: int = 9000               # Maximum safe RPM
    idle_rpm: int = 1000                  # Idle speed
    
    # Component condition (1.0 = perfect, 0.0 = destroyed)
    crankshaft_condition: float = 1.0
    pistons_condition: float = 1.0
    connecting_rods_condition: float = 1.0
    valvetrain_condition: float = 1.0
    camshaft_condition: float = 1.0
    turbo_condition: float = 1.0          # Only relevant if turbocharged
    supercharger_condition: float = 1.0   # Only relevant if supercharged
    
    # Cooling and lubrication
    cooling_efficiency: float = 1.0
    oil_condition: float = 1.0
    coolant_condition: float = 1.0
    
    # Exhaust system
    exhaust_condition: float = 1.0
    catalytic_converter_condition: float = 1.0
    
    # Reliability and performance
    reliability_rating: float = 0.85      # Base reliability (0.0-1.0)
    fuel_consumption_rate: float = 1.0    # Relative fuel consumption
    oil_consumption_rate: float = 0.05    # L per hour
    
    # Mileage tracking
    total_km: float = 0.0                 # Total kilometers run
    km_since_rebuild: float = 0.0         # KM since last rebuild
    
    def simulate_wear(self, intensity: float, duration_minutes: float):
        """
        Simulate engine wear over a session
        
        Args:
            intensity: Racing intensity (0.0-1.0, where 1.0 is maximum attack)
            duration_minutes: Session duration in minutes
        """
        wear_factor = intensity * (duration_minutes / 60.0)
        
        # Core mechanical components
        self.crankshaft_condition -= 0.0008 * wear_factor
        self.pistons_condition -= 0.0015 * wear_factor
        self.connecting_rods_condition -= 0.0012 * wear_factor
        self.valvetrain_condition -= 0.001 * wear_factor
        self.camshaft_condition -= 0.0009 * wear_factor
        
        # Forced induction systems wear faster
        if self.aspiration == AspirationType.TURBOCHARGED:
            self.turbo_condition -= 0.0025 * wear_factor
        elif self.aspiration == AspirationType.SUPERCHARGED:
            self.supercharger_condition -= 0.002 * wear_factor
        elif self.aspiration == AspirationType.TWINCHARGED:
            self.turbo_condition -= 0.0025 * wear_factor
            self.supercharger_condition -= 0.002 * wear_factor
        
        # Fluids and cooling
        self.cooling_efficiency -= 0.0005 * wear_factor
        self.oil_condition -= 0.001 * wear_factor
        self.coolant_condition -= 0.0008 * wear_factor
        self.exhaust_condition -= 0.0007 * wear_factor
        
        # Ensure all conditions stay within valid range
        self._clamp_conditions()
    
    def get_power_output(self) -> float:
        """Calculate current power output based on component conditions"""
        # Average condition of critical power-producing components
        condition_multiplier = (
            self.pistons_condition * 0.3 +
            self.crankshaft_condition * 0.2 +
            self.valvetrain_condition * 0.2 +
            self.turbo_condition * 0.15 +
            self.cooling_efficiency * 0.15
        )
        
        return self.max_power_bhp * condition_multiplier
    
    def get_overall_condition(self) -> float:
        """Calculate overall engine health (0.0-1.0)"""
        conditions = [
            self.crankshaft_condition,
            self.pistons_condition,
            self.connecting_rods_condition,
            self.valvetrain_condition,
            self.camshaft_condition,
            self.cooling_efficiency,
            self.oil_condition,
            self.exhaust_condition
        ]
        
        if self.aspiration == AspirationType.TURBOCHARGED:
            conditions.append(self.turbo_condition)
        elif self.aspiration == AspirationType.SUPERCHARGED:
            conditions.append(self.supercharger_condition)
        
        return sum(conditions) / len(conditions)
    
    def requires_rebuild(self) -> bool:
        """Check if engine needs rebuild"""
        overall = self.get_overall_condition()
        return overall < 0.5 or any([
            self.crankshaft_condition < 0.3,
            self.pistons_condition < 0.3,
            self.connecting_rods_condition < 0.3
        ])
    
    def rebuild(self):
        """Perform complete engine rebuild"""
        self.crankshaft_condition = 1.0
        self.pistons_condition = 1.0
        self.connecting_rods_condition = 1.0
        self.valvetrain_condition = 1.0
        self.camshaft_condition = 1.0
        self.turbo_condition = 1.0
        self.supercharger_condition = 1.0
        self.cooling_efficiency = 1.0
        self.exhaust_condition = 1.0
        self.km_since_rebuild = 0.0
    
    def service(self):
        """Perform routine service (fluids, minor components)"""
        self.oil_condition = 1.0
        self.coolant_condition = 1.0
        self.cooling_efficiency = min(1.0, self.cooling_efficiency + 0.1)
    
    def _clamp_conditions(self):
        """Ensure all condition values stay in valid range [0.0, 1.0]"""
        self.crankshaft_condition = max(0.0, min(1.0, self.crankshaft_condition))
        self.pistons_condition = max(0.0, min(1.0, self.pistons_condition))
        self.connecting_rods_condition = max(0.0, min(1.0, self.connecting_rods_condition))
        self.valvetrain_condition = max(0.0, min(1.0, self.valvetrain_condition))
        self.camshaft_condition = max(0.0, min(1.0, self.camshaft_condition))
        self.turbo_condition = max(0.0, min(1.0, self.turbo_condition))
        self.supercharger_condition = max(0.0, min(1.0, self.supercharger_condition))
        self.cooling_efficiency = max(0.0, min(1.0, self.cooling_efficiency))
        self.oil_condition = max(0.0, min(1.0, self.oil_condition))
        self.coolant_condition = max(0.0, min(1.0, self.coolant_condition))
        self.exhaust_condition = max(0.0, min(1.0, self.exhaust_condition))


@dataclass
class HybridPowerUnit:
    """
    Hybrid Energy Recovery System
    
    Models modern hybrid racing technology including MGU-K, MGU-H,
    battery storage, and energy management strategies.
    """
    system_type: HybridSystemType
    storage_type: EnergyStorageType
    capacity_kwh: float                   # Energy storage capacity
    
    # Energy management
    state_of_charge: float = 0.0          # Current energy stored (kWh)
    max_deployment_rate_kw: float = 120.0 # Max power deployment (kW)
    max_harvest_rate_kw: float = 100.0    # Max power harvesting (kW)
    
    # Operational modes
    ers_mode: ERSMode = ERSMode.BALANCED
    deployment_enabled: bool = True
    harvesting_enabled: bool = True
    
    # Efficiency and condition
    efficiency: float = 0.95              # Energy transfer efficiency
    health: float = 1.0                   # System condition (1.0 = perfect)
    battery_health: float = 1.0           # Battery degradation
    mgu_k_health: float = 1.0             # MGU-K condition
    mgu_h_health: float = 1.0             # MGU-H condition (if equipped)
    
    # Thermal management
    temperature: float = 40.0             # Operating temperature (°C)
    optimal_temp_min: float = 35.0
    optimal_temp_max: float = 60.0
    
    # Usage statistics
    total_energy_deployed_kwh: float = 0.0
    total_energy_harvested_kwh: float = 0.0
    
    def deploy_energy(self, requested_kw: float, duration_seconds: float) -> float:
        """
        Deploy electrical energy to assist propulsion
        
        Args:
            requested_kw: Power requested (kW)
            duration_seconds: Duration of deployment
        
        Returns:
            Actual power delivered (kW)
        """
        if not self.deployment_enabled or self.state_of_charge <= 0:
            return 0.0
        
        # Limit by max deployment rate and available energy
        actual_kw = min(requested_kw, self.max_deployment_rate_kw)
        energy_needed = (actual_kw * duration_seconds) / 3600.0  # Convert to kWh
        
        if self.state_of_charge >= energy_needed:
            self.state_of_charge -= energy_needed
            self.total_energy_deployed_kwh += energy_needed
            return actual_kw * self.efficiency * self.health
        else:
            # Deploy remaining energy
            available_kw = (self.state_of_charge * 3600.0) / duration_seconds
            deployed_energy = self.state_of_charge
            self.state_of_charge = 0.0
            self.total_energy_deployed_kwh += deployed_energy
            return available_kw * self.efficiency * self.health
    
    def harvest_energy(self, available_kw: float, duration_seconds: float) -> float:
        """
        Harvest energy from braking or exhaust heat
        
        Args:
            available_kw: Power available for harvesting (kW)
            duration_seconds: Duration of harvesting
        
        Returns:
            Actual power harvested (kW)
        """
        if not self.harvesting_enabled:
            return 0.0
        
        # Limit by max harvest rate and available capacity
        actual_kw = min(available_kw, self.max_harvest_rate_kw)
        energy_available = (actual_kw * duration_seconds) / 3600.0  # Convert to kWh
        remaining_capacity = self.capacity_kwh - self.state_of_charge
        
        if remaining_capacity >= energy_available:
            harvested = energy_available * self.efficiency * self.health
            self.state_of_charge += harvested
            self.total_energy_harvested_kwh += harvested
            return actual_kw
        else:
            # Harvest until full
            stored = remaining_capacity
            self.state_of_charge = self.capacity_kwh
            self.total_energy_harvested_kwh += stored
            return (stored * 3600.0) / duration_seconds
    
    def simulate_wear(self, intensity: float, duration_minutes: float):
        """Simulate hybrid system degradation"""
        wear_factor = intensity * (duration_minutes / 60.0)
        
        self.health -= 0.0003 * wear_factor
        self.battery_health -= 0.0004 * wear_factor
        self.mgu_k_health -= 0.0005 * wear_factor
        
        if self.system_type in [HybridSystemType.ERS_H, HybridSystemType.FULL_HYBRID]:
            self.mgu_h_health -= 0.0006 * wear_factor
        
        self._clamp_conditions()
    
    def get_overall_condition(self) -> float:
        """Calculate overall hybrid system health"""
        conditions = [self.health, self.battery_health, self.mgu_k_health]
        if self.system_type in [HybridSystemType.ERS_H, HybridSystemType.FULL_HYBRID]:
            conditions.append(self.mgu_h_health)
        return sum(conditions) / len(conditions)
    
    def reset_charge(self, percentage: float = 1.0):
        """Reset state of charge to specified percentage"""
        self.state_of_charge = self.capacity_kwh * max(0.0, min(1.0, percentage))
    
    def _clamp_conditions(self):
        """Ensure all condition values stay valid"""
        self.health = max(0.0, min(1.0, self.health))
        self.battery_health = max(0.0, min(1.0, self.battery_health))
        self.mgu_k_health = max(0.0, min(1.0, self.mgu_k_health))
        self.mgu_h_health = max(0.0, min(1.0, self.mgu_h_health))
        self.state_of_charge = max(0.0, min(self.capacity_kwh, self.state_of_charge))


__all__ = ['EngineComponent', 'HybridPowerUnit']
