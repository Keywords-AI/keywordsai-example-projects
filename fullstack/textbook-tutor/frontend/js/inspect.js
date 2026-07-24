/** Inspect panel: the per-answer RAG trace, and grading on demand.
 *
 * **Evaluate** does not score anything locally. It asks the server to run this
 * one answer through the five deployed graders as a one-row Respan experiment,
 * then shows the result here. So the number on screen and the number on the
 * Experiments page are the same number, and it is directly comparable to the
 * regression baseline from `scripts/run_experiment.py` — both grade the exact
 * prompt the model saw. See PROJECT_LOG §26.
 *
 * The earlier version of this panel called `/evaluators/{id}/run/`, which
 * computes a score, bills for it, and persists nothing.
 */
import { $ } from "./dom.js";
import { state, LEVERS, EVAL_ORDER } from "./state.js";
import { escapeHtml, fmtScore } from "./markdown.js";
import { evaluateAnswer } from "./api.js";

export function closeInspect() {
  state.currentInspect = null;
  $("inspect").hidden = true;
}

export function openInspect(idx) {
  const t = state.turns[idx];
  if (!t || !t.trace) return;
  state.currentInspect = idx;
  const r = t.trace.retrieve, g = t.trace.generate;
  const chunks = r.chunks
    .map((c) => `<div class="chunk">${escapeHtml(c.title)} · p.${escapeHtml(c.page)} · score ${c.score}${c.kind === "figure_caption" ? " · figure" : ""}<div class="snip">${escapeHtml(c.snippet)}…</div></div>`)
    .join("");

  // The span id is the join key: it finds this exact answer on the platform.
  const span = t.log_id
    ? `<div class="insp-span">span <code>${escapeHtml(t.log_id)}</code></div>`
    : "";

  $("inspBody").innerHTML = `
    <div class="insp-q">${escapeHtml(t.question)}</div>
    <div class="step">
      <div class="step-head">① RETRIEVE</div>
      <div class="step-body">${r.count} chunk${r.count === 1 ? "" : "s"} across the subject's books${r.latency_ms !== undefined ? ` · ${r.latency_ms} ms` : ""}${r.log_id ? " · logged to Respan" : ""}${chunks}</div>
    </div>
    <div class="step">
      <div class="step-head">② GENERATE</div>
      <div class="step-body">${escapeHtml(g.model)} · ${g.latency_ms} ms · via Respan Gateway</div>
    </div>
    <div class="step" id="scoreStep">
      <div class="step-head">③ GRADE</div>
      <div class="step-body" id="scoreBody"></div>
    </div>
    <button class="btn btn-primary eval-btn" id="evalBtn">Evaluate</button>
    <div class="insp-note" id="evalNote">Runs the five deployed graders over this
      answer as a Respan experiment, so the score is stored and comparable across
      runs. Takes under a minute.</div>
    ${span}`;

  // An answer keeps its score, so reopening the chat shows it rather than
  // spending another experiment run on a question already graded.
  if (t.scores) {
    showScored(idx, t);
  } else if (!t.log_id) {
    $("evalBtn").disabled = true;
    $("evalBtn").textContent = "No span id (older answer)";
  } else {
    $("evalBtn").onclick = () => runEval(idx);
  }
  $("inspect").hidden = false;
}

/** Already graded: show the stored scores, and offer a re-run explicitly. */
function showScored(idx, t) {
  renderScores(t.scores, t.experimentId);
  $("evalBtn").hidden = true;
  $("evalNote").innerHTML =
    'Scored by a Respan experiment. <a href="#" id="rerunBtn">Run it again</a> ' +
    'to re-grade — that starts a new experiment.';
  $("rerunBtn").onclick = (e) => { e.preventDefault(); runEval(idx); };
}

/** Sorted the way the pipeline runs, with anything unrecognised after. */
function ordered(names) {
  return [...names].sort((a, b) => {
    const ia = EVAL_ORDER.indexOf(a), ib = EVAL_ORDER.indexOf(b);
    if (ia === -1 && ib === -1) return a.localeCompare(b);
    if (ia === -1) return 1;
    if (ib === -1) return -1;
    return ia - ib;
  });
}

function renderScores(scores, experimentId) {
  const rows = ordered(Object.keys(scores)).map((name) => {
    const s = scores[name];
    const lever = !s.pass && LEVERS[name]
      ? `<div class="lever">${escapeHtml(LEVERS[name])}</div>` : "";
    return `<div class="evalrow"><span>${escapeHtml(name.replace(/^RAG · /, ""))}</span>` +
           `<span class="chip ${s.pass ? "s-pass" : "s-fail"}">${fmtScore(s.score)}</span></div>${lever}`;
  }).join("");
  $("scoreBody").innerHTML = rows +
    (experimentId ? `<div class="evd">experiment <code>${escapeHtml(experimentId)}</code></div>` : "");
}

async function runEval(idx) {
  const btn = $("evalBtn"), t = state.turns[idx];
  if (!t.log_id) return;
  btn.disabled = true;
  btn.hidden = false;
  btn.textContent = "Grading…";
  $("evalNote").textContent = "";
  $("scoreBody").innerHTML = '<div class="evd">starting<span class="dots"></span></div>';
  try {
    const res = await evaluateAnswer(state.activeChatId, t.log_id, t.question, (msg) => {
      $("scoreBody").innerHTML = `<div class="evd">${escapeHtml(msg)}<span class="dots"></span></div>`;
    });
    if (res.status === "ready") {
      t.scores = res.scores;
      t.experimentId = res.experiment_id;
      showScored(idx, t);
      return;                    // showScored hides the button; nothing to re-enable
    } else if (res.status === "pending") {
      // Log ingestion is async — right after an answer the span isn't there yet.
      $("scoreBody").innerHTML = '<div class="evd">The span isn\'t logged yet. Try again in a moment.</div>';
    } else if (res.status === "unconfigured") {
      $("scoreBody").innerHTML = '<div class="evd">No graders in this workspace. Run <code>python -m scripts.setup_respan --apply</code>, then restart the server.</div>';
    } else {
      $("scoreBody").innerHTML = `<div class="evd">Couldn't grade this answer${res.detail ? " — " + escapeHtml(res.detail) : ""}.</div>`;
    }
  } catch (e) {
    $("scoreBody").innerHTML = `<div class="evd">Evaluation failed — ${escapeHtml(e.message)}.</div>`;
  }
  btn.disabled = false;
  btn.textContent = "Evaluate";
}
