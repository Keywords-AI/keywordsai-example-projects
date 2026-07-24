/** Entry point: wire up the static chrome, then load the sidebar.
 *
 * Modules are deferred, so the DOM is already parsed when this runs.
 */
import { $ } from "./dom.js";
import { state } from "./state.js";
import { getConfig } from "./api.js";
import { loadSubjects, createSubject } from "./subjects.js";
import { newChat } from "./chats.js";
import { ask, setImage, autosize } from "./chat.js";
import { closeInspect } from "./inspect.js";
import { initTheme } from "./theme.js";

initTheme();

// The Chat/Subject switch decides what + creates. A chat made here is unfiled;
// dragging it onto a subject is what gives it materials.
const kindBtns = [...document.querySelectorAll("#newKind .seg-btn")];
kindBtns.forEach((b) => {
  b.onclick = () => {
    state.newKind = b.dataset.kind;
    kindBtns.forEach((x) => x.classList.toggle("active", x === b));
    $("newBtn").title = state.newKind === "subject" ? "New subject" : "New chat";
    if (state.newKind !== "subject") $("newForm").classList.remove("open");
  };
});

$("newBtn").onclick = () => {
  if (state.newKind !== "subject") { newChat(null); return; }
  const f = $("newForm");
  f.classList.toggle("open");
  if (f.classList.contains("open")) $("newName").focus();
};
$("cancelBtn").onclick = () => $("newForm").classList.remove("open");
$("createBtn").onclick = createSubject;

/** The Ask / Lecture switch in the composer. Server owns the list, so a new
 *  mode needs no frontend change beyond a placeholder here. */
function renderModes() {
  const box = $("modeSeg");
  if (!box || !state.modes.length) return;
  box.innerHTML = state.modes.map((m) =>
    `<button class="seg-btn ${m.id === state.mode ? "active" : ""}" data-mode="${m.id}" ` +
    `type="button" title="${m.note || ""}">${m.label}</button>`).join("");
  box.querySelectorAll(".seg-btn").forEach((b) => {
    b.onclick = () => {
      state.mode = b.dataset.mode;
      box.querySelectorAll(".seg-btn").forEach((x) => x.classList.toggle("active", x === b));
      $("send").textContent = state.mode === "lecture" ? "Teach" : "Ask";
      const q = $("q");
      if (!q.disabled) {
        q.placeholder = state.mode === "lecture"
          ? "What should I teach?" : "Ask a question…";
      }
    };
  });
}

// inspect panel
$("inspClose").onclick = closeInspect;

// composer
$("send").onclick = ask;
$("qimg").addEventListener("change", (e) => {
  const f = e.target.files[0];
  if (f) setImage(f);
});
$("q").addEventListener("input", autosize);
$("q").addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    ask();
  }
});

// Model allowlist and teaching styles are owned by the server.
try {
  const cfg = await getConfig();
  state.models = cfg.models || [];
  state.defaultModel = cfg.default_model || "";
  state.styles = cfg.styles || [];
  state.modes = cfg.modes || [];
  renderModes();
  // The new-subject style dropdown is filled from the server's list.
  const sel = $("newInstr");
  if (sel) {
    sel.innerHTML = state.styles
      .map((st) => `<option value="${st.value.replace(/"/g, "&quot;")}">${st.label}</option>`)
      .join("");
  }
} catch (e) { /* leave the model picker empty */ }

loadSubjects();
