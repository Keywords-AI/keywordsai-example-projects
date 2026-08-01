"""Re-ingest one book through the real replace flow (drop old chunks -> parse ->
caption -> chunk -> index -> update registry). Same steps as the upload_book
endpoint, but runnable from the CLI so a parser change (e.g. turning LlamaParse
on) can be applied to a book already in a subject without clicking through the UI.

    python -m scripts.reingest_book <subject_id> <filename>
"""
import sys
import time

from backend import config, ingestion, store, subjects


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit("usage: python -m scripts.reingest_book <subject_id> <filename>")
    subject_id, filename = sys.argv[1], sys.argv[2]

    subject = subjects.get(subject_id) if hasattr(subjects, "get") else None
    path = config.UPLOADS_DIR / subject_id / filename
    if not path.is_file():
        sys.exit(f"no such upload: {path}")

    # Keep the existing citation title.
    books = (subject or {}).get("books", []) if subject else []
    prior = next((b for b in books if b["filename"] == filename), None)
    title = (prior or {}).get("title") or path.stem

    # Same one-time setup the app does at startup: pins the local bge-small
    # embedder. Skipping it lets LlamaIndex fall back to a default OpenAI
    # embedding model that isn't installed, which fails at index time.
    store.init_settings()

    print(f"parser: {'LlamaParse' if config.LLAMA_CLOUD_API_KEY else 'built-in SimpleDirectoryReader'}")
    print(f"re-ingesting {filename!r} (title={title!r}) into subject {subject_id} ...")

    if prior:
        store.delete_book(subject_id, filename)
        print("dropped old chunks")

    t0 = time.time()
    result = ingestion.ingest(path, subject_id, title)
    subjects.upsert_book(subject_id, {"filename": filename, "title": title, **result})
    print(f"done in {time.time() - t0:.1f}s: {result}")


if __name__ == "__main__":
    main()
