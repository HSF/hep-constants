#!/usr/bin/env python3
"""Parse CODATA ASCII files and generate C++ headers with constexpr constants."""

import argparse
import logging
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
    data_section = False
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Look for the separator line that indicates start of data
            if line.startswith('---') and len(line) > 50:  # Long separator line
                data_section = True
                continue
            
            # Skip lines before the data section
            if not data_section:
                continue
            
            # Modern CODATA files have the structure 
            # NAME    VALUE     UNCERTAINTY    [UNITS]
            # Each of the pieces can have spaces, and UNITS are optional
            # Subtleties:
            # - UNCERTAINTY can be "(exact)" for defined values
            # - VALUE can have a trailing ellipsis
            #
            # Each piece is separated **by at least 2 spaces** which is the key to the regexp
            # match below
            # Example: "alpha particle mass                                         6.644 656 75 e-27        0.000 000 29 e-27        kg"
            pieces = re.split(r"\s{2,}", line)
            if len(pieces) < 3 or len(pieces) > 4:
                logging.warning(f"Got an unexpected number of splits from this CODATA line:\n{line}")
                continue

            # Convert the name into a valid C++ identifier
            # Remove spaces and underscores
            codata_cpp_name = re.sub(r'[\s\-]', '_', pieces[0]).strip()
            # Remove non-word characters
            codata_cpp_name = re.sub(r'[^\w_]', '', codata_cpp_name)

            # Change the value into a valid C++ numerical value
            codata_value = re.sub(r'\s', '', pieces[1])
            # Remove training ellipsis
            codata_value = re.sub(r"\.\.\.", "", codata_value)

            # Uncertainty
            codata_uncertainty = re.sub(r'\s', '', pieces[2])

            # Units
            if len(pieces) == 4:
                codata_units = pieces[3]
            else:
                codata_units = ""
            
            # Convert to HEP units if possible
            hep_unit_info = None
            # if unit:
            #     try:
            #         si_value = float(value)
            #         hep_conversion = convert_si_to_hep(si_value, unit)
            #         if hep_conversion:
            #             hep_value, hep_unit, conversion_desc = hep_conversion
            #             hep_unit_info = f"{hep_value} {hep_unit} ({conversion_desc})"
            #     except ValueError:
            #         pass
            
            # print(f":{codata_uncertainty}:")
            constants.append((codata_cpp_name, codata_value, codata_uncertainty, codata_units, hep_unit_info))
    
    # print(constants)
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
    parser.add_argument('--prefixes', action='store_true',
                       help='Also generate SI prefixes header')
    parser.add_argument('--units', action='store_true',
                       help='Also generate HEP units header')
    
    args = parser.parse_args()
    
    # Process all CODATA files in the directory
    process_codata_directory(args.input_dir, args.template, args.output_dir)
    
    print(f"Processing complete. Headers generated in {args.output_dir}")
    
    # Generate prefixes header if requested
    if args.prefixes:
        from generate_prefixes import generate_prefixes_header
        generate_prefixes_header(args.output_dir / 'prefixes.hpp')
        print("Also generated prefixes.hpp")
    
    # Generate units header if requested
    if args.units:
        from generate_units import generate_units_header
        generate_units_header(args.output_dir / 'units.hpp')
        print("Also generated units.hpp")


if __name__ == '__main__':
    main()