"""Source-diverse retrieval + grounded multi-book synthesis, plus a per-query
RAG **trace** (what each step did) for the in-app observability panel.

Steps: Retrieve -> Generate, each emitting a span to Respan.

No grading happens here. Answer quality is measured on the Respan platform by
running the five deployed graders as an **experiment** over a fixed question set
(`scripts/run_experiment.py`), where one run is comparable to the next.
"""
import json
import re
import time
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor

import anthropic
from llama_index.core.vector_stores import ExactMatchFilter, MetadataFilters

from . import config, store

SYSTEM_TEMPLATE = """You are the tutor for {tutor_name}. You help a student learn \
from this course's assigned materials, and you answer using ONLY the excerpts \
provided with the question below.
{instructions}
HOW TO ANSWER
- Teach clearly and in a logical order, the way a good tutor would.
- Earlier turns of this conversation tell you what the student is asking about —
  a follow-up like "explain that again" or "why?" refers back to them. Use them to
  understand the question, not as a source of facts.
- Draw on all the relevant excerpts and bring them together into one coherent answer.
- Cite every claim with its source and page, like [<source title>, p. 12]. When
  more than one source supports a point, cite each. Put nothing else inside the
  brackets — only the title and page. Theorem, example, and exercise numbers go in
  your sentence: write "by Exercise 16 [Axler, p. 130]", never the form
  "[Axler, p. 130, Exercise 16]".
- When the sources differ, or one adds detail another leaves out, say so plainly
  rather than silently choosing one.
- Use the wording and terminology the materials themselves use; don't substitute
  outside terms.

STAY INSIDE THE MATERIALS
- Use only what is in the excerpts. Never add outside knowledge, even when you are
  confident it is correct.
- Your earlier answers are not a source. Every claim must be re-grounded in, and
  cited from, the excerpts provided with THIS question — even if you said it before.
- If the excerpts do not contain the answer, say exactly:
  "The course materials don't cover this." Do not guess or fill gaps.
- If they only partly cover it, teach what is there and state plainly what is missing.
"""

LECTURE_TEMPLATE = """You are the tutor for {tutor_name}. A student has asked to be \
TAUGHT the concept behind a question, not simply given the answer. Teach a short \
lecture from this course's assigned materials, using ONLY the excerpts provided.
{instructions}
HOW TO TEACH
- Open with the idea in one or two sentences, in the materials' own terms.
- Then build it up in the order the materials do. The excerpts are given in
  reading order; follow that order rather than jumping around.
- Define each term the first time it appears, the way the materials define it.
- Work through an example if the excerpts contain one. Don't invent your own.
- Say how this connects to what comes before or after it in the book, when the
  excerpts show that.
- Close with what a student should be able to do with this.

STAY INSIDE THE MATERIALS
- Use only what is in the excerpts. Never add outside knowledge, even when you
  are confident it is correct, and even when it would round the lecture out.
- Cite each claim with its source and page, like [<source title>, p. 12]. Put nothing
  else inside the brackets — only the title and page; theorem or exercise numbers go in
  your sentence, as in "by Exercise 16 [Axler, p. 130]", not "[Axler, p. 130, Exercise 16]".
- Where the excerpts stop short, say so plainly: "the materials introduce this
  but don't develop it here". A lecture with an honest gap is worth more than a
  smooth one you filled in yourself.
- If the excerpts don't cover the concept at all, say exactly:
  "The course materials don't cover this." Do not teach it from memory.
"""

SOLVE_TEMPLATE = """You are the tutor for {tutor_name}. A student has uploaded an \
exercise (shown to you as an image, and transcribed below). Solve it the \
way a good tutor would — teaching the method as you work through it — using ONLY the \
course's assigned materials provided with it.
{instructions}
HOW TO SOLVE
- Work the problem step by step. Apply the definitions, theorems, methods, and notation
  from the excerpts; you may carry out the algebra or calculation each method requires.
- Cite the material behind each step, like [<source title>, p. 12]. Put nothing else
  inside the brackets — only the title and page; theorem or exercise numbers go in the
  sentence, as in "by 6.30 [Axler, p. 207]", not "[Axler, p. 207, 6.30]".
- Use the wording and notation the materials use; don't substitute outside conventions.
- Explain your reasoning so the student learns the method, not just the final answer.

STAY GROUNDED IN THE COURSE
- The METHOD must come from the materials. Don't introduce techniques the materials do
  not teach, even if you are confident they would work.
- If the materials don't contain the method needed for this exercise, say exactly:
  "The course materials don't cover the method needed for this exercise." Then say what
  is missing rather than guessing.
- If the image isn't a legible exercise, say so plainly.
"""

