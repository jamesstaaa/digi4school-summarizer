---
name: digi4school-summarizer
description: >
  Extract text from an e-book in the user's digi4school library (Austrian school
  textbook platform) using a browser (Claude's built-in pane or the Chrome
  extension), then do whatever the user asks with it (summary, flashcards, vocab, Q&A).
  The USER logs in; this skill never handles passwords. Trigger when the user
  wants to pull information out of a digi4school / "digibook" textbook, names a
  book on digi4school, or says "/digi4school-summarizer".
---

# digi4school book extractor

Drives the user's **already-logged-in browser** — either Claude's **built-in
browser pane** (no extension needed) or the **Claude-in-Chrome** extension — to open
a book from their digi4school library and extract clean page text, then transforms
that text into whatever the user wants. Use whichever browser is available; the
built-in pane is the zero-install default (tools `mcp__Claude_Browser__*`), the Chrome
extension is the alternative (tools `mcp__claude-in-chrome__*`).

## Hard rules
- **Never type the user's password or log in.** The user is signed in already.
  If a page shows a login screen, stop and ask the user to log in themselves,
  then continue.
- Only read books the user already owns in their own library. This is their
  purchased material, read for their own study — do not reproduce whole books
  verbatim to third parties; the normal use is summaries/study aids for the user.
- Use whichever browser the user is signed in on — **prefer Claude's built-in
  browser pane** (no install); the Chrome extension is the alternative. Detect what's
  available rather than assuming one.
- **Information fidelity (important to this user):** everything in the output must
  come ONLY from the extracted book pages. Never add outside/background knowledge,
  never infer, embellish or "fill gaps". If the pages don't say it, it isn't in the
  summary. Word-for-word is NOT required — faithful meaning is.
- **Language:** write the summary in the book's own language by default (e.g. German
  for Austrian HAK textbooks). Only use another language if the user asks this time.
- **Source priority (presentation-first):** when the user asks for a chapter/topic,
  FIRST check the book's Lernmaterialien → PräsentationsBox for a presentation
  (`.ppsx`) covering it. If one exists, use THAT as the source — it's the publisher's
  own topic summary and reads directly as PowerPoint (no OCR). Only fall back to
  OCR / reading the pages (3B / method A) when no presentation covers the requested
  chapter, or the user explicitly wants the full page-level detail. Tell the user
  which presentation you're using. These materials are still part of the book, so the
  fidelity rule holds (info only from the presentation/pages, nothing external).

## Prerequisites
- A browser is available. Prefer Claude's **built-in browser pane** (no install;
  `mcp__Claude_Browser__*`) — the user logs into digi4school in that pane. If the user
  prefers their own Chrome, use the **Claude-in-Chrome** extension instead
  (`list_connected_browsers` should return a browser; if not, ask them to connect it).
- With the Chrome extension, load its tools first (they are usually deferred):
  `ToolSearch select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__read_page,mcp__claude-in-chrome__get_page_text,mcp__claude-in-chrome__javascript_tool,mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__list_connected_browsers`

## Inputs to get from the user (ask only what's missing)
1. **Which book** — a title or keyword (e.g. "Unternehmensrechnung", "Mathematik V").
2. **The exam scope** — this is how students actually get it, so accept EITHER form:
   - **page numbers** ("pp. 40–55"), or
   - **topic name(s)** ("Joint Ventures", "Markteintritt", "the liquidity chapter").
   If given topics, the agent LOCATES them in the book itself (step 1a) — the user
   should not have to find page numbers. Default to what they gave; don't force a range.
3. **Output form** — summary / key points (default), flashcards, vocabulary, quiz
   questions, raw text, or a knowledge graph (hand off to the `graphify` skill).

