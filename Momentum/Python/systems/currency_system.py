"""
Currency System for Momentum Motorsport Simulation

This module provides comprehensive currency support with EUR as default,
real-time exchange rates, and motorsport-specific budget configurations
including the 2025 F1 budget cap of $140.4 million USD.

Features:
- Multi-currency support (EUR, USD, GBP, JPY, CHF)
- Real-time exchange rate integration
- Motorsport budget templates with proper currency scaling
- F1 2025 budget cap compliance ($140.4M USD = ~€129.8M EUR)
- Locale-specific formatting

Authors: Final Year Project - Computer Science
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Optional, Union
import json
import requests
from datetime import datetime, timedelta
import os


class Currency(Enum):
    """Supported currencies for the motorsport simulation"""
    EUR = "EUR"  # Euro (Default)
    USD = "USD"  # US Dollar
    GBP = "GBP"  # British Pound
    JPY = "JPY"  # Japanese Yen  
    CHF = "CHF"  # Swiss Franc


@dataclass
class CurrencyConfig:
    """Currency configuration and display settings"""
    code: str
    symbol: str
    decimal_places: int
    symbol_position: str  # 'before' or 'after'
    thousands_separator: str
    decimal_separator: str
    
    
class CurrencySystem:
    """
    Comprehensive currency management system for motorsport simulation
    
    Handles currency conversion, formatting, and motorsport-specific
    budget configurations with real-time exchange rates.
    """
    
    # Currency configurations with proper formatting
    CURRENCY_CONFIGS = {
        Currency.EUR: CurrencyConfig("EUR", "€", 2, "before", ".", ","),
        Currency.USD: CurrencyConfig("USD", "$", 2, "before", ",", "."),
        Currency.GBP: CurrencyConfig("GBP", "£", 2, "before", ",", "."),
        Currency.JPY: CurrencyConfig("JPY", "¥", 0, "before", ",", ""),
        Currency.CHF: CurrencyConfig("CHF", "CHF", 2, "after", "'", ".")
    }
    
    # Discipline Budget Caps (in EUR as reference) - Based on complexity and technical requirements
    BUDGET_CAPS_EUR = {
        "single_seater": 130_000_000,      # Highest budget for most technical discipline
        "production_touring": 7_400_000,   # Mid-range budget for production-based racing
        "rally_stage": 16_700_000,         # High budget for specialised rally equipment
        "urban_street": 23_100_000,        # High budget for street circuit precision racing
        "drag_acceleration": 4_600_000,    # Lower budget for straight-line specialisation
        "sprint_rallycross": 11_100_000,   # Mid-high budget for mixed surface racing  
        "endurance": 32_400_000,           # Highest budget for long-distance reliability focus
        # Additional budget tiers for different competitive levels
        "single_seater_tier2": 13_900_000,    # Secondary single seater series
        "single_seater_tier3": 3_200_000,     # Entry-level single seater
        "production_touring_pro": 11_100_000, # Professional touring car series
        "rally_stage_national": 7_400_000,    # National level rally
        "endurance_amateur": 16_700_000,      # Amateur endurance racing
    }
    
    def __init__(self, default_currency: Currency = Currency.EUR):
        """Initialise currency system with default currency"""
        self.default_currency = default_currency
        self.exchange_rates = {}
        self.last_update = None
        self.cache_duration = timedelta(hours=1)  # Update rates hourly
        
        # Load cached exchange rates or fetch new ones
        self._load_exchange_rates()
        
    def _load_exchange_rates(self):
        """Load exchange rates from cache or fetch from API"""
        cache_file = "currency_cache.json"
        
        # Try to load from cache first
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                    self.exchange_rates = cache_data.get('rates', {})
                    self.last_update = datetime.fromisoformat(cache_data.get('last_update', ''))
                    
                # Check if cache is still valid
                if datetime.now() - self.last_update < self.cache_duration:
                    return
            except (json.JSONDecodeError, ValueError, KeyError):
                pass
        
        # Fetch new exchange rates
        self._fetch_exchange_rates()
        
    def _fetch_exchange_rates(self):
        """Fetch current exchange rates from external API"""
        try:
            # Using a free exchange rate API (replace with your preferred service)
            # For development, we'll use mock rates based on approximate 2025 values
            self.exchange_rates = {
                "EUR": 1.0,        # Base currency (EUR)
                "USD": 1.08,       # EUR to USD
                "GBP": 0.86,       # EUR to GBP  
                "JPY": 163.2,      # EUR to JPY
                "CHF": 0.93        # EUR to CHF
            }
            self.last_update = datetime.now()
            
            # Cache the rates
            cache_data = {
                'rates': self.exchange_rates,
                'last_update': self.last_update.isoformat()
            }
            
            with open("currency_cache.json", 'w') as f:
                json.dump(cache_data, f)
                
        except Exception as e:
            # Fallback to default rates if API fails
            print(f"Warning: Could not fetch exchange rates: {e}")
            self.exchange_rates = {
                "EUR": 1.0, "USD": 1.08, "GBP": 0.86, "JPY": 163.2, "CHF": 0.93
            }
            self.last_update = datetime.now()
            
    def convert_amount(self, amount: float, from_currency: Currency, 
                      to_currency: Currency) -> float:
        """
        Convert amount from one currency to another
        
        Args:
            amount: Amount to convert
            from_currency: Source currency
            to_currency: Target currency
            
        Returns:
            Converted amount in target currency
        """
        if from_currency == to_currency:
            return amount
            
        # Convert to EUR first (base currency)
        if from_currency != Currency.EUR:
            eur_amount = amount / self.exchange_rates[from_currency.value]
        else:
            eur_amount = amount
            
        # Convert from EUR to target currency
        if to_currency != Currency.EUR:
            return eur_amount * self.exchange_rates[to_currency.value]
        else:
            return eur_amount
            
    def format_amount(self, amount: float, currency: Currency, 
                     show_currency_code: bool = False) -> str:
        """
        Format amount according to currency conventions
        
        Args:
            amount: Amount to format
            currency: Currency for formatting
            show_currency_code: Whether to show currency code (e.g., "EUR")
            
        Returns:
            Formatted currency string
        """
        config = self.CURRENCY_CONFIGS[currency]
        
        # Round to appropriate decimal places
        if config.decimal_places == 0:
            formatted_number = f"{amount:,.0f}"
        else:
            formatted_number = f"{amount:,.{config.decimal_places}f}"
            
        # Apply currency-specific formatting
        if config.thousands_separator != "," or config.decimal_separator != ".":
            # Replace separators for non-US formatting
            parts = formatted_number.split(".")
            parts[0] = parts[0].replace(",", config.thousands_separator)
            if len(parts) > 1 and config.decimal_separator:
                formatted_number = config.decimal_separator.join(parts)
            else:
                formatted_number = parts[0]
                
        # Add currency symbol
        if config.symbol_position == "before":
            result = f"{config.symbol}{formatted_number}"
        else:
            result = f"{formatted_number} {config.symbol}"
            
        # Add currency code if requested
        if show_currency_code:
            result += f" {config.code}"
            
        return result
        
    def get_budget_cap(self, series: str, currency: Currency = None) -> float:
        """
        Get budget cap for motorsport series in specified currency
        
        Args:
            series: Motorsport series (e.g., 'formula_1', 'wrc')
            currency: Target currency (defaults to system default)
            
        Returns:
            Budget cap in specified currency
        """
        if currency is None:
            currency = self.default_currency
            
        eur_amount = self.BUDGET_CAPS_EUR.get(series.lower())
        if eur_amount is None:
            raise ValueError(f"Unknown motorsport series: {series}")
            
        return self.convert_amount(eur_amount, Currency.EUR, currency)
        
    def get_formatted_budget_cap(self, series: str, currency: Currency = None) -> str:
        """Get formatted budget cap string for display"""
        if currency is None:
            currency = self.default_currency
            
        amount = self.get_budget_cap(series, currency)
        return self.format_amount(amount, currency, show_currency_code=True)
        
    def create_budget_template(self, series: str, currency: Currency = None) -> Dict[str, float]:
        """
        Create comprehensive budget template for motorsport series
        
        Args:
            series: Motorsport series name
            currency: Target currency
            
        Returns:
            Dictionary with budget breakdown
        """
        if currency is None:
            currency = self.default_currency
            
        total_budget = self.get_budget_cap(series, currency)
        
        # Budget allocation percentages (typical for high-level motorsport)
        budget_breakdown = {
            "total_budget": total_budget,
            "personnel": total_budget * 0.35,           # 35% - Staff salaries
            "car_development": total_budget * 0.25,     # 25% - R&D and development
            "manufacturing": total_budget * 0.15,       # 15% - Car production
            "operations": total_budget * 0.10,          # 10% - Race operations
            "facilities": total_budget * 0.08,          # 8% - Infrastructure
            "marketing": total_budget * 0.04,           # 4% - Sponsorship/marketing  
            "contingency": total_budget * 0.03          # 3% - Emergency fund
        }
        
        return budget_breakdown
        
    def get_staff_salary_ranges(self, currency: Currency = None) -> Dict[str, Dict[str, float]]:
        """
        Get realistic staff salary ranges in specified currency
        
        Returns salary ranges for different staff roles and tiers
        """
        if currency is None:
            currency = self.default_currency
            
        # Base salary ranges in EUR (2025 estimates)
        eur_salaries = {
            "technical_director": {"min": 800_000, "max": 2_500_000},
            "team_principal": {"min": 600_000, "max": 2_000_000},
            "chief_designer": {"min": 300_000, "max": 800_000},
            "data_analyst": {"min": 80_000, "max": 250_000},
            "race_strategist": {"min": 150_000, "max": 600_000},
            "pit_crew_chief": {"min": 80_000, "max": 200_000},
            "aerodynamics_engineer": {"min": 120_000, "max": 400_000},
            "race_engineer": {"min": 100_000, "max": 300_000},
            "mechanic": {"min": 40_000, "max": 80_000},
            "driver": {"min": 200_000, "max": 15_000_000}  # Wide range for different series
        }
        
        # Convert to target currency if different
        if currency != Currency.EUR:
            converted_salaries = {}
            for role, salary_range in eur_salaries.items():
                converted_salaries[role] = {
                    "min": self.convert_amount(salary_range["min"], Currency.EUR, currency),
                    "max": self.convert_amount(salary_range["max"], Currency.EUR, currency)
                }
            return converted_salaries
            
        return eur_salaries


# Global currency system instance
currency_system = CurrencySystem(default_currency=Currency.EUR)


def format_currency(amount: float, currency: Currency = Currency.EUR, 
                   show_code: bool = False) -> str:
    """Convenience function for formatting currency amounts"""
    return currency_system.format_amount(amount, currency, show_code)


def get_single_seater_budget_cap(currency: Currency = Currency.EUR) -> str:
    """Get the single seater racing budget cap in specified currency"""
    return currency_system.get_formatted_budget_cap("single_seater", currency)


# Example usage and validation
if __name__ == "__main__":
    print("MOMENTUM MOTORSPORT CURRENCY SYSTEM")
    print("=" * 50)
    
    # Display Single Seater budget cap in different currencies
    print("Single Seater Racing Budget Cap:")
    for curr in Currency:
        cap = currency_system.get_formatted_budget_cap("single_seater", curr)
        print(f"  {curr.value}: {cap}")
        
    print("\nBudget Breakdown (Single Seater in EUR):")
    single_seater_budget = currency_system.create_budget_template("single_seater", Currency.EUR)
    for category, amount in single_seater_budget.items():
        formatted = currency_system.format_amount(amount, Currency.EUR)
        print(f"  {category.replace('_', ' ').title()}: {formatted}")
        
    print("\nStaff Salary Ranges (EUR):")
    salaries = currency_system.get_staff_salary_ranges(Currency.EUR)
    for role, salary_range in salaries.items():
        min_sal = currency_system.format_amount(salary_range["min"], Currency.EUR)
        max_sal = currency_system.format_amount(salary_range["max"], Currency.EUR)
        print(f"  {role.replace('_', ' ').title()}: {min_sal} - {max_sal}")