"""Synthetic retrieval-recall benchmark: the number the rest of RAG is judged by.

The generation graders (groundedness, citation validity) can score ~1.0 while
retrieval quietly hands the model the wrong pages. This measures retrieval on its
own terms, the way jxnl's "systematic RAG improvement" post says to do it first:

    for a sample of real chunks in a subject's index:
        ask a cheap model to write a question that chunk answers
        run that question through retrieval
        did the chunk it came from come back, and at what rank?

From the ranks we get recall@k and MRR. Because the query was written FROM a
known chunk, "the right answer" is unambiguous: it is that chunk. This is the
one retrieval metric with a ground truth, so it is the one to move when you add
hybrid search, a reranker, or change chunking, and re-run.

    python -m scripts.retrieval_benchmark                       # default subject, 40 questions
    python -m scripts.retrieval_benchmark --subject "Linear Algebra" --n 60 --seed 7
    python -m scripts.retrieval_benchmark --n 40 --out evals/retrieval_baseline.json

Retrieval runs against the WHOLE subject collection (no per-book filter), so this
measures raw findability of a chunk. The production pipeline (`rag._retrieve`)
additionally caps at TOP_K_PER_BOOK per book, so recall@TOP_K_PER_BOOK below is
the number that reflects what actually reaches the model today; it is called out
separately in the summary.
"""
import argparse
import json
import random
from datetime import datetime, timezone

import anthropic
import chromadb

from backend import config, rag, store, subjects

# k values the recall curve is reported at. TOP_K_PER_BOOK is inserted so the
# production setting always appears even if it isn't in this list.
DEFAULT_KS = [1, 3, 5, 10, 20]

_QUESTION_PROMPT = (
    "Below is one excerpt from a textbook. Write ONE specific question a student "
    "would plausibly ask whose answer is contained in this excerpt. Requirements:\n"
    "- Answerable from THIS excerpt alone.\n"
    "- Use a student's words; do NOT quote the excerpt verbatim or name a page/figure number.\n"
    "- One question, no preamble.\n"
    "If the excerpt is front-matter, a table of contents, a bare heading, or has no "
    "substantive content to ask about, reply with exactly: SKIP\n\n"
    "Excerpt:\n\"\"\"\n{chunk}\n\"\"\""
)


def _client() -> anthropic.Anthropic:
    if config.USE_GATEWAY:
        return anthropic.Anthropic(api_key=config.RESPAN_API_KEY, base_url=config.RESPAN_GATEWAY_URL)
    return anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)


def _norm(text: str) -> str:
    return " ".join((text or "").split())


def _gen_question(client: anthropic.Anthropic, model: str, chunk_text: str) -> str | None:
    kwargs = dict(
        model=model,
        max_tokens=120,
        messages=[{"role": "user", "content": _QUESTION_PROMPT.format(chunk=chunk_text[:2400])}],
    )
    if config.USE_GATEWAY:
        kwargs["metadata"] = {"respan_params": {"metadata": {"app": "textbook-tutor", "kind": "benchmark-question"}}}
    resp = client.messages.create(**kwargs)
    q = "".join(b.text for b in resp.content if b.type == "text").strip()
    return None if not q or q.strip().upper() == "SKIP" else q


def _load_chunks(subject_id: str) -> list[dict]:
    col = chromadb.PersistentClient(path=str(config.CHROMA_DIR)).get_collection(
        store.collection_name(subject_id)
    )
    got = col.get(include=["documents", "metadatas"])
    return [
        {"id": cid, "text": doc, "meta": meta or {}}
        for cid, doc, meta in zip(got["ids"], got["documents"], got["metadatas"])
    ]


def _eligible(chunk: dict, min_chars: int) -> bool:
    """Skip captions, front-matter and stubs: things that make degenerate questions."""
    meta = chunk["meta"]
    if meta.get("content_type") != "text":
        return False
    if len(_norm(chunk["text"])) < min_chars:
        return False
    page = meta.get("page")
    # Front matter (roman-numeral or non-numeric pages) rarely holds a real concept.
    return isinstance(page, int) or (isinstance(page, str) and page.isdigit())


def _rank_of(gold: dict, hits: list) -> int | None:
    """1-based rank of the gold chunk in hits, matched by node_id then by text."""
    gold_norm = _norm(gold["text"])
    for i, h in enumerate(hits, 1):
        if h.node.node_id == gold["id"] or _norm(h.node.get_content()) == gold_norm:
            return i
    return None