> **Mission (why this agent exists):** save a student from photographing pages and
> pasting them into an AI by hand. Given a book + a topic or page range, do the
> whole locate→extract→summarize loop automatically, as efficiently as possible
> (presentations where they exist, OCR where they don't). Built to be open-sourced,
> so keep it self-contained and publisher-agnostic — no user-specific data baked in.

## Interaction flow (what the user sees — keep it simple)
When the user asks for a summary (a topic or a page range), do this:
1. **Pre-flight FIRST, silently.** Before extracting anything, resolve the scope (§1a)
   and check the route (§1b): how many chapters it spans, whether presentations cover
   them, which route applies. Do this quickly — **do NOT narrate the mechanics.**
2. **Then, before you start, ask the user (plain terms) and WAIT for the answer.** Ask in ONE
   message, **in the user's own language** — the language they wrote their request in (if
   unclear, their system/app language). Never ask a German speaker in English, etc. Ask:
   - what you're about to do + the scope + a rough **time estimate** from the route you found
     (give both: with figures / without figures — see the route-times table below);
   - **how should it be exported — Word (.docx), PDF, or straight into the chat?** (default Word);
   - **should the figures, diagrams, models and tables from the pages be included? (yes/no).**
   Skip any item the user already answered in their request (e.g. "as a Word doc with figures").
   Example (German): *"Bereit, die Seiten 50–100 zusammenzufassen (~5 Min. mit Abbildungen,
   ~3 Min. ohne). Als Word, PDF oder hier im Chat? Sollen Abbildungen, Grafiken und Modelle
   aus den Seiten eingefügt werden? (ja/nein)"* — Example (English): *"Ready to summarise pages
   50–100 (~5 min with figures, ~3 without). Export as Word, PDF, or here in the chat? Include the
   figures, diagrams and models from the pages? (yes/no)"*
   Keep it short: **what + how long + those two choices.** The user does NOT care *how*
   (presentations vs OCR vs pacing) — never explain the extraction method, routes, or safety.
   (The interaction language is the user's; the **summary itself** stays in the **book's**
   language unless they ask otherwise — see Hard rules.)
3. **Then do it and deliver in the chosen format.**

**Export rule (IMPORTANT — the user wants this):** by default always produce a **file**
(Word or PDF), and **NEVER write the full summary into the chat unless the user explicitly
chose "chat."** Ask the export format up front (step 2) — do NOT dump the whole summary into
the message and only then offer a file. Mapping: **Word** → build with `python-docx`; **PDF**
→ build the Word doc then convert to PDF (e.g. `export_pdf`, LibreOffice `soffice --headless
--convert-to pdf`, or render Markdown→PDF); **chat** → write it in the message as normal.
Deliver the file with SendUserFile and save it in the project folder.

## Summary style (MANDATORY — this is what "summary" means here)
The output is a **study summary (Lernzettel style)** — NOT a paraphrase, retelling or
transcript of the book. A document that follows the book sentence by sentence is WRONG.
1. **Telegraphic, not prose.** Bullets and fragments. No full sentences unless unavoidable.
   No intro/outro, no "this chapter covers…", no commentary about the book.
2. **Keep all the information, drop the words.** Every definition, rule, term, formula,
   number, list of types/steps, cause → effect, pro/con and named example stays. Cut
   repetition, filler, lead-in text, decoration and the **exercises** (Aufgaben /
   Aufgabenstellungen / Übungen) — skip exercises entirely unless the user asks for them.
3. **Key term first, in bold:** `**Begriff:** Definition in ≤ 15 words`. One idea per bullet,
   max 2 lines.
4. **Shorthand:** → (führt zu), = (ist), ↑ ↓, ≥, z. B.; enumerations on one line ("A, B, C").
5. **Structure = the book's own headings** (same numbering, with the page reference).
6. **Comparisons are tables:** Vorteile/Nachteile, Typen, Vergleiche → a table, never paragraphs.
7. **Examples in one short line** ("Bsp.: …").
8. **Length:** about **70–90 words per BOOK page** in the document; the builder hard-fails above
   110 words/page (exit code 3) — then merge and shorten, but **never drop facts to get under it.**
9. **Completeness check before building:** walk the source page by page — every heading, bold
   term, definition, list and figure must appear (shortened). Only exercises and decoration
   may be missing.

Example — WRONG (book-style prose): *"Neue Märkte: Ehemalige Sowjetrepubliken, Indien, China und
viele Länder Asiens, Lateinamerikas und Afrikas haben sich dem Weltmarkt geöffnet."* /
*"Die Globalisierung wirkt auf Ökonomie, Ökologie und Gesellschaft."*
RIGHT (summary style): `**Neue Märkte:** Ex-UdSSR, Indien, China, Asien/Lateinamerika/Afrika → Öffnung
zum Weltmarkt` / `**Auswirkungen:** Ökonomie, Ökologie, Gesellschaft`.

