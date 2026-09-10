from office_toolkit.extract import assemble_fragments
from office_toolkit.models import ExtractedFragment


def fragment(page, bbox, rows, title=None):
    return ExtractedFragment(page_number=page, bbox=bbox, rows=rows, title=title)


def test_joins_multi_page_table_and_removes_only_repeated_header():
    parts = [
        fragment(1, (20, 100, 580, 760), [["ID", "Value"], ["1", "Alpha"]], "Asset Register"),
        fragment(2, (20, 20, 580, 300), [["ID", "Value"], ["2", "Beta"]]),
    ]
    tables = assemble_fragments(parts, {1: 800, 2: 800})
    assert len(tables) == 1
    assert tables[0].title == "Asset Register"
    assert tables[0].source_pages == [1, 2]
    assert tables[0].rows == [["ID", "Value"], ["1", "Alpha"], ["2", "Beta"]]


def test_keeps_separate_tables_on_same_page():
    parts = [
        fragment(1, (20, 100, 580, 300), [["A"], ["1"]], "First"),
        fragment(1, (20, 400, 580, 600), [["B"], ["2"]], "Second"),
    ]
    tables = assemble_fragments(parts, {1: 800})
    assert [table.title for table in tables] == ["First", "Second"]


def test_different_column_count_starts_new_table():
    parts = [
        fragment(1, (20, 500, 580, 790), [["A", "B"], ["1", "2"]], "Two Columns"),
        fragment(2, (20, 10, 580, 300), [["A", "B", "C"], ["3", "4", "5"]]),
    ]
    tables = assemble_fragments(parts, {1: 800, 2: 800})
    assert len(tables) == 2

