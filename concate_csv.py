#!/usr/bin/env python3
"""
Concatenate multiple CSV files in a directory into a single CSV file.
No pandas required - uses only standard library.
"""

import argparse
import csv
from pathlib import Path
from typing import List, Optional


def get_csv_files(directory: str, pattern: str = "*.csv") -> List[Path]:
    """
    Get all CSV files in a directory matching the pattern.

    Args:
        directory: Path to directory containing CSV files
        pattern: Glob pattern for matching files (default: *.csv)

    Returns:
        List of Path objects for CSV files, sorted by name
    """
    dir_path = Path(directory)

    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    if not dir_path.is_dir():
        raise ValueError(f"Path is not a directory: {directory}")

    csv_files = sorted(dir_path.glob(pattern))

    if not csv_files:
        raise ValueError(
            f"No CSV files found in {directory} matching pattern '{pattern}'")

    return csv_files


def concat_csv_files(
    input_dir: str,
    output_file: str,
    pattern: str = "*.csv",
    skip_header: bool = True,
    encoding: str = 'utf-8'
) -> None:
    """
    Concatenate multiple CSV files into a single file.

    Args:
        input_dir: Directory containing CSV files
        output_file: Path to output concatenated CSV file
        pattern: Glob pattern for matching files (default: *.csv)
        skip_header: If True, only keep header from first file (default: True)
        encoding: File encoding (default: utf-8)
    """
    csv_files = get_csv_files(input_dir, pattern)

    print(f"Found {len(csv_files)} CSV files to concatenate")
    print(f"Output file: {output_file}")
    print("-" * 50)

    total_rows = 0
    header_written = False

    with open(output_file, 'w', newline='', encoding=encoding) as outfile:
        writer = None

        for idx, csv_file in enumerate(csv_files, 1):
            print(f"[{idx}/{len(csv_files)}] Processing: {csv_file.name}")

            try:
                with open(csv_file, 'r', newline='', encoding=encoding) as infile:
                    reader = csv.reader(infile)

                    rows = list(reader)

                    if not rows:
                        print(
                            f"  ⚠ Warning: {csv_file.name} is empty, skipping")
                        continue

                    # Handle header
                    if skip_header:
                        if not header_written:
                            # Write header from first file
                            for row in rows:
                                outfile.write(','.join(row) + '\n')
                                total_rows += 1
                            header_written = True
                        else:
                            # Skip header, write data rows only
                            for row in rows[1:]:
                                outfile.write(','.join(row) + '\n')
                                total_rows += 1
                    else:
                        # Write all rows including headers
                        for row in rows:
                            outfile.write(','.join(row) + '\n')
                            total_rows += 1

                    data_rows = len(
                        rows) - (1 if skip_header and header_written else 0)
                    print(f"  ✓ Added {data_rows} rows")

            except Exception as e:
                print(f"  ✗ Error processing {csv_file.name}: {e}")
                continue

    print("-" * 50)
    print(f"✓ Concatenation complete!")
    print(f"  Total rows written: {total_rows}")
    print(f"  Output saved to: {output_file}")


def concat_csv_files_alternative(
    input_dir: str,
    output_file: str,
    pattern: str = "*.csv",
    skip_header: bool = True,
    encoding: str = 'utf-8'
) -> None:
    """
    Alternative implementation using csv.DictReader/DictWriter.
    Better for preserving CSV structure and handling quoted fields.
    """
    csv_files = get_csv_files(input_dir, pattern)

    print(f"Found {len(csv_files)} CSV files to concatenate")
    print(f"Output file: {output_file}")
    print("-" * 50)

    total_rows = 0
    fieldnames = None

    with open(output_file, 'w', newline='', encoding=encoding) as outfile:
        writer = None

        for idx, csv_file in enumerate(csv_files, 1):
            print(f"[{idx}/{len(csv_files)}] Processing: {csv_file.name}")

            try:
                with open(csv_file, 'r', newline='', encoding=encoding) as infile:
                    reader = csv.DictReader(infile)

                    # Initialize writer with fieldnames from first file
                    if writer is None:
                        fieldnames = reader.fieldnames
                        if not fieldnames:
                            print(
                                f"  ⚠ Warning: {csv_file.name} has no header, skipping")
                            continue
                        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                        if skip_header:
                            writer.writeheader()

                    # Write rows
                    rows_added = 0
                    for row in reader:
                        writer.writerow(row)
                        rows_added += 1
                        total_rows += 1

                    print(f"  ✓ Added {rows_added} rows")

            except Exception as e:
                print(f"  ✗ Error processing {csv_file.name}: {e}")
                continue

    print("-" * 50)
    print(f"✓ Concatenation complete!")
    print(f"  Total data rows written: {total_rows}")
    print(f"  Output saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Concatenate multiple CSV files into a single CSV file"
    )
    parser.add_argument(
        "input_dir",
        help="Directory containing CSV files to concatenate"
    )
    parser.add_argument(
        "-o", "--output",
        default="concatenated.csv",
        help="Output CSV file path (default: concatenated.csv)"
    )
    parser.add_argument(
        "-p", "--pattern",
        default="*.csv",
        help="File pattern to match (default: *.csv)"
    )
    parser.add_argument(
        "--keep-all-headers",
        action="store_true",
        help="Keep headers from all files (default: keep only first header)"
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="File encoding (default: utf-8)"
    )
    parser.add_argument(
        "--use-dictreader",
        action="store_true",
        help="Use DictReader/DictWriter for better CSV handling"
    )

    args = parser.parse_args()

    try:
        if args.use_dictreader:
            concat_csv_files_alternative(
                args.input_dir,
                args.output,
                pattern=args.pattern,
                skip_header=not args.keep_all_headers,
                encoding=args.encoding
            )
        else:
            concat_csv_files(
                args.input_dir,
                args.output,
                pattern=args.pattern,
                skip_header=not args.keep_all_headers,
                encoding=args.encoding
            )
    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