## Figures & models (when the user said yes)
If the user wants figures (step 2 — ask in their language), then every informational **figure,
model, diagram, chart, schema or process flow** on the pages in scope goes into the document
**as the book's own image** — never retype a diagram as text boxes or lists. Also embed any table too complex to rebuild cleanly; simple tables (≤ 4
columns, short cells) are rebuilt as real Word tables instead. Skip decorative stock photos,
logos, icons, QR codes and anything that belongs to an exercise.
- **Figure pass (all routes):** figures are not in the extracted text (and on these viewers
  vector diagrams/tables are drawn as shapes, not image files), so after the text step visit
  each page in scope in the viewer — same paced setup as the visual-reading fallback (close the
  Lernmaterialien panel, fit the page, next-page arrow, wait ~2.2 s) — and for each
  informational figure take a `zoom` of just that figure. This also double-checks the text.
- **Crop quality:** region slightly generous so no edge, title or legend is cut off; ≥ ~800 px
  wide. Look at every crop — if any edge is clipped, redo it with a larger region.
- Every image result prints a **file path** — copy the file to the working folder with a
  meaningful name (`fig_p48_marktuebersicht.png`) and add a `figure` block exactly where it
  belongs, caption = `Titel (S. N)`.
- **Presentation route:** the deck is used for the TEXT only. Its slide shapes can't be exported
  as images reliably, so figures still come from the book pages via the figure pass.
- ~2–3 s per page → about **+2–3 min per 50 pages** (the "with figures" column below). If the
  user answers "no", skip the figure pass entirely and use the "no figures" time.

## Always take the fastest route to the content (speed ladder)
Minimising the user's time is the whole point. For the requested topic/pages, use the
HIGHEST available source on this ladder and stop — never do slower work when a faster
source exists, and never process more pages than the topic needs (scope tightly via the
search in step 1a):
1. **An already-condensed, machine-readable source** — a chapter presentation
   (PräsentationsBox `.ppsx`) or a file the user hands you (e.g. a PowerPoint). Read it
   directly → ~1–2 min to a Word doc. The fastest path; prefer it whenever one covers
   the chapter.
2. **A real text layer in the reader** (e.g. Hölzel) → grab the text instantly, summarise.
3. **OCR** when pages are outlined SVG and the viewer allows tesseract.js (e.g. TRAUNER)
   → automated via `ocrFast` (paced fetch + parallel OCR), ~1–1.5 min per 50 pages (see §3B).
4. **Visual reading** when OCR is blocked by CSP (e.g. digi4school native / Best Shots)
   → slowest, hands-free but minutes; minimise by reading ONLY the located pages.
Tell the user upfront which route applies and the rough time, so expectations are set.

**Realistic safe-max times (50 pages, finished document — paced, low risk):**

| Route | With figures | No figures | Account risk |
|-------|------------------------|------------|--------------|
| 1. Presentation (`.ppsx`) | ~4–6 min | ~2 min | ~none for the deck; figure pass = normal viewing |
| 2. Text layer (Hölzel) | ~4–6 min | ~2–3 min | low (acts like a reader) |
| 3. OCR (`ocrFast`, TRAUNER) | ~5–7 min | ~3 min | low–moderate |
| 4. Visual reading (native/Best Shots) | ~4–6 min | ~3–5 min | low (uses the real reader) |

(On route 4 the text is read during the same page visit that finds the figures, so figures add
little there.) Walls that can't be beaten while staying safe: the **~1 page/s** safe fetch/visit
rate (faster → ban risk climbs), the **figure pass** (~2–3 s/page, one visit per page in scope),
and the **~1–2 min** the model needs to write the summary (a shorter, telegraphic summary
writes a bit faster). The real speed lever is **route selection** (reach for a presentation).

## Procedure

### 1. Open the library and find the book
- `navigate` to `https://digi4school.at/overview`.
- `screenshot`. The user's books are under **"Ausgewählte Bücher"**; the
  **E-Books** tab (bottom) lists all owned titles if the book isn't on the overview.
- Match the user's keyword to a title and `left_click` it. This opens the book in
  a **new tab** on the publisher's viewer (e.g. `hoelzel.at/squares/...`,
  `trauner-digibook...`, `scook`, or the classic `a.digi4school.at` SVG reader).
- Grab the new tab's id from the tab context and `screenshot` it to confirm the
  book opened.

