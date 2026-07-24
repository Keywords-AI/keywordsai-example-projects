"""Grade the tutor by running an **experiment** on Respan.

The app does not score its own answers. A score for one live answer, computed in
a browser and stored nowhere, is a number with nothing to compare it to. An
experiment is the opposite: the same fixed question set, the same graders, run
again after every change, so "did that help?" has an answer.

What it does:

  1. Runs the real RAG pipeline over `evals/questions.json` — the same retrieval
     and the same prompt the app uses, so the graders read what a student would.
  2. Uploads each {input, output} pair as a row in a Respan dataset.
  3. Creates an experiment over that dataset with a `duplicate` (passthrough)
     workflow — generation already happened locally, so the experiment only
     grades — and the five deployed evaluation pipelines attached.
  4. Waits for it to finish and prints where to read the scores.

Passthrough matters: retrieval runs against local Chroma, so Respan cannot
reproduce an answer from a prompt id. We generate here, then hand over the
finished input/output.

Run from the project root:

    python -m scripts.run_experiment                    # every question
    python -m scripts.run_experiment --subject "Linear Algebra"
    python -m scripts.run_experiment --name "top-k 8"   # label the run
    python -m scripts.run_experiment --dry-run          # generate, upload nothing
"""
import argparse
import json
import sys
import time

from backend import config, experiments, rag, store, subjects

QUESTIONS_FILE = config.BASE_DIR / "evals" / "questions.json"


# --- generating the rows -----------------------------------------------------

def load_questions(subject_filter: str | None) -> list[dict]:
    if not QUESTIONS_FILE.exists():
        sys.exit(f"No question set at {QUESTIONS_FILE}")
    items = json.loads(QUESTIONS_FILE.read_text())["questions"]
    if subject_filter:
        items = [q for q in items if q["subject"].lower() == subject_filter.lower()]
    return items


def _subject_by_name(name: str) -> dict | None:
    for s in subjects.list_subjects():
        if s["name"].lower() == name.lower():
            return subjects.get(s["id"])
    return None


def generate(items: list[dict]) -> tuple[list[dict], list[str]]:
    """Answer each question with the real pipeline. Returns (rows, skipped)."""
    rows, skipped, missing = [], [], set()
    # A throwaway chat with no style and the default model: an experiment should
    # measure the pipeline, not one chat's teaching style.
    chat = {"id": "experiment", "instructions": "", "model": None}

    for i, q in enumerate(items, 1):
        subject = _subject_by_name(q["subject"])
        if subject is None:
            missing.add(q["subject"])
            skipped.append(f'{q["subject"]}: {q["question"]}')
            continue
        print(f"  [{i}/{len(items)}] {q['subject']} · {q['question'][:58]}")
        result = rag.answer(subject, chat, q["question"], include_prompt=True,
                            mode=q.get("mode", "qa"))
        prompt = (result.get("trace") or {}).get("prompt")
        if not prompt:
            # No trace means an early exit — no books, or nothing retrieved.
            skipped.append(f'{q["subject"]}: {q["question"]} ({result["answer"][:60]})')
            continue
        rows.append({
            "input": prompt,
            "output": result["answer"],
            "metadata": {"subject": q["subject"], "kind": q.get("kind", ""),
                         "mode": q.get("mode", "qa"), "difficulty": q.get("difficulty", ""),
                         "question": q["question"], "log_id": result.get("log_id") or ""},
        })
    for name in sorted(missing):
        print(f"  ! no subject named {name!r} on this machine — its questions were skipped")
    return rows, skipped


# --- main --------------------------------------------------------------------

# --- per-slice reporting -----------------------------------------------------

# Short column headers for the slice table, in a fixed order. Retrieval graders
# first, since the slice exists mainly to read them: an easy question pins them
# to the ceiling, a hard one does not.
_GRADER_SHORT = [
    ("RAG · context relevance", "ctx-rel"),
    ("RAG · context completeness", "ctx-cmp"),
    ("RAG · context utilization", "ctx-use"),
    ("RAG · groundedness", "ground"),
    ("RAG · citation validity", "cite"),
]

# Order slices weak-to-strong-ish so the table reads top to bottom like the mix.
_SLICE_ORDER = ["answerable/easy", "answerable/medium", "answerable/hard",
                "answerable/plain", "partial", "out-of-corpus", "lecture"]


def _slice_label(meta: dict) -> str:
    """Bucket a question: lecture mode, else kind, with difficulty on answerable."""
    if meta.get("mode") == "lecture":
        return "lecture"
    kind = meta.get("kind") or "?"
    if kind == "answerable":
        return f"answerable/{meta.get('difficulty') or 'plain'}"
    return kind


