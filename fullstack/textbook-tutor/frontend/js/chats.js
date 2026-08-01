/** Opening, creating and heading a chat.
 *
 * Teaching style is chosen when a chat starts and is fixed for its lifetime —
 * the header shows it as a read-only chip. Changing style means starting a new
 * chat on the same subject, which keeps a thread internally coherent.
 */
import { $ } from "./dom.js";
import { state } from "./state.js";
import { escapeHtml } from "./markdown.js";
import * as api from "./api.js";
import { renderChat } from "./chat.js";
import { closeInspect } from "./inspect.js";
import { chooseOption, promptText, confirmAction } from "./modal.js";

export function clearMain() {
  state.activeChatId = null;
  state.activeSubjectId = null;
  $("mainHead").innerHTML = '<span class="status">Add a subject, then start a chat.</span>';
  $("materials").hidden = true;
  $("thread").innerHTML = "";
  closeInspect();
  $("q").disabled = true;
  $("send").disabled = true;
  $("q").placeholder = "Start a chat to ask a question…";
}

/** Start a chat, asking which teaching style to use.
 *  With no subjectId the chat is unfiled — drag it onto a subject to give it
 *  materials. */
export async function newChat(subjectId) {
  const subject = subjectId ? state.subjects.find((s) => s.id === subjectId) : null;
  const style = await pickStyle(subject);
  if (style === null) return;            // cancelled
  const chat = subjectId
    ? await api.createChat(subjectId, style, null)
    : await api.createUnfiledChat(style, null);
  const { loadSubjects } = await import("./subjects.js");
  await loadSubjects(chat.id);
}

/** Style chooser — the list comes from the server. */
function pickStyle(subject) {
  const styles = state.styles || [];
  const def = (subject && subject.default_instructions) || "";
  return chooseOption({
    title: "New chat",
    hint: "Choose how this tutor should teach. The style is fixed once the chat starts — to use a different one, start another chat.",
    // The stored style string doubles as the description; the label is short.
    options: styles.map((st) => ({
      label: st.label,
      note: st.value || "No specific style — teach it straight.",
      value: st.value,
    })),
    selected: def,
  });
}

export async function openChat(chatId) {
  const chat = await api.getChat(chatId);
  if (chat.detail) { clearMain(); return; }   // deleted underneath us
  state.activeChatId = chat.id;
  state.activeSubjectId = chat.subject ? chat.subject.id : null;

  const subject = chat.subject;            // null when the chat is unfiled
  const books = (subject && subject.books) || [];
  const hasBooks = books.length > 0;
  const chips = books.map((b) => `<span class="book-chip">${escapeHtml(b.title)}</span>`).join("");

  const opts = state.models.map((m) => {
    const sel = chat.model === m.id ? " selected" : "";
    return `<option value="${m.id}"${sel}>${escapeHtml(m.label)}${m.note ? " — " + escapeHtml(m.note) : ""}</option>`;
  }).join("");
  const defLabel = (state.models.find((m) => m.id === state.defaultModel) || {}).label || state.defaultModel;
  const modelPicker = state.models.length
    ? `<select class="f model-pick" id="modelPick" title="Model used to answer in this chat">` +
      `<option value=""${chat.model ? "" : " selected"}>Default — ${escapeHtml(defLabel)}</option>${opts}</select>`
    : "";

  const styleLabel = escapeHtml(chat.style_label || styleLabelFor(chat.instructions));
  $("mainHead").innerHTML =
    `<span class="main-title" id="renameTitle" title="Click to rename this chat">${escapeHtml(chat.title || "New chat")}</span>` +
    `<span class="chip style-chip" title="Teaching style is fixed for this chat — start a new one to change it">${styleLabel}</span>` +
    `<span class="subject-of">${subject ? escapeHtml(subject.name) : "Unfiled — drag onto a subject"}</span>` +
    `<div class="books">${subject ? (chips || '<span class="status">no books yet</span>') : ""}</div>` +
    `<div class="head-right"><span class="status" id="status"></span>${modelPicker}` +
    `${hasBooks ? '<button class="btn" id="manageBtn">Manage</button>' : ""}` +
    `${subject ? '<label class="btn">Add book<input id="file" type="file" accept="application/pdf" hidden /></label>' : ""}` +
    `<span class="del" id="del">Delete chat</span></div>`;

  const { onFile, removeBook, renameBook } = await import("./subjects.js");
  if ($("file")) $("file").onchange = onFile;
  $("del").onclick = () => deleteChat(chat.id, chat.title);
  $("renameTitle").onclick = () => renameChat(chat.id, chat.title);
  if ($("modelPick")) {
    $("modelPick").onchange = async (e) => {
      await api.setChatModel(chat.id, e.target.value);
      const { loadSubjects } = await import("./subjects.js");
      await loadSubjects(chat.id);
    };
  }
  if ($("manageBtn")) {
    $("manageBtn").onclick = () => {
      state.materialsOpen = !state.materialsOpen;
      $("materials").hidden = !state.materialsOpen;
    };
  }

  $("materials").innerHTML = books.length
    ? books.map((b) =>
        `<div class="mat-row"><span class="mat-title">${escapeHtml(b.title)}</span>` +
        `<span class="mat-meta">${b.pages}p · ${b.chunks} chunks${b.figures ? " · " + b.figures + " fig" : ""} · ${escapeHtml(b.filename)}</span>` +
        `<button class="mat-ren" data-file="${encodeURIComponent(b.filename)}" data-title="${encodeURIComponent(b.title)}">Rename</button>` +
        `<button class="mat-del" data-file="${encodeURIComponent(b.filename)}">Remove</button></div>`
      ).join("")
    : '<div class="mat-empty">No materials yet.</div>';
  $("materials").querySelectorAll(".mat-del").forEach((el) => {
    el.onclick = () => removeBook(decodeURIComponent(el.dataset.file));
  });
  $("materials").querySelectorAll(".mat-ren").forEach((el) => {
    el.onclick = () => renameBook(decodeURIComponent(el.dataset.file), decodeURIComponent(el.dataset.title));
  });
  $("materials").hidden = !(state.materialsOpen && hasBooks);

  $("q").disabled = false;
  $("send").disabled = false;
  $("q").placeholder = !subject
    ? "Drag this chat onto a subject to give it materials…"
    : (hasBooks ? "Ask a question…" : "Add a textbook first…");

  const { renderSidebar } = await import("./subjects.js");
  renderSidebar();
  renderChat(chat.messages || [], hasBooks, !!subject);
}

function styleLabelFor(instructions) {
  const text = (instructions || "").trim();
  if (!text) return "Default";
  const known = (state.styles || []).find((s) => s.value === text);
  return known ? known.label : text.split("—")[0].split(".")[0].trim().slice(0, 24) || "Custom";
}

async function renameChat(chatId, cur) {
  const title = await promptText({
    title: "Rename chat", label: "Chat title", value: cur || "", confirmLabel: "Rename",
  });
  if (!title) return;
  await api.renameChat(chatId, title);
  const { loadSubjects } = await import("./subjects.js");
  await loadSubjects(chatId);
}

async function deleteChat(chatId, title) {
  const ok = await confirmAction({
    title: "Delete chat",
    hint: `"${title || "New chat"}" and its history will be removed. The subject's books stay.`,
    confirmLabel: "Delete chat",
  });
  if (!ok) return;
  await api.deleteChat(chatId);
  state.activeChatId = null;
  closeInspect();
  const { loadSubjects } = await import("./subjects.js");
  await loadSubjects();
}