### 1a. Resolve the scope → pages (when the user gave topic names, not page numbers)
Students are usually told the exam scope as topics or chapter names, not page numbers.
Turn a topic into a location using the book's own tools (works even on textless/image
books — the viewer has a server-side text index):
- **Full-text search (primary):** the viewer has a Suche panel. Put the term in the
  search input (`#txtSearch` in the TRAUNER viewer) and run it. Results come back as
  lines **"N Ergebnis(se) auf Seite <page>"** — read them and pick the **page cluster
  with the most/most-concentrated hits** as the topic's main treatment. (E.g. "Joint
  Venture" → densest on p48–52, peak p51; scattered mentions elsewhere are ignorable.)
- **Chapter/presentation titles:** the PräsentationsBox decks are named by chapter
  (`01 Risikomanagement`, `02 Internationale Geschäftstätigkeit`, `03 Dienstleistungs-
  betriebe`, …) — a topic that matches a chapter name maps straight to that chapter's
  deck (which is also the preferred source, see 1b).
- **Thumbnail nav / TOC** (the Navigation icon) as a visual fallback.
Confirm the resolved page span with the user if it's ambiguous or spread out, then
proceed. If page numbers were given, skip this step.

### 1b. Check the Lernmaterialien for a chapter presentation (do this FIRST for a chapter/topic summary)
Before extracting pages, see whether the chapter already has a publisher presentation:
- Open the **Lernmaterialien** panel (paperclip / materials icon, top-right in the
  TRAUNER viewer). Materials are listed **per current page/chapter**, so navigate to a
  page inside the requested chapter first.
- Under **Schüler → PräsentationsBox** are the `.ppsx` presentations (the topic
  summaries), e.g. `02 Internationale Geschaeftstaetigkeit.ppsx`; **WorkBox** holds
  PDFs. Match the title to the requested chapter/topic.
- If a matching presentation exists: tell the user which one, then **download** it
  (these downloads are part of the Approbation; honour the download-permission rule —
  since the user set presentation-first as the default, naming the file and proceeding
  is enough). Put it in its own empty folder.
- Read it with `python-pptx` (or the `pptx` skill): pull slide text + speaker notes,
  then summarise from that in the book's language. This is the preferred path — skip
  the OCR/visual page extraction below unless no presentation covers the chapter.
- If the deck is too sparse for the depth asked, say so and offer to supplement from
  the pages (OCR / method A).
- **Completeness check:** a deck is a condensed view. Compare the headings of the requested
  pages (page headings from the search/TOC/viewer) with what the deck covers; for any heading
  the deck skips, take that part from the pages (OCR / method A) so no information is lost.
- The deck is used for **text only** — figures still come from the book pages (see
  "Figures & models").

### 2. Detect the viewer and confirm text is extractable (fallback: no matching presentation)
Run this in the book tab (`javascript_tool`):
```js
JSON.stringify({
  url: location.href,
  totalPages: (document.body.innerText.match(/von\s+(\d+)/)||[])[1],
  indesignPages: document.querySelectorAll('.asol_seite').length,   // Hölzel/InDesign HTML export
  svgText: document.querySelectorAll('svg text').length,            // classic digi4school SVG reader
  hasNumInput: !!document.querySelector('input.num')
}, null, 2)
```
- **`.asol_seite` present** → InDesign/HTML viewer (VALIDATED, e.g. Hölzel
  "squares"). Use method A.
- **`svg text` > 0** → classic SVG reader. Use method B (per-page SVG text).
- Neither, or `indesignPages`/`svgText` are 0 → text may be image-only; fall back
  to screenshotting pages. Tell the user it'll be slower/less exact.

### 3A. Extract (InDesign/HTML viewer — validated)
Pages are real HTML text in `div.asol_seite`, lazy-loaded a few at a time. Navigate
with the page-number box (`input.num`) and collect rendered pages, deduping by text.
**Chunk the range** (~10–15 pages per call) so no single call runs too long
(~1.4s/page). Run per chunk:
```js
const START = 42, END = 52;                 // set per chunk
const norm = s => s.replace(/­|​/g,'').replace(/[ \t]*\n[ \t]*/g,' ').replace(/\s{2,}/g,' ').trim();
const num = document.querySelector('input.num');
const seen = new Map();
const collect = () => document.querySelectorAll('.asol_seite').forEach(p=>{
  const t = norm(p.innerText);
  if (t.length>40) { const k=t.slice(0,60); if(!seen.has(k)) seen.set(k,t); }
});
const jump = async pg => {
  num.focus(); num.value=String(pg);
  num.dispatchEvent(new Event('input',{bubbles:true}));
  num.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',keyCode:13,which:13,bubbles:true}));
  await new Promise(r=>setTimeout(r,1400)); collect();
};
for (let pg=START; pg<=END; pg++) await jump(pg);
[...seen.values()].join('\n\n');   // returned to you as the chunk's text
```
Concatenate chunks in order. (The viewer keeps a sliding window of rendered pages,
sometimes with duplicate nodes — the `seen` map handles both.)