if config.USE_GATEWAY:
    _client = anthropic.Anthropic(api_key=config.RESPAN_API_KEY, base_url=config.RESPAN_GATEWAY_URL)
else:
    _client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)


# --- retrieval ---------------------------------------------------------------

def _rrf_fuse(ranked_lists: list[list], k: int, top_n: int) -> list:
    """Reciprocal Rank Fusion of several ranked node lists into one.

    Each list is in descending relevance. A node's fused score is the sum over
    lists of 1/(k + rank), so appearing high in either list lifts it and a node
    both agree on wins. Pure and index-free (operates on node ids), so it is unit
    tested without a live store. Mutates the kept nodes' `.score` to the fused
    value so the downstream source-diverse merge, which sorts by score, stays
    consistent whether or not fusion ran.
    """
    scores: dict[str, float] = {}
    nodes: dict = {}
    for ranked in ranked_lists:
        for rank, nw in enumerate(ranked, 1):
            nid = nw.node.node_id
            scores[nid] = scores.get(nid, 0.0) + 1.0 / (k + rank)
            nodes.setdefault(nid, nw)
    ordered = sorted(nodes.values(), key=lambda nw: scores[nw.node.node_id], reverse=True)
    out = []
    for nw in ordered[:top_n]:
        nw.score = scores[nw.node.node_id]
        out.append(nw)
    return out


def _book_hits(index, subject_id: str, filename: str, query: str, top_n: int) -> list:
    """Top-`top_n` chunks from ONE book, through the full retrieval stack.

    Candidates come from dense vector search, or RRF(dense, BM25) when hybrid is
    on. When reranking is on, a wider pool is fetched and a cross-encoder picks
    the top_n from it. The single seam both production and the benchmark go
    through, so a flag flip moves the app and the measurement together.
    """
    filters = MetadataFilters(filters=[ExactMatchFilter(key="source", value=filename)])
    # Rerank needs a wider pool to reorder; without it, fetch exactly top_n.
    pool = max(top_n, config.RERANK_CANDIDATES) if config.RERANK else top_n

    if config.HYBRID_SEARCH:
        cand_n = max(config.HYBRID_CANDIDATES, pool)
        dense = index.as_retriever(similarity_top_k=cand_n, filters=filters).retrieve(query)
        lexical = store.keyword_hits(subject_id, filename, query, cand_n)
        candidates = _rrf_fuse([dense, lexical], config.RRF_K, pool)
    else:
        candidates = index.as_retriever(similarity_top_k=pool, filters=filters).retrieve(query)

    if config.RERANK:
        candidates = store.rerank(query, candidates, top_n)
    return candidates[:top_n]


def _retrieve(subject: dict, query: str):
    """Coverage-first source-diverse retrieval (one best chunk per book, then by score)."""
    books = subject.get("books", [])
    if not books:
        return []
    index = store.get_index(subject["id"])

    per_book = [
        _book_hits(index, subject["id"], book["filename"], query, config.TOP_K_PER_BOOK)
        for book in books
    ]
    return _merge_source_diverse(per_book, config.MAX_CONTEXT_CHUNKS)


def ranked_candidates(subject: dict, query: str, top_n: int) -> list:
    """One ranked list across all books, score-sorted, for retrieval measurement.

    Unlike `_retrieve` (coverage-first, one chunk per book guaranteed) this ranks
    purely by relevance and returns up to `top_n`, so the benchmark can read
    recall@k and MRR off true rank. Respects HYBRID_SEARCH via the same seam the
    app uses, so the benchmark measures exactly what production would retrieve.
    """
    books = subject.get("books", [])
    if not books:
        return []
    index = store.get_index(subject["id"])
    pooled = []
    for book in books:
        pooled.extend(_book_hits(index, subject["id"], book["filename"], query, top_n))
    pooled.sort(key=lambda nw: (nw.score or 0.0), reverse=True)
    return pooled[:top_n]


