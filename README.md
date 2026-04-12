# HEP Constants

This is a project for the generation of C++ header files
automatically from CODATA values of physical constants.

It takes advantage of unit and SI prefix definitions from
the SciKit-HEP project [hepunits](https://github.com/scikit-hep/hepunits)
and uses some lightweight symbolic manipulation from
[sympy](https://docs.sympy.org/latest/index.html) to be able
to output C++ constexpr expressions.

Constants, units and prefixes are all organised in namespaces.

## Generated files

Generated files are checked in under `output/`:

- `codata_<year>.hpp`: C++ headers with CODATA constants in the
  `physicalconstants::codata<year>` namespace.
- `codata_<year>.py`: Python modules with the same CODATA constants.
- `units.hpp`: HEP unit conversion constants from `hepunits`, in the
  `physicalconstants::units` namespace.
- `prefixes.hpp`: SI prefix constants from `hepunits`, in the
  `physicalconstants::prefixes` namespace.

For example, use the 2022 CODATA constants and HEP units from C++:

```cpp
#include "output/codata_2022.hpp"
#include "output/prefixes.hpp"
#include "output/units.hpp"

int main() {
  using namespace physicalconstants::codata2022;
  using namespace physicalconstants::prefixes;
  using namespace physicalconstants::units;

  constexpr double electron_mass_mev = electron_mass_energy_equivalent_in_MeV;
  constexpr double one_gev_in_mev = GeV / MeV;
  constexpr double kilometer = kilo * meter;

  static_assert(speed_of_light_in_vacuum == 299792458.0);
  static_assert(one_gev_in_mev == 1000.0);

  return electron_mass_mev > 0.0 && kilometer > meter ? 0 : 1;
}
```

See `examples/basic_codata_usage.cpp` for a complete example that can be
compiled from the repository root:

```console
g++ -std=c++17 -I. examples/basic_codata_usage.cpp -o basic_codata_usage
./basic_codata_usage
```

## Regenerating outputs

The generator scripts are run from the repository root. The default CODATA
generator command writes C++ headers to `output/`:

```console
python3 src/codata_constants.py
```

To regenerate the Python CODATA modules, select the Python template and suffix:

```console
python3 src/codata_constants.py --template templates/codata_py.jinja2 --suffix py
```

The HEP units and SI prefixes are generated separately:

```console
python3 src/generate_units.py
python3 src/generate_prefixes.py
```

## Tests

Run the Python tests with:

```console
python3 -m pytest
```

*This is a work in progress, contributions welcome.*
