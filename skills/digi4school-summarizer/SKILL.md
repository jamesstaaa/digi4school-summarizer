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
2. **Then, before you start, ask ONE question and WAIT.** In the **user's own language** (the language
   they wrote in; system language if unclear — never ask a German speaker in English). Say what you are
   about to do + the scope + a rough **time estimate** (with / without figures), and ask: **should the
   figures, models and tables from the pages be included? (yes/no)**. Skip it if they already said so.
   Example (German): *"Bereit, die Seiten 51–65 zusammenzufassen (~6 Min. mit Abbildungen, ~3 Min. ohne).
   Sollen Abbildungen, Modelle und Tabellen aus den Seiten eingefügt werden? (ja/nein)"* — English:
   *"Ready to summarise pages 51–65 (~6 min with figures, ~3 without). Include the figures, models and
   tables from the pages? (yes/no)"*. The user does NOT care *how* — never explain routes, OCR or pacing.
   (The summary itself stays in the **book's** language — see Hard rules.)
3. **Then do it.** The output is always a **Word (.docx) file** (no PDF step, no Word export/layout check
   — the builder's layout is already tested). Never dump the summary into the chat. Save the file in the
   working folder and send it with SendUserFile.

## Summary style (MANDATORY — this is what "summary" means here)
The output is a **study summary (Lernzettel style)** — NOT a paraphrase, retelling or
transcript of the book. A document that follows the book sentence by sentence is WRONG.
1. **Telegraphic, not prose.** Bullets and fragments. No full sentences unless unavoidable.
   No intro/outro, no "this chapter covers…", no commentary about the book.
2. **Keep all the information, drop the words.** Every definition, rule, term, formula,
   number, list of types/steps, cause → effect, pro/con and named example stays. Cut
   repetition, filler, lead-in text, decoration and the **exercises** (Aufgaben /
   Aufgabenstellungen / Übungen) — skip the exercise QUESTIONS unless the user asks for them. Fact
   text inside an exercise box (case/info text, e.g. a company or market description) is book content:
   keep its facts as ONE labelled bullet ("Fallmaterial S. N: …").
   **Keep the "why" with every fact.** A measure keeps its purpose, an example keeps its point, a list
   keeps ALL its items and the names/countries it gives. Short must not become cryptic: "Ford Probe
   (Name)" that no longer says why it was a flop is a LOST fact; "Metro: Modelle je Land" without the
   four model names is a lost fact.
3. **Key term first, in bold:** `**Begriff:** Definition in ≤ 15 words`. One idea per bullet,
   max 2 lines.
4. **Shorthand:** → (führt zu), = (ist), ↑ ↓, ≥, z. B.; enumerations on one line ("A, B, C").
5. **Structure = the book's own headings** (same numbering, with the page reference).
6. **Tables, models and comparisons come from the BOOK as images — never retype them.** If the
   book shows a table, comparison, Vorteile/Nachteile box, model, scheme, chart or process flow,
   embed the book's own image of it (see "Figures & models") and do NOT also retype its content
   as bullets or a Word table. Only when the book presents a comparison as running text (no
   table/graphic) may you build a small table yourself, using only the book's wording.
7. **Examples in one short line** ("Bsp.: …").
8. **One tight pass — write it short the FIRST time:** about **65–80 words per BOOK page** (≈ 1,000–1,100
   words for 15 pages; measured: a first pass at 46 words/page lost about 20 small facts, restoring them
   gave 72 words/page). Do NOT write a long draft and shorten it afterwards (that is a second full write,
   1–2 min wasted). While writing: never restate what an embedded image already shows; examples in one
   line; merge lead-in bullets; no asides (head counts, anecdote details) unless exam-relevant. The
   builder hard-fails above 110 words/page (exit code 3) — then cut filler, **never facts** — and prints a
   CHECK line below 45 words/page: then re-read for lost facts (fine only on exercise-heavy pages).
9. **Completeness pass BEFORE building (do not skip):** go through the page text page by page. For each
   page tick off every heading, bold term, definition, number, named example (with its point), list item
   and measure (with its purpose) in your summary and add what is missing. Only exercise questions,
   decoration and what an embedded image shows may be absent.

Example — WRONG (book-style prose): *"Neue Märkte: Ehemalige Sowjetrepubliken, Indien, China und
viele Länder Asiens, Lateinamerikas und Afrikas haben sich dem Weltmarkt geöffnet."* /
*"Die Globalisierung wirkt auf Ökonomie, Ökologie und Gesellschaft."*
RIGHT (summary style): `**Neue Märkte:** Ex-UdSSR, Indien, China, Asien/Lateinamerika/Afrika → Öffnung
zum Weltmarkt` / `**Auswirkungen:** Ökonomie, Ökologie, Gesellschaft`.

## Figures & models (when the user said yes)
**The user's rule: information ONLY from the book, and anything the book shows as a table, model, scheme,
diagram or chart goes into the document as the BOOK'S OWN IMAGE — never retyped, redrawn or rebuilt.**
Covers: tables (incl. Vorteile/Nachteile boxes), models, process flows, schemes, charts. Skip: stock photos,
logos, icons, QR codes, portraits, and anything that belongs to an exercise (Aufgaben).

**Lean method — do NOT screenshot every page** (TRAUNER / outlined-SVG viewers; code in §3B):
1. **Find them from the page data, not by looking:** `await D4S.figures(page)` returns each table/model box
   in book units (a page is 909 × 1286): `table` (the book's red header bars), `table-noheader`, `graphic`
   (coloured chart). Run it for all pages in scope in ONE call. Exercise boxes (green) and text boxes
   (beige "Aha"/"Beispiel") are not returned — correct. Tested on pp. 51–65 of a TRAUNER book: found 10 of
   11 figures with exact boxes, no hits on exercise pages; it misses beige-on-white sample forms (optional).
2. **Crop only those boxes:** per box `await D4S.region(page, x-6, y-6, w+12, h+12, {outW:1600})`, then
   `computer zoom` with `save_to_disk:true` on `[0,0,viewportW,viewportH]` (batch 5–6 per browser_batch
   call). Look at each crop; redo a clipped one. Trim the white margins with Pillow (bbox + ~8 px).
   (Browser → local file without screenshots is NOT possible: Chrome blocks/hangs the local upload.)
3. Embed: `figure` (one) or `figures` (several small, side by side); caption = `Titel (S. N)`; place it
   right after the bullet it belongs to. Wide tables `width_cm` ≈ 15; narrow ones ≈ 9–12.
4. **Check numbers without viewing every page** (OCR misreads digits, e.g. 9,58 → 9,538): after pass 1
   (`D4S.ocrFast(a,b)`) start pass 2 in the background while you crop and write:
   `D4S.p2 = {}; D4S.ocrFast(a,b,{scale:3.5, into:D4S.p2})`. Before building run
   `D4S.numDiff(D4S.pages, D4S.p2)` — it lists numbers that differ between the passes (tested: caught
   9,538 vs 9,58 and 194.679.484 vs …434; also flags stray single digits). View **only those pages**
   (`D4S.region(p,0,0,909,1286,{outW:1400})` + zoom) and fix the summary. Heuristic, not proof: if both
   passes misread the same way it shows nothing. Numbers inside embedded images are always right.
- **Presentation route:** the deck gives TEXT only; tables/figures still come from the pages as above.
- **Other viewers** (no renderer): jump to the page, `zoom` on the figure with `save_to_disk:true`.
- If the user answers "no", skip all of this.

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

**Realistic times (50 pages, finished document, requests paced as described below):**

| Route | With figures | No figures | What it does on the site |
|-------|------------------------|------------|--------------|
| 1. Presentation (`.ppsx`) | ~6–9 min | ~2 min | downloads one file; the figure pass reads page files |
| 2. Text layer (Hölzel) | ~6–9 min | ~2–3 min | loads the pages the way the viewer does |
| 3. OCR (`ocrFast`, TRAUNER) | ~6 min (est.) | ~3 min | fetches page files directly, one at a time |
| 4. Visual reading (native/Best Shots) | ~5–8 min | ~3–5 min | uses the viewer as intended |

(Only the OCR route was timed: 15 pages of a TRAUNER book with figures took **11.6 min** with the old flow —
~4 min of that was a hanging Word export and extra checks, ~1.3 min rewriting the summary a second
time. The lean flow here should take **~6 min** — an estimate, not yet timed. Walls: the ~1 page/s request rate,
and ~2 min to write ~1,000 words. The other rows are rough estimates.)

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
- **Exact page ranges:** a deck follows the chapter, not page numbers. If the user asked for exact
  pages (e.g. "S. 30–50") that start or end mid-chapter, or the deck's content differs from the
  pages, use the **page text** (OCR / method A) for those pages instead — the user wants the
  information of THOSE pages, from the book. Use a deck only when the request is a whole chapter/topic.

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
  // Paced + parallel OCR. Page fetches start one at a time, ~minGap ms apart plus a small random
  // offset, to keep server load low; OCR itself runs in parallel in the local browser.
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
    const run = async (w) => { while (i < q.length) { const d = q[i++]; const cv = await paced(d); const { data } = await w.recognize(cv); (opts.into || S.pages)[d] = (data.text || '').replace(/[ \t]+\n/g, '\n').trim(); } };
    await Promise.all(S._pool.slice(0, K).map(run));
    return { done: q.length };
  };
  S.dump = function () { return S.pages; };
  S.text = function () {
    return Object.keys(S.pages).map(Number).sort((a, b) => a - b).map((p) => `\n===== Seite ${p} =====\n${S.pages[p]}`).join('\n');
  };
  // Show OCR text of pages a..b in a full-screen <article> overlay, so the page-text tool can return it
  // (a JS return value is cut off after ~1.5k chars; the overlay gives ~25k chars per call = ~10 pages).
  S.show = function (a, b) {
    let o = document.getElementById('d4s-out'); if (o) o.remove();
    o = document.createElement('div'); o.id = 'd4s-out';
    o.style.cssText = 'position:fixed;inset:0;z-index:2147483647;background:#fff;color:#000;overflow:auto;padding:12px;';
    const art = document.createElement('article'), pre = document.createElement('pre');
    pre.style.cssText = 'white-space:pre-wrap;font:12px monospace;margin:0';
    pre.textContent = Object.keys(S.pages).map(Number).filter((p) => p >= a && p <= b).sort((x, y) => x - y)
      .map((p) => `\n===== Seite ${p} =====\n${S.pages[p]}`).join('\n');
    art.appendChild(pre); o.appendChild(art); document.body.appendChild(o); return pre.textContent.length;
  };
  S.hide = function () { const o = document.getElementById('d4s-out'); if (o) o.remove(); };
  // Render a REGION (book units; a page = 909 x 1286) of a page at high resolution, photos INCLUDED, as a
  // full-frame overlay, for a sharp `zoom` screenshot of a table / model / chart.
  S._cache = S._cache || {};
  S.region = async function (page, x, y, w, h, opts = {}) {
    const offset = opts.offset ?? 2, outW = opts.outW ?? 1600, svgN = page + offset;
    let svg = S._cache[svgN];
    if (!svg) {
      svg = await (await fetch(`${S._base}/${svgN}.svg`, { credentials: 'include' })).text();
      const refs = [...new Set([...svg.matchAll(/(?:xlink:href|href)="([^"#][^"]*\.(?:png|jpe?g|gif))"/gi)].map((m) => m[1]))];
      for (const r of refs) {
        const b = await (await fetch(new URL(r, S._base + '/').href, { credentials: 'include' })).blob();
        const d = await new Promise((res) => { const fr = new FileReader(); fr.onload = () => res(fr.result); fr.readAsDataURL(b); });
        svg = svg.split('"' + r + '"').join('"' + d + '"');
      }
      S._cache[svgN] = svg;
    }
    const url = URL.createObjectURL(new Blob([svg], { type: 'image/svg+xml' }));
    const img = new Image(); await new Promise((r) => { img.onload = r; img.onerror = r; img.src = url; });
    const k = outW / w, c = document.createElement('canvas');
    c.width = Math.round(w * k); c.height = Math.round(h * k);
    const ctx = c.getContext('2d'); ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, c.width, c.height);
    ctx.drawImage(img, -x * k, -y * k, 909 * k, 1286 * k); URL.revokeObjectURL(url);
    let o = document.getElementById('d4s-reg'); if (o) o.remove();
    o = document.createElement('div'); o.id = 'd4s-reg';
    o.style.cssText = 'position:fixed;left:0;top:0;width:100vw;height:100vh;z-index:2147483647;background:#fff;display:flex;align-items:flex-start;justify-content:center;';
    c.style.cssText = 'max-width:100vw;max-height:100vh;width:auto;height:auto;object-fit:contain;';
    o.appendChild(c); document.body.appendChild(o);
    return { page, region: [x, y, w, h], vw: innerWidth, vh: innerHeight };
  };
  S.regionOff = function () { const o = document.getElementById('d4s-reg'); if (o) o.remove(); };
  // Find the book's tables/models/charts from the page data (no screenshot). TRAUNER style: red header bars (173,34,40).
  S.figures = async function (page, offset = 2) {
    const txt = await (await fetch(`${S._base}/${page + offset}.svg`, { credentials: 'include' })).text();
    const photos = [...txt.matchAll(/<image\b[^>]*>/g)].map((m) => { const a = m[0], g = (k) => +(a.match(new RegExp('\\b' + k + '="([^"]*)"')) || [])[1]; return { x: g('x'), y: g('y'), w: g('width'), h: g('height') }; }).filter((b) => b.w > 40 && b.h > 40);
    const clean = txt.replace(/<image\b[^>]*\/>/g, '').replace(/<image\b[\s\S]*?<\/image>/g, '');
    const host = document.createElement('div'); host.style.cssText = 'position:absolute;left:-99999px;top:0;visibility:hidden'; host.innerHTML = clean; document.body.appendChild(host);
    const els = [];
    host.querySelector('svg').querySelectorAll('path,rect').forEach((el) => {
      if (el.closest('defs')) return;
      const cs = getComputedStyle(el); let b; try { b = el.getBBox(); } catch (e) { return; }
      const m = cs.fill.match(/\d+/g);
      els.push({ x: b.x, y: b.y, w: b.width, h: b.height, c: m ? m.map(Number) : null, stroke: cs.stroke !== 'none' && cs.strokeWidth !== '0px' });
    });
    host.remove();
    const near = (c, r, g, b, t = 8) => c && Math.abs(c[0] - r) < t && Math.abs(c[1] - g) < t && Math.abs(c[2] - b) < t;
    const isWhite = (c) => !c || (c[0] > 250 && c[1] > 250 && c[2] > 250) || (c[0] < 12 && c[1] < 12 && c[2] < 12);
    const isGray = (c) => c && Math.abs(c[0] - c[1]) < 8 && Math.abs(c[1] - c[2]) < 8;
    const isRed = (e) => near(e.c, 173, 34, 40, 8) && e.w > 80 && e.h > 15 && e.h < 60;
    const isBeige = (e) => near(e.c, 242, 238, 227, 3);
    const isPink = (e) => e.c && e.c[0] >= 215 && e.c[1] >= 150 && e.c[1] <= 225 && e.c[2] >= 140 && e.c[2] <= 215 && e.c[0] - e.c[1] > 12 && !isBeige(e);
    const isBody = (e) => (isPink(e) || isBeige(e)) && e.w > 40 && e.w < 800;
    const found = [];
    const inside = (e) => found.some((f) => e.x >= f.x - 2 && e.y >= f.y - 2 && e.x + e.w <= f.x + f.w + 2 && e.y + e.h <= f.y + f.h + 2);
    const grow = (x0, y0, x1, y1) => {
      const cand = els.filter(isBody).concat(photos);
      let g = true;
      while (g) {
        g = false;
        for (const e of cand) { const ox = Math.min(x1, e.x + e.w) - Math.max(x0, e.x); if (ox > 0.5 * Math.min(e.w, x1 - x0) && e.y <= y1 + 6 && e.y + e.h > y1 + 0.5) { y1 = e.y + e.h; g = true; } }
        for (const e of els) {
          if (isWhite(e.c) || e.w > 800 || e.h > (y1 - y0) + 5 || e.w < 20) continue;
          if (Math.min(y1, e.y + e.h) - Math.max(y0, e.y) < 0.6 * e.h) continue;
          if (Math.abs(e.x - x1) <= 3 && e.x + e.w > x1) { x1 = e.x + e.w; g = true; } else if (Math.abs(e.x + e.w - x0) <= 3 && e.x < x0) { x0 = e.x; g = true; }
        }
      }
      return [x0, y0, x1, y1];
    };
    const finish = (x0, y0, x1, y1, kind) => {
      let frame = null;
      for (const e of els) if (e.stroke && !e.c && e.x <= x0 + 1 && e.y <= y0 + 1 && e.x + e.w >= x1 - 1 && e.y + e.h >= y1 - 1 && e.w < x1 - x0 + 60 && e.h < y1 - y0 + 80) { if (!frame || e.w * e.h < frame.w * frame.h) frame = e; }
      const b = frame || { x: x0, y: y0, w: x1 - x0, h: y1 - y0 };
      found.push({ x: b.x, y: b.y, w: b.w, h: b.h, kind });
    };
    const reds = els.filter(isRed).sort((a, b) => a.y - b.y || a.x - b.x), used = new Set();
    for (const r of reds) {
      if (used.has(r)) continue;
      const row = reds.filter((q) => Math.abs(q.y - r.y) < 4 && !used.has(q)); row.forEach((q) => used.add(q));
      const [x0, y0, x1, y1] = grow(Math.min(...row.map((q) => q.x)), r.y, Math.max(...row.map((q) => q.x + q.w)), Math.max(...row.map((q) => q.y + q.h)));
      finish(x0, y0, x1, y1, 'table');
    }
    const pinks = els.filter((e) => isPink(e) && e.w > 100 && e.h > 30 && !inside(e)).sort((a, b) => a.y - b.y), usedP = new Set();
    for (const p of pinks) {
      if (usedP.has(p)) continue; usedP.add(p);
      const [x0, y0, x1, y1] = grow(p.x, p.y, p.x + p.w, p.y + p.h);
      pinks.forEach((q) => { if (q.x >= x0 - 2 && q.y >= y0 - 2 && q.x + q.w <= x1 + 2 && q.y + q.h <= y1 + 2) usedP.add(q); });
      if ((x1 - x0) * (y1 - y0) > 20000) finish(x0, y0, x1, y1, 'table-noheader');
    }
    const others = els.filter((e) => !isWhite(e.c) && !isGray(e.c) && !isBeige(e) && !isPink(e) && !isRed(e) && e.w >= 80 && e.w <= 300 && e.h >= 80 && !inside(e) && !(e.c[1] > 215 && e.c[0] > 200 && e.c[2] > 170 && e.w > 250));
    if (others.length) finish(Math.min(...others.map((e) => e.x)), Math.min(...others.map((e) => e.y)), Math.max(...others.map((e) => e.x + e.w)), Math.max(...others.map((e) => e.y + e.h)), 'graphic');
    return found.map((f) => ({ kind: f.kind, box: [f.x, f.y, f.w, f.h].map(Math.round) }));
  };
  // Numbers that differ between two OCR passes (a, b = {page: text}) — those pages need a look.
  S.numDiff = function (a, b) {
    const num = (t) => (t.match(/\d[\d.,]*\d|\d/g) || []).map((s) => s.replace(/[.,]$/, ''));
    const bag = (l) => l.reduce((m, x) => ((m[x] = (m[x] || 0) + 1), m), {});
    const out = {};
    for (const p of Object.keys(a)) {
      const x = bag(num(a[p])), y = bag(num(b[p] || '')), pa = [], pb = [];
      new Set([...Object.keys(x), ...Object.keys(y)]).forEach((k) => { if ((x[k] || 0) > (y[k] || 0)) pa.push(k); if ((y[k] || 0) > (x[k] || 0)) pb.push(k); });
      if (pa.length || pb.length) out[p] = { pass1: pa, pass2: pb };
    }
    return out;
  };
})();
```
2. Confirm the offset once (navigate `?page=42`, read `#txtPage`), then OCR in
   **~8-page chunks** (13 pages ran into the ~45 s tool limit; the OCR keeps running in the page
   if a call times out — just check `Object.keys(D4S.pages)` afterwards). The worker pool is cached
   on `window` across calls: `await D4S.ocrFast(40,47,{offset:2});` … `await D4S.ocrFast(48,55,{offset:2});`
3. Read the text with `D4S.show(a,b)` (≤ ~10 pages) and then the page-text tool, one range at a
   time (`D4S.hide()` afterwards). ~1.5 min for 21 pages measured (first chunk +~11 s for the
   model load); `{lang:'eng'}` for English. Always check numbers against the page image (see
   "Figures & models").

**Request pacing (keep this — it limits load on the publisher's servers):**
- `ocrFast` fetches page files **one at a time, ~1–1.7 s apart** (`minGapMs` 1000 + a random 0–700 ms so
  requests don't pile up on the same instant), and never fetches pages in parallel. Do not remove the
  gate and do not fetch a whole book in one go.
- **OCR parallelism (`workers`) runs only in the user's own browser** — it adds no requests to the
  server. Default ≤ 4 workers to spare a weak laptop's RAM/CPU.
- **Shared use:** default spacing is ~1 s per page; for a widely shared build raise `minGapMs` to
  ~1500–2000, because the load adds up across many users.
- **Scope tight:** only fetch the pages the topic needs (step 1a search), never the whole book.
- **Be honest with the user about account risk:** automated access may go against digi4school's or the
  publisher's terms of use, and the platform could limit or suspend the account. Pacing reduces the
  load, it does **not** make this risk-free or allowed. If a user asks, say this plainly.
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

### Build the Word document — ALWAYS with the bundled builder
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
   bullet = its sub-bullets), `figure` (the BOOK's image of a table/model/chart: `path`, `caption`,
   `width_cm`, optional `max_h_cm`), `figures` (several small images side by side), `note` (a shaded
   "Aha!/Merke" box), `table` (`header`, `rows`, `widths`; `\n- ` inside a cell = bullets) — **only for
   a comparison the book gives as running text, never to retype a table the book shows**, `pagebreak`.
   Inline `**bold**` only. Put each figure block where the figure belongs in the text.
4. Run `python3 build_summary_docx.py spec.json "<name>.docx"`. **Exit code 3 = too long** →
   tighten (merge bullets, shorten, drop filler — never drop facts) and rebuild until it passes.
5. Save the file in the working folder and send it with SendUserFile. File name:
   `<Buch>_<Thema-oder-Seiten>.docx`. Done — do not render or re-check it in Word.

### 4. Deliver what the user asked for
- The result is a **Word file**; do NOT write the whole summary into chat.
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
