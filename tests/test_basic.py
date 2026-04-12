#!/usr/bin/env python3
"""Basic tests for the CODATA parser and C++ header generator."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from codata_constants import generate_cpp_header, parse_codata_file


def test_parse_codata_file(tmp_path):
    """Test parsing of a simple CODATA file."""
    codata_file = tmp_path / "allascii_2022.txt"
    codata_file.write_text("""# Test CODATA file

  Quantity                                                       Value                 Uncertainty           Unit
-----------------------------------------------------------------------------------------------------------------------------
speed of light in vacuum                                      299 792 458            (exact)              m s^-1
Planck constant                                               6.626 070 15 e-34      (exact)              J Hz^-1
""")

    constants = parse_codata_file(codata_file)

    assert constants == [
        ("speed_of_light_in_vacuum", "299792458", "(exact)", "m s^-1"),
        ("Planck_constant", "6.62607015e-34", "(exact)", "J Hz^-1"),
    ]


def test_generate_cpp_header(tmp_path):
    """Test generation of C++ header from constants."""
    constants = [
        ("speed_of_light_in_vacuum", "299792458", "(exact)", "m s^-1"),
        ("Planck_constant", "6.62607015e-34", "(exact)", "J Hz^-1"),
    ]
    template_file = tmp_path / "test_header.jinja2"
    output_file = tmp_path / "test.hpp"

    template_file.write_text("""// Test header
{% for name, value, uncertainty, unit in constants %}
constexpr double {{ name }} = {{ value }};
{% endfor %}
""")

    generate_cpp_header(constants, template_file, output_file, "2022")

    content = output_file.read_text()

    assert "constexpr double speed_of_light_in_vacuum = 299792458;" in content
    assert "constexpr double Planck_constant = 6.62607015e-34;" in content


def test_basic_codata_usage_example_compiles(tmp_path):
    """Test the C++ usage example against the checked-in generated headers."""
    compiler = shutil.which("g++") or shutil.which("c++")
    if compiler is None:
        pytest.skip("C++ compiler not available")

    repo_root = Path(__file__).parent.parent
    source_file = repo_root / "examples" / "basic_codata_usage.cpp"
    executable = tmp_path / "basic_codata_usage"

    subprocess.run(
        [compiler, "-std=c++17", "-I", str(repo_root), str(source_file), "-o", str(executable)],
        check=True,
    )
    subprocess.run([str(executable)], check=True)


if __name__ == '__main__':
    raise SystemExit(pytest.main([__file__]))