### 3B. Extract (TRAUNER digibox — outlined-SVG viewer, VALIDATED)
Host `a.trauner-digibox.com/ebook/<id>/?page=N`. Each page is an SVG at
`.../<id>/N.svg`, but there is **no text layer**: body text is drawn as vector
glyph outlines (`<use href="#f…">`), so `svg text` is 0 and the text is **not**
directly scrapable. Figures/photos are separate raster files
(`.../<id>/N/img/K.png|jpg`). There is a page offset: the SVG index N in the URL
is usually the printed page + 2 — confirm once (navigate `?page=42`, read `#txtPage`).

**Primary: OCR the text automatically (preferred — OCR module inlined below).**
Runs entirely inside the authenticated tab; no local installs, no cookies. It
fetches each page SVG, strips the photos, renders the text to a hi-res canvas, and
OCRs it with tesseract.js. Steps (via the Chrome `javascript_tool`):
1. Inject this OCR module once (paste the whole block as the `javascript_tool` text; it defines `window.D4S`):
```js
(function () {
  const S = (window.D4S = window.D4S || {});
  S.pages = S.pages || {}; S._pool = S._pool || null; S._base = S._base || null; S._lang = S._lang || 'deu';
  function detectBase() {
    const obj = document.querySelector('object[type="image/svg+xml"]');
    if (obj && obj.data && /\/\d+\.svg/.test(obj.data)) return obj.data.replace(/\/[^/]+\.svg.*$/, '');
    const m = location.href.match(/^(https?:\/\/[^?]*\/ebook\/\d+(?:\/\d+)?)\b/);
    return m ? m[1] : null;
  }
  S.ensureTesseract = async function () {
    if (typeof Tesseract !== 'undefined') return;
    await new Promise((res, rej) => {
      const s = document.createElement('script');
      s.src = 'https://cdnjs.cloudflare.com/ajax/libs/tesseract.js/5.1.1/tesseract.min.js';
      s.onload = res; s.onerror = () => rej(new Error('tesseract.js blocked (CSP?)'));
      document.head.appendChild(s);
      setTimeout(() => rej(new Error('tesseract.js load timeout')), 15000);
    });
  };
  S.renderCanvas = async function (svgN, scale = 2.5) {
    let svg = await (await fetch(`${S._base}/${svgN}.svg`, { credentials: 'include' })).text();
    svg = svg.replace(/<image\b[\s\S]*?\/>/g, '').replace(/<image\b[\s\S]*?<\/image>/g, '');
    const url = URL.createObjectURL(new Blob([svg], { type: 'image/svg+xml' }));
    const img = new Image(); await new Promise((r) => { img.onload = r; img.onerror = r; img.src = url; });
    const c = document.createElement('canvas');
    c.width = (img.naturalWidth || 900) * scale; c.height = (img.naturalHeight || 1280) * scale;
    const ctx = c.getContext('2d'); ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, c.width, c.height);
    ctx.scale(scale, scale); ctx.drawImage(img, 0, 0); URL.revokeObjectURL(url); return c;
  };
  // Paced + parallel OCR. Fetch STARTS are serialised ~minGap+jitter apart (human-like, NEVER a
  // burst); OCR runs in parallel across a worker pool (local, invisible to the server).
  S.ocrFast = async function (start, end, opts = {}) {
    const offset = opts.offset ?? 2, scale = opts.scale || 2.5;
    const minGap = opts.minGapMs ?? 1000, jitter = opts.jitterMs ?? 700;
    const K = Math.max(1, Math.min(opts.workers ?? Math.min(navigator.hardwareConcurrency || 4, 4), 8));
    S._lang = opts.lang || S._lang; S._base = opts.base || S._base || detectBase();
    if (!S._base) throw new Error('Could not detect ebook base URL — pass {base:".../ebook/<id>"}');
    await S.ensureTesseract();
    S._pool = S._pool || []; while (S._pool.length < K) S._pool.push(await Tesseract.createWorker(S._lang));
    let gate = Promise.resolve();
    const paced = (d) => { const turn = gate.then(() => new Promise(r => setTimeout(r, minGap + Math.random() * jitter))); gate = turn; return turn.then(() => S.renderCanvas(d + offset, scale)); };
    const q = []; for (let d = start; d <= end; d++) q.push(d); let i = 0;
    const run = async (w) => { while (i < q.length) { const d = q[i++]; const cv = await paced(d); const { data } = await w.recognize(cv); S.pages[d] = (data.text || '').replace(/[ \t]+\n/g, '\n').trim(); } };
    await Promise.all(S._pool.slice(0, K).map(run));
    return { done: q.length };
  };
  S.dump = function () { return S.pages; };
  S.text = function () {
    return Object.keys(S.pages).map(Number).sort((a, b) => a - b).map((p) => `\n===== Seite ${p} =====\n${S.pages[p]}`).join('\n');
  };
})();
```
2. Confirm the offset once (navigate `?page=42`, read `#txtPage`), then OCR in
   **~12-page chunks** so each call stays under the ~45s tool timeout — the worker
   pool is cached on `window` across calls:
   `await D4S.ocrFast(40,51,{offset:2});` … `await D4S.ocrFast(52,63,{offset:2});`
