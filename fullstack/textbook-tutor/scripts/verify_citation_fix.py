"""Regenerate the p.130 dual-map answer with the fixed prompt and score its
citations with the exact grader code, to confirm the 0.14 is resolved."""
import re
from backend import rag, store, subjects

Q = ("How do I show that a linear map from a finite-dimensional space to a "
     "finite-dimensional space W is the zero map if and only if its dual map is zero?")


def grade(inp: str, out: str) -> tuple[float, list]:
    available = set()
    for title, page in re.findall(r'\[([^\]]+?),\s*p\.\s*([^\]]+?)\]', inp):
        available.add((title.strip(), page.strip()))
    cited = []
    for group in re.findall(r'\[([^\]]+)\]', out):
        for piece in group.split(';'):
            m = re.match(r'\s*(.+?),\s*p\.\s*(.+?)\s*$', piece)
            if m:
                cited.append((m.group(1).strip(), m.group(2).strip()))

    def valid(t, p):
        if (t, p) in available:
            return True
        parts = [x.strip() for x in re.split(r'[-–,]', p) if x.strip()]
        return len(parts) > 1 and all((t, x) in available for x in parts)

    if not cited:
        return 1.0, []
    marked = [(t, p, valid(t, p)) for t, p in cited]
    return round(sum(1 for _, _, ok in marked if ok) / len(cited), 2), marked


def main():
    store.init_settings()
    subject = subjects.get("bc3796f39d32")
    chat = {"id": "verify", "instructions": "", "model": None}
    result = rag.answer(subject, chat, Q, include_prompt=True, mode="qa")
    prompt = (result.get("trace") or {}).get("prompt") or ""
    answer = result["answer"]
    score, marked = grade(prompt, answer)
    print(f"citation validity: {score}   ({sum(ok for *_, ok in marked)}/{len(marked)} valid)\n")
    for t, p, ok in marked:
        print(f"  [{'OK ' if ok else 'BAD'}]  ({t!r}, page={p!r})")
    # show the bracketed citations as they appear in prose
    print("\nbracketed citations in the answer:")
    for b in re.findall(r'\[[^\]]*p\.\s*[^\]]*\]', answer):
        print("   ", b)


if __name__ == "__main__":
    main()
