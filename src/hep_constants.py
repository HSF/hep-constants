"""Map the important CODATA unit names to the standard HEP C++ constant names

The C++ variable names are taken from CLHEP.
"""

import os
import sys
sys.path.append(os.getcwd())

from jinja2 import Environment, FileSystemLoader, select_autoescape
import math
from pathlib import Path
from sympy import symbols, Eq
from sympy.printing import cxxcode

import hepunits.units.prefixes as prefixes
import hepunits.units.units as units

# Make a symbol dictionary from all of the units and prefixes...
sp = {name: symbols(name) for name in dir(prefixes)}
su = {name: symbols(name) for name in dir(units)}

# Import CODATA values to Python
from output import codata_2022 as codata

"""
    cpp_var_def_str(eqn)

Print a string corresponding to the C++ code to define a
constexpr variable.

As this uses sympy symbols it will be a symbolic expression
when the other symbols are used, but numerical values when
those are used.
"""
def cpp_var_def_str(eqn):
    return cxxcode(eqn.lhs) + " = " + cxxcode(eqn.rhs)

def construct_hep_constants():
    hep_constants = []
    list_of_equations = []

    # Define here the variables we want to appear in the output
    # and the equation that defines the variable
    c_light = symbols('c_light')
    list_of_equations.append(Eq(c_light, codata.speed_of_light_in_vacuum * su['m'] / su['s']))

    c_light2 = symbols('c_light2')
    list_of_equations.append(Eq(c_light2, c_light**2))

    Avogadro = symbols('Avogadro')
    list_of_equations.append(Eq(Avogadro, codata.Avogadro_constant * su['mole']))

    h_Planck = symbols('h_Planck')
    hbar_Planck = symbols('hbar_Planck')
    hbarc = symbols('hbarc')
    hbarc_squared = symbols('hbarc_squared')
    list_of_equations.append(Eq(h_Planck, codata.Planck_constant * su["joule"] * su["second"]))
    list_of_equations.append(Eq(hbar_Planck, h_Planck / (2 * math.pi)))
    list_of_equations.append(Eq(hbarc, hbar_Planck * c_light))
    list_of_equations.append(Eq(hbarc_squared, hbarc_squared**2))

    # Add these to the structure for Jinja
    for eqn in list_of_equations:
        hep_constants.append(cpp_var_def_str(eqn))

    return hep_constants


def generate_cpphep_header(constants, year: str,
                        template_path = Path("templates/hep_cpp_constants.jinja2"), 
                        output_path = Path("output/hepconstants.cpp")) -> None:
    """
    Generate a C++ header file with constexpr constants using Jinja2 template.
    
    Args:
        constants: List of constants as valid C++ assignments
        template_path: Path to Jinja2 template file
        output_path: Path where the C++ header will be written
        year: CODATA year for namespace
    """
    # Setup Jinja2 environment
    env = Environment(
        loader=FileSystemLoader(template_path.parent),
        autoescape=select_autoescape()
    )
    
    template = env.get_template(template_path.name)
    
    # Prepare data for template
    data = {
        'constants': constants,
        'year': year,
        'namespace': f'hepconstants{year}'
    }
    
    # Render template
    rendered = template.render(data)
    
    # Write output
    with open(output_path, 'w') as f:
        f.write(rendered)

def main():
    # Proof of concept - these should all be configurable later
    hep_constants = construct_hep_constants()
    year = 2022
    # print(hep_constants)

    generate_cpphep_header(constants = hep_constants, year = year, 
                           output_path = Path("output") / Path(f"hepconstants_{year}.cpp"))

main()
