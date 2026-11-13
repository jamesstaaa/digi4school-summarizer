#!/usr/bin/env python3
"""build_summary_docx.py - turn a JSON summary spec into a clean, consistent Word document.

Usage:  python3 build_summary_docx.py spec.json out.docx

Spec (JSON):
{
  "title": "Internationale Geschaeftstaetigkeit",
  "subtitle": "Praxisblicke Betriebswirtschaft IV - S. 40-55",
  "source": "Praxisblicke Betriebswirtschaft IV (TRAUNER), S. 40-55",   # shown in the footer
  "source_pages": 16,                       # pages of the BOOK that were summarised (length guard)
  "max_words_per_page": 110,                # optional override of the length guard
  "blocks": [
    {"h1": "1 Risiken", "pages": "S. 40-46"},
    {"h2": "1.1 Wirtschaftliche Risiken"},
    {"bullets": ["**Begriff:** kurze Definition", ["Unterpunkt", "Unterpunkt"], "naechster Punkt"]},
    {"table": {"header": ["Zollart", "Funktion"], "rows": [["**Schutzzoll**", "schuetzt Inlandsproduzenten"]],
               "widths": [1, 3]}},
    {"figure": {"path": "/abs/path/fig.png", "caption": "Markteintritt (S. 48)", "width_cm": 12}},
    {"note": "**Merke:** ..."},
    {"pagebreak": true}
  ]
}
Inline formatting: **bold** only. A list that directly follows a bullet string = its sub-bullets.
Table cells may contain several lines separated by \\n (lines starting with "- " become bullets).
Exit code 3 = file written but the summary is TOO LONG for the source pages -> tighten and rebuild.
"""
import json
import os
import re
import sys

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ACCENT = RGBColor(0xB3, 0x1B, 0x1B)
GREY = RGBColor(0x66, 0x66, 0x66)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
USABLE_CM = 17.0          # A4 (21 cm) minus 2 x 2 cm margins
MAX_FIG_HEIGHT_CM = 10.5
DEFAULT_MAX_WORDS_PER_PAGE = 110


# ---------- low-level helpers ----------
def _set_fonts(style, name="Calibri"):
    style.font.name = name
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for a in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        rfonts.attrib.pop(qn(a), None)
    for a in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(a), name)


def _shade(cell, hex_fill):
    tcpr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_fill)
    tcpr.append(shd)


def _row_flag(row, tag):
    trpr = row._tr.get_or_add_trPr()
    el = OxmlElement(tag)
    el.set(qn("w:val"), "true")
    trpr.append(el)


def _cell_margins(table, top=40, bottom=40, left=80, right=80):
    tblpr = table._tbl.tblPr
    mar = OxmlElement("w:tblCellMar")
    for side, val in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        el = OxmlElement(f"w:{side}")
        el.set(qn("w:w"), str(val))
        el.set(qn("w:type"), "dxa")
        mar.append(el)
    tblpr.append(mar)


def _runs(p, text, size=None, color=None, italic=False, bold_all=False):
    for part in re.split(r"(\*\*.+?\*\*)", text):
        if not part:
            continue
        is_b = part.startswith("**") and part.endswith("**") and len(part) > 4
        r = p.add_run(part[2:-2] if is_b else part)
        if is_b or bold_all:
            r.bold = True
        if italic:
            r.italic = True
        if size:
            r.font.size = Pt(size)
        if color is not None:
            r.font.color.rgb = color


def _bottom_border(p, color="B31B1B", sz=8):
    ppr = p._p.get_or_add_pPr()
    pb = OxmlElement("w:pBdr")
    b = OxmlElement("w:bottom")
    b.set(qn("w:val"), "single")
    b.set(qn("w:sz"), str(sz))
    b.set(qn("w:space"), "1")
    b.set(qn("w:color"), color)
    pb.append(b)
    ppr.append(pb)


def _page_field(p):
    run = p.add_run()
    run.font.size = Pt(8)
    run.font.color.rgb = GREY
    a = OxmlElement("w:fldChar")
    a.set(qn("w:fldCharType"), "begin")
    t = OxmlElement("w:instrText")
    t.set(qn("xml:space"), "preserve")
    t.text = "PAGE"
    c = OxmlElement("w:fldChar")
    c.set(qn("w:fldCharType"), "end")
    run._r.append(a)
    run._r.append(t)
    run._r.append(c)