def _merge_source_diverse(per_book: list[list], max_chunks: int) -> list:
    """Take the best chunk from every book that hit, then fill by score.

    Split out from _retrieve so it can be tested without a live index. The point
    is coverage: a weaker book still gets one chunk in, so it can be cited and
    synthesis actually has more than one source to work with.
    """
    selected, seen = [], set()

    def take(node):
        nid = node.node.node_id
        if nid not in seen:
            seen.add(nid)
            selected.append(node)

    for nodes in per_book:
        if nodes:
            take(nodes[0])
    rest = [n for nodes in per_book for n in nodes[1:]]
    rest.sort(key=lambda n: (n.score or 0.0), reverse=True)
    for node in rest:
        if len(selected) >= max_chunks:
            break
        take(node)
    if len(selected) > max_chunks:
        selected.sort(key=lambda n: (n.score or 0.0), reverse=True)
        selected = selected[:max_chunks]
    return selected


def _expand_for_lecture(subject: dict, nodes: list) -> list:
    """Add the chunks either side of each hit, in reading order.

    Top-K by similarity returns the best-matching fragments, which is right for
    answering a question and wrong for teaching a concept: a lecture needs the
    passage the idea lives in, and textbook prose is sequential. So each hit
    brings its neighbours, and the result is ordered by position in the book
    rather than by score, so the excerpts read as continuous material.

    Best effort. If the store can't supply neighbours the lecture is still built
    from the ordinary hits, which is worse but not broken.
    """
    wanted: dict[str, set[str]] = {}
    for n in nodes:
        src = n.node.metadata.get("source")
        if src:
            wanted.setdefault(src, set()).add(n.node.node_id)
    try:
        extra, positions = store.neighbours(subject["id"], wanted,
                                            config.LECTURE_NEIGHBOUR_WINDOW)
    except Exception:
        return nodes
    return _in_reading_order(nodes, extra, positions, config.LECTURE_MAX_CHUNKS)


def _in_reading_order(hits: list, extra: list, positions: dict, max_chunks: int) -> list:
    """Merge hits and their neighbours, ordered as they appear in each book.

    Split out from _expand_for_lecture so the ordering and the budget can be
    tested without a live index. Hits are never dropped to make room for a
    neighbour: if the budget binds, neighbours go first.
    """
    hit_ids = {n.node.node_id for n in hits}
    keep = list(hits)
    room = max(0, max_chunks - len(keep))
    keep.extend([n for n in extra if n.node.node_id not in hit_ids][:room])
    # By book, then by position in it. A node with no known position sorts last
    # within its book rather than silently jumping to the front.
    keep.sort(key=lambda n: (n.node.metadata.get("source") or "",
                             positions.get(n.node.node_id, 10**6)))
    return keep


def _title_map(subject: dict) -> dict:
    # filename -> current display title, so renaming a book updates citations live
    return {b["filename"]: b["title"] for b in subject.get("books", [])}


def _title_page(n, title_map: dict):
    src = n.node.metadata.get("source")
    title = title_map.get(src) or n.node.metadata.get("display_title") or src or "?"
    return title, str(n.node.metadata.get("page", "?"))


def _format_context(nodes, title_map: dict) -> str:
    blocks = []
    for n in nodes:
        title, page = _title_page(n, title_map)
        blocks.append(f"[{title}, p. {page}]\n{n.node.get_content().strip()}")
    return "\n\n---\n\n".join(blocks)


def _citations(nodes, title_map: dict) -> list[str]:
    seen, out = set(), []
    for n in nodes:
        title, page = _title_page(n, title_map)
        if (title, page) not in seen:
            seen.add((title, page))
            out.append(f"{title}, p. {page}")
    return out


