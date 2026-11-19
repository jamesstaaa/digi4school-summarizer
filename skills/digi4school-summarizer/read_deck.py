#!/usr/bin/env python3
"""read_deck.py - print the text of a PowerPoint (.ppsx/.pptx) without any extra package.

Usage:  python3 -I read_deck.py deck.ppsx > deck.txt

A .ppsx/.pptx is a zip of XML files, so Python's standard library is enough (no python-pptx).
Output: one block per slide, in presentation order:  --- Folie N (K Bilder) ---  then the text lines.
Lines that repeat on at least half of the slides (navigation breadcrumbs of the publisher's template) are
dropped. Speaker notes are added as "[Notizen] ...". Slides with "(1 Bilder)" and almost no text carry their
content in an image: take that content from the book pages instead.
"""
import html
import re
import sys
import zipfile
from collections import Counter


def main(path):
    z = zipfile.ZipFile(path)
    pres = z.read("ppt/presentation.xml").decode("utf8")
    rels = z.read("ppt/_rels/presentation.xml.rels").decode("utf8")
    rid2t = {}
    for m in re.finditer(r"<Relationship\b[^>]*>", rels):
        tag = m.group(0)
        i, t = re.search(r'Id="([^"]+)"', tag), re.search(r'Target="([^"]+)"', tag)
        if i and t:
            rid2t[i.group(1)] = t.group(1)
    order = [rid2t[r] for r in re.findall(r'<p:sldId [^>]*r:id="([^"]+)"', pres) if r in rid2t]
    slides = []
    for t in order:
        x = z.read("ppt/" + t).decode("utf8")
        paras = []
        for p in re.findall(r"<a:p>.*?</a:p>|<a:p [^>]*>.*?</a:p>", x, re.S):
            s = "".join(html.unescape(m) for m in re.findall(r"<a:t>(.*?)</a:t>", p, re.S)).strip()
            if s:
                paras.append(s)
        notes = ""
        rp = "ppt/slides/_rels/" + t.split("/")[-1] + ".rels"
        if rp in z.namelist():
            m = re.search(r'Target="\.\./notesSlides/([^"]+)"', z.read(rp).decode("utf8"))
            if m:
                nx = z.read("ppt/notesSlides/" + m.group(1)).decode("utf8")
                notes = " ".join(html.unescape(a) for a in re.findall(r"<a:t>(.*?)</a:t>", nx, re.S)).strip()
        slides.append((paras, len(re.findall(r"<p:pic>", x)), "" if re.fullmatch(r"\d*", notes) else notes))
    freq = Counter(line for paras, _, _ in slides for line in set(paras))
    boiler = {line for line, n in freq.items() if n >= max(3, len(slides) / 2)}
    for i, (paras, pics, notes) in enumerate(slides, 1):
        print(f"--- Folie {i} ({pics} Bilder) ---")
        print("\n".join(p for p in paras if p not in boiler))
        if notes:
            print("[Notizen] " + notes)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        raise SystemExit(2)
    main(sys.argv[1])
