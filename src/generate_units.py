#!/usr/bin/env python3
"""Generate C++ header with HEP units from hepunits using Jinja template."""

import sys
from pathlib import Path

# Add the hepunits package to the path
sys.path.insert(0, '.pixi/envs/default/lib/python3.14/site-packages')

from hepunits.units import *
from jinja2 import Environment, FileSystemLoader, select_autoescape

def generate_units_header(output_path: Path) -> None:
    """Generate C++ header with HEP units using Jinja template."""
    
    # Define the units and their relationships
    # Based on the hepunits package structure
    
    # Additional units that can be defined in terms of base units
    length_units = {
        # Already defined in template, but could add more here
    }
    
    time_units = {
        # Already defined in template
    }
    
    energy_units = {
        'keV': 'kilo * eV',
        'GeV': 'giga * eV',
        'TeV': 'tera * eV',
        'PeV': 'peta * eV',
        'EeV': 'exa * eV',
        'ZeV': 'zetta * eV',
        'YeV': 'yotta * eV',
    }
    
    mass_units = {
        'gram': 'kilo * kilogram',
        'mg': 'milli * gram',
        'ug': 'micro * gram',
        'ng': 'nano * gram',
        'pg': 'pico * gram',
        'fg': 'femto * gram',
        'ag': 'atto * gram',
    }
    
    current_units = {
        # Base unit is ampere (A)
    }
    
    temperature_units = {
        # Base unit is kelvin (K)
    }
    
    substance_units = {
        # Base unit is mole (mol)
    }
    
    luminous_units = {
        # Base unit is candela (cd)
    }
    
    angle_units = {
        'degree': 'pi / 180.0 * radian',
        'arcmin': 'minute / 60.0 * degree',
        'arcsec': 'second / 3600.0 * degree',
    }
    
    data = {
        'length_units': length_units,
        'time_units': time_units,
        'energy_units': energy_units,
        'mass_units': mass_units,
        'current_units': current_units,
        'temperature_units': temperature_units,
        'substance_units': substance_units,
        'luminous_units': luminous_units,
        'angle_units': angle_units,
    }
    
    # Setup Jinja2 environment
    env = Environment(
        loader=FileSystemLoader(Path('templates')),
        autoescape=select_autoescape()
    )
    
    template = env.get_template('units_header.jinja2')
    
    # Render template
    rendered = template.render(data)
    
    # Write output
    with open(output_path, 'w') as f:
        f.write(rendered)

if __name__ == '__main__':
    output_file = Path('output/units.hpp')
    generate_units_header(output_file)
    print(f"Generated {output_file}")