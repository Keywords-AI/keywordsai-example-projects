"""RAG roadmap step 2: does hybrid (vector + BM25) retrieve better than vector alone?

Generates one fixed set of hard, chunk-specific questions (same generator as the
recall benchmark), then scores retrieval recall/MRR TWICE over that same set:
once vector-only, once hybrid (RRF of vector + BM25). Questions are held fixed
across both, so the only variable is the retrieval method.

Reports recall@k for both, MRR, and, most usefully, the per-question movement:
how many chunks hybrid rescued (miss -> hit) versus regressed (hit -> miss).

    python -m scripts.hybrid_experiment --n 60 --seed 13
    python -m scripts.hybrid_experiment --out evals/hybrid_experiment.json
"""
import argparse
import json
import random
from datetime import datetime, timezone

from backend import config, rag, store, subjects
from scripts.retrieval_benchmark import _client, _eligible, _gen_question, _load_chunks, _rank_of

KS = [1, 3, 5, 8, 10, 20]


def _measure(subject: dict, cases: list, max_k: int) -> dict:
    ranks = []
    for gold, q in cases:
        hits = rag.ranked_candidates(subject, q, max_k)
        ranks.append(_rank_of(gold, hits))
    n = len(ranks)
    recall = {k: sum(1 for r in ranks if r is not None and r <= k) / n for k in KS}
    mrr = sum((1.0 / r) for r in ranks if r is not None) / n
    return {"ranks": ranks, "recall_at_k": recall, "mrr": round(mrr, 4)}


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
    cases = []
    for gold in sample:
        q = _gen_question(client, model, gold["text"])
        if q:
            cases.append((gold, q))
    print(f"generated {len(cases)} questions ({len(sample) - len(cases)} skipped)\n")

    max_k = max(KS)
    original = config.HYBRID_SEARCH
    try:
        config.HYBRID_SEARCH = False
        vector = _measure(subject, cases, max_k)
        config.HYBRID_SEARCH = True
        hybrid = _measure(subject, cases, max_k)
    finally:
        config.HYBRID_SEARCH = original

    # Per-question movement at the production budget (recall that reaches the model).
    pk = config.TOP_K_PER_BOOK
    rescued, regressed = [], []
    for (gold, q), rv, rh in zip(cases, vector["ranks"], hybrid["ranks"]):
        in_v = rv is not None and rv <= pk
        in_h = rh is not None and rh <= pk
        if in_h and not in_v:
            rescued.append({"page": gold["meta"].get("page"), "q": q, "v_rank": rv, "h_rank": rh})
        elif in_v and not in_h:
            regressed.append({"page": gold["meta"].get("page"), "q": q, "v_rank": rv, "h_rank": rh})

    return {
        "subject": subject_name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "n_cases": len(cases),
        "seed": seed,
        "production_k": pk,
        "rrf_k": config.RRF_K,
        "hybrid_candidates": config.HYBRID_CANDIDATES,
        "vector": {"recall_at_k": vector["recall_at_k"], "mrr": vector["mrr"]},
        "hybrid": {"recall_at_k": hybrid["recall_at_k"], "mrr": hybrid["mrr"]},
        "rescued_at_prod_k": rescued,
        "regressed_at_prod_k": regressed,
    }


def _print(res: dict) -> None:
    pk = res["production_k"]
    print("\n" + "=" * 66)
    print(f"HYBRID vs VECTOR  ·  {res['subject']}  ·  {res['n_cases']} questions  "
          f"(RRF_K={res['rrf_k']}, pool={res['hybrid_candidates']})")
    print("-" * 66)
    print(f"  {'k':>4} {'vector':>9} {'hybrid':>9} {'Δ':>8}")
    for k in KS:
        v, h = res["vector"]["recall_at_k"][k], res["hybrid"]["recall_at_k"][k]
        star = "  <- production" if k == pk else ""
        print(f"  {k:>4} {v:>9.2f} {h:>9.2f} {h - v:>+8.2f}{star}")
    print(f"  {'MRR':>4} {res['vector']['mrr']:>9.3f} {res['hybrid']['mrr']:>9.3f} "
          f"{res['hybrid']['mrr'] - res['vector']['mrr']:>+8.3f}")
    print("-" * 66)
    print(f"  at production k={pk}: rescued {len(res['rescued_at_prod_k'])}, "
          f"regressed {len(res['regressed_at_prod_k'])}")
    for r in res["rescued_at_prod_k"][:6]:
        print(f"    + p.{r['page']}  vec#{r['v_rank']}->hyb#{r['h_rank']}  {r['q'][:52]}")
    for r in res["regressed_at_prod_k"][:6]:
        print(f"    - p.{r['page']}  vec#{r['v_rank']}->hyb#{r['h_rank']}  {r['q'][:52]}")
    print("=" * 66)


def main() -> None:
    ap = argparse.ArgumentParser(description="Hybrid vs vector retrieval recall.")
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
