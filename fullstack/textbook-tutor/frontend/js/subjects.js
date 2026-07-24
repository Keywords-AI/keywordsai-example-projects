/** Sidebar: unfiled chats, then subjects with their chats nested.
 *
 * A subject is a body of material — books plus a search index. Chats are the
 * conversations over it. A chat can also sit unfiled, with no subject and so no
 * materials, until it is dragged onto one.
 */
import { $ } from "./dom.js";
import { state, chatById } from "./state.js";
import { escapeHtml } from "./markdown.js";
import * as api from "./api.js";
import { openChat, clearMain } from "./chats.js";
import { closeInspect } from "./inspect.js";
import { promptText, confirmAction } from "./modal.js";

/** Same 24-box, 2px stroke, currentColor line art as the theme toggle. */
const TRASH = `<svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 6.5h16M9.5 6.5V4.5h5v2M6.5 6.5l1 13h9l1-13M10.5 10v6M13.5 10v6"/></svg>`;

export async function loadSubjects(selectChatId) {
  const data = await api.getSidebar();
  state.subjects = data.subjects || [];
  state.unfiled = data.unfiled || [];
  renderSidebar();

  // Prefer an explicit target, then whatever was open, then the first chat.
  const target = selectChatId
    || (chatById(state.activeChatId) ? state.activeChatId : null)
    || (state.unfiled[0] || state.subjects.flatMap((s) => s.chats || [])[0] || {}).id
    || null;
  if (target) openChat(target); else clearMain();
}

const chatRow = (c) => `
  <div class="chat-row ${c.id === state.activeChatId ? "active" : ""}" data-chat="${c.id}" draggable="true">
    <div class="chat-title">${escapeHtml(c.title || "New chat")}</div>
    <div class="chat-meta">${escapeHtml(c.style_label || "Default")}</div>
  </div>`;

export function renderSidebar() {
  const list = $("subjectList");
  if (!state.subjects.length && !state.unfiled.length) {
    list.innerHTML = '<div class="side-empty">Nothing yet.<br>Pick Chat or Subject above, then +.</div>';
    return;
  }

  // Unfiled chats sit above the subjects and double as the drop target for
  // dragging a chat back out of one.
  const unfiled = `
    <div class="unfiled dropzone" data-subject="">
      <div class="subject-head"><span class="subject-name plain">Unfiled</span></div>
      ${state.unfiled.map(chatRow).join("") || '<div class="chat-empty">Drag a chat here to unfile it</div>'}
    </div>`;

  const subjects = state.subjects.map((s) => `
    <div class="subject dropzone" data-subject="${s.id}">
      <div class="subject-head">
        <span class="subject-name" data-rename="${s.id}" title="Click to rename">${escapeHtml(s.name)}</span>
        <span class="subject-books">${s.book_count} book${s.book_count === 1 ? "" : "s"}</span>
        <button class="icon-btn tiny trash" data-del="${s.id}" title="Delete subject (its chats are kept)" aria-label="Delete subject">${TRASH}</button>
      </div>
      ${(s.chats || []).map(chatRow).join("") || '<div class="chat-empty">No chats — drag one here</div>'}
    </div>`).join("");

  list.innerHTML = unfiled + subjects;

  list.querySelectorAll(".chat-row").forEach((el) => {
    el.onclick = () => {
      state.materialsOpen = false;
      closeInspect();
      openChat(el.dataset.chat);
    };
    el.ondragstart = (e) => {
      e.dataTransfer.setData("text/plain", el.dataset.chat);
      e.dataTransfer.effectAllowed = "move";
      el.classList.add("dragging");
    };
    el.ondragend = () => el.classList.remove("dragging");
  });

  list.querySelectorAll("[data-rename]").forEach((el) => {
    el.onclick = (e) => { e.stopPropagation(); renameSubject(el.dataset.rename); };
  });
  list.querySelectorAll("[data-del]").forEach((el) => {
    el.onclick = (e) => { e.stopPropagation(); deleteSubject(el.dataset.del); };
  });

  list.querySelectorAll(".dropzone").forEach((zone) => {
    zone.ondragover = (e) => { e.preventDefault(); zone.classList.add("drop-over"); };
    zone.ondragleave = () => zone.classList.remove("drop-over");
    zone.ondrop = async (e) => {
      e.preventDefault();
      zone.classList.remove("drop-over");
      const chatId = e.dataTransfer.getData("text/plain");
      if (!chatId) return;
      // "" is the unfiled zone; the API takes null to mean "no subject".
      await api.moveChat(chatId, zone.dataset.subject || null);
      await loadSubjects(state.activeChatId);
    };
  });
}

