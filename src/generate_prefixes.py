#!/usr/bin/env python3
"""Generate C++ header with SI prefixes from hepunits using Jinja template."""

import sys
from pathlib import Path

import hepunits.units.prefixes as prefixes
from jinja2 import Environment, FileSystemLoader, select_autoescape

def generate_prefixes_header(output_path: Path) -> None:
    """Generate C++ header with SI prefixes using Jinja template."""
    
    # Prepare data for template
    data = {
        "pfx": { prefix : getattr(prefixes, prefix) for prefix in dir(prefixes) }
    }
    print(data)
    
    # Setup Jinja2 environment
    env = Environment(
        loader=FileSystemLoader(Path('templates')),
        autoescape=select_autoescape()
    )
    
    template = env.get_template('prefixes_header.jinja2')
    
    # Render template
    rendered = template.render(data)
    
    # Write output
    with open(output_path, 'w') as f:
        f.write(rendered)

if __name__ == '__main__':
    output_file = Path('output/prefixes.hpp')
    generate_prefixes_header(output_file)
    print(f"Generated {output_file}")
