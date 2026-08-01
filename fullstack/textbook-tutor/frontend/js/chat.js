/** The conversation thread: rendering turns, asking, and the image composer. */
import { $ } from "./dom.js";
import { state } from "./state.js";
import { escapeHtml, mdToHtml } from "./markdown.js";
import * as api from "./api.js";
import { openInspect } from "./inspect.js";

/** Show a freshly generated chat title in the header and the sidebar. */
async function applyTitle(title) {
  const head = $("renameTitle");
  if (head) head.textContent = title;
  const row = document.querySelector(`.chat-row[data-chat="${state.activeChatId}"] .chat-title`);
  if (row) row.textContent = title;
  // Keep state in step so a later re-render doesn't revert to "New chat".
  const { chatById } = await import("./state.js");
  const c = chatById(state.activeChatId);
  if (c) { c.title = title; c.title_generated = true; }
}

/** Rebuild the thread from persisted history.
 *  `filed` is false for a chat that isn't in a subject yet — it has nowhere to
 *  retrieve from, so the empty state points at the fix rather than at books. */
export function renderChat(history, hasBooks, filed = true) {
  const thread = $("thread");
  thread.innerHTML = "";
  state.turns = [];
  if (!history.length) {
    const empty = !filed
      ? "This chat isn't in a subject yet.<br>Drag it onto one in the sidebar to give it materials."
      : (hasBooks
        ? "Ask a question.<br>Answers come only from this subject's books, cited by source."
        : "This subject has no books yet.<br>Click “Add book” to upload a PDF.");
    thread.innerHTML = '<div class="empty">' + empty + "</div>";
    return;
  }
  let lastQ = "";
  history.forEach((t) => {
    if (t.role === "user") {
      lastQ = t.content;
      appendTurn("user", escapeHtml(t.content));
    } else {
      appendTurn("tutor", mdToHtml(t.content), t.citations, {
        question: lastQ,
        answer: t.content,
        trace: t.trace,
        request_id: t.trace && t.trace.request_id,
        log_id: t.trace && t.trace.log_id,
        // Grading costs an experiment run, so a stored score is reused rather
        // than recomputed when the chat is reopened.
        scores: t.scores,
        experimentId: t.experiment_id,
      });
    }
  });
}

export function appendTurn(who, contentHtml, cites, meta) {
  document.querySelector(".empty")?.remove();
  const el = document.createElement("div");
  el.className = "turn " + who;

  let html = '<div class="role">' + (who === "user" ? "You" : "Tutor") + "</div>";
  html += '<div class="msg' + (who === "user" ? "" : " md") + '">' + contentHtml + "</div>";
  if (cites && cites.length) {
    html += '<div class="cites">' + cites.map((c) => '<span class="chip">' + escapeHtml(c) + "</span>").join("") + "</div>";
  }
  let myIdx = -1;
  if (who === "tutor" && meta && meta.trace) {
    myIdx = state.turns.push(meta) - 1;
    html += '<button class="inspect-btn" data-idx="' + myIdx + '">Inspect ⌁</button>';
  }
  el.innerHTML = html;

  const ib = el.querySelector(".inspect-btn");
  if (ib) {
    state.turns[myIdx].el = el;
    ib.onclick = () => openInspect(+ib.dataset.idx);
  }
  $("thread").appendChild(el);
  el.scrollIntoView({ behavior: "smooth", block: "end" });
  return el;
}

// --- image attachment (solve-an-exercise turns) ---

export function setImage(f) {
  state.pendingImage = f;
  const bar = $("attachBar");
  bar.hidden = false;
  bar.innerHTML = `<img src="${URL.createObjectURL(f)}" alt="" /><span>${escapeHtml(f.name)}</span><span class="x" id="imgX">remove</span>`;
  $("imgX").onclick = clearImage;
}

export function clearImage() {
  state.pendingImage = null;
  $("qimg").value = "";
  const bar = $("attachBar");
  bar.hidden = true;
  bar.innerHTML = "";
}

export function autosize() {
  const t = $("q");
  t.style.height = "auto";
  t.style.height = Math.min(t.scrollHeight, 160) + "px";
}

export async function ask() {
  const qv = $("q").value.trim(), img = state.pendingImage;
  if ((!qv && !img) || state.busy || !state.activeChatId) return;
  state.busy = true;
  $("send").disabled = true;
  $("q").value = "";
  autosize();

  let userHtml = "";
  if (img) userHtml += `<img class="q-img" src="${URL.createObjectURL(img)}" alt="exercise" />`;
  userHtml += `<div>${escapeHtml(qv || "Solve this exercise")}</div>`;
  appendTurn("user", userHtml);
  clearImage();

  // An image means solve, whatever the mode switch says.
  const mode = img ? "solve" : state.mode;
  const waiting = img ? "reading &amp; solving" : (mode === "lecture" ? "preparing a lecture" : "thinking");
  const pending = appendTurn("tutor", '<span class="dots">' + waiting + "</span>");
  const msg = pending.querySelector(".msg");
  try {
    let text = "", streamed = false, final = null, newTitle = null;
    await api.askStream(state.activeChatId, qv, img, mode, (ev) => {
      if (ev.type === "delta") {
        // Plain text while streaming: markdown is rendered once at the end,
        // because half-arrived tables, bold and $math$ render as garbage.
        if (!streamed) { streamed = true; msg.textContent = ""; msg.classList.add("streaming"); }
        text += ev.text;
        msg.textContent = text;
        msg.scrollIntoView({ block: "end" });
      } else if (ev.type === "title") {
        // An untitled chat just got named — reflect it without a reload.
        newTitle = ev.title;
      } else if (ev.type === "done") {
        final = ev;
      } else if (ev.type === "error") {
        throw new Error(ev.detail);
      }
    });
    if (!final) throw new Error("stream ended without a result");

    // Swap the raw stream for the rendered answer, now that it's complete.
    pending.remove();
    appendTurn("tutor", mdToHtml(final.answer), final.citations, {
      question: final.query || qv,
      answer: final.answer,
      trace: final.trace,
      request_id: final.request_id,
      log_id: final.log_id,
    });
    if (newTitle) await applyTitle(newTitle);
  } catch (err) {
    msg.classList.remove("streaming");
    msg.textContent = "Something went wrong.";
  }
  state.busy = false;
  $("send").disabled = false;
  $("q").focus();
}