def _trace_chunks(nodes, title_map: dict) -> list[dict]:
    out = []
    for n in nodes:
        title, page = _title_page(n, title_map)
        text = " ".join(n.node.get_content().split())
        out.append({
            "title": title, "page": page, "score": round(n.score or 0.0, 3),
            "kind": n.node.metadata.get("content_type", "text"), "snippet": text[:160],
        })
    return out


# --- retrieval span -----------------------------------------------------------

# Retrieval runs against local Chroma, so it never touches the gateway and would
# otherwise leave no trace at all — the RRAG guide wants a span per pipeline step.
# We post one ourselves via the Spans API.
#
# It is NOT joined to the generation span: the gateway logs that one server-side,
# and respan_params has no trace_unique_id / span_parent_id to hand it. Both spans
# instead carry the same `request_id` in metadata, which is how they correlate.
_RESPAN_API = "https://api.respan.ai/api"
_span_pool = ThreadPoolExecutor(max_workers=2)


def _post_retrieval_span(payload: dict) -> None:
    """Best effort — an observability span must never break an answer."""
    try:
        req = urllib.request.Request(
            f"{_RESPAN_API}/request-logs/",
            data=json.dumps(payload).encode(),
            headers={"Authorization": f"Bearer {config.RESPAN_API_KEY}",
                     "Content-Type": "application/json"},
            method="POST")
        urllib.request.urlopen(req, timeout=30).close()
    except Exception:
        pass


def _log_retrieval(subject: dict, query: str, context: str, latency_s: float,
                   request_id: str, chunk_count: int) -> str | None:
    """Record the retrieve step as its own span. Returns its id, or None.

    Fired on a worker thread: the answer shouldn't wait on telemetry. The id is
    generated here rather than read back, because the API honours a
    client-supplied unique_id.
    """
    if not config.RESPAN_API_KEY:
        return None
    span_id = uuid.uuid4().hex
    _span_pool.submit(_post_retrieval_span, {
        "unique_id": span_id,
        "log_type": "task",
        "span_name": "retrieve",
        "model": "retrieval",
        "input": query,
        "output": context,
        "latency": round(latency_s, 4),
        "status_code": 200,
        "customer_identifier": "textbook-tutor:retrieve",
        "metadata": {"app": "textbook-tutor", "subject": subject["name"], "step": "retrieve",
                     "request_id": request_id, "chunks": str(chunk_count)},
    })
    return span_id


# --- chat titles --------------------------------------------------------------

_TITLE_SYS = (
    "You name a tutoring conversation from its first exchange. Reply with a "
    "title of 3-6 words naming the specific topic covered — no quotes, no "
    "trailing punctuation, no preamble. Prefer the concrete subject matter over "
    "the phrasing of the question: 'Calvin cycle phases', not 'Explaining a "
    "question about the Calvin cycle'."
)


def generate_title(subject: dict, question: str, answer: str) -> str | None:
    """Name a chat from its first exchange, or None if that fails.

    Uses the answer as well as the question because questions are often
    "can you explain this?" while the answer reveals what was actually covered.
    Runs on the cheap model — this is labelling, not reasoning.
    """
    kwargs = dict(
        model=config.REWRITE_MODEL,
        max_tokens=32,
        system=_TITLE_SYS,
        messages=[{"role": "user", "content":
                   f"Student asked:\n{question[:600]}\n\nTutor answered:\n{answer[:1200]}\n\nTitle:"}],
    )
    if config.USE_GATEWAY:
        kwargs["metadata"] = {"respan_params": {
            "customer_identifier": "textbook-tutor:title",
            "metadata": {"app": "textbook-tutor", "subject": subject["name"], "step": "title"},
        }}
    try:
        resp = _client.messages.create(**kwargs)
        title = "".join(b.text for b in resp.content if b.type == "text").strip()
        title = title.strip("\"'").rstrip(".").strip()
        return title[:80] or None
    except Exception:
        return None


# --- conversation memory ------------------------------------------------------

