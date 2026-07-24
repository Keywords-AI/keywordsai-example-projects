/** Shared mutable UI state and constants.
 *
 * Exported as one object rather than as individual `let`s: ES module bindings
 * are read-only for importers, so `activeChatId = x` in another module would not
 * compile. Mutating properties of a shared object works everywhere.
 */
export const state = {
  /** Subjects, each with a `chats` array — the sidebar's source of truth. */
  subjects: [],
  /** Chats not filed under any subject, so with no materials to answer from. */
  unfiled: [],
  /** What the sidebar's + button creates: "chat" | "subject". */
  newKind: "chat",
  activeSubjectId: null,
  activeChatId: null,
  busy: false,
  materialsOpen: false,
  /** Per tutor-turn: {question, answer, trace, el, scores?} */
  turns: [],
  currentInspect: null,
  /** File attached for a solve-an-exercise turn */
  pendingImage: null,
  /** Model allowlist and teaching styles from the server. */
  models: [],
  defaultModel: "",
  styles: [],
  /** Study modes from the server, and the one selected in the composer. */
  modes: [],
  mode: "qa",
};

/** Which knob to reach for when a grader fails. Keyed by the evaluator's name
 *  on the platform, so a workspace can deploy others and they just show a score. */
export const LEVERS = {
  "RAG · context relevance": "Lever → retrieval: revisit chunking, top-K, or add a similarity floor.",
  "RAG · context completeness": "Lever → retrieval: raise Top-K or refine chunking so the answer is fully covered.",
  "RAG · groundedness": "Lever → generation: tighten the prompt to stay within the sources.",
  "RAG · context utilization": "Lever → generation: the model ignored retrieved context — strengthen the prompt.",
  "RAG · citation validity": "Lever → generation: constrain citations to the provided excerpts.",
};

/** Display order, retrieval steps first. Anything else sorts after, by name. */
export const EVAL_ORDER = [
  "RAG · context relevance",
  "RAG · context completeness",
  "RAG · groundedness",
  "RAG · context utilization",
  "RAG · citation validity",
];

/** The subject a chat belongs to, or null if it is unfiled. */
export const subjectOf = (chatId) =>
  state.subjects.find((s) => (s.chats || []).some((c) => c.id === chatId)) || null;

/** A chat by id, whether filed under a subject or unfiled. */
export const chatById = (chatId) => {
  for (const s of state.subjects) {
    const c = (s.chats || []).find((x) => x.id === chatId);
    if (c) return c;
  }
  return state.unfiled.find((x) => x.id === chatId) || null;
};
