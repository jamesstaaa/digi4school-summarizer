# digi4school-summarizer

A **Claude Code** skill that summarizes **your own** [digi4school](https://digi4school.at) e-textbooks.
You tell it a book and either an **exam scope by page numbers** (`pp. 40–55`) or **by topic**
(`Joint Ventures`), and it finds that part in the book, pulls the content the fastest way
available, and hands you a summary — so you never have to photograph pages and paste them
into an AI by hand.

> **You log in yourself. The skill never sees or types your password.**

> **Status — early version.** It has been run end to end on **one book** (Praxisblicke Betriebswirtschaft IV,
> TRAUNER, pages 30–65). Other books and readers may work or may not; see [What has been tested](#what-has-been-tested).
> **It only works inside Claude Code, not in the normal Claude app.**

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
- **Account risk:** the skill drives your own logged-in browser session and requests page files one at a
  time, spaced about 1–2 seconds apart to keep the load on the publisher's servers low. Automated
  access may still go against digi4school's or the publisher's terms of use, and the platform could
  limit or suspend your account. Spacing the requests reduces load; it does not make this allowed or
  risk-free. Use it on your own books and your own account, only for the pages you need.
- Provided as-is under the MIT license, with no warranty. If in doubt, check with your
  school or the publisher.

---

## What it does

1. **Locate** — you give a topic or page range. If you give a topic, it finds the pages
   using the book's own search (tested on TRAUNER books).
2. **Ask first** — a few short multiple-choice questions in your language (use the chapter presentation, if the
   book has one, or book pages only? include the book's figures, models and tables?), then an estimated time
   for the finished file.
3. **Extract the fastest way** (see the speed ladder below) — the chapter presentation if you chose it,
   otherwise the reader's text layer, otherwise OCR, otherwise on-screen reading.
4. **Summarize** — a short, telegraphic **study summary** (bullets under the book's own headings, key
   terms in bold, about 80–110 words per book page), in the **book's own language**, using **only** what's in
   the book. Figures, models and tables are embedded as the book's own images, never retyped. Delivered as a
   clean **Word document**, and afterwards it asks whether you want a shorter version.

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

### ✅ Recommended — one line in a Terminal (install **and** update)

Open a **Terminal** (the macOS/Linux terminal app — **not** the Claude app) and paste this
single line, then press Enter:

```bash
rm -rf /tmp/d4s && mkdir -p /tmp/d4s && curl -fsSL https://github.com/jamesstaaa/digi4school-summarizer/archive/refs/heads/main.tar.gz -o /tmp/d4s/skill.tgz && tar -xzf /tmp/d4s/skill.tgz -C /tmp/d4s && test -d /tmp/d4s/digi4school-summarizer-main/skills/digi4school-summarizer && mkdir -p "$HOME/.claude/skills" && rm -rf "$HOME/.claude/skills/digi4school-summarizer" && cp -R /tmp/d4s/digi4school-summarizer-main/skills/digi4school-summarizer "$HOME/.claude/skills/" && rm -rf /tmp/d4s && { python3 -m pip install --user --quiet python-docx Pillow 2>/dev/null || true; } && test -f "$HOME/.claude/skills/digi4school-summarizer/build_summary_docx.py" && echo "✅ Installed / updated — start a NEW Claude Code session (Code tab), then just ask for a summary." || echo "❌ Install failed (your existing install, if any, was kept) — check your internet connection and run the line again."
```

It downloads the latest skill from GitHub, copies it into `~/.claude/skills/` (the skill
folder: `SKILL.md` + the Word builder), installs the Python packages for the Word output,
checks that everything arrived, and cleans up. It prints **✅** when it worked and **❌** if
not. Then **start a new Claude Code session** and use it in the **Code** area (the Code tab of
the desktop app, or the `claude` CLI) — not the regular chat.

**Updating:** paste the **same line again** — it replaces your old copy with the latest one.
Skills load when a session starts, so open a **new** Code session afterwards. (Plugin route:
`claude plugin update`.)

### Alternative — as a Claude Code plugin (`claude` CLI / terminal only)

> ⚠️ This has to be done in a **terminal** with the `claude` CLI. The Claude **desktop app's
> Plugins menu cannot add a GitHub marketplace** — it only browses ones already installed, so
> `/plugin marketplace add …` typed in the app just opens that browser and finds nothing.

```
claude plugin marketplace add jamesstaaa/digi4school-summarizer
claude plugin install digi4school-summarizer@digi4school-tools
```

(Inside an interactive `claude` session the same commands are `/plugin marketplace add …`
then `/plugin install …`, one line at a time.)

### Alternative — manual

The skill is one folder (`SKILL.md` + the small `build_summary_docx.py` Word builder). From a downloaded copy of the repo:
```bash
cp -R skills/digi4school-summarizer ~/.claude/skills/
```
then `pip3 install python-docx Pillow`, and restart Claude. (`install.sh` / `install.ps1` in
the repo do the same.)

---

### Maintainer notes (publishing)

This repo is **both** the plugin and its marketplace (`.claude-plugin/plugin.json` +
`.claude-plugin/marketplace.json`). To publish: set `owner.name`/`author.name` to your name,
push to GitHub, and share the one-line Terminal installer above (or the `claude plugin`
commands). Bump `version` in `plugin.json` on
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

## How it works

For the pages you ask for, it takes the **highest route that works** and never does slower work than it has to:

1. a chapter presentation (`.ppsx`) if the book has one for that chapter,
2. otherwise the reader's real text layer,
3. otherwise OCR of the rendered pages (when the reader allows it),
4. otherwise reading the pages on screen.

## What has been tested

| Route | For | Status |
|------|-----|--------|
| 1. Chapter presentation | books with a `.ppsx` deck | **Never run.** It also needs `python-pptx`, which the installer does not install. |
| 2. Text layer | Hölzel books | **Partly tested:** text extraction worked; no full summary was made. |
| 3. OCR | TRAUNER books | **Tested end to end** on Praxisblicke Betriebswirtschaft IV, pages 30–65. |
| 4. Reading on screen | digi4school-native books (e.g. Best Shots) | **Not tested.** Only found that OCR is blocked there. |

Routes 1, 2 and 4 are **experimental**: use them expecting that they may need fixing.

**Measured speed (one run each, one book, one computer):** pages 51–65 (15 pages, with the book's
figures) went from the first command to a saved Word file in **4.3 minutes**. An earlier version of
the same job took 11.6 minutes. Expect variation; the other routes have no measured time yet.

**Figures:** the book's tables and models are found by TRAUNER's colours and embedded as the book's own
images. That worked for 10 of 11 figures on pages 51–65 (a beige sample form was missed). Other
publishers' books use other colours, so the finder may find nothing there.

## Limitations & honesty

- **It runs only in Claude Code** (the `claude` CLI, claude.ai/code, or the desktop app's
  Code area), **not the regular Claude app/chat**. So your users must already be Claude Code
  users — a developer-oriented environment, not something a typical student or non-technical
  person uses. Reaching regular-Claude-app users, or anyone with no AI tool, would need a
  separate **standalone app** (a much larger project — a skill cannot be one).
- Figures/diagrams that are images come through only where the skill captures them; summaries
  of **image-only** books rely on OCR/reading and inherit those limits (e.g. column order in
  dense tables).
- It summarizes **only** what's in the book — no outside facts added. A fact check on one 15-page
  summary found the first version had left out about 20 small facts (reasons, examples, list items);
  the skill now has rules, a warning, and an automatic coverage check (it lists numbers and names from the page text
  that the summary lacks; on that example it flagged 8 of 10 known lost facts, with many harmless extras), but **always skim the result against your book**.
- Numbers come from OCR; a second text pass flags differences, but it can miss a number that both
  passes read wrong. Numbers inside embedded images are always the book's own.
- The Word builder checks the layout by structure (pictures and tables inside the margins, nothing floating, captions kept with their pictures) and prints `LAYOUT OK`. 

## Roadmap

- Wider publisher coverage as new readers are encountered.
- A cross-reader OCR path for readers that block in-page OCR.
- (Bigger) a standalone, zero-setup app so non-technical users — and regular Claude-app users —
  can use it **without Claude Code**.

## License

[MIT](LICENSE).
