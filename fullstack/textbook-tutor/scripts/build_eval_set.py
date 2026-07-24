"""Generate HARD, verified eval questions grounded in a subject's own chunks.

The hand-written question set is too easy to register retrieval changes: most
questions are generic definitions the book covers redundantly, so `top_k=3` and
`top_k=8` score the same. This builds discriminating questions the way the
"improve your RAG" post prescribes synthetic data, but with a quality gate so the
survivors are durable enough to live in evals/questions.json:

  sample a real chunk
    -> a capable model writes a question SPECIFIC to that passage
    -> a second model verifies it is answerable from that passage alone AND not
       answerable from generic knowledge (the difficulty gate)
    -> confirm the source chunk is actually retrievable (a fair, answerable Q)
    -> keep it, tagged with its gold page and the rank retrieval gave the chunk

Output is candidates for review, written to --out. Curate into questions.json by
hand; the gold_page comes from LlamaParse's numeric page metadata, so it is
trustworthy, but the phrasing still deserves a human read.

    python -m scripts.build_eval_set --subject "Linear Algebra" --target 14 --out evals/hard_candidates.json
"""
import argparse
import json
import random
from datetime import datetime, timezone

from backend import config, rag, store, subjects
from scripts.retrieval_benchmark import _client, _eligible, _gen_question, _load_chunks, _rank_of

_WRITE_PROMPT = (
    "You are setting a hard exam question from ONE excerpt of a textbook. Write a "
    "single question that:\n"
    "- can be answered ONLY using the specific content of this excerpt (a particular "
    "theorem, example, condition, or step), not a generic definition;\n"
    "- a student could NOT answer from general knowledge without this passage;\n"
    "- is phrased naturally, as a student would ask it, and names no page/figure number.\n"
    "One question, no preamble. If the excerpt is too thin to support one, reply SKIP.\n\n"
    "Excerpt:\n\"\"\"\n{chunk}\n\"\"\""
)

_VERIFY_PROMPT = (
    "Excerpt:\n\"\"\"\n{chunk}\n\"\"\"\n\n"
    "Candidate question: {question}\n\n"
    "Judge the question against the excerpt. Reply with ONLY a JSON object:\n"
    '{{"answerable_from_excerpt": bool, "specific_to_this_passage": bool, '
    '"answerable_from_generic_knowledge": bool, "difficulty": "easy|medium|hard", '
    '"reason": "one short clause"}}\n'
    "Keep in mind: a good discriminating question is answerable from the excerpt, "
    "specific to it, and NOT answerable from generic knowledge."
)


def _verify(client, model, chunk_text: str, question: str) -> dict | None:
    resp = client.messages.create(
        model=model, max_tokens=250,
        messages=[{"role": "user", "content": _VERIFY_PROMPT.format(chunk=chunk_text[:2400], question=question)}],
    )
    raw = "".join(b.text for b in resp.content if b.type == "text").strip()
    start, end = raw.find("{"), raw.rfind("}")
    if start < 0 or end < 0:
        return None
    try:
        return json.loads(raw[start:end + 1])
    except json.JSONDecodeError:
        return None


def _keep(v: dict) -> bool:
    return bool(
        v.get("answerable_from_excerpt")
        and v.get("specific_to_this_passage")
        and not v.get("answerable_from_generic_knowledge")
        and v.get("difficulty") in ("medium", "hard")
    )


def run(subject_name: str, target: int, seed: int, gen_model: str, verify_model: str,
        min_chars: int, retrievable_within: int) -> dict:
    store.init_settings()
    summary = next((s for s in subjects.list_subjects()
                    if s["name"].lower() == subject_name.lower()), None)
    subject = subjects.get(summary["id"]) if summary else None
    if not subject:
        raise SystemExit(f"no subject named {subject_name!r}")

    chunks = [c for c in _load_chunks(subject["id"]) if _eligible(c, min_chars)]
    rng = random.Random(seed)
    rng.shuffle(chunks)
    client = _client()

    kept, seen_pages = [], set()
    examined = 0
    for gold in chunks:
        if len(kept) >= target:
            break
        page = gold["meta"].get("page")
        if page in seen_pages:                     # one question per page, for spread
            continue
        examined += 1
        q = _gen_question(client, gen_model, gold["text"])
        if not q:
            continue
        verdict = _verify(client, verify_model, gold["text"], q)
        if not verdict or not _keep(verdict):
            continue
        # Fair question = the book can actually surface the answer.
        rank = _rank_of(gold, rag.ranked_candidates(subject, q, retrievable_within))
        if rank is None:
            continue
        seen_pages.add(page)
        kept.append({
            "subject": subject_name, "kind": "answerable", "question": q,
            "gold_page": page, "difficulty": verdict["difficulty"], "gold_rank": rank,
        })
        print(f"  kept {len(kept)}/{target}  p.{page} [{verdict['difficulty']}] rank {rank}: {q[:64]}")

    print(f"\nexamined {examined} chunks, kept {len(kept)}")
    return {
        "subject": subject_name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "gen_model": gen_model, "verify_model": verify_model,
        "candidates": kept,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Build hard, verified eval questions.")
    ap.add_argument("--subject", default="Linear Algebra")
    ap.add_argument("--target", type=int, default=14)
    ap.add_argument("--seed", type=int, default=21)
    ap.add_argument("--gen-model", default="claude-sonnet-5")
    ap.add_argument("--verify-model", default="claude-sonnet-5")
    ap.add_argument("--min-chars", type=int, default=350)
    ap.add_argument("--retrievable-within", type=int, default=12,
                    help="gold chunk must appear in the top-N to count as answerable")
    ap.add_argument("--out", default="evals/hard_candidates.json")
    args = ap.parse_args()

    res = run(args.subject, args.target, args.seed, args.gen_model, args.verify_model,
              args.min_chars, args.retrievable_within)
    from pathlib import Path
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(res, indent=2))
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
