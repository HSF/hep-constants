#!/usr/bin/env python3
"""Basic tests for the CODATA parser and C++ header generator."""

import os
import sys
import tempfile
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from main import parse_codata_file, generate_cpp_header


def test_parse_codata_file():
    """Test parsing of a simple CODATA file."""
    # Create a temporary CODATA file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("""# Test CODATA file
# Name Value Uncertainty

speed_of_light 299792458 0
Planck_constant 6.62607015e-34 0
""")
        temp_file = f.name
    
    try:
        # Parse the file
        constants = parse_codata_file(Path(temp_file))
        
        # Verify results
        assert len(constants) == 2
        assert constants[0] == ('speed_of_light', '299792458', '0')
        assert constants[1] == ('Planck_constant', '6.62607015e-34', '0')
        
        print("✓ parse_codata_file test passed")
        
    finally:
        # Clean up
        os.unlink(temp_file)


def test_generate_cpp_header():
    """Test generation of C++ header from constants."""
    # Test constants
    constants = [
        ('speed_of_light', '299792458', '0'),
        ('Planck_constant', '6.62607015e-34', '0')
    ]
    
    # Create temporary template file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jinja2', delete=False) as f:
        f.write("""// Test header
{% for name, value, uncertainty in constants %}
constexpr double {{ name }} = {{ value }};
{% endfor %}
""")
        template_file = f.name
    
    # Create temporary output file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.hpp', delete=False) as f:
        output_file = f.name
    
    try:
        # Generate header
        generate_cpp_header(constants, Path(template_file), Path(output_file))
        
        # Read and verify output
        with open(output_file, 'r') as f:
            content = f.read()
        
        assert 'constexpr double speed_of_light = 299792458;' in content
        assert 'constexpr double Planck_constant = 6.62607015e-34;' in content
        
        print("✓ generate_cpp_header test passed")
        
    finally:
        # Clean up
        os.unlink(template_file)
        os.unlink(output_file)


if __name__ == '__main__':
    test_parse_codata_file()
    test_generate_cpp_header()
    print("All tests passed!")