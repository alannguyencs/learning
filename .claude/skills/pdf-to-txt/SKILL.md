---
name: pdf-to-txt
description: Convert PDF files to text using scripts/pdf_to_txt.py
---

# PDF to Text Converter

Convert PDF file(s) to `.txt` using the `scripts/pdf_to_txt.py` script.

**Argument:** `<pdf_file_or_directory> [--output <output_directory>]`

- `<pdf_file_or_directory>` — required; a single PDF file path or a directory containing PDF files
- `--output` — optional; directory to save `.txt` files (defaults to same location as input)

## Instructions

1. Parse `$ARGUMENTS` to extract the **input directory** and optional **output directory**.
2. Verify the input directory exists. If not, tell the user and stop.
3. Run the conversion script via the Bash tool:
   ```bash
   python scripts/pdf_to_txt.py --input <input_dir>
   # or, if --output was specified:
   python scripts/pdf_to_txt.py --input <input_dir> --output <output_dir>
   ```
4. After the script completes, list the generated `.txt` files and report how many PDFs were converted.

## Requirements

- Python 3 must be available
- `pypdf` library — if missing, install it first:
  ```bash
  pip install pypdf
  ```

## Notes

- The script converts **all** PDF files found in the input directory
- Output files are named `<original_name>.txt`
- Page numbers are preserved in the output
- If `pypdf` is not installed, install it automatically before running the script

## Output

After conversion, print a summary:

| File | Output |
|------|--------|
| example.pdf | example.txt |
| ... | ... |

Followed by: `Converted N PDF(s) successfully.`
