#!/usr/bin/env python3
"""Convert PDF file(s) to .txt files."""

import argparse
import sys
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    print("Error: pypdf is not installed. Run: pip install pypdf")
    sys.exit(1)


def pdf_to_txt(pdf_path: Path, output_dir: Path) -> Path:
    """Extract text from a PDF and write to a .txt file."""
    reader = PdfReader(pdf_path)
    lines = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        lines.append(f"--- Page {i} ---\n{text}")
    out_path = output_dir / (pdf_path.stem + ".txt")
    out_path.write_text("\n\n".join(lines), encoding="utf-8")
    return out_path


def main():
    """Parse arguments and convert PDF(s) to text."""
    parser = argparse.ArgumentParser(
        description="Convert PDFs to .txt files."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="PDF file or directory containing PDF files",
    )
    parser.add_argument(
        "--output",
        help="Directory to save .txt files (default: same as input)",
    )
    args = parser.parse_args()

    input_path = Path(args.input)

    if input_path.is_file():
        pdfs = [input_path]
        default_output = input_path.parent
    elif input_path.is_dir():
        pdfs = sorted(input_path.glob("*.pdf"))
        default_output = input_path
    else:
        print(f"Error: '{input_path}' does not exist.")
        sys.exit(1)

    output_dir = Path(args.output) if args.output else default_output
    output_dir.mkdir(parents=True, exist_ok=True)

    if not pdfs:
        print(f"No PDF files found in '{input_path}'.")
        sys.exit(0)

    for pdf in pdfs:
        out = pdf_to_txt(pdf, output_dir)
        print(f"{pdf.name} -> {out}")

    print(f"\nConverted {len(pdfs)} PDF(s) successfully.")


if __name__ == "__main__":
    main()
