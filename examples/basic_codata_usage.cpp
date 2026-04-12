#include <iostream>

#include "output/codata_2022.hpp"
#include "output/prefixes.hpp"
#include "output/units.hpp"

int main() {
  using namespace physicalconstants::codata2022;
  using namespace physicalconstants::prefixes;
  using namespace physicalconstants::units;

  constexpr double electron_mass_mev = electron_mass_energy_equivalent_in_MeV;
  constexpr double proton_mass_mev = proton_mass_energy_equivalent_in_MeV;
  constexpr double one_gev_in_mev = GeV / MeV;
  constexpr double kilometer = kilo * meter;

  static_assert(speed_of_light_in_vacuum == 299792458.0);
  static_assert(one_gev_in_mev == 1000.0);
  static_assert(kilometer > meter);

  std::cout << "electron mass energy: " << electron_mass_mev << " MeV\n";
  std::cout << "proton mass energy: " << proton_mass_mev << " MeV\n";
  std::cout << "1 GeV in MeV: " << one_gev_in_mev << "\n";
  std::cout << "1 km in HEP length units: " << kilometer << "\n";

  return 0;
}