def _history_messages(history: list[dict], limit: int) -> list[dict]:
    """Map stored chat turns onto Claude messages (our "tutor" -> "assistant").

    Stored turns carry citations/trace/has_image too; only the text is replayed.
    Past images aren't re-sent — the user turn already holds their transcription.
    """
    if limit <= 0 or not history:
        return []
    out: list[dict] = []
    for turn in history[-limit:]:
        content = (turn.get("content") or "").strip()
        if not content:
            continue
        role = "assistant" if turn.get("role") == "tutor" else "user"
        if out and out[-1]["role"] == role:
            out[-1]["content"] += "\n\n" + content   # keep the transcript alternating
        else:
            out.append({"role": role, "content": content})
    # A window can start mid-exchange, but the API requires a leading user turn.
    while out and out[0]["role"] != "user":
        out.pop(0)
    return out


_REWRITE_SYS = (
    "You rewrite a student's latest message into a standalone search query for a "
    "textbook search engine. Use the conversation to resolve references like \"that\", "
    "\"it\", or \"explain it more simply\" into the actual topic being discussed. "
    "Output ONLY the rewritten query — no preamble, no quotes, no explanation. If the "
    "message is already self-contained, output it unchanged."
)


def _standalone_query(subject: dict, query: str, history_msgs: list[dict]) -> str:
    """Resolve a follow-up into a self-contained retrieval query.

    Without this, "explain that more simply" is embedded literally and retrieves
    chunks about simplicity rather than about whatever "that" was.
    """
    transcript = "\n".join(
        f"{'Student' if m['role'] == 'user' else 'Tutor'}: {m['content'][:600]}"
        for m in history_msgs
    )
    kwargs = dict(
        model=config.REWRITE_MODEL,
        max_tokens=200,
        system=_REWRITE_SYS,
        messages=[{"role": "user", "content":
                   f"Conversation so far:\n{transcript}\n\n"
                   f"Student's latest message: {query}\n\nStandalone search query:"}],
    )
    if config.USE_GATEWAY:
        kwargs["metadata"] = {"respan_params": {
            "customer_identifier": "textbook-tutor:rewrite",
            "metadata": {"app": "textbook-tutor", "subject": subject["name"], "step": "rewrite"},
        }}
    try:
        resp = _client.messages.create(**kwargs)
        return "".join(b.text for b in resp.content if b.type == "text").strip() or query
    except Exception:
        return query   # retrieving on the raw query beats failing the whole answer


# --- generation --------------------------------------------------------------

_TRANSCRIBE_PROMPT = (
    "This image shows a homework exercise or problem from a course. Transcribe it "
    "exactly as text: include every part (a, b, c, ...), all numbers, variables, and "
    "mathematical notation (write math in LaTeX — $...$ inline, $$...$$ for display). "
    "If it contains a diagram, add a one-line description in brackets. Output ONLY the "
    "transcription — do NOT solve it."
)


def _transcribe(subject: dict, image: dict) -> str:
    """Read the exercise off an uploaded image into text (drives retrieval).

    Raises on API failure. The caller needs to tell "the photo is unreadable"
    (empty transcription) apart from "the call failed" — swallowing the error
    here made an outage look like the student's photo was bad.
    """
    kwargs = dict(
        model=config.CAPTION_MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": image["media_type"], "data": image["data"]}},
            {"type": "text", "text": _TRANSCRIBE_PROMPT},
        ]}],
    )
    if config.USE_GATEWAY:
        kwargs["metadata"] = {"respan_params": {
            "customer_identifier": "textbook-tutor:transcribe",
            "metadata": {"app": "textbook-tutor", "subject": subject["name"], "step": "transcribe"},
        }}
    resp = _client.messages.create(**kwargs)
    return "".join(b.text for b in resp.content if b.type == "text").strip()