def run(subject_name: str, n: int, seed: int, ks: list[int], model: str, min_chars: int) -> dict:
    store.init_settings()

    # Full record (list_subjects strips books) so retrieval can run per book.
    summary = next((s for s in subjects.list_subjects()
                    if s["name"].lower() == subject_name.lower()), None)
    subject = subjects.get(summary["id"]) if summary else None
    if not subject:
        raise SystemExit(f"no subject named {subject_name!r}. have: "
                         f"{[s['name'] for s in subjects.list_subjects()]}")
    subject_id = subject["id"]

    chunks = [c for c in _load_chunks(subject_id) if _eligible(c, min_chars)]
    if not chunks:
        raise SystemExit(f"subject {subject_name!r} has no eligible text chunks to sample")
    rng = random.Random(seed)
    sample = rng.sample(chunks, min(n, len(chunks)))

    max_k = max(ks)
    client = _client()

    ranks: list[int | None] = []
    records, skipped = [], 0
    for i, gold in enumerate(sample, 1):
        q = _gen_question(client, model, gold["text"])
        if q is None:
            skipped += 1
            continue
        # Retrieve through the real seam so HYBRID_SEARCH is reflected here.
        hits = rag.ranked_candidates(subject, q, max_k)
        rank = _rank_of(gold, hits)
        ranks.append(rank)
        records.append({"question": q, "gold_page": gold["meta"].get("page"), "rank": rank})
        mark = f"rank {rank}" if rank else f"MISS (not in top {max_k})"
        print(f"[{i}/{len(sample)}] p.{gold['meta'].get('page')}: {mark}  {q[:70]}")

    graded = [r for r in ranks]  # includes None (miss)
    n_graded = len(graded)
    recall = {k: sum(1 for r in graded if r is not None and r <= k) / n_graded for k in ks} if n_graded else {}
    mrr = (sum((1.0 / r) for r in graded if r is not None) / n_graded) if n_graded else 0.0
    found = [r for r in graded if r is not None]

    return {
        "subject": subject_name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "question_model": model,
        "config": {
            "TOP_K_PER_BOOK": config.TOP_K_PER_BOOK,
            "MAX_CONTEXT_CHUNKS": config.MAX_CONTEXT_CHUNKS,
            "CHUNK_SIZE": config.CHUNK_SIZE,
            "CHUNK_OVERLAP": config.CHUNK_OVERLAP,
            "EMBED_MODEL": config.EMBED_MODEL,
            "LLAMAPARSE": bool(config.LLAMA_CLOUD_API_KEY),
            "HYBRID_SEARCH": config.HYBRID_SEARCH,
            "RRF_K": config.RRF_K,
            "HYBRID_CANDIDATES": config.HYBRID_CANDIDATES,
        },
        "n_requested": n,
        "n_graded": n_graded,
        "n_skipped": skipped,
        "eligible_chunks": len(chunks),
        "recall_at_k": recall,
        "production_k": config.TOP_K_PER_BOOK,
        "recall_at_production_k": recall.get(config.TOP_K_PER_BOOK),
        "mrr": round(mrr, 4),
        "median_rank_when_found": (sorted(found)[len(found) // 2] if found else None),
        "misses": [r for r in records if r["rank"] is None],
        "records": records,
    }


def _print_summary(res: dict) -> None:
    print("\n" + "=" * 60)
    print(f"RETRIEVAL RECALL  ·  {res['subject']}")
    print(f"  parser: {'LlamaParse' if res['config']['LLAMAPARSE'] else 'built-in'} | "
          f"embed: {res['config']['EMBED_MODEL']} | chunk: {res['config']['CHUNK_SIZE']}/{res['config']['CHUNK_OVERLAP']}")
    print(f"  retrieval: {'HYBRID (vector + BM25, RRF)' if res['config']['HYBRID_SEARCH'] else 'vector only'}")
    print(f"  graded {res['n_graded']} questions ({res['n_skipped']} skipped) "
          f"from {res['eligible_chunks']} eligible chunks")
    print("-" * 60)
    for k, v in sorted(res["recall_at_k"].items()):
        star = "   <- production (TOP_K_PER_BOOK)" if k == res["production_k"] else ""
        print(f"  recall@{k:<3} {v:.2f}{star}")
    print(f"  MRR        {res['mrr']:.3f}")
    print(f"  median rank when found: {res['median_rank_when_found']}")
    print(f"  misses: {len(res['misses'])}/{res['n_graded']}")
    print("=" * 60)


def main() -> None:
    ap = argparse.ArgumentParser(description="Synthetic retrieval-recall benchmark.")
    ap.add_argument("--subject", default="Linear Algebra")
    ap.add_argument("--n", type=int, default=40, help="questions to generate/grade")
    ap.add_argument("--seed", type=int, default=13, help="sampling seed (reproducible runs)")
    ap.add_argument("--model", default=config.REWRITE_MODEL, help="model that writes the questions")
    ap.add_argument("--min-chars", type=int, default=300, help="skip chunks shorter than this")
    ap.add_argument("--out", default=None, help="write full JSON result here (for diffing runs)")
    args = ap.parse_args()

    ks = sorted(set(DEFAULT_KS) | {config.TOP_K_PER_BOOK})
    res = run(args.subject, args.n, args.seed, ks, args.model, args.min_chars)
    _print_summary(res)

    if args.out:
        from pathlib import Path
        p = Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(res, indent=2))
        print(f"\nwrote {p}")


if __name__ == "__main__":
    main()
