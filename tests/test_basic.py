"""Tests for parsing CODATA records and rendering the project header."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from codata_constants import generate_cpp_header, parse_codata_file


def test_parse_codata_file(tmp_path):
    source = tmp_path / "allascii_2022.txt"
    source.write_text(
        "Quantity  Value  Uncertainty  Unit\n" + "-" * 80 + "\n"
        "speed of light in vacuum  299 792 458  (exact)  m s^-1\n"
        "alpha particle-electron mass ratio  7294.299 541 71  0.000 000 17\n"
    )

    assert parse_codata_file(source) == [
        ("speed_of_light_in_vacuum", "299792458", "(exact)", "m s^-1"),
        ("alpha_particle_electron_mass_ratio", "7294.29954171", "0.00000017", ""),
    ]


def test_generate_cpp_header(tmp_path):
    output = tmp_path / "codata_2022.hpp"
    template = ROOT / "templates" / "codata_cpp_header.jinja2"
    constants = [("alpha_particle_mass", "6.6446573450e-27", "0.0000000021e-27", "kg")]

    generate_cpp_header(constants, template, output, "2022")

    header = output.read_text()
    assert "namespace codata2022 {" in header
    assert "constexpr double alpha_particle_mass = 6.6446573450e-27;" in header
