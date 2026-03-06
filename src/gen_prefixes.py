#! /usr/bin/python3

import hepunits.units.prefixes as prefixes

def generate_prefixes():
    for prefix in dir(prefixes):
        print(f"constexpr double {prefix} = {getattr(prefixes, prefix)};")

generate_prefixes()
