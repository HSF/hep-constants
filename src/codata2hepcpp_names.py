"""Map the important CODATA unit names to the standard HEP C++ constant names

The C++ variable names are taken from CLHEP.
"""

import os
import sys
print(sys.path)
sys.path.append(os.getcwd())

from sympy import symbols, Eq
from sympy.printing import cxxcode

import hepunits.units.prefixes as prefixes
import hepunits.units.units as units

# Make a symbol dictionary from all of the units and prefixes...
sp = {name: symbols(name) for name in dir(prefixes)}
su = {name: symbols(name) for name in dir(units)}

# Import CODATA values to Python
from output import codata_2022 as codata

def cpp_var_def_str(eqn):
    return "constexpr double " + cxxcode(eqn.lhs) + " = " + cxxcode(eqn.rhs) + ";"

c_light = symbols('c_light')
c_light2 = symbols('c_light2')

c_eq = Eq(c_light, codata.speed_of_light_in_vacuum * su['m'] / su['s'])
c2_eq = Eq(c_light2, c_light**2)

print(cpp_var_def_str(c_eq))
print(cpp_var_def_str(c2_eq))


# """
# Simple class holding the mapping from CODATA name to "standard" HEP name and
# the conversion from the CODATA SI unit value to the HEP unit (mm, MeV, etc.).

# The conversion should make sense as a constexpr, based on the prefixes and
# units value headers.
# """
# class Codata2HEP:
#     def __init__(self, codata_name: str, hep_name: str, si_to_hep: str):
#         self.codata_name = codata_name
#         self.hep_name = hep_name
#         self.si_to_hep = si_to_hep

#     def __repr__(self):
#         return f"Codata2HEP(codata_name='{self.codata_name}', hep_name='{self.hep_name}', si_to_hep='{self.si_to_hep}')"



# # This are the values that we want to convert to HEP style/units constants
# hep_physical_constants_list = []
# hep_physical_constants_list.append(Codata2HEP("Avogadro constant", "Avogadro", ""))
# hep_physical_constants_list.append(Codata2HEP("speed of light in vacuum", "c_light", "m * s"))


# codata2cpp = {
#     "Avogadro constant": "Avogadro",
#     "speed of light in vacuum": "c_light",
#     "Planck constant": "h_Planck",
#     "Boltzmann constant": "k_Boltzmann",
#     "electron mass energy equivalent in MeV": "electron_mass_c2",
#     "proton mass energy equivalent in MeV": "proton_mass_c2",
#     "neutron mass energy equivalent in MeV": "neutron_mass_c2",
#     "atomic mass constant energy equivalent in MeV": "amu_c2",
#     "atomic mass constant": "amu",
#     "vacuum mag. permeability": "mu0",
#     "vacuum electric permittivity": "epsilon0",
# }