def _print_by_slice(found: list[dict], rows: list[dict]) -> None:
    # Join a graded span back to its question. The dataset input IS the row input,
    # so it's an exact key; fall back to finding the question text in the span.
    by_input = {r["input"]: r["metadata"] for r in rows}

    def meta_for(span):
        m = by_input.get(span.get("input") or "")
        if m:
            return m
        blob = (span.get("input") or "") + " " + (span.get("output") or "")
        return next((r["metadata"] for r in rows if r["metadata"]["question"] in blob), None)

    grouped = experiments.averages_by(found, meta_for, _slice_label)
    if not grouped:
        return

    present = [(name, short) for name, short in _GRADER_SHORT if name in grouped]
    present += [(n, n[:7]) for n in grouped if n not in dict(_GRADER_SHORT)]  # any extras
    slices = [s for s in _SLICE_ORDER if any(s in grouped[n] for n, _ in present)]
    slices += sorted({s for n, _ in present for s in grouped[n]} - set(_SLICE_ORDER))

    def n_in(slice_):
        return max((len(grouped[n].get(slice_, [])) for n, _ in present), default=0)

    print("\n  by slice (avg | n):")
    header = "    " + f"{'slice':<18}{'n':>4}  " + "".join(f"{short:>9}" for _, short in present)
    print(header)
    for s in slices:
        cells = ""
        for name, _ in present:
            vals = grouped[name].get(s, [])
            cells += f"{(sum(vals)/len(vals)):>9.2f}" if vals else f"{'—':>9}"
        print(f"    {s:<18}{n_in(s):>4}  {cells}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--subject", help="only questions for this subject")
    ap.add_argument("--name", default="", help="label for this run, e.g. 'top-k 8'")
    ap.add_argument("--dry-run", action="store_true",
                    help="generate answers and print them; upload nothing")
    args = ap.parse_args(argv)

    if not args.dry_run and not config.EXPERIMENTS_CONFIGURED:
        print("Not configured. Needs RESPAN_API_KEY and the five EVAL_PIPELINE_* ids "
              "in .env — run /setup-respan to provision them.", file=sys.stderr)
        return 1

    items = load_questions(args.subject)
    if not items:
        print("No questions matched.", file=sys.stderr)
        return 1

    # The app does this at startup; a script has to do it for itself or the
    # embedding model falls back to OpenAI's and retrieval fails on import.
    store.init_settings()

    print(f"Answering {len(items)} question(s) with the real pipeline…")
    rows, skipped = generate(items)
    for s in skipped:
        print(f"  skipped: {s}")
    if not rows:
        print("Nothing to grade.", file=sys.stderr)
        return 1
    print(f"{len(rows)} answer(s) ready.")

    if args.dry_run:
        for r in rows:
            print(f"\n--- {r['metadata']['question']}\n{r['output'][:400]}")
        return 0

    # Stamped by the caller, not the script: a run is identified by what changed.
    label = args.name or time.strftime("%Y-%m-%d %H:%M")
    name = f"textbook-tutor · {label}"

    print(f"Uploading {len(rows)} row(s)…")
    description = f"RAG regression set, {len(rows)} answers from the real pipeline."
    dataset_id = experiments.create_dataset(name, description)
    landed = experiments.add_rows(dataset_id, rows)
    if landed < len(rows):
        print(f"  ! only {landed}/{len(rows)} rows landed — grading what did",
              file=sys.stderr)

    pipelines = experiments.pipeline_versions(list(config.EVAL_PIPELINE_IDS.values()))
    if not pipelines:
        print("No evaluator pipelines resolved — check EVAL_PIPELINE_* in .env",
              file=sys.stderr)
        return 1
    print(f"Grading with {len(pipelines)} graders, one experiment each…")
    # One per experiment, never bundled: see experiments.grade_dataset.
    found, experiment_ids = experiments.grade_dataset(
        name, description, dataset_id, len(rows), pipelines,
        on_progress=lambda m: print(f"  {m}"))

    averages = experiments.averages(found)
    if averages:
        print()
        for evaluator in sorted(averages):
            vals = averages[evaluator]
            print(f"  {evaluator:32} {sum(vals)/len(vals):.2f}   (n={len(vals)}, "
                  f"min {min(vals):.2f}, max {max(vals):.2f})")
        _print_by_slice(found, rows)
    else:
        print("\nNo scores came back.", file=sys.stderr)
    print(f"\ndataset     {dataset_id}")
    for eid in experiment_ids:
        print(f"experiment  {eid}")
    return 0 if averages else 1


if __name__ == "__main__":
    raise SystemExit(main())
