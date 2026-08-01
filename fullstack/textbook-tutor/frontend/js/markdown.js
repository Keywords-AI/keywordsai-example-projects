/** Rendering the tutor's answers: escaping, a small markdown subset, KaTeX. */

export const escapeHtml = (s) =>
  s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

/** Always two decimals. `String(+x.toFixed(2))` renders 0 and 1 bare, which
 *  reads as a flag rather than a score on a 0-1 scale. */
export function fmtScore(v) {
  return v === null || v === undefined ? "—" : (+v).toFixed(2);
}

/** Typeset one LaTeX span; on any failure (incl. KaTeX not loaded) fall back
 *  to the raw source rather than losing the maths entirely. */
function renderTex(tex, display) {
  try {
    return katex.renderToString(tex, { displayMode: display, throwOnError: false });
  } catch (e) {
    return escapeHtml((display ? "$$" : "$") + tex + (display ? "$$" : "$"));
  }
}

const inline = (s) =>
  escapeHtml(s)
    // Bold first, so the single-asterisk italic pass below can't chew into it.
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/\*([^*\n]+)\*/g, "<em>$1</em>")
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\[([^\]]*?p\.\s*[^\]]+)\]/gi, '<span class="cite">$1</span>');

const isTableRow = (l) => /^\s*\|.*\|\s*$/.test(l);
const isTableRule = (l) => /^\s*\|[\s:|-]+\|\s*$/.test(l);
const cells = (l) => l.trim().replace(/^\||\|$/g, "").split("|").map((c) => c.trim());

/** `| a | b |` + `|---|---|` + rows → a real table. Solve-mode answers use
 *  these constantly for summary tables, and they used to render as raw pipes. */
function renderTable(rows) {
  const head = cells(rows[0]);
  const body = rows.slice(2).map(cells);
  const th = head.map((c) => `<th>${inline(c)}</th>`).join("");
  const tr = body
    .map((r) => `<tr>${head.map((_, i) => `<td>${inline(r[i] ?? "")}</td>`).join("")}</tr>`)
    .join("");
  return `<div class="tablewrap"><table><thead><tr>${th}</tr></thead><tbody>${tr}</tbody></table></div>`;
}

export function mdToHtml(src) {
  // 1) Pull maths out first so the line-based markdown pass can't split
  //    $$…$$ across lines or escape its contents.
  const math = [];
  src = src.replace(/\$\$([\s\S]+?)\$\$/g, (_, tex) => {
    math.push({ tex: tex.trim(), display: true });
    return `\n@@M${math.length - 1}@@\n`;
  });
  src = src.replace(/\$([^$\n]+?)\$/g, (_, tex) => {
    math.push({ tex: tex.trim(), display: false });
    return `@@M${math.length - 1}@@`;
  });

  const lines = src.split(/\r?\n/);
  let html = "", list = null, quote = [];
  const close = () => { if (list) { html += "</" + list + ">"; list = null; } };
  const flushQuote = () => {
    if (quote.length) {
      html += "<blockquote>" + quote.map((q) => "<p>" + inline(q) + "</p>").join("") + "</blockquote>";
      quote = [];
    }
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trimEnd();
    if (!line.trim()) { close(); flushQuote(); continue; }

    // A table is a run of pipe rows whose second line is the |---| rule.
    if (isTableRow(line) && isTableRow(lines[i + 1] || "") && isTableRule(lines[i + 1])) {
      close(); flushQuote();
      const rows = [];
      while (i < lines.length && isTableRow(lines[i])) rows.push(lines[i++]);
      i--;
      html += renderTable(rows);
      continue;
    }

    let m;
    if ((m = line.match(/^>\s?(.*)/))) { close(); quote.push(m[1]); continue; }
    flushQuote();

    if (/^(-{3,}|\*{3,}|_{3,})$/.test(line.trim())) { close(); html += "<hr>"; }
    else if ((m = line.match(/^###\s+(.*)/))) { close(); html += "<h4>" + inline(m[1]) + "</h4>"; }
    else if ((m = line.match(/^##\s+(.*)/))) { close(); html += "<h3>" + inline(m[1]) + "</h3>"; }
    else if ((m = line.match(/^#\s+(.*)/))) { close(); html += "<h2>" + inline(m[1]) + "</h2>"; }
    else if ((m = line.match(/^\d+\.\s+(.*)/))) {
      if (list !== "ol") { close(); html += "<ol>"; list = "ol"; }
      html += "<li>" + inline(m[1]) + "</li>";
    } else if ((m = line.match(/^[-*]\s+(.*)/))) {
      if (list !== "ul") { close(); html += "<ul>"; list = "ul"; }
      html += "<li>" + inline(m[1]) + "</li>";
    } else { close(); html += "<p>" + inline(line) + "</p>"; }
  }
  close();
  flushQuote();

  // 2) Restore maths as typeset KaTeX.
  return html.replace(/@@M(\d+)@@/g, (_, i) => renderTex(math[+i].tex, math[+i].display));
}
