"""One-off repair for tutors whose books were registered more than once.

Before upload became a replace, re-uploading a PDF appended a second registry
entry AND wrote a fresh set of chunks into Chroma with new node ids. The
node-id dedup in retrieval cannot see those, so the same page could occupy
several slots of the context budget.

This collapses each duplicated filename back to one registry entry and
re-ingests the file once, so the collection holds exactly one copy of its
chunks. The surviving title is the most recent one, i.e. what the UI already
displays — rename afterwards in the UI if you want the original back.

Dry run (default) prints the plan and changes nothing:

    python -m scripts.repair_duplicate_books

Apply it:

    python -m scripts.repair_duplicate_books --apply
"""
import sys
from collections import Counter

from backend import config, ingestion, store, tutors


def _duplicates(books: list[dict]) -> list[str]:
    counts = Counter(b["filename"] for b in books)
    return [f for f, n in counts.items() if n > 1]


def main(apply: bool) -> int:
    state = tutors._load()
    planned, skipped = 0, 0

    for tutor_id, tutor in state["tutors"].items():
        books = tutor.get("books", [])
        dupes = _duplicates(books)
        if not dupes:
            continue

        print(f"\n{tutor['name']}  ({tutor_id})")
        for filename in dupes:
            entries = [b for b in books if b["filename"] == filename]
            title = entries[-1]["title"]          # what the UI currently shows
            path = config.UPLOADS_DIR / tutor_id / filename

            titles = " / ".join(dict.fromkeys(b["title"] for b in entries))
            print(f"  {filename}")
            print(f"    registered {len(entries)}x as: {titles}")

            if not path.exists():
                print("    SKIP — file missing on disk, cannot re-ingest safely")
                skipped += 1
                continue

            print(f"    -> collapse to 1 entry titled {title!r}, re-ingest once")
            planned += 1
            if not apply:
                continue

            store.delete_book(tutor_id, filename)
            result = ingestion.ingest(path, tutor_id, title)
            tutors.upsert_book(tutor_id, {"filename": filename, "title": title, **result})
            print(f"    done — {result.get('pages')} pages, {result.get('chunks')} chunks")

    print()
    if not planned and not skipped:
        print("No duplicate books found. Nothing to do.")
    elif apply:
        print(f"Repaired {planned} book(s)." + (f" Skipped {skipped}." if skipped else ""))
    else:
        print(f"Dry run: {planned} book(s) would be repaired."
              + (f" {skipped} skipped." if skipped else ""))
        print("Re-run with --apply to make these changes.")
    return 0


if __name__ == "__main__":
    apply = "--apply" in sys.argv
    if apply:
        store.init_settings()
    raise SystemExit(main(apply))
