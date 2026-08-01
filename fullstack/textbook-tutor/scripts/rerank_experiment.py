"""RAG roadmap step 3: does a cross-encoder reranker order retrieval better?

Same design as hybrid_experiment: one fixed set of hard, chunk-specific questions,
scored twice, vector-only then vector+rerank, questions held constant so the only
variable is the reranker.

A reranker only REORDERS the retrieved pool (RERANK_CANDIDATES); it cannot add a
chunk vector search never fetched. So its ceiling is vector's recall at the pool
size, and its job is to lift recall@1..k toward that ceiling. Watch recall@8
(production) move toward recall@20, and MRR rise.

    python -m scripts.rerank_experiment --n 60 --seed 13
    python -m scripts.rerank_experiment --out evals/rerank_experiment.json
"""
import argparse
import json
import random
from datetime import datetime, timezone

from backend import config, rag, store, subjects
from scripts.retrieval_benchmark import _client, _eligible, _gen_question, _load_chunks, _rank_of

KS = [1, 3, 5, 8, 10, 20]


def _measure(subject: dict, cases: list, max_k: int) -> dict:
    ranks = [_rank_of(gold, rag.ranked_candidates(subject, q, max_k)) for gold, q in cases]
    n = len(ranks)
    return {
        "ranks": ranks,
        "recall_at_k": {k: sum(1 for r in ranks if r is not None and r <= k) / n for k in KS},
        "mrr": round(sum((1.0 / r) for r in ranks if r is not None) / n, 4),
    }


def run(subject_name: str, n: int, seed: int, model: str, min_chars: int) -> dict:
    store.init_settings()
    summary = next((s for s in subjects.list_subjects()
                    if s["name"].lower() == subject_name.lower()), None)
    subject = subjects.get(summary["id"]) if summary else None
    if not subject:
        raise SystemExit(f"no subject named {subject_name!r}")

    chunks = [c for c in _load_chunks(subject["id"]) if _eligible(c, min_chars)]
    rng = random.Random(seed)
    sample = rng.sample(chunks, min(n, len(chunks)))

    client = _client()
    cases = [(g, q) for g in sample if (q := _gen_question(client, model, g["text"]))]
    print(f"generated {len(cases)} questions ({len(sample) - len(cases)} skipped)\n")

    max_k = max(KS)
    orig_rerank, orig_hybrid = config.RERANK, config.HYBRID_SEARCH
    try:
        config.HYBRID_SEARCH = False  # isolate the reranker on top of pure vector
        config.RERANK = False
        vector = _measure(subject, cases, max_k)
        config.RERANK = True
        reranked = _measure(subject, cases, max_k)
    finally:
        config.RERANK, config.HYBRID_SEARCH = orig_rerank, orig_hybrid

    pk = config.TOP_K_PER_BOOK
    rescued, regressed = [], []
    for (gold, q), rv, rr in zip(cases, vector["ranks"], reranked["ranks"]):
        in_v = rv is not None and rv <= pk
        in_r = rr is not None and rr <= pk
        if in_r and not in_v:
            rescued.append({"page": gold["meta"].get("page"), "q": q, "v_rank": rv, "r_rank": rr})
        elif in_v and not in_r:
            regressed.append({"page": gold["meta"].get("page"), "q": q, "v_rank": rv, "r_rank": rr})

    return {
        "subject": subject_name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "n_cases": len(cases),
        "seed": seed,
        "production_k": pk,
        "rerank_model": config.RERANK_MODEL,
        "rerank_candidates": config.RERANK_CANDIDATES,
        "vector": {"recall_at_k": vector["recall_at_k"], "mrr": vector["mrr"]},
        "reranked": {"recall_at_k": reranked["recall_at_k"], "mrr": reranked["mrr"]},
        "rescued_at_prod_k": rescued,
        "regressed_at_prod_k": regressed,
    }


def _print(res: dict) -> None:
    pk = res["production_k"]
    print("\n" + "=" * 66)
    print(f"RERANK vs VECTOR  ·  {res['subject']}  ·  {res['n_cases']} questions")
    print(f"  model: {res['rerank_model']}  pool: {res['rerank_candidates']}")
    print("-" * 66)
    print(f"  {'k':>4} {'vector':>9} {'rerank':>9} {'Δ':>8}")
    for k in KS:
        v, r = res["vector"]["recall_at_k"][k], res["reranked"]["recall_at_k"][k]
        star = "  <- production" if k == pk else ""
        print(f"  {k:>4} {v:>9.2f} {r:>9.2f} {r - v:>+8.2f}{star}")
    print(f"  {'MRR':>4} {res['vector']['mrr']:>9.3f} {res['reranked']['mrr']:>9.3f} "
          f"{res['reranked']['mrr'] - res['vector']['mrr']:>+8.3f}")
    print("-" * 66)
    print(f"  at production k={pk}: rescued {len(res['rescued_at_prod_k'])}, "
          f"regressed {len(res['regressed_at_prod_k'])}")
    for r in res["rescued_at_prod_k"][:6]:
        print(f"    + p.{r['page']}  vec#{r['v_rank']}->rr#{r['r_rank']}  {r['q'][:52]}")
    for r in res["regressed_at_prod_k"][:6]:
        print(f"    - p.{r['page']}  vec#{r['v_rank']}->rr#{r['r_rank']}  {r['q'][:52]}")
    print("=" * 66)


def main() -> None:
    ap = argparse.ArgumentParser(description="Cross-encoder rerank vs vector retrieval.")
    ap.add_argument("--subject", default="Linear Algebra")
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--seed", type=int, default=13)
    ap.add_argument("--model", default=config.REWRITE_MODEL)
    ap.add_argument("--min-chars", type=int, default=300)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    res = run(args.subject, args.n, args.seed, args.model, args.min_chars)
    _print(res)
    if args.out:
        from pathlib import Path
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(res, indent=2))
        print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
