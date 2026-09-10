from pathlib import Path
import sys

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def draw_table(pdf, x, y_top, widths, rows, row_height=22):
    total_width = sum(widths)
    y_bottom = y_top - row_height * len(rows)
    pdf.line(x, y_top, x + total_width, y_top)
    for row_index, row in enumerate(rows):
        y = y_top - row_height * row_index
        pdf.line(x, y, x + total_width, y)
        cursor = x
        for col_index, value in enumerate(row):
            pdf.drawString(cursor + 4, y - 15, value)
            cursor += widths[col_index]
    pdf.line(x, y_bottom, x + total_width, y_bottom)
    cursor = x
    pdf.line(cursor, y_top, cursor, y_bottom)
    for width in widths:
        cursor += width
        pdf.line(cursor, y_top, cursor, y_bottom)


def create(path: Path):
    pdf = canvas.Canvas(str(path), pagesize=letter)
    pdf.setFont("Helvetica", 9)
    pdf.drawCentredString(306, 770, "CONFIDENTIAL PROJECT REPORT")
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, 735, "Asset Register")
    pdf.setFont("Helvetica", 9)
    rows = [["ID", "Description", "Amount"]] + [
        [str(number), f"Item {number}", f"{number * 10}.00"] for number in range(1, 27)
    ]
    draw_table(pdf, 50, 710, [70, 280, 110], rows)
    pdf.drawCentredString(306, 20, "Page 1 of 2")
    pdf.showPage()

    pdf.setFont("Helvetica", 9)
    pdf.drawCentredString(306, 770, "CONFIDENTIAL PROJECT REPORT")
    remaining = [["ID", "Description", "Amount"]] + [
        [str(number), f"Item {number}", f"{number * 10}.00"] for number in range(27, 32)
    ]
    draw_table(pdf, 50, 735, [70, 280, 110], remaining)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, 530, "Project Contacts")
    pdf.setFont("Helvetica", 9)
    draw_table(
        pdf,
        50,
        505,
        [180, 280],
        [["Role", "Name"], ["Manager", "A. Example"], ["Coordinator", "B. Example"]],
    )
    pdf.drawCentredString(306, 20, "Page 2 of 2")
    pdf.save()


if __name__ == "__main__":
    create(Path(sys.argv[1]))