def _count_words(blocks):
    n = 0

    def w(s):
        return len(re.sub(r"\*\*", "", str(s)).split())

    for b in blocks:
        for k in ("h1", "h2", "h3", "p", "note"):
            if k in b:
                n += w(b[k])
        if "bullets" in b:
            def walk(items):
                t = 0
                for it in items:
                    t += walk(it) if isinstance(it, list) else w(it)
                return t
            n += walk(b["bullets"])
        if "table" in b:
            tb = b["table"]
            n += sum(w(c) for c in tb.get("header", []))
            n += sum(w(c) for r in tb.get("rows", []) for c in r)
        if "figure" in b:
            n += w(b["figure"].get("caption", ""))
    return n


# ---------- builder ----------
def build(spec, out_path):
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21), Cm(29.7)
    sec.left_margin = sec.right_margin = Cm(2)
    sec.top_margin, sec.bottom_margin = Cm(1.8), Cm(1.8)

    normal = doc.styles["Normal"]
    _set_fonts(normal)
    normal.font.size = Pt(10)
    normal.paragraph_format.space_after = Pt(2)
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.line_spacing = 1.05

    for name, size, color, before, after in (
        ("Heading 1", 14, ACCENT, 12, 3),
        ("Heading 2", 11.5, ACCENT, 8, 2),
        ("Heading 3", 10.5, RGBColor(0x33, 0x33, 0x33), 6, 1),
    ):
        st = doc.styles[name]
        _set_fonts(st)
        st.font.size = Pt(size)
        st.font.bold = True
        st.font.italic = False
        st.font.color.rgb = color
        st.paragraph_format.space_before = Pt(before)
        st.paragraph_format.space_after = Pt(after)
        st.paragraph_format.keep_with_next = True

    for name, indent in (("List Bullet", 0.55), ("List Bullet 2", 1.15)):
        st = doc.styles[name]
        _set_fonts(st)
        st.font.size = Pt(10)
        st.paragraph_format.space_after = Pt(1.5)
        st.paragraph_format.left_indent = Cm(indent)
        st.paragraph_format.first_line_indent = Cm(-0.45)

    # title block
    p = doc.add_paragraph()
    _runs(p, spec.get("title", "Zusammenfassung"), size=20, color=ACCENT, bold_all=True)
    p.paragraph_format.space_after = Pt(0)
    if spec.get("subtitle"):
        p = doc.add_paragraph()
        _runs(p, spec["subtitle"], size=10.5, color=GREY)
        p.paragraph_format.space_after = Pt(4)
    _bottom_border(p if spec.get("subtitle") else doc.paragraphs[-1])

    # footer
    fp = sec.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = fp.add_run((("Quelle: " + spec["source"] + "  |  ") if spec.get("source") else "") + "Seite ")
    r.font.size = Pt(8)
    r.font.color.rgb = GREY
    _page_field(fp)

    for b in spec.get("blocks", []):
        if "h1" in b or "h2" in b or "h3" in b:
            key = "h1" if "h1" in b else ("h2" if "h2" in b else "h3")
            hp = doc.add_paragraph(style={"h1": "Heading 1", "h2": "Heading 2", "h3": "Heading 3"}[key])
            hp.add_run(b[key])
            if b.get("pages"):
                pr = hp.add_run("   " + b["pages"])
                pr.bold = False
                pr.font.size = Pt(9)
                pr.font.color.rgb = GREY
        elif "p" in b:
            _runs(doc.add_paragraph(), b["p"])
        elif "bullets" in b:
            prev_para = None
            for it in b["bullets"]:
                if isinstance(it, list):
                    for sub in it:
                        sp = doc.add_paragraph(style="List Bullet 2")
                        _runs(sp, sub)
                else:
                    prev_para = doc.add_paragraph(style="List Bullet")
                    _runs(prev_para, it)
        elif "table" in b:
            _table(doc, b["table"])
        elif "figure" in b:
            _figure(doc, b["figure"])
        elif "note" in b:
            t = doc.add_table(rows=1, cols=1)
            t.alignment = WD_TABLE_ALIGNMENT.CENTER
            t.style = "Table Grid"
            c = t.rows[0].cells[0]
            c.width = Cm(USABLE_CM)
            _shade(c, "FFF6D6")
            c.paragraphs[0].paragraph_format.space_after = Pt(0)
            _runs(c.paragraphs[0], b["note"], size=9.5)
            _row_flag(t.rows[0], "w:cantSplit")
            _cell_margins(t, 60, 60, 100, 100)
            doc.add_paragraph().paragraph_format.space_after = Pt(2)
        elif b.get("pagebreak"):
            doc.add_page_break()

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    doc.save(out_path)


