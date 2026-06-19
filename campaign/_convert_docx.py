"""Konvertiert alle .docx im campaign-Ordner nach Markdown."""
import glob
import os
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph


def iter_block_items(parent):
    """Liefert Paragraphen und Tabellen in Dokumentreihenfolge."""
    from docx.document import Document as _Doc
    from docx.oxml.table import CT_Tbl
    from docx.oxml.text.paragraph import CT_P
    body = parent.element.body
    for child in body.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)


def para_to_md(p):
    text = p.text.strip()
    if not text:
        return ""
    style = (p.style.name or "").lower()
    if style.startswith("heading") or style.startswith("überschrift"):
        digits = "".join(c for c in style if c.isdigit())
        level = int(digits) if digits else 1
        level = min(max(level, 1), 6)
        return "#" * level + " " + text
    if style.startswith("title") or style.startswith("titel"):
        return "# " + text
    if "list" in style:
        return "- " + text
    return text


def table_to_md(t):
    rows = t.rows
    if not rows:
        return ""
    lines = []
    header = [c.text.strip().replace("\n", " ") for c in rows[0].cells]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("| " + " | ".join("---" for _ in header) + " |")
    for r in rows[1:]:
        cells = [c.text.strip().replace("\n", " ") for c in r.cells]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def convert(path):
    doc = Document(path)
    out = []
    prev_list = False
    for block in iter_block_items(doc):
        if isinstance(block, Paragraph):
            md = para_to_md(block)
            out.append(md)
        else:
            out.append("")
            out.append(table_to_md(block))
            out.append("")
    # leere Zeilen zusammenfassen
    text = "\n\n".join(s for s in out if s != "")
    return text + "\n"


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    for path in sorted(glob.glob(os.path.join(base, "*.docx"))):
        if os.path.basename(path).startswith("~$"):
            continue
        md_path = os.path.splitext(path)[0] + ".md"
        try:
            md = convert(path)
        except Exception as e:
            print("FEHLER", os.path.basename(path), e)
            continue
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md)
        print("OK", os.path.basename(md_path), len(md), "Zeichen")


if __name__ == "__main__":
    main()
