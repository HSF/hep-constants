#!/usr/bin/env python3
"""Parse CODATA ASCII files and generate C++ headers with constexpr constants."""

import argparse
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape
from hep_unit_conversions import parse_unit_from_codata_line, convert_si_to_hep


def parse_codata_file(file_path: Path) -> List[Tuple[str, str, str, Optional[str], Optional[str]]]:
    """
    Parse a CODATA ASCII file and extract constant data with units.
    
    Args:
        file_path: Path to the CODATA ASCII file
        
    Returns:
        List of tuples containing (name, value, uncertainty, unit, hep_unit)
    """
    constants = []
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('{') or line.startswith('---'):
                continue
            
            # Skip header lines and empty lines
            if 'Quantity' in line or 'Value' in line or 'Unit' in line:
                continue
            
            # Parse the line - CODATA format has name followed by value and uncertainty
            # The name is the first sequence of non-whitespace characters
            parts = line.split()
            if len(parts) >= 3:
                # Extract name (may contain spaces, so we need to be careful)
                # Look for the pattern: name followed by numeric values
                name_match = re.match(r'^([\w\s]+?)\s+([\d\.]+)\s+([\d\.]+)', line)
                if name_match:
                    name = name_match.group(1).strip()
                    value = name_match.group(2)
                    uncertainty = name_match.group(3)
                    
                    # Extract unit from the line
                    unit = parse_unit_from_codata_line(line)
                    
                    # Convert to HEP units if possible
                    hep_unit_info = None
                    if unit:
                        try:
                            si_value = float(value.replace(' ', ''))
                            hep_conversion = convert_si_to_hep(si_value, unit)
                            if hep_conversion:
                                hep_value, hep_unit, conversion_desc = hep_conversion
                                hep_unit_info = f"{hep_value} {hep_unit} ({conversion_desc})"
                        except ValueError:
                            pass
                    
                    # Clean up name by replacing spaces and special characters
                    name = re.sub(r'[\s\-]', '_', name)
                    name = re.sub(r'[^\w]', '', name)
                    
                    constants.append((name, value, uncertainty, unit, hep_unit_info))
    
    return constants


def extract_year_from_filename(filename: str) -> str:
    """
    Extract year from CODATA filename.
    
    Args:
        filename: CODATA filename (e.g., 'allascii_2010.txt')
        
    Returns:
        Year as string (e.g., '2010')
    """
    match = re.search(r'(\d{4})', filename)
    if match:
        return match.group(1)
    return 'unknown'


def generate_cpp_header(constants: List[Tuple[str, str, str, Optional[str], Optional[str]]], template_path: Path, output_path: Path, year: str) -> None:
    """
    Generate a C++ header file with constexpr constants using Jinja2 template.
    
    Args:
        constants: List of constant tuples (name, value, uncertainty, unit, hep_unit)
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
        'namespace': f'codata{year}'
    }
    
    # Render template
    rendered = template.render(data)
    
    # Write output
    with open(output_path, 'w') as f:
        f.write(rendered)


def process_codata_directory(input_dir: Path, template_path: Path, output_dir: Path) -> None:
    """
    Process all CODATA files in a directory and generate C++ headers.
    
    Args:
        input_dir: Directory containing CODATA ASCII files
        template_path: Path to Jinja2 template file
        output_dir: Directory where C++ headers will be written
    """
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process each CODATA file
    codata_files = list(input_dir.glob('allascii_*.txt'))
    
    if not codata_files:
        print(f"No CODATA files found in {input_dir}")
        return
    
    for codata_file in codata_files:
        # Extract year from filename
        year = extract_year_from_filename(codata_file.name)
        
        # Parse the CODATA file
        constants = parse_codata_file(codata_file)
        
        # Generate output filename
        output_file = output_dir / f"codata_{year}.hpp"
        
        # Generate C++ header
        generate_cpp_header(constants, template_path, output_file, year)
        
        print(f"Generated {output_file.name}: {len(constants)} constants")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Parse CODATA ASCII files and generate C++ headers')
    parser.add_argument('--input_dir', type=Path, default=Path('data/codata'), 
                       help='Directory containing CODATA ASCII files')
    parser.add_argument('--template', type=Path, default=Path('templates/cpp_header.jinja2'),
                       help='Path to Jinja2 template file')
    parser.add_argument('--output_dir', type=Path, default=Path('output'),
                       help='Directory for output C++ headers')
    
    args = parser.parse_args()
    
    # Process all CODATA files in the directory
    process_codata_directory(args.input_dir, args.template, args.output_dir)
    
    print(f"Processing complete. Headers generated in {args.output_dir}")


if __name__ == '__main__':
    main()