def answer_stream(subject: dict, chat: dict, query: str, image: dict | None = None,
                  history: list[dict] | None = None, include_prompt: bool = False,
                  mode: str = "qa"):
    """Answer a question, yielding events as they happen.

    Yields, in order:
      {"type": "meta",  citations, retrieve, query}  once retrieval is done, so
                                                     the UI can show sources
                                                     before any text arrives
      {"type": "delta", text}                        each chunk of the answer
      {"type": "done",  answer, citations, trace, log_id, request_id, query}

    Early exits (no books, unreadable image, nothing retrieved) yield a single
    "done" carrying the message. `answer()` below drains this, so the streaming
    and blocking paths cannot drift apart.
    """
    if not subject.get("books"):
        yield {"type": "done", "answer": "This subject has no materials yet — add a textbook first.",
               "citations": [], "trace": None, "query": query, "log_id": None, "request_id": None}
        return

    # An uploaded exercise image is transcribed to text so it can drive retrieval;
    # the image itself is also handed to the solver so it sees the exact problem.
    exercise_text = None
    if image:
        try:
            exercise_text = _transcribe(subject, image)
        except Exception as e:
            yield {"type": "done",
                   "answer": f"I couldn't read that image — the transcription step failed "
                             f"({type(e).__name__}). This is a problem on our side, not with "
                             f"your photo. Please try again.",
                   "citations": [], "trace": None, "query": query, "log_id": None, "request_id": None}
            return
    effective_query = "\n\n".join(p for p in [(query or "").strip(), exercise_text or ""] if p).strip()
    if not effective_query:
        yield {"type": "done", "answer": "Please type a question, or upload a legible photo of an exercise.",
               "citations": [], "trace": None, "query": query, "log_id": None, "request_id": None}
        return

    # Retrieve on a self-contained query. In solve mode the transcription is
    # already standalone, so rewriting it would only risk losing the exercise.
    history_msgs = _history_messages(history or [], config.HISTORY_TURNS)
    retrieval_query = effective_query
    if history_msgs and not image:
        retrieval_query = _standalone_query(subject, effective_query, history_msgs)

    # Stamped before retrieval so the retrieve and generate spans can carry the
    # same request_id and be correlated after the fact.
    request_id = uuid.uuid4().hex
    t_retrieve = time.perf_counter()
    nodes = _retrieve(subject, retrieval_query)
    retrieve_ms = round((time.perf_counter() - t_retrieve) * 1000)
    if not nodes:
        yield {"type": "done", "answer": "The course materials don't cover this.", "citations": [],
               "trace": None, "query": effective_query, "log_id": None, "request_id": None}
        return

    # Lecture wants a continuous run of the book, so pull the chunks either side
    # of each hit and present them in reading order. Q&A keeps the tight,
    # score-ordered set: more context is not better when answering one question.
    if mode == "lecture" and not image:
        nodes = _expand_for_lecture(subject, nodes)

    tm = _title_map(subject)
    context = _format_context(nodes, tm)
    # Retrieval touches only local Chroma, so it produces no gateway span; post
    # one so the retrieve step is visible in Respan like the LLM steps are.
    retrieval_log_id = _log_retrieval(subject, retrieval_query, context,
                                      retrieve_ms / 1000, request_id, len(nodes))

    style = (chat.get("instructions") or "").strip()
    # An attached image means solve, whatever mode was selected: the student is
    # pointing at a specific exercise, which is not a request for a lecture.
    effective_mode = "solve" if image else mode
    template = {"solve": SOLVE_TEMPLATE, "lecture": LECTURE_TEMPLATE}.get(
        effective_mode, SYSTEM_TEMPLATE)
    system = template.format(
        tutor_name=subject["name"],
        instructions=(f"\nTeaching style: {style}\n" if style else ""),
    )
    if image:
        prompt_text = (
            f"Excerpts (each labelled with its source and page):\n\n{context}\n\n"
            f"The student's exercise, transcribed from the attached image:\n{exercise_text}\n\n"
            "Solve the exercise, showing each step and citing the course material behind each method you use."
        )
        user_content = [
            {"type": "image", "source": {"type": "base64", "media_type": image["media_type"], "data": image["data"]}},
            {"type": "text", "text": prompt_text},
        ]
    elif effective_mode == "lecture":
        user_content = (f"Excerpts (each labelled with its source and page, in reading "
                        f"order):\n\n{context}\n\nTeach the concept behind this question: {query}")
    else:
        user_content = f"Excerpts (each labelled with its source and page):\n\n{context}\n\nQuestion: {query}"

    # max_tokens bounds thinking AND answer text together, so a hard solve-mode
    # exercise can spend most of the budget thinking and cut the answer mid-step.
    # 16k is Anthropic's non-streaming guidance and leaves room for both.
    # Per-chat model override, falling back to the configured default.
    model = config.resolve_model(chat.get("model"))
    kwargs = dict(
        model=model,
        max_tokens=16000,
        system=system,
        messages=history_msgs + [{"role": "user", "content": user_content}],
    )
    thinking = config.thinking_config(model)
    if thinking:
        kwargs["thinking"] = thinking
    if config.USE_GATEWAY:
        kwargs["metadata"] = {"respan_params": {
            "customer_identifier": "textbook-tutor:generate",  # first-class field online-eval automations filter on
            "metadata": {"app": "textbook-tutor", "subject": subject["name"],
                         "chat": chat.get("title") or chat["id"], "step": "generate",
                         "mode": effective_mode, "request_id": request_id},
        }}

    tm_citations = _citations(nodes, tm)
    retrieve_trace = {"count": len(nodes), "chunks": _trace_chunks(nodes, tm),
                      "query": retrieval_query,
                      "rewritten": retrieval_query != effective_query,
                      "latency_ms": retrieve_ms,
                      "log_id": retrieval_log_id}
    # Sources first: the UI can show which chunks were used before any text
    # arrives, which is most of the wait on a long answer.
    yield {"type": "meta", "citations": tm_citations, "retrieve": retrieve_trace,
           "query": effective_query}

    t0 = time.perf_counter()
    parts = []
    # Streaming keeps the gateway's x-respan-log-id header reachable via
    # stream.response, so the Inspect panel can still find this exact span.
    with _client.messages.stream(**kwargs) as stream:
        for chunk in stream.text_stream:
            parts.append(chunk)
            yield {"type": "delta", "text": chunk}
        resp = stream.get_final_message()
        log_id = stream.response.headers.get("x-respan-log-id")  # gateway only
    latency_ms = round((time.perf_counter() - t0) * 1000)

    text = "".join(parts).strip()
    if not text:
        text = "(No answer was generated. Try rephrasing your question.)"
        yield {"type": "delta", "text": text}
    # Don't present a cut-off answer as a complete one — it will look like the
    # tutor simply stopped teaching partway through a step.
    if resp.stop_reason == "max_tokens":
        cut = "\n\n_(This answer hit the output limit and was cut off mid-explanation.)_"
        text += cut
        yield {"type": "delta", "text": cut}

    trace = {
        "retrieve": retrieve_trace,
        "generate": {"model": model, "latency_ms": latency_ms,
                     "mode": effective_mode, "stop_reason": resp.stop_reason,
                     "history_turns": len(history_msgs)},
        "request_id": request_id,
        "log_id": log_id,
    }
    if exercise_text:
        trace["exercise"] = exercise_text
    # The composed user message, for callers that need to grade the exact input
    # the model saw — scripts/run_experiment.py. Off by default: it is several KB
    # of context that the browser has no use for.
    if include_prompt and isinstance(user_content, str):
        trace["prompt"] = user_content
    yield {"type": "done", "answer": text, "citations": tm_citations, "trace": trace,
           "request_id": request_id, "log_id": log_id, "query": effective_query}


def answer(subject: dict, chat: dict, query: str, image: dict | None = None,
           history: list[dict] | None = None, include_prompt: bool = False,
           mode: str = "qa") -> dict:
    """Blocking form of answer_stream — drains the stream and returns the result.

    Kept as the programmatic entry point (scripts, tests). Implemented on top of
    the generator so there is only one copy of the pipeline to keep correct.
    """
    for event in answer_stream(subject, chat, query, image=image, history=history,
                               include_prompt=include_prompt, mode=mode):
        if event["type"] == "done":
            return {k: v for k, v in event.items() if k != "type"}
    return {"answer": "(No answer was generated.)", "citations": [], "trace": None,
            "query": query, "log_id": None, "request_id": None}
