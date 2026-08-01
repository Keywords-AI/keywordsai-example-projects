/** In-app dialogs, styled like the rest of the app.
 *
 * Replaces window.prompt/confirm, which render as a Chrome-chrome box quoting
 * "localhost:8000 says" — jarring against the Geist/monochrome UI, unstyleable,
 * and in the style picker it forced people to type a number.
 *
 * Every function resolves to the chosen value, or null if dismissed. Escape and
 * a backdrop click always dismiss.
 */
import { $ } from "./dom.js";
import { escapeHtml } from "./markdown.js";

let closeActive = null;   // dismisses whatever dialog is open

/** Build the shell, wire dismissal, and hand back the body to fill. */
function open({ title, hint }) {
  closeActive?.();
  const back = document.createElement("div");
  back.className = "modal-back";
  back.innerHTML =
    `<div class="modal" role="dialog" aria-modal="true" aria-label="${escapeHtml(title)}">` +
    `<div class="modal-head">${escapeHtml(title)}</div>` +
    (hint ? `<div class="modal-hint">${escapeHtml(hint)}</div>` : "") +
    `<div class="modal-body"></div>` +
    `<div class="modal-foot"></div></div>`;
  document.body.appendChild(back);

  // Remember what had focus so dismissing returns the user where they were.
  const restoreTo = document.activeElement;
  let settle = () => {};
  const close = (value) => {
    document.removeEventListener("keydown", onKey, true);
    back.remove();
    closeActive = null;
    if (restoreTo && restoreTo.focus) restoreTo.focus();
    settle(value);
  };
  const onKey = (e) => {
    if (e.key === "Escape") { e.preventDefault(); close(null); }
  };
  document.addEventListener("keydown", onKey, true);
  back.onclick = (e) => { if (e.target === back) close(null); };
  closeActive = () => close(null);

  const done = new Promise((resolve) => { settle = resolve; });
  return {
    body: back.querySelector(".modal-body"),
    foot: back.querySelector(".modal-foot"),
    close,
    done,
  };
}

function button(label, kind = "") {
  const b = document.createElement("button");
  b.className = "btn " + kind;
  b.type = "button";
  b.textContent = label;
  return b;
}

/** Pick one of a list. Clicking a row chooses it — one click, not two. */
export function chooseOption({ title, hint, options, selected }) {
  const m = open({ title, hint });
  m.body.className = "modal-body options";
  options.forEach((o) => {
    const row = document.createElement("button");
    row.type = "button";
    row.className = "opt" + (o.value === selected ? " current" : "");
    row.innerHTML = `<span class="opt-label">${escapeHtml(o.label)}</span>` +
      (o.note ? `<span class="opt-note">${escapeHtml(o.note)}</span>` : "");
    row.onclick = () => m.close(o.value);
    m.body.appendChild(row);
  });
  const cancel = button("Cancel");
  cancel.onclick = () => m.close(null);
  m.foot.appendChild(cancel);
  (m.body.querySelector(".opt.current") || m.body.querySelector(".opt"))?.focus();
  return m.done;
}

/** Ask for a line of text. Enter confirms. */
export function promptText({ title, hint, label, value = "", confirmLabel = "Save" }) {
  const m = open({ title, hint });
  const input = document.createElement("input");
  input.className = "f";
  input.value = value;
  if (label) input.setAttribute("aria-label", label);
  m.body.appendChild(input);

  const submit = () => {
    const v = input.value.trim();
    if (v) m.close(v);
  };
  input.onkeydown = (e) => {
    if (e.key === "Enter") { e.preventDefault(); submit(); }
  };
  const cancel = button("Cancel");
  cancel.onclick = () => m.close(null);
  const ok = button(confirmLabel, "btn-primary");
  ok.onclick = submit;
  m.foot.append(cancel, ok);
  input.focus();
  input.select();
  return m.done;
}

/** Confirm a destructive action. Resolves true only if confirmed. */
export function confirmAction({ title, hint, confirmLabel = "Delete" }) {
  const m = open({ title, hint });
  const cancel = button("Cancel");
  cancel.onclick = () => m.close(null);
  const ok = button(confirmLabel, "btn-primary danger");
  ok.onclick = () => m.close(true);
  m.foot.append(cancel, ok);
  ok.focus();
  return m.done.then((v) => v === true);
}