// --- subjects ---

export async function createSubject() {
  const name = $("newName").value.trim();
  if (!name) { $("newName").focus(); return; }
  await api.createSubject(name, $("newInstr").value.trim());
  $("newName").value = "";
  $("newForm").classList.remove("open");
  await loadSubjects(state.activeChatId);
}

async function renameSubject(subjectId) {
  const s = state.subjects.find((x) => x.id === subjectId);
  const name = await promptText({
    title: "Rename subject", label: "Subject name", value: s ? s.name : "", confirmLabel: "Rename",
  });
  if (!name) return;
  await api.renameSubject(subjectId, name);
  await loadSubjects(state.activeChatId);
}

async function deleteSubject(subjectId) {
  const s = state.subjects.find((x) => x.id === subjectId);
  if (!s) return;
  const n = (s.chats || []).length;
  const kept = n
    ? ` Its ${n} chat${n === 1 ? "" : "s"} will be kept and moved to Unfiled.`
    : "";
  const ok = await confirmAction({
    title: "Delete subject",
    hint: `"${s.name}" and its ${s.book_count} book${s.book_count === 1 ? "" : "s"} will be removed, along with the search index.${kept}`,
    confirmLabel: "Delete subject",
  });
  if (!ok) return;
  await api.deleteSubject(subjectId);
  state.materialsOpen = false;
  closeInspect();
  await loadSubjects(chatById(state.activeChatId) ? state.activeChatId : null);
}

// --- books ---

export async function onFile(e) {
  const f = e.target.files[0];
  if (!f) return;
  const suggested = f.name.replace(/\.pdf$/i, "");
  const chosen = await promptText({
    title: "Add book",
    hint: "This short title appears in every citation, like [Campbell, p. 12].",
    label: "Citation title", value: suggested, confirmLabel: "Upload",
  });
  if (!chosen) { e.target.value = ""; return; }   // cancelled — don't ingest
  const title = chosen.trim();
  $("status").innerHTML = 'ingesting<span class="dots"></span>';
  try {
    const data = await api.uploadBook(state.activeSubjectId, f, title);
    // `replaced` means this filename already existed and was re-ingested.
    $("status").textContent = data.status === "ok"
      ? `${data.replaced ? "replaced · " : ""}${data.pages}p · ${data.chunks} chunks${data.figures ? " · " + data.figures + " fig" : ""}`
      : "upload failed";
    await loadSubjects(state.activeChatId);
  } catch (err) {
    $("status").textContent = "upload failed";
  }
  e.target.value = "";
}

export async function removeBook(filename) {
  const ok = await confirmAction({
    title: "Remove book",
    hint: `"${filename}" and its chunks will be removed from this subject. Existing answers keep their citations.`,
    confirmLabel: "Remove book",
  });
  if (!ok) return;
  await api.removeBook(state.activeSubjectId, filename);
  await loadSubjects(state.activeChatId);
}

export async function renameBook(filename, cur) {
  const title = await promptText({
    title: "Rename book",
    hint: "Used in citations. Renaming updates existing answers too — no re-ingest.",
    label: "Citation title", value: cur, confirmLabel: "Rename",
  });
  if (!title) return;
  await api.renameBook(state.activeSubjectId, filename, title);
  await loadSubjects(state.activeChatId);
}
