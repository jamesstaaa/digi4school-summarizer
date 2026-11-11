/*
 * trauner-ocr.js — in-browser OCR text extractor for the TRAUNER digibox viewer
 * (and other digi4school viewers whose pages are outlined SVGs with no text layer).
 *
 * WHY: On these books the page text is drawn as vector glyph OUTLINES — there is no
 * selectable/Unicode text to scrape. Instead of reading each page by eye, this renders
 * each page's SVG (text only, photos stripped) to a high-res canvas inside the
 * authenticated browser tab and OCRs it with tesseract.js (German by default).
 *
 * USAGE (run inside the book's tab via the Claude-in-Chrome javascript_tool):
 *   1) Inject this whole file once (paste as the `text` of a javascript_exec call).
 *   2) await D4S.init();                      // auto-detects ebook id from the URL; loads tesseract.js
 *   3) Calibrate the page offset ONCE: navigate ?page=N, read #txtPage; offset = N - displayedPage.
 *      (TRAUNER HAK IV "Praxisblicke" = offset 2. Confirm per book.)
 *   4) OCR in CHUNKS of ~4 pages so each call stays under the ~45s tool timeout:
 *        await D4S.ocr(40, 43, {offset:2});   // displayed pages 40..43
 *        await D4S.ocr(44, 47, {offset:2});   // ...continue
 *      The worker is cached on window across calls (no re-download after page 1).
 *   5) Collect everything:  D4S.dump()         // {page:text} for every page OCR'd so far
 *
 * NOTES / LIMITS:
 *  - ~8s per page after the first (first page ~11s incl. model download).
 *  - Reading order on multi-column pages / tables can interleave (margin notes, table
 *    columns). Good enough to summarise from; for clean raw text, treat as a draft.
 *  - Photos/figures are stripped (we only want text). To EMBED figures in a document,
 *    still capture them separately with the viewer's `zoom` (see SKILL.md 3B step 4).
 *  - Lang: pass {lang:'eng'} etc. for non-German books.
 */
(function () {
  const S = (window.D4S = window.D4S || {});
  S.pages = S.pages || {};              // displayedPage -> text
  S._worker = S._worker || null;
  S._base = S._base || null;            // e.g. https://a.trauner-digibox.com/ebook/6368
  S._lang = S._lang || 'deu';

  function detectBase() {
    // Prefer stripping the filename off the <object data=".../ebook/<id>[/<part>]/<n>.svg">
    // so it works for both TRAUNER (.../ebook/6368/44.svg) and the digi4school native
    // viewer (.../ebook/5351/1/89.svg, with a module segment).
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

  S.init = async function (opts = {}) {
    S._base = opts.base || detectBase();
    S._lang = opts.lang || S._lang;
    if (!S._base) throw new Error('Could not detect ebook base URL — pass {base:".../ebook/<id>"}');
    await S.ensureTesseract();
    if (!S._worker) S._worker = await Tesseract.createWorker(S._lang);
    return { base: S._base, lang: S._lang };
  };

  S.renderCanvas = async function (svgN, scale = 2.5) {
    let svg = await (await fetch(`${S._base}/${svgN}.svg`, { credentials: 'include' })).text();
    svg = svg.replace(/<image\b[\s\S]*?\/>/g, '').replace(/<image\b[\s\S]*?<\/image>/g, ''); // drop photos
    const url = URL.createObjectURL(new Blob([svg], { type: 'image/svg+xml' }));
    const img = new Image();
    await new Promise((r) => { img.onload = r; img.onerror = r; img.src = url; });
    const c = document.createElement('canvas');
    c.width = (img.naturalWidth || 900) * scale; c.height = (img.naturalHeight || 1280) * scale;
    const ctx = c.getContext('2d');
    ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, c.width, c.height);
    ctx.scale(scale, scale); ctx.drawImage(img, 0, 0);
    URL.revokeObjectURL(url);
    return c;
  };

  // OCR displayed pages [startDisplayed..endDisplayed]; svgN = displayed + offset.
  S.ocr = async function (startDisplayed, endDisplayed, opts = {}) {
    const offset = opts.offset != null ? opts.offset : 2;
    const scale = opts.scale || 2.5;
    if (!S._worker) await S.init(opts);
    const out = {};
    for (let d = startDisplayed; d <= endDisplayed; d++) {
      const canvas = await S.renderCanvas(d + offset, scale);
      const { data } = await S._worker.recognize(canvas);
      const text = (data.text || '').replace(/[ \t]+\n/g, '\n').trim();
      S.pages[d] = text; out[d] = text.length;
    }
    return { ocrd: out, note: 'char counts; use D4S.dump() for full text' };
  };

  S.dump = function () { return S.pages; };
  S.text = function () {
    return Object.keys(S.pages).map(Number).sort((a, b) => a - b)
      .map((p) => `\n===== Seite ${p} =====\n${S.pages[p]}`).join('\n');
  };
})();
"D4S ready: await D4S.init(); then D4S.ocr(start,end,{offset:2}) in ~4-page chunks; D4S.text() to collect.";
