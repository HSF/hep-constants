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
            
            # Skip empty lines and comment lines
            if not line or line.startswith('{'):
                continue
            
            # Skip header lines
            if 'Quantity' in line or 'Value' in line or 'Unit' in line:
                continue
            
            # CODATA format: name, then value (space-separated digits), then uncertainty (space-separated digits), then unit
            # Example: "alpha particle mass                                         6.644 656 75 e-27        0.000 000 29 e-27        kg"
            
            # Use a more robust approach to parse CODATA format
            # The format is: name, value (space-separated digits), uncertainty (space-separated digits), unit
            
            # Split the line into parts
            parts = line.split()
            
            # Find where numeric data ends and unit begins
            # Work backwards to find the last numeric part
            last_numeric_idx = -1
            for i in range(len(parts)-1, -1, -1):
                if re.match(r'^\d|\.|\+|-|e|E', parts[i]):
                    last_numeric_idx = i
                    break
            
            if last_numeric_idx == -1:
                continue
            
            # The unit starts after the last numeric part
            unit_parts = parts[last_numeric_idx + 1:]
            numeric_parts = parts[:last_numeric_idx + 1]
            
            # Find where the numeric data actually starts (separate from name)
            # Work backwards through numeric_parts to find the start of numeric data
            # A part is numeric if it looks like a number (digits, decimal point, scientific notation)
            numeric_start = 0
            for i in range(len(numeric_parts)-1, -1, -1):
                part = numeric_parts[i]
                # Check if this part looks like a number
                # It should either start with a digit, or be a scientific notation exponent
                is_numeric = False
                if re.match(r'^\d', part):  # Starts with digit
                    is_numeric = True
                elif re.match(r'^\.', part):  # Starts with decimal point
                    is_numeric = True
                elif re.match(r'^\+|^-', part):  # Starts with sign
                    # Check if next part is numeric
                    if i + 1 < len(numeric_parts) and re.match(r'^\d', numeric_parts[i+1]):
                        is_numeric = True
                elif re.match(r'^e|E', part):  # Scientific notation exponent
                    # Check if previous part ends with digit (or is a decimal point)
                    if i > 0:
                        prev_part = numeric_parts[i-1]
                        # Check if previous part ends with digit or is a decimal point
                        ends_with_digit = prev_part[-1].isdigit() if prev_part else False
                        is_decimal_point = (prev_part == '.')
                        if ends_with_digit or is_decimal_point:
                            is_numeric = True
                
                if not is_numeric:
                    numeric_start = i + 1
                    break
            
            if numeric_start >= len(numeric_parts):
                continue
            
            # Extract components
            name_parts = numeric_parts[:numeric_start]
            numeric_data = numeric_parts[numeric_start:]
            unit = ' '.join(unit_parts) if unit_parts else None
            name = ' '.join(name_parts).strip()
            
            # Find where value ends and uncertainty begins
            # The uncertainty typically starts with "0." and has many zeros
            split_idx = len(numeric_data)
            
            # First, check if this might be an exact value (no uncertainty)
            # If the unit contains "(exact)" or similar, there might be no uncertainty
            if unit and any(word in unit.lower() for word in ['(exact)', 'exact', '(defined)']):
                # For exact values, all numeric data is the value
                split_idx = len(numeric_data)
            else:
                for i in range(1, len(numeric_data)):
                    # Look for the pattern that indicates uncertainty start
                    if re.match(r'^0\.0*', numeric_data[i]):
                        split_idx = i
                        break
                    # If we see "e" followed by digits, that's part of the exponent
                    if i > 0 and re.match(r'^e|E', numeric_data[i]) and re.match(r'^\d', numeric_data[i-1]):
                        continue
                    # Removed the heuristic that was causing incorrect splits
                    # We now rely only on the 0. pattern which is more reliable
                
                if split_idx == len(numeric_data):
                    # If we couldn't find a good split, try to find where the pattern changes
                    # Look for the first occurrence of "0." pattern (most reliable indicator)
                    for i in range(1, len(numeric_data)):
                        if re.match(r'^0\.', numeric_data[i]):
                            split_idx = i
                            break
                    
                    # If still no split found, leave split_idx at len(numeric_data)
                    # This means no uncertainty was detected, so all numeric data is the value
            
            # Reconstruct value and uncertainty by removing spaces
            if split_idx == len(numeric_data):
                # No uncertainty detected - all numeric data is the value
                value_parts = numeric_data
                uncertainty_parts = []
                value = ''.join(value_parts)
                uncertainty = ""
            else:
                value_parts = numeric_data[:split_idx]
                uncertainty_parts = numeric_data[split_idx:]
                value = ''.join(value_parts)
                uncertainty = ''.join(uncertainty_parts)
            
            # Clean up trailing dots (ellipsis) that would cause compilation errors
            value = re.sub(r'\.+$', '', value)  # Remove trailing dots
            uncertainty = re.sub(r'\.+$', '', uncertainty)  # Remove trailing dots
            
            # Clean up name - be more careful to preserve meaningful parts
            # First convert spaces and hyphens to underscores
            name = re.sub(r'[\s\-]', '_', name)
            # Remove only problematic characters, but preserve underscores that separate words
            name = re.sub(r'[^\w_]', '', name)  # Keep underscores
            # Remove duplicate underscores
            name = re.sub(r'_+', '_', name)
            # Remove leading/trailing underscores
            name = name.strip('_')
            
            # Convert to HEP units if possible
            hep_unit_info = None
            if unit:
                try:
                    si_value = float(value)
                    hep_conversion = convert_si_to_hep(si_value, unit)
                    if hep_conversion:
                        hep_value, hep_unit, conversion_desc = hep_conversion
                        hep_unit_info = f"{hep_value} {hep_unit} ({conversion_desc})"
                except ValueError:
                    pass
            
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