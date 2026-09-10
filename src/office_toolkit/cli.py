from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from .export import export_tables
from .extract import extract_tables


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="office-toolkit", description="OfficeToolKit utilities")
    commands = parser.add_subparsers(dest="command", required=True)
    extract = commands.add_parser("pdf-tables", help="Extract PDF tables into an Excel workbook")
    extract.add_argument("pdf", type=Path, help="Input PDF file")
    extract.add_argument("-o", "--output", type=Path, help="Output .xlsx path")
    extract.add_argument("--header-ratio", type=float, default=0.07, help="Top page fraction to ignore")
    extract.add_argument("--footer-ratio", type=float, default=0.07, help="Bottom page fraction to ignore")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "pdf-tables":
        output = args.output or args.pdf.with_suffix(".xlsx")
        if output.suffix.lower() != ".xlsx":
            print("error: output must end in .xlsx", file=sys.stderr)
            return 2
        try:
            tables = extract_tables(
                args.pdf,
                header_ratio=args.header_ratio,
                footer_ratio=args.footer_ratio,
            )
            result = export_tables(tables, output)
        except (OSError, RuntimeError, ValueError, subprocess.CalledProcessError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        print(f"Created {result} with {len(tables)} table(s).")
        return 0
    return 2
if __name__ == "__main__":
    raise SystemExit(main())
