# digi4school-summarizer

A **Claude Code** skill that summarizes **your own** [digi4school](https://digi4school.at) e-textbooks.
You tell it a book and either an **exam scope by page numbers** (`pp. 40–55`) or **by topic**
(`Joint Ventures`), and it finds that part in the book, pulls the content the fastest way
available, and hands you a summary — so you never have to photograph pages and paste them
into an AI by hand.

> **You log in yourself. The skill never sees or types your password.**

---

## ⚠️ Runs in Claude Code ONLY — not the regular Claude app

This is a **Claude Code** skill/plugin. It works **only** in Claude Code:
- the **`claude` CLI** in a terminal,
- **[claude.ai/code](https://claude.ai/code)**, or
- the **Code** area of the Claude **desktop app**.

It does **NOT** work in the normal Claude app / chat (claude.ai) — there is no `/plugin`
command, no skill loading, and no browser/Python automation there, so the install commands
below simply won't be recognised. This tool is therefore for people **already using Claude
Code**. Reaching regular-Claude-app users (or people with no AI tool) would require a
separate **standalone app**, which a Claude Code skill cannot be — see
[Limitations & honesty](#limitations--honesty).

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

- **Claude Code** — the `claude` CLI, claude.ai/code, or the Code area of the desktop app
  (NOT the regular Claude app/chat) — with a browser tool, either:
  - the **built-in browser pane** (no install; recommended for non-technical users), **or**
  - the **Claude-in-Chrome** extension (uses your own Chrome).
- **Python 3** with `python-docx` and `Pillow` (only needed for the Word-document output):
  `pip3 install python-docx Pillow`
- A **digi4school account** with the book(s) you want to summarize.

> **No Chrome extension required.** The built-in browser pane works out of the box — you just
> log into digi4school once in that pane.

## Install

### Recommended — inside Claude, no download, no Terminal

If you already use Claude, install it as a plugin. Type these two lines in Claude's
message box (replace `<owner>` with the GitHub account hosting this repo):

```
/plugin marketplace add <owner>/digi4school-summarizer
/plugin install digi4school-summarizer@digi4school-tools
```

Pick a scope and confirm in the panel that opens. If the skill doesn't appear right away,
run `/reload-plugins`. For the Word-document output you also need Python with `python-docx`
and `Pillow` — the skill installs these itself on first use, or run `pip3 install python-docx Pillow`.

**Using it:** just ask in plain language — *"summarize the Joint Ventures topic from my
Praxisblicke book as a Word doc"* — or run `/digi4school-summarizer:digi4school-summarizer`.

### Alternative — one-command installer

Download the repo (**Code ▸ Download ZIP** then unzip, or `git clone`) and run once:

- macOS / Linux: `bash install.sh`
- Windows (PowerShell): `./install.ps1`

Then restart Claude. This copies the skill into `~/.claude/skills/` and installs the Python
deps. Invoke the installed skill with `/digi4school-summarizer`.

### Alternative — manual (single file)

The skill is a single self-contained `SKILL.md`; copy it yourself:
```bash
cp -R skills/digi4school-summarizer ~/.claude/skills/
```
then `pip3 install python-docx Pillow`, and restart Claude.

> Nothing registers a skill with *zero* action — the plugin flow gets it down to two lines
> typed inside Claude, which is as close as it gets.

---

### Maintainer notes (publishing)

This repo is **both** the plugin and its marketplace (`.claude-plugin/plugin.json` +
`.claude-plugin/marketplace.json`). To publish: set `owner.name`/`author.name` to your name,
push to GitHub, and share the two `/plugin` commands above. Bump `version` in `plugin.json` on
each release — users only get updates when the version string changes (third-party marketplaces
don't auto-update). Validate locally with `claude plugin validate .`.

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

- **It runs only in Claude Code** (the `claude` CLI, claude.ai/code, or the desktop app's
  Code area), **not the regular Claude app/chat**. So your users must already be Claude Code
  users — a developer-oriented environment, not something a typical student or non-technical
  person uses. Reaching regular-Claude-app users, or anyone with no AI tool, would need a
  separate **standalone app** (a much larger project — a skill cannot be one).
- Figures/diagrams that are images come through only where the skill captures them; summaries
  of **image-only** books rely on OCR/reading and inherit those limits (e.g. column order in
  dense tables).
- It summarizes **only** what's in the book — no outside facts added.

## Roadmap

- Wider publisher coverage as new readers are encountered.
- A cross-reader OCR path for readers that block in-page OCR.
- (Bigger) a standalone, zero-setup app so non-technical users — and regular Claude-app users —
  can use it **without Claude Code**.

## License

[MIT](LICENSE).
