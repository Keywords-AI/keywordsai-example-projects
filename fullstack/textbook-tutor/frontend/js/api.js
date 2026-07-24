/** Every backend call lives here, so UI modules never build URLs by hand. */

async function json(path, opts) {
  return (await fetch(path, opts)).json();
}

const jsonBody = (method, body) => ({
  method,
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(body),
});

const subjectPath = (id, suffix = "") => `/api/subjects/${encodeURIComponent(id)}${suffix}`;
const chatPath = (id, suffix = "") => `/api/chats/${encodeURIComponent(id)}${suffix}`;

// --- app config ---
export const getConfig = () => json("/api/config");

// --- sidebar ---
/** Subjects with their chats, plus unfiled chats — one request. */
export const getSidebar = () => json("/api/sidebar");

// --- subjects ---
export const getSubject = (id) => json(subjectPath(id));
export const createSubject = (name, defaultInstructions) =>
  json("/api/subjects", jsonBody("POST", { name, default_instructions: defaultInstructions }));
export const renameSubject = (id, name) => fetch(subjectPath(id), jsonBody("PATCH", { name }));
export const setSubjectDefaultModel = (id, model) =>
  fetch(subjectPath(id), jsonBody("PATCH", { default_model: model }));
export const deleteSubject = (id) => fetch(subjectPath(id), { method: "DELETE" });

// --- books ---
export const uploadBook = (id, file, title) => {
  const fd = new FormData();
  fd.append("file", file);
  fd.append("title", title);
  return json(subjectPath(id, "/books"), { method: "POST", body: fd });
};
export const removeBook = (id, filename) =>
  fetch(subjectPath(id, `/books?filename=${encodeURIComponent(filename)}`), { method: "DELETE" });
export const renameBook = (id, filename, title) =>
  fetch(subjectPath(id, "/books"), jsonBody("PATCH", { filename, title }));

// --- chats ---
export const createChat = (subjectId, instructions, model) =>
  json(subjectPath(subjectId, "/chats"), jsonBody("POST", { instructions, model }));
/** A chat with no subject yet — file it by dragging it onto one. */
export const createUnfiledChat = (instructions, model) =>
  json("/api/chats", jsonBody("POST", { instructions, model }));
/** subjectId null files the chat back out of every subject. */
export const moveChat = (chatId, subjectId) =>
  json(chatPath(chatId, "/move"), jsonBody("POST", { subject_id: subjectId }));
export const getChat = (id) => json(chatPath(id));
export const renameChat = (id, title) => fetch(chatPath(id), jsonBody("PATCH", { title }));
export const setChatModel = (id, model) => fetch(chatPath(id), jsonBody("PATCH", { model }));
export const deleteChat = (id) => fetch(chatPath(id), { method: "DELETE" });

// --- asking ---
export const ask = (chatId, question, image) => {
  const fd = new FormData();
  fd.append("question", question);
  if (image) fd.append("image", image);
  return json(chatPath(chatId, "/query"), { method: "POST", body: fd });
};

/** Streamed ask. Calls onEvent for each server-sent event: `meta` once
 *  retrieval lands, `delta` per chunk of text, `title` when an untitled chat is
 *  named from its first exchange, then `done` (or `error`). */
export async function askStream(chatId, question, image, mode, onEvent) {
  const fd = new FormData();
  fd.append("question", question);
  fd.append("mode", mode || "qa");
  if (image) fd.append("image", image);
  const res = await fetch(chatPath(chatId, "/query/stream"), { method: "POST", body: fd });
  if (!res.ok || !res.body) throw new Error("stream failed: " + res.status);

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buf = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });
    // SSE frames are separated by a blank line; a chunk can split one in half.
    const frames = buf.split("\n\n");
    buf = frames.pop();
    for (const frame of frames) {
      const line = frame.split("\n").find((l) => l.startsWith("data: "));
      if (line) onEvent(JSON.parse(line.slice(6)));
    }
  }
}

// --- evaluation ---
/** Grade one answer as a one-row experiment on Respan.
 *  SSE, because the round trip is 20-60s; `onStep` gets progress messages. */
export function evaluateAnswer(chatId, logId, label, onStep) {
  return new Promise((resolve, reject) => {
    const url = chatPath(chatId, `/evaluate?log_id=${encodeURIComponent(logId)}`)
      + `&label=${encodeURIComponent(label || "")}`;
    const es = new EventSource(url);
    es.onmessage = (e) => {
      const msg = JSON.parse(e.data);
      if (msg.type === "step") { onStep && onStep(msg.message); return; }
      es.close();
      if (msg.type === "error") reject(new Error(msg.detail || "failed"));
      else resolve(msg);
    };
    es.onerror = () => { es.close(); reject(new Error("connection lost")); };
  });
}
