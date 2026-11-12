# digi4school-summarizer

A Claude skill that summarizes **your own** [digi4school](https://digi4school.at) e-textbooks.
You tell it a book and either an **exam scope by page numbers** (`pp. 40–55`) or **by topic**
(`Joint Ventures`), and it finds that part in the book, pulls the content the fastest way
available, and hands you a summary — so you never have to photograph pages and paste them
into an AI by hand.

> **You log in yourself. The skill never sees or types your password.**

---

## ⚠️ Please read first (scope & responsibility)

- This tool is for making **personal study summaries of textbooks you already own** in your
  own digi4school account. It is **not** for copying, redistributing, or reproducing books.
- On some publishers' readers the text has no selectable layer, so the skill uses OCR /
  on-screen reading of pages you are already entitled to view. Depending on where you live
  and the publisher's terms, automated extraction may be restricted — **you are responsible
  for using this within your local copyright law and digi4school's terms of use.**
- Provided as-is under the MIT license, with no warranty. If in doubt, check with your
  school or the publisher.

---

## What it does

1. **Locate** — you give a topic or page range. If you give a topic, it finds the pages
   using the book's own search (works even on image-only books).
2. **Extract the fastest way** (see the speed ladder below) — a ready-made chapter
   presentation if one exists, otherwise the reader's text layer, otherwise OCR, otherwise
   on-screen reading.
3. **Summarize** — in the **book's own language**, using **only** what's in the book, and
   deliver it as a **Word document** (figures and comparison tables included where useful).

## Requirements

- **Claude** with skills support and a browser tool — either:
  - the **built-in browser pane** (no install; recommended for non-technical users), **or**
  - the **Claude-in-Chrome** extension (uses your own Chrome).
- **Python 3** with `python-docx` and `Pillow` (only needed for the Word-document output):
  `pip3 install python-docx Pillow`
- A **digi4school account** with the book(s) you want to summarize.

> **No Chrome extension required.** The built-in browser pane works out of the box — you just
> log into digi4school once in that pane.

## Install

**Option A — drop-in skill (simplest):** copy the skill folder into your Claude skills directory:

```bash
cp -R skills/digi4school-summarizer ~/.claude/skills/
```

Then restart Claude. That's it. (The skill is a **single self-contained `SKILL.md`** —
no other files or dependencies to wire up.)

**Option B — as a Claude plugin:** this repo includes a `.claude-plugin/plugin.json` manifest,
so it can be added through your Claude plugin/marketplace flow if you use one.

## How to use

In Claude, either type the command or just ask in plain language:

```
/digi4school-summarizer
```

or

```
Summarize the "Joint Ventures" topic from my Praxisblicke IV book as a Word doc.
Summarize Praxisblicke IV pages 40–55 in German, with the figures.
```

The skill will open the book in the browser (log in if asked), find the part you named,
pick the fastest extraction route, and give you a `.docx`.

## How it works — the speed ladder

It always takes the **highest available** route and never does slower work than it has to:

| Route | When it applies | Speed |
|------|-----------------|-------|
| **1. Ready-made deck** (chapter presentation `.ppsx`, or a file you send) | a presentation covers the chapter | ~1–2 min |
| **2. Real text layer** | reader has selectable text (e.g. Hölzel) | near-instant |
| **3. OCR** | outlined-SVG pages + reader allows it (e.g. TRAUNER) | ~8 s/page, automated |
| **4. On-screen reading** | OCR blocked by the reader (e.g. digi4school native) | slowest, but still hands-free |

Validated on three publishers (Hölzel, TRAUNER, digi4school native). Others are auto-detected
and handled by the same logic, and may need a one-time confirmation on first use.

## Limitations & honesty

- It's a **Claude skill**, so you need Claude with skills + a browser — it is not (yet) a
  one-click app for a completely non-technical user. A standalone app would be a separate,
  larger project (see Roadmap).
- Figures/diagrams that are images come through only where the skill captures them; summaries
  of **image-only** books rely on OCR/reading and inherit those limits (e.g. column order in
  dense tables).
- It summarizes **only** what's in the book — no outside facts added.

## Roadmap

- Wider publisher coverage as new readers are encountered.
- A cross-reader OCR path for readers that block in-page OCR.
- (Bigger) a standalone, zero-setup app so non-technical users can use it without Claude skills.

## License

[MIT](LICENSE).
