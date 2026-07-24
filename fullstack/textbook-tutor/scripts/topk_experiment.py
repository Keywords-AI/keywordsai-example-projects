"""Step 0 of the RAG roadmap: what does a bigger retrieval budget actually buy?

Sweeps TOP_K_PER_BOOK through several values and, for each, runs the REAL
production pipeline (`rag._retrieve`, including the coverage-first per-book merge
and the MAX_CONTEXT_CHUNKS cap) over one fixed, seeded question set. Reports both
halves of the trade-off the "improve your RAG" post insists on together:

    recall  (did the chunk the question came from reach the model?)
    cost    (how many chunks, and how many characters of context, that took)

Same synthetic questions across every setting, so the only variable is the knob.
Reuses the question generator and sampling from retrieval_benchmark, so a hit
here means the same thing as recall there.

    python -m scripts.topk_experiment --n 50 --seed 13
    python -m scripts.topk_experiment --ks 3,5,8,10 --out evals/topk_experiment.json
"""
import argparse
import json
import random
from datetime import datetime, timezone

from backend import config, rag, store, subjects
from scripts.retrieval_benchmark import _client, _eligible, _gen_question, _load_chunks, _norm


def _hit(gold: dict, nodes: list) -> bool:
    gold_norm = _norm(gold["text"])
    return any(n.node.node_id == gold["id"] or _norm(n.node.get_content()) == gold_norm
               for n in nodes)


def run(subject_name: str, n: int, seed: int, ks: list[int], model: str, min_chars: int) -> dict:
    store.init_settings()
    # list_subjects() returns stripped summaries (book_count, no books); the real
    # pipeline needs the full record, so resolve the id then fetch it in full.
    summary = next((s for s in subjects.list_subjects()
                    if s["name"].lower() == subject_name.lower()), None)
    subject = subjects.get(summary["id"]) if summary else None
    if not subject:
        raise SystemExit(f"no subject named {subject_name!r}")

    chunks = [c for c in _load_chunks(subject["id"]) if _eligible(c, min_chars)]
    rng = random.Random(seed)
    sample = rng.sample(chunks, min(n, len(chunks)))

    # Generate questions ONCE, shared across every top-k setting.
    client = _client()
    cases = []  # (gold_chunk, question)
    for i, gold in enumerate(sample, 1):
        q = _gen_question(client, model, gold["text"])
        if q:
            cases.append((gold, q))
    print(f"generated {len(cases)} questions ({len(sample) - len(cases)} skipped)\n")

    title_map = rag._title_map(subject)
    original_k = config.TOP_K_PER_BOOK
    rows = []
    try:
        for k in ks:
            config.TOP_K_PER_BOOK = k  # rag._retrieve reads this at call time
            hits, chunk_counts, ctx_chars = 0, [], []
            for gold, q in cases:
                nodes = rag._retrieve(subject, q)
                if _hit(gold, nodes):
                    hits += 1
                chunk_counts.append(len(nodes))
                ctx_chars.append(len(rag._format_context(nodes, title_map)))
            rows.append({
                "top_k_per_book": k,
                "recall": round(hits / len(cases), 4),
                "avg_chunks_to_model": round(sum(chunk_counts) / len(chunk_counts), 2),
                "avg_context_chars": round(sum(ctx_chars) / len(ctx_chars)),
                "approx_context_tokens": round(sum(ctx_chars) / len(ctx_chars) / 4),
            })
            print(f"  top_k={k:<2}  recall={rows[-1]['recall']:.2f}  "
                  f"chunks={rows[-1]['avg_chunks_to_model']:<5} "
                  f"~{rows[-1]['approx_context_tokens']} tok/query")
    finally:
        config.TOP_K_PER_BOOK = original_k

    base = next((r for r in rows if r["top_k_per_book"] == original_k), rows[0])
    for r in rows:
        r["recall_delta_vs_prod"] = round(r["recall"] - base["recall"], 4)
        r["context_x_vs_prod"] = round(r["avg_context_chars"] / base["avg_context_chars"], 2)

    return {
        "subject": subject_name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "question_model": model,
        "n_cases": len(cases),
        "seed": seed,
        "production_top_k": original_k,
        "max_context_chunks": config.MAX_CONTEXT_CHUNKS,
        "results": rows,
    }


def _print_table(res: dict) -> None:
    print("\n" + "=" * 74)
    print(f"TOP-K SWEEP  ·  {res['subject']}  ·  {res['n_cases']} questions  "
          f"(MAX_CONTEXT_CHUNKS={res['max_context_chunks']})")
    print("-" * 74)
    print(f"  {'top_k':>5} {'recall':>7} {'Δrecall':>8} {'chunks':>7} {'~tokens':>8} {'ctx×':>6}")
    for r in res["results"]:
        prod = "  <- production" if r["top_k_per_book"] == res["production_top_k"] else ""
        print(f"  {r['top_k_per_book']:>5} {r['recall']:>7.2f} {r['recall_delta_vs_prod']:>+8.2f} "
              f"{r['avg_chunks_to_model']:>7} {r['approx_context_tokens']:>8} {r['context_x_vs_prod']:>5}x{prod}")
    print("=" * 74)


def main() -> None:
    ap = argparse.ArgumentParser(description="Sweep TOP_K_PER_BOOK: recall vs context cost.")
    ap.add_argument("--subject", default="Linear Algebra")
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--seed", type=int, default=13)
    ap.add_argument("--ks", default="3,5,8,10", help="comma-separated top-k values")
    ap.add_argument("--model", default=config.REWRITE_MODEL)
    ap.add_argument("--min-chars", type=int, default=300)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    ks = [int(x) for x in args.ks.split(",")]
    res = run(args.subject, args.n, args.seed, ks, args.model, args.min_chars)
    _print_table(res)

    if args.out:
        from pathlib import Path
        p = Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(res, indent=2))
        print(f"\nwrote {p}")


if __name__ == "__main__":
    main()
