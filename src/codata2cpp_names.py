"""Map the important CODATA unit names to the standard HEP C++ constant names

The C++ variable names are taken from CLHEP.
"""

codata2cpp = {
    "Avogadro constant": "Avogadro",
    "speed of light in vacuum": "c_light",
    "Planck constant": "h_Planck",
    "Boltzmann constant": "k_Boltzmann",
    "electron mass energy equivalent in MeV": "electron_mass_c2",
    "proton mass energy equivalent in MeV": "proton_mass_c2",
    "neutron mass energy equivalent in MeV": "neutron_mass_c2",
    "atomic mass constant energy equivalent in MeV": "amu_c2",
    "atomic mass constant": "amu",
    "vacuum mag. permeability": "mu0",
    "vacuum electric permittivity": "epsilon0",
}
