# Installing OfficeToolKit on another system

OfficeToolKit processes PDFs and creates Excel files locally. It does not contain network, upload, telemetry, SharePoint, or authentication code.

## Prerequisites

- Python 3.10 through 3.14. Python 3.13 is fully supported.
- `pip` and the standard-library `venv` module

The Python dependencies include `pdfplumber` for PDF extraction and `openpyxl`
for Excel workbook creation. Node.js is not required.

## Connected installation

Extract the archive, open a terminal in the extracted `OfficeToolKit` folder,
and create an isolated Python 3.13 environment:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install .
```

On Windows PowerShell:

```powershell
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install .
```

The package keeps all build and dependency metadata in `pyproject.toml` and
includes a minimal `setup.py` compatibility shim. If installation reports a
packaging error, confirm the active interpreter and installer:

```bash
python --version
python -m pip --version
```

For development and sample-PDF testing, install the optional tools:

```bash
python -m pip install -e ".[dev]"
```

Run the tool:

```bash
office-toolkit pdf-tables input.pdf --output output.xlsx
```

## Offline installation

On a connected preparation computer, download the Python packages for the target operating system and Python version:

```bash
python -m pip download --dest offline-wheels .
```

Copy the project and `offline-wheels` directory to the offline system, then run:

```bash
python -m pip install --no-index --find-links offline-wheels .
```

Once the Python wheels are installed, processing requires no internet connection.

## Verification

Check the command without processing a document:

```bash
office-toolkit --help
```

Run the included extraction tests from the project folder:

```bash
python -m pytest
```

Run an end-to-end sample conversion:

```bash
python tests/create_sample_pdf.py sample.pdf
office-toolkit pdf-tables sample.pdf --output sample.xlsx
```

The test runner is optional and only needed for development or verification.
