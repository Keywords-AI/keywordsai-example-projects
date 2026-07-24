"""One-off migration: tutors → subjects + chats.

The old model had one object doing three jobs — a corpus, a persona and a single
conversation. This splits it: a **subject** owns the books, and **chats** hold
the conversations, so many chats can share one subject.

Each tutor becomes one subject plus one chat containing its existing history and
inheriting its teaching style.

The subject keeps the tutor's id, deliberately: `storage/uploads/{id}/` and the
Chroma collection `tutor_{id}` are both keyed by it, so nothing moves on disk and
**nothing is re-embedded**.

Run from the project root:

    python -m scripts.migrate_to_subjects            # dry run, shows the plan
    python -m scripts.migrate_to_subjects --apply
"""
import json
import sys

from backend import chats, config, subjects


def _legacy() -> dict:
    if not config.LEGACY_TUTORS_FILE.exists():
        return {}
    return json.loads(config.LEGACY_TUTORS_FILE.read_text()).get("tutors", {})


def main(apply: bool) -> int:
    tutors = _legacy()
    if not tutors:
        print(f"No {config.LEGACY_TUTORS_FILE.name} found — nothing to migrate.")
        return 0

    if config.SUBJECTS_FILE.exists() and json.loads(config.SUBJECTS_FILE.read_text()).get("subjects"):
        print("subjects.json already has data — refusing to migrate over it.")
        print("Move it aside first if you really mean to re-run.")
        return 1

    planned = 0
    state = {"subjects": {}}
    chat_state = {"chats": {}}

    for tutor_id, t in tutors.items():
        turns = []
        legacy_msgs = config.LEGACY_CHATS_DIR / f"{tutor_id}.json"
        if legacy_msgs.exists():
            turns = json.loads(legacy_msgs.read_text())

        style = (t.get("instructions") or "").strip()
        print(f"\n{t.get('name')}  ({tutor_id})")
        print(f"  books   : {len(t.get('books', []))} (id reused — no re-ingest)")
        print(f"  style   : {config.style_label(style)}")
        print(f"  chat    : 1, carrying {len(turns)} turn(s)")
        planned += 1
        if not apply:
            continue

        state["subjects"][tutor_id] = {
            "id": tutor_id,
            "name": t.get("name", "Untitled subject"),
            "created_at": t.get("created_at"),
            "default_instructions": style,
            "default_model": t.get("model"),
            "books": t.get("books", []),
        }
        chat_id = chats.uuid.uuid4().hex[:12]
        chat_state["chats"][chat_id] = {
            "id": chat_id,
            "subject_id": tutor_id,
            # Untitled so the first new question generates one; existing threads
            # keep the subject name as a stand-in until then.
            "title": t.get("name"),
            "title_generated": False,
            "instructions": style,
            "model": t.get("model"),
            "created_at": t.get("created_at"),
            "updated_at": t.get("created_at"),
            "turn_count": len(turns),
        }
        if turns:
            config.MESSAGES_DIR.mkdir(parents=True, exist_ok=True)
            (config.MESSAGES_DIR / f"{chat_id}.json").write_text(json.dumps(turns, indent=2))

    if apply:
        config.SUBJECTS_FILE.write_text(json.dumps(state, indent=2))
        config.CHATS_FILE.write_text(json.dumps(chat_state, indent=2))

    print()
    if apply:
        print(f"Migrated {planned} tutor(s) → {planned} subject(s), one chat each.")
        print(f"Left in place: {config.LEGACY_TUTORS_FILE.name} and "
              f"{config.LEGACY_CHATS_DIR.name}/ — delete them once you're happy.")
    else:
        print(f"Dry run: {planned} tutor(s) would be migrated.")
        print("Re-run with --apply to write subjects.json and chats.json.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main("--apply" in sys.argv))
