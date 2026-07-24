"""Is `graders.json` still what this workspace actually runs?

`/setup-respan` provisions a new workspace from
`.claude/skills/setup-respan/graders.json`. Every time a grader is improved on
the platform, that file goes stale, and the next person to run the skill gets
the old, worse grader with no sign anything is wrong. That has happened three
times: groundedness, citation validity, then context completeness.

This is the check that catches it. It is a script rather than a test because it
needs the live API, and the test suite deliberately makes no network calls.

    python -m scripts.check_graders          # report drift
    python -m scripts.check_graders --sync   # pull live definitions into the file

Exits non-zero when anything has drifted, so it can gate a release.
"""
import argparse
import json
import os
import sys

from backend import config, experiments

GRADERS_FILE = config.BASE_DIR / ".claude" / "skills" / "setup-respan" / "graders.json"

# The grader (not pipeline) ids, which /setup-respan also records in .env.
ENV_KEYS = {
    "context_relevance": "EVAL_ID_CONTEXT_RELEVANCE",
    "context_completeness": "EVAL_ID_CONTEXT_COMPLETENESS",
    "groundedness": "EVAL_ID_GROUNDEDNESS",
    "context_utilization": "EVAL_ID_CONTEXT_UTILIZATION",
    "citation_validity": "EVAL_ID_CITATION_VALIDITY",
}

FIELDS = ["evaluator_definition", "scoring_rubric", "model"]


def _shipped() -> dict:
    return {g["key"]: g for g in json.loads(GRADERS_FILE.read_text())}


def _live_config(grader_id: str) -> dict:
    live = experiments._call("GET", f"/evaluators/{grader_id}/")
    return {k: v for k, v in (live.get("llm_config") or {}).items() if v is not None}, \
        (live.get("code_config") or {})


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sync", action="store_true",
                    help="overwrite graders.json with the live definitions")
    args = ap.parse_args(argv)

    if not config.RESPAN_API_KEY:
        print("RESPAN_API_KEY is not set; nothing to compare against.", file=sys.stderr)
        return 1

    shipped = _shipped()
    data = json.loads(GRADERS_FILE.read_text())
    drifted = []

    for key, env_key in ENV_KEYS.items():
        grader_id = os.environ.get(env_key)
        if not grader_id:
            print(f"  {key:22} skipped ({env_key} not in .env)")
            continue
        llm, code = _live_config(grader_id)
        g = shipped[key]

        diffs = []
        for f in FIELDS:
            if (g.get("llm_config") or {}).get(f, "") != llm.get(f, ""):
                if f in llm or f in (g.get("llm_config") or {}):
                    diffs.append(f)
        a = (g.get("code_config") or {}).get("eval_code_snippet", "").strip()
        b = code.get("eval_code_snippet", "").strip()
        if a != b:
            diffs.append("eval_code_snippet")

        if diffs:
            drifted.append(key)
            print(f"  {key:22} DRIFTED: {', '.join(diffs)}")
            if args.sync:
                for entry in data:
                    if entry["key"] == key:
                        if llm:
                            entry["llm_config"] = llm
                        if code:
                            entry["code_config"] = code
        else:
            print(f"  {key:22} matches")

    if drifted and args.sync:
        GRADERS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        print(f"\nsynced {len(drifted)} grader(s) into {GRADERS_FILE.name}. Commit it.")
        return 0
    if drifted:
        print(f"\n{len(drifted)} grader(s) have drifted. A fresh /setup-respan would "
              f"provision the old ones.\nRun with --sync to update the file.",
              file=sys.stderr)
        return 1
    print("\ngraders.json matches the live workspace.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