def _table(doc, tb):
    header = tb.get("header", [])
    rows = tb.get("rows", [])
    ncols = len(header) if header else len(rows[0])
    weights = tb.get("widths") or [1] * ncols
    total = float(sum(weights))
    widths = [Cm(USABLE_CM * w / total) for w in weights]
    t = doc.add_table(rows=(1 if header else 0) + len(rows), cols=ncols)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.style = "Table Grid"
    t.autofit = False
    _cell_margins(t)

    def fill(cell, text, size=9, white=False, bold_all=False):
        cell.text = ""
        lines = str(text).split("\n")
        para = cell.paragraphs[0]
        for i, line in enumerate(lines):
            if i > 0:
                para = cell.add_paragraph()
            para.paragraph_format.space_after = Pt(0.5)
            if line.startswith("- "):
                para.paragraph_format.left_indent = Cm(0.35)
                para.paragraph_format.first_line_indent = Cm(-0.3)
                line = "• " + line[2:]
            _runs(para, line, size=size, color=WHITE if white else None, bold_all=bold_all)

    r0 = 0
    if header:
        for j, h in enumerate(header):
            c = t.rows[0].cells[j]
            fill(c, h, size=9.5, white=True, bold_all=True)
            _shade(c, "B31B1B")
        _row_flag(t.rows[0], "w:tblHeader")
        _row_flag(t.rows[0], "w:cantSplit")
        r0 = 1
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            c = t.rows[r0 + i].cells[j]
            fill(c, val)
            if j == 0:
                _shade(c, "F6E3E3")
            elif i % 2 == 1:
                _shade(c, "FAF5F5")
        _row_flag(t.rows[r0 + i], "w:cantSplit")
    for row in t.rows:
        for j, c in enumerate(row.cells):
            c.width = widths[j]
    sp = doc.add_paragraph()
    sp.paragraph_format.space_after = Pt(3)


def _figure(doc, fg):
    from PIL import Image

    path = fg["path"]
    if not os.path.exists(path):
        raise SystemExit("figure not found: " + path)
    with Image.open(path) as im:
        w_px, h_px = im.size
    width = min(float(fg.get("width_cm", 12)), USABLE_CM)
    height = width * h_px / w_px
    if height > MAX_FIG_HEIGHT_CM:
        width *= MAX_FIG_HEIGHT_CM / height
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(1)
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(path, width=Cm(width))
    if fg.get("caption"):
        c = doc.add_paragraph()
        c.alignment = WD_ALIGN_PARAGRAPH.CENTER
        c.paragraph_format.space_after = Pt(6)
        _runs(c, fg["caption"], size=8.5, color=GREY, italic=True)


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        raise SystemExit(2)
    with open(sys.argv[1], encoding="utf-8") as f:
        spec = json.load(f)
    build(spec, sys.argv[2])
    words = _count_words(spec.get("blocks", []))
    pages = spec.get("source_pages")
    msg = f"OK: wrote {sys.argv[2]} | {words} words"
    if pages:
        per = words / float(pages)
        cap = float(spec.get("max_words_per_page", DEFAULT_MAX_WORDS_PER_PAGE))
        msg += f" for {pages} source pages = {per:.0f} words/page (limit {cap:.0f})"
        print(msg)
        if per > cap:
            print(f"TOO LONG: tighten to <= {int(cap * pages)} words (cut filler, merge bullets, drop exercises) and rebuild.")
            raise SystemExit(3)
    else:
        print(msg + " | WARNING: set source_pages so the length guard can run")


if __name__ == "__main__":
    main()
