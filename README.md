# OfficeToolKit

OfficeToolKit is a Python-first collection of small office utilities. Tool 1 extracts tables from a text-based PDF, joins tables that continue onto the next page, removes recurring page header/footer regions, and writes each logical table to its own Excel worksheet.

All processing is Python-only, local, and works without an internet connection
after its dependencies are installed. See `INSTALL.md` for connected and offline
installation instructions.

The extracted cell strings are not interpreted, corrected, converted, or recalculated. The only content cleanup removes PDF extraction artifacts such as null characters and outer whitespace. A repeated table header at a page boundary is omitted when joining the continuation.

## Tool 1: PDF tables to Excel

### Requirements

- Python 3.10 through 3.14 (Python 3.13 is fully supported)

Create an isolated environment and install the Python package. On a computer with
Python 3.13 installed:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

On Windows PowerShell, activate the environment with
`.venv\Scripts\Activate.ps1`. The `dev` extra installs the sample-PDF generator
and test runner; use `python -m pip install .` for runtime-only installation.

Run the converter:

```bash
office-toolkit pdf-tables input.pdf --output output.xlsx
```

### Page headers and footers

By default, the top and bottom 7% of every page are ignored. Adjust this for a particular document layout:

```bash
office-toolkit pdf-tables input.pdf -o output.xlsx --header-ratio 0.10 --footer-ratio 0.08
```

### Behavior and limitations

- Works best on text-based PDFs whose tables have visible ruling lines.
- A table continuation is detected using consecutive pages, equal column count, and position near the page boundaries.
- Worksheet names use the closest text above each table, with Excel-invalid characters removed and duplicate names made unique.
- Untitled tables receive `Table 1`, `Table 2`, and so on.
- Scanned/image-only PDFs need an OCR phase, which is intentionally not included in Phase 1.
- Ambiguous borderless tables may require document-specific table settings in a future profile/configuration layer.

The extraction and workbook modules are separate so a later SharePoint downloader
can supply a local PDF without changing the table processing pipeline. Credentials
and browser-session handling should live in that future integration, not in this
extractor.

## Development

```bash
python -m pytest
python tests/create_sample_pdf.py sample.pdf
office-toolkit pdf-tables sample.pdf --output sample.xlsx
```
