from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ExtractedFragment:
    """A table detected on one PDF page."""

    page_number: int
    bbox: tuple[float, float, float, float]
    rows: list[list[str]]
    title: str | None = None


@dataclass
class ExtractedTable:
    """One logical table, possibly assembled from several pages."""

    title: str
    rows: list[list[str]]
    source_pages: list[int] = field(default_factory=list)

