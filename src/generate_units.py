#!/usr/bin/env python3
"""Generate C++ header with HEP units from hepunits using Jinja template."""

from pathlib import Path

import hepunits.units.units as units
from jinja2 import Environment, FileSystemLoader, select_autoescape

def generate_units_header(output_path: Path) -> None:
    """Generate C++ header with HEP units using Jinja template."""
    
    # Prepare data for template
    data = {
        "unts": { unit : getattr(units, unit) for unit in dir(units) }
    }
    
    # Setup Jinja2 environment
    env = Environment(
        loader=FileSystemLoader(Path('templates')),
        autoescape=select_autoescape()
    )
    
    template = env.get_template('units_cpp_header.jinja2')
    
    # Render template
    rendered = template.render(data)
    
    # Write output
    with open(output_path, 'w') as f:
        f.write(rendered)

if __name__ == '__main__':
    output_file = Path('output/units.hpp')
    generate_units_header(output_file)
    print(f"Generated {output_file}")