3. Collect with `D4S.text()` and summarise/transform from that.
   ~1–1.5 min for 50 pages (first chunk +~11s for the model load); `{lang:'eng'}` for English.

**Pacing & safety policy (do NOT remove — it's what keeps this looking human):**
- `ocrFast` **serialises fetch STARTS ~1–1.7 s apart** (minGap 1000 + jitter 700) and
  NEVER fetches pages in parallel. That paced, sequential, jittered pattern reads as a fast
  skimmer, not a scraper — the one thing that would get an account flagged is firing many
  page requests at once, so **never bypass the gate or fetch a whole book in a burst.**
- **OCR parallelism (`workers`) is LOCAL only** — invisible to the server, safe for speed.
  Default ≤4 workers to spare a weak laptop's RAM/CPU; raise only on strong hardware.
- **Personal vs public:** default `minGapMs` ~1000 (≈1 page/s, fast-skim). For a PUBLIC/shared
  build raise it to ~1500–2000 — the risk is the *aggregate* rate across many users, not one run.
- **Scope tight:** only OCR the pages the topic needs (step 1a search), never the whole book.
Caveat: reading order on multi-column pages / tables can interleave (margin notes, table
columns merge). Fine to summarise from; for clean raw text, treat as a draft and tidy. If
tesseract.js is blocked (CSP) on some host, fall back to visual reading.

**Figures for a document (always visual):** OCR drops the photos, so to EMBED a
figure, navigate to its page and use `computer` `zoom` with `save_to_disk:true` on
the figure's region — only for the few pages that have an embeddable graphic, not
every page.

**Fallback: read pages visually** (when OCR is blocked or you only need a few pages):
one-time setup — close the "Lernmaterialien" panel (its ×), zoom out ~2× (the
magnifier −) so the page fits the ~824px capture width, jump to the first page via
`#txtPage` — then step with the in-app **next-page arrow** ("Nächste Seite", NOT URL
navigation, which reloads and resets zoom/panel), wait ~2.2s, screenshot, read.

### 3B-alt. Extract (other classic SVG readers with a real text layer)
If `svg text` > 0 (some publishers), read `svg text` content in document order and
advance pages with the next-page control. Confirm the first page matches the
screenshot before looping. (Verify on first use.)

### Build the document (Word/PDF) — ALWAYS with the bundled builder
Do **not** improvise `python-docx` code — use `build_summary_docx.py`, which guarantees a clean,
consistent layout (title block, numbered headings with page refs, tight bullets, tables with a
header row that never split across pages, figures with captions, footer with source + page
number) and enforces the length limit.
1. Deps (self-heal): `python3 -c "import docx, PIL" 2>/dev/null || pip3 install python-docx Pillow`.
   If that fails (restricted environment), fall back to a Markdown file and tell the user.
2. Locate the builder (it ships in this skill's folder):
   `find ~/.claude -name build_summary_docx.py -path '*digi4school-summarizer*' 2>/dev/null | head -1`
   If nothing is found, download it:
   `curl -fsSL https://raw.githubusercontent.com/jamesstaaa/digi4school-summarizer/main/skills/digi4school-summarizer/build_summary_docx.py -o build_summary_docx.py`
3. Write the summary as a **JSON spec** (format and example in the script's docstring):
   `title`, `subtitle`, `source`, **`source_pages`** (number of BOOK pages summarised — required
   for the length guard) and `blocks`: `h1`/`h2`/`h3` (+ `pages`), `bullets` (a list right after a
   bullet = its sub-bullets), `table` (`header`, `rows`, `widths`; `\n- ` inside a cell = bullets),
   `figure` (`path`, `caption`, `width_cm`), `note` (a shaded "Merke" box), `pagebreak`.
   Inline `**bold**` only. Put each figure block where the figure belongs in the text.
4. Run `python3 build_summary_docx.py spec.json "<name>.docx"`. **Exit code 3 = too long** →
   tighten (merge bullets, shorten, drop filler — never drop facts) and rebuild until it passes.
5. **PDF** (if chosen): `soffice --headless --convert-to pdf --outdir <dir> "<name>.docx"` when
   LibreOffice exists; otherwise deliver the `.docx` and tell the user to use *File ▸ Save as PDF*.
6. Save the file in the project/working folder and send it with SendUserFile. File name:
   `<Buch>_<Thema-oder-Seiten>.docx`.

### 4. Deliver what the user asked for
- **Honour the export format chosen in step 2** (Word / PDF / chat). Default is a **Word
  file** — do NOT write the whole summary into chat unless the user explicitly picked "chat."
- Keep the page the text came from so you can cite "p. N" when useful.
- **Summary / key points**: follow **"Summary style"** above exactly — telegraphic bullets and
  tables under the book's own headings, in the book's own language, only content from the
  pages — no outside facts, no paraphrased prose. Figures/models embedded per **"Figures & models."**
- **Flashcards / vocab / quiz**: generate from the extracted text; offer to save
  as a file (CSV/Markdown) in the current project.
- **Raw text**: write to a file rather than dumping huge text into chat.
- **Knowledge graph**: invoke the `graphify` skill with the extracted text.
- Note which pages were covered and anything that looked image-only (figures,
  tables as images) and so isn't in the text.

### 5. Clean up
Close tabs this skill opened with `tabs_close_mcp` when done, unless the user
wants the book left open.

## Notes / caveats
- Validated 2026-11-11 on three viewers:
  - **Hölzel "squares"** (`hoelzel.at/squares/...`) = clean HTML text layer → method A, fast.
  - **TRAUNER digibox** (`a.trauner-digibox.com/ebook/<id>/?page=N`) = outlined SVG,
    no text layer, offset +2 → method 3B OCR works (CSP allows tesseract.js). Has
    PräsentationsBox decks + `#txtSearch`.
  - **digi4school native** (`a.digi4school.at/ebook/<id>/<part>/index.html?page=N`,
    SVG at `.../<part>/N.svg`, offset 0) = ALSO outlined SVG, no text layer, BUT its
    **CSP blocks loading tesseract.js and blocks in-tab SVG→canvas rendering** — so the
    automated OCR tool does NOT run here. Fall back to **visual reading** (screenshots;
    the pages render crisply). It still has `#txtSearch` (topic→pages) and the raw
    `N.svg` is fetchable with auth. Materials here can be audio-only (no presentations).
  Re-confirm the detection step — and do the CSP check (try injecting tesseract.js;
  if it's blocked, read visually) — the first time you hit a new publisher.
- Speed note: method A (Hölzel) is near-instant. Method 3B (TRAUNER) has no text
  layer; `ocrFast` extracts the text automatically (paced + parallel, ~1–1.5 min / 50 pp.) so
  you no longer read every page by eye — you only visually visit the few pages that
  have a figure to embed. OCR reading-order on columns/tables is imperfect, so for
  pixel-clean raw text the glyph-map decoder (render each unique glyph once → map to a
  character → reassemble by position) is the accurate-but-heavier upgrade; build it
  only if OCR's column errors actually block the use case.
- Figures, some tables, and worked examples are embedded as `.png` images and are
  NOT in the extracted text. If the user needs those, screenshot the page.
- Synthetic page jumps work on the Hölzel viewer; if a viewer ignores them, fall
  back to real clicks on the next-page arrow via the `computer` tool.
