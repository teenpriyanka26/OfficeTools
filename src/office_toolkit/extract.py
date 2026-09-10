from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

import pdfplumber

from .models import ExtractedFragment, ExtractedTable


DEFAULT_TABLE_SETTINGS: dict[str, Any] = {
    "vertical_strategy": "lines",
    "horizontal_strategy": "lines",
    "snap_tolerance": 4,
    "join_tolerance": 4,
    "intersection_tolerance": 5,
    "text_tolerance": 3,
}


def _clean_cell(value: object) -> str:
    """Normalize extraction artifacts only; never interpret or transform data."""
    if value is None:
        return ""
    return str(value).replace("\x00", "").strip()


def _normalize_row(row: Iterable[object], width: int | None = None) -> list[str]:
    cells = [_clean_cell(cell) for cell in row]
    if width is not None:
        cells = (cells + [""] * width)[:width]
    return cells


def _row_signature(row: Iterable[str]) -> tuple[str, ...]:
    return tuple(re.sub(r"\s+", " ", cell).strip().casefold() for cell in row)


def _looks_like_page_marker(text: str) -> bool:
    compact = re.sub(r"\s+", " ", text).strip()
    return bool(
        re.fullmatch(r"(?:page\s*)?\d+(?:\s*(?:of|/)\s*\d+)?", compact, re.I)
        or re.fullmatch(r"[-–—]?\s*\d+\s*[-–—]?", compact)
    )


def _extract_title(page: Any, bbox: tuple[float, float, float, float]) -> str | None:
    """Return the closest non-footer text line immediately above a table."""
    x0, top, x1, _ = bbox
    page_x0, page_top, page_x1, _ = page.bbox
    search_top = max(page_top, top - min(110.0, page.height * 0.16))
    if top <= search_top:
        return None
    region = page.crop((max(page_x0, x0 - 8), search_top, min(page_x1, x1 + 8), top))
    words = region.extract_words(use_text_flow=True, keep_blank_chars=False) or []
    if not words:
        return None

    lines: list[list[dict[str, Any]]] = []
    for word in sorted(words, key=lambda item: (round(item["top"] / 3), item["x0"])):
        if not lines or abs(lines[-1][0]["top"] - word["top"]) > 3:
            lines.append([word])
        else:
            lines[-1].append(word)

    for line in reversed(lines):
        text = " ".join(word["text"] for word in sorted(line, key=lambda item: item["x0"])).strip()
        if text and not _looks_like_page_marker(text):
            return text
    return None


def _page_fragments(
    page: Any,
    page_number: int,
    *,
    header_ratio: float,
    footer_ratio: float,
    table_settings: dict[str, Any],
) -> list[ExtractedFragment]:
    # Cropping removes recurring page furniture before table detection. Coordinates
    # remain relative to the cropped page, which is sufficient for continuation tests.
    content = page.crop((0, page.height * header_ratio, page.width, page.height * (1 - footer_ratio)))
    found = content.find_tables(table_settings=table_settings)
    fragments: list[ExtractedFragment] = []
    for table in sorted(found, key=lambda item: (item.bbox[1], item.bbox[0])):
        # Detection settings belong to find_tables(); Table.extract() accepts only
        # text tolerances in pdfplumber and otherwise uses the detected cell grid.
        raw_rows = table.extract() or []
        rows = [_normalize_row(row) for row in raw_rows]
        rows = [row for row in rows if any(cell != "" for cell in row)]
        if not rows:
            continue
        width = max(len(row) for row in rows)
        rows = [_normalize_row(row, width) for row in rows]
        content_top = float(content.bbox[1])
        relative_bbox = (
            float(table.bbox[0]),
            float(table.bbox[1]) - content_top,
            float(table.bbox[2]),
            float(table.bbox[3]) - content_top,
        )
        fragments.append(
            ExtractedFragment(
                page_number=page_number,
                bbox=relative_bbox,
                rows=rows,
                title=_extract_title(content, table.bbox),
            )
        )
    return fragments


def _is_continuation(previous: ExtractedFragment, current: ExtractedFragment, page_height: float) -> bool:
    if current.page_number != previous.page_number + 1:
        return False
    if len(previous.rows[0]) != len(current.rows[0]):
        return False
    previous_near_bottom = previous.bbox[3] >= page_height * 0.72
    current_near_top = current.bbox[1] <= page_height * 0.30
    explicit_new_title = bool(current.title and current.bbox[1] - page_height * 0.06 > 20)
    return previous_near_bottom and current_near_top and not explicit_new_title


def _append_continuation(existing: list[list[str]], incoming: list[list[str]]) -> None:
    if not incoming:
        return
    # Drop only a repeated column header at a page boundary. No data rows are edited.
    if existing and _row_signature(existing[0]) == _row_signature(incoming[0]):
        incoming = incoming[1:]
    existing.extend(incoming)


def assemble_fragments(
    fragments: list[ExtractedFragment], page_heights: dict[int, float]
) -> list[ExtractedTable]:
    """Join page fragments when geometry and column structure indicate continuation."""
    if not fragments:
        return []

    result: list[ExtractedTable] = []
    group_last: ExtractedFragment | None = None
    untitled_count = 0
    used_titles: Counter[str] = Counter()

    for fragment in fragments:
        continuing = bool(
            result
            and group_last
            and _is_continuation(group_last, fragment, page_heights[group_last.page_number])
        )
        if continuing:
            _append_continuation(result[-1].rows, fragment.rows)
            result[-1].source_pages.append(fragment.page_number)
        else:
            title = (fragment.title or "").strip()
            if not title:
                untitled_count += 1
                title = f"Table {untitled_count}"
            used_titles[title] += 1
            unique_title = title if used_titles[title] == 1 else f"{title} ({used_titles[title]})"
            result.append(
                ExtractedTable(
                    title=unique_title,
                    rows=[row[:] for row in fragment.rows],
                    source_pages=[fragment.page_number],
                )
            )
        group_last = fragment
    return result


def extract_tables(
    pdf_path: str | Path,
    *,
    header_ratio: float = 0.07,
    footer_ratio: float = 0.07,
    table_settings: dict[str, Any] | None = None,
) -> list[ExtractedTable]:
    """Extract complete logical tables from a text-based PDF."""
    path = Path(pdf_path)
    if not path.is_file():
        raise FileNotFoundError(f"PDF not found: {path}")
    if not 0 <= header_ratio < 0.4 or not 0 <= footer_ratio < 0.4:
        raise ValueError("Header and footer ratios must be between 0 and 0.4")

    settings = dict(DEFAULT_TABLE_SETTINGS)
    if table_settings:
        settings.update(table_settings)

    fragments: list[ExtractedFragment] = []
    page_heights: dict[int, float] = {}
    with pdfplumber.open(path) as pdf:
        for number, page in enumerate(pdf.pages, start=1):
            page_heights[number] = float(page.height * (1 - header_ratio - footer_ratio))
            fragments.extend(
                _page_fragments(
                    page,
                    number,
                    header_ratio=header_ratio,
                    footer_ratio=footer_ratio,
                    table_settings=settings,
                )
            )
    return assemble_fragments(fragments, page_heights)
