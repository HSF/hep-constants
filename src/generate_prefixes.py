#!/usr/bin/env python3
"""Generate C++ header with SI prefixes from hepunits using Jinja template."""

import sys
from pathlib import Path

# Add the hepunits package to the path
sys.path.insert(0, '.pixi/envs/default/lib/python3.14/site-packages')

from hepunits.units.prefixes import *
from jinja2 import Environment, FileSystemLoader, select_autoescape

# SI prefixes and their values
si_prefixes = {
    'quetta': quetta,
    'ronna': ronna,
    'yotta': yotta,
    'zetta': zetta,
    'exa': exa,
    'peta': peta,
    'tera': tera,
    'giga': giga,
    'mega': mega,
    'kilo': kilo,
    'hecto': hecto,
    'deca': deca,
    'deci': deci,
    'centi': centi,
    'milli': milli,
    'micro': micro,
    'nano': nano,
    'pico': pico,
    'femto': femto,
    'atto': atto,
    'zepto': zepto,
    'yocto': yocto,
    'ronto': ronto,
    'quecto': quecto,
}

# Binary prefixes
binary_prefixes = {
    'kibi': kibi,
    'mebi': mebi,
    'gibi': gibi,
    'tebi': tebi,
    'pebi': pebi,
    'exbi': exbi,
    'zebi': zebi,
    'yobi': yobi,
}

# Miscellaneous prefixes
misc_prefixes = {
    'googol': googol,
}

def generate_prefixes_header(output_path: Path) -> None:
    """Generate C++ header with SI prefixes using Jinja template."""
    
    # Prepare data for template
    data = {
        'si_prefixes': si_prefixes,
        'binary_prefixes': binary_prefixes,
        'misc_prefixes': misc_prefixes,
    }
    
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