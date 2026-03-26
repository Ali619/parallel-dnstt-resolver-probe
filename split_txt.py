#!/usr/bin/env python3
"""
Split a large text file into smaller files of 1000 lines each.
"""

import argparse
from pathlib import Path
from typing import Iterator, List


def read_chunks(file_path: Path, chunk_size: int = 1000) -> Iterator[List[str]]:
    """
    Read file in chunks of specified size.

    Args:
        file_path: Path to input file
        chunk_size: Number of lines per chunk

    Yields:
        List of lines for each chunk
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        chunk = []
        for line in f:
            chunk.append(line)
            if len(chunk) == chunk_size:
                yield chunk
                chunk = []

        # Yield remaining lines if any
        if chunk:
            yield chunk


def split_file(input_file: str, output_dir: str = ".", chunk_size: int = 1000) -> None:
    """
    Split a text file into multiple files of chunk_size lines each.

    Args:
        input_file: Path to the input text file
        output_dir: Directory to save output files (default: current directory)
        chunk_size: Number of lines per output file (default: 1000)
    """
    input_path = Path(input_file)
    output_path = Path(output_dir)

    # Validation
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    if not input_path.is_file():
        raise ValueError(f"Input path is not a file: {input_file}")

    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)

    # Process chunks
    line_number = 1
    file_count = 0

    for chunk in read_chunks(input_path, chunk_size):
        start_line = line_number
        end_line = line_number + len(chunk) - 1

        # Generate output filename: 1_1000.txt, 1001_2000.txt, etc.
        output_filename = f"{start_line}_{end_line}.txt"
        output_file_path = output_path / output_filename

        # Write chunk to file
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.writelines(chunk)

        print(f"Created: {output_filename} ({len(chunk)} lines)")

        line_number += len(chunk)
        file_count += 1

    print(f"\nSplit complete: {file_count} files created")
    print(f"Total lines processed: {line_number - 1}")


def main():
    parser = argparse.ArgumentParser(
        description="Split a text file into multiple files of 1000 lines each"
    )
    parser.add_argument(
        "-i", "--input_file",
        help="Path to the input text file"
    )
    parser.add_argument(
        "-o", "--output-dir",
        default="./split",
        help="Output directory for split files (default: current directory)"
    )
    parser.add_argument(
        "-c", "--chunk-size",
        type=int,
        default=1000,
        help="Number of lines per output file (default: 1000)"
    )

    args = parser.parse_args()

    try:
        split_file(args.input_file, args.output_dir, args.chunk_size)
    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
