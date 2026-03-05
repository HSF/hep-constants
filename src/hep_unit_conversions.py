#!/usr/bin/env python3
"""HEP unit conversions and mapping from SI units."""

import re
from typing import Dict, Optional, Tuple


# HEP unit conversion factors (from hepunits)
# These are the conversion factors from SI units to HEP units
HEP_UNIT_CONVERSIONS = {
    # Length: 1 meter = 1000 mm (HEP base unit)
    'm': ('mm', 1000.0, 'meter to millimeter'),
    'meter': ('mm', 1000.0, 'meter to millimeter'),
    'meters': ('mm', 1000.0, 'meter to millimeter'),
    
    # Time: 1 second = 1e9 ns (HEP base unit)
    's': ('ns', 1e9, 'second to nanosecond'),
    'second': ('ns', 1e9, 'second to nanosecond'),
    'seconds': ('ns', 1e9, 'second to nanosecond'),
    
    # Mass: derived from energy (E=mc²), but we'll handle separately
    'kg': ('MeV/c²', 5.6095883571872e32, 'kilogram to MeV/c²'),  # 1 kg = 5.6095883571872e32 MeV/c²
    'kilogram': ('MeV/c²', 5.6095883571872e32, 'kilogram to MeV/c²'),
    'kilograms': ('MeV/c²', 5.6095883571872e32, 'kilogram to MeV/c²'),
    
    # Electric current: 1 ampere = 1 C/s = 1 eplus/ns (since eplus = 1 in HEP units)
    'A': ('eplus/ns', 1.0, 'ampere to eplus/ns'),
    'ampere': ('eplus/ns', 1.0, 'ampere to eplus/ns'),
    'amperes': ('eplus/ns', 1.0, 'ampere to eplus/ns'),
    
    # Temperature: 1 kelvin = 1 K (same in HEP)
    'K': ('K', 1.0, 'kelvin to kelvin'),
    'kelvin': ('K', 1.0, 'kelvin to kelvin'),
    
    # Amount of substance: 1 mole = 1 mol (same in HEP)
    'mol': ('mol', 1.0, 'mole to mole'),
    'mole': ('mol', 1.0, 'mole to mole'),
    
    # Luminous intensity: 1 candela = 1 cd (same in HEP)
    'cd': ('cd', 1.0, 'candela to candela'),
    'candela': ('cd', 1.0, 'candela to candela'),
    
    # Common derived units
    'J': ('MeV', 6.241509074e12, 'joule to MeV'),  # 1 J = 6.241509074e12 MeV
    'joule': ('MeV', 6.241509074e12, 'joule to MeV'),
    'joules': ('MeV', 6.241509074e12, 'joule to MeV'),
    
    'C': ('eplus', 6.241509074e18, 'coulomb to eplus'),  # 1 C = 6.241509074e18 eplus
    'coulomb': ('eplus', 6.241509074e18, 'coulomb to eplus'),
    'coulombs': ('eplus', 6.241509074e18, 'coulomb to eplus'),
    
    'V': ('MeV/eplus', 1e6, 'volt to MeV/eplus'),  # 1 V = 1e6 MeV/eplus
    'volt': ('MeV/eplus', 1e6, 'volt to MeV/eplus'),
    'volts': ('MeV/eplus', 1e6, 'volt to MeV/eplus'),
    
    'T': ('MeV/(eplus*mm²)', 1e10, 'tesla to MeV/(eplus*mm²)'),  # Approximate
    'tesla': ('MeV/(eplus*mm²)', 1e10, 'tesla to MeV/(eplus*mm²)'),
}


def parse_unit_from_codata_line(line: str) -> Optional[str]:
    """
    Extract the unit from a CODATA line.
    
    Args:
        line: CODATA line
        
    Returns:
        Unit string or None if not found
    """
    # CODATA format: ...value uncertainty unit
    # Look for the unit at the end of the line
    parts = line.strip().split()
    if len(parts) >= 4:
        # The unit is typically the last part
        potential_unit = parts[-1]
        
        # Clean up common unit notations
        if potential_unit.endswith('^-1'):
            return potential_unit
        elif potential_unit.endswith('^2'):
            return potential_unit
        elif potential_unit.endswith('^3'):
            return potential_unit
        elif potential_unit in ['m', 's', 'kg', 'A', 'K', 'mol', 'cd', 'J', 'C', 'V', 'T']:
            return potential_unit
        elif potential_unit.startswith('m'):
            return potential_unit
        elif potential_unit.startswith('kg'):
            return potential_unit
        elif potential_unit.startswith('s'):
            return potential_unit
        elif potential_unit.startswith('A'):
            return potential_unit
        elif potential_unit.startswith('K'):
            return potential_unit
        elif potential_unit.startswith('mol'):
            return potential_unit
        elif potential_unit.startswith('cd'):
            return potential_unit
        elif potential_unit.startswith('J'):
            return potential_unit
        elif potential_unit.startswith('C'):
            return potential_unit
        elif potential_unit.startswith('V'):
            return potential_unit
        elif potential_unit.startswith('T'):
            return potential_unit
    
    return None


def get_hep_conversion(unit: str) -> Optional[Tuple[str, float, str]]:
    """
    Get HEP unit conversion for a given SI unit.
    
    Args:
        unit: SI unit string
        
    Returns:
        Tuple of (hep_unit, conversion_factor, description) or None
    """
    # Handle complex units (like m^2, m^-1, etc.)
    base_unit_match = re.match(r'^([a-zA-Z]+)(.*)$', unit)
    if base_unit_match:
        base_unit = base_unit_match.group(1)
        exponent_part = base_unit_match.group(2)
        
        if base_unit in HEP_UNIT_CONVERSIONS:
            hep_unit, factor, desc = HEP_UNIT_CONVERSIONS[base_unit]
            # Handle exponents
            if exponent_part == '^2':
                return (f'{hep_unit}²', factor, f'{desc} squared')
            elif exponent_part == '^3':
                return (f'{hep_unit}³', factor, f'{desc} cubed')
            elif exponent_part == '^-1':
                return (f'1/{hep_unit}', 1.0/factor, f'inverse {desc}')
            else:
                return (hep_unit, factor, desc)
    
    # Try direct lookup
    if unit in HEP_UNIT_CONVERSIONS:
        return HEP_UNIT_CONVERSIONS[unit]
    
    # Try without plural 's'
    if unit.endswith('s') and unit[:-1] in HEP_UNIT_CONVERSIONS:
        return HEP_UNIT_CONVERSIONS[unit[:-1]]
    
    return None


def convert_si_to_hep(value: float, unit: str) -> Optional[Tuple[float, str, str]]:
    """
    Convert SI value to HEP units.
    
    Args:
        value: Value in SI units
        unit: SI unit string
        
    Returns:
        Tuple of (hep_value, hep_unit, conversion_description) or None
    """
    conversion = get_hep_conversion(unit)
    if conversion:
        hep_unit, factor, desc = conversion
        hep_value = value * factor
        return (hep_value, hep_unit, desc)
    
    return None