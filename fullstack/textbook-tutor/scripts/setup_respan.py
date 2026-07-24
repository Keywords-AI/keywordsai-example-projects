"""Provision the five RAG graders in a Respan workspace, without Claude Code.

Grader ids are workspace-specific, so they can't ship in the repo: the objects
have to exist before the ids do. This is that provisioning step as a plain
command, so the README can say "set your key, run one thing" and mean it for
everybody, Claude Code or not:

    python -m scripts.setup_respan            # dry run: say what would happen
    python -m scripts.setup_respan --apply    # create what's missing, write .env

Idempotent, and matched by NAME. Anything already in the workspace is reused,
so running it twice is a no-op rather than a second set of graders. That matters
because the platform will happily hold five identically named pipelines and the
ids in `.env` would then be a coin flip.

Provisioning is five steps per grader, and only four of them are ordinary REST:

    create evaluator   POST /evaluators/
    commit it          POST /evaluators/{id}/versions/
    wrap in pipeline   POST /workflows/                 <-- see _pipeline_tasks
    commit it          POST /workflows/{id}/commits/     <-- NOT /versions/
    deploy it          POST /workflows/{id}/deployments/

Committing is not optional: `create` leaves a draft, and a grader only ever runs
its last committed version. A pipeline additionally has to be deployed before an
experiment can call it.
"""
import argparse
import json
import re
import sys
import urllib.error

from backend import config, experiments

GRADERS_FILE = config.BASE_DIR / "evals" / "graders.json"
ENV_FILE = config.BASE_DIR / ".env"

# Both id families end up in .env, and they are NOT interchangeable.
# EVAL_ID_* are grader ids, read by scripts/check_graders.py to diff the live
# definition against graders.json. EVAL_PIPELINE_* are pipeline workflow_ids,
# read by backend/config.py and handed to experiments. Writing one where the
# other belongs fails in a way that looks like a grader bug.
GRADER_ENV = "EVAL_ID_{}"
PIPELINE_ENV = "EVAL_PIPELINE_{}"


def _pipeline_tasks(grader_id: str, grader: dict) -> list[dict]:
    """The one-node Blockly graph a single-grader pipeline is made of.

    This is the ugly part, and the reason it's spelled out here rather than
    posted as `{"steps": [...]}`: there is no REST endpoint that takes a grader
    id and wraps it. `POST /workflows/` takes the visual editor's own node
    format, so the `_blockly_*` keys below are load-bearing, undocumented, and
    reproduced from a pipeline the editor built. `mcp__respan__create_evaluation_
    pipeline` constructs exactly this server-side.

    If the Evaluators page ever stops rendering a pipeline made here, compare
    against a fresh one built in the UI (`GET /workflows/{id}/`) before assuming
    the API broke. The `evaluator_id[:30]` truncation is deliberate: that is how
    the editor derives a node id, and the page keys off it.
    """
    node = grader_id[:30]
    task_id = f"blockly_hidden_eval_{node}"
    kind = grader["type"]                      # "llm" or "code"
    cfg = {
        "data_source": "original_event",
        "evaluator_id": grader_id,
        "score_config": grader.get("score_config") or {},
        "score_value_type": grader["score_value_type"],
        "_blockly_node_id": node,
        "_blockly_is_result": True,
        "_blockly_hidden_eval": True,
        "_blockly_output_field": "primary_score",
        "_blockly_evaluator_kind": kind,
    }
    # The pipeline embeds a SNAPSHOT of the grader, not a live reference, so
    # editing the grader later does not change what the pipeline runs.
    if grader.get("llm_config"):
        cfg["llm_config"] = grader["llm_config"]
    if grader.get("code_config"):
        cfg["code_config"] = grader["code_config"]
    return [{"id": task_id, "type": "eval", "label": task_id,
             "config": cfg, "generation_method": kind}]


def _by_name(path: str, body: dict, id_field: str) -> dict[str, str]:
    """{name: id} for everything already in the workspace, ALL pages.

    Following `next` is not optional. These endpoints page at 10, and `count` is
    the size of the page you were handed, not the size of the collection — so a
    single-page read looks complete and silently isn't. Stopping at page one
    reports an existing grader as missing, and the caller then creates a second
    one with the same name.
    """
    found: dict[str, str] = {}
    page = 1
    while True:
        sep = "&" if "?" in path else "?"
        chunk = experiments._call("POST", f"{path}{sep}page={page}", body)
        for r in chunk.get("results", []):
            # Later entries win, so a name held twice resolves to the newest.
            if r.get("name"):
                found[r["name"]] = r[id_field]
        if not chunk.get("next"):
            return found
        page += 1


def _ensure_grader(grader: dict, existing: dict[str, str], apply: bool) -> tuple[str, bool]:
    name = grader["name"]
    if name in existing:
        return existing[name], False
    if not apply:
        return "<would create>", True

    payload = {k: grader[k] for k in
               ("name", "description", "type", "score_value_type",
                "score_config", "passing_conditions")
               if grader.get(k) is not None}
    for k in ("llm_config", "code_config"):
        if grader.get(k):
            payload[k] = grader[k]

    grader_id = experiments._call("POST", "/evaluators/", payload)["id"]
    # Draft -> committed. Without this the grader scores with nothing behind it.
    experiments._call("POST", f"/evaluators/{grader_id}/versions/",
                      {"version_description": "provisioned by scripts.setup_respan"})
    return grader_id, True


def _ensure_pipeline(grader: dict, grader_id: str, existing: dict[str, str],
                     apply: bool) -> tuple[str, bool]:
    name = grader["name"]
    if name in existing:
        return existing[name], False
    if not apply:
        return "<would create>", True

    created = experiments._call("POST", "/workflows/", {
        "name": name,
        "description": grader.get("description") or "",
        "type": "evaluators",
        "trigger_event_type": "eval_only",
        "tasks": _pipeline_tasks(grader_id, grader),
    })
    workflow_id = created["workflow_id"]
    # Commit is /commits/, NOT /versions/. `POST /workflows/{id}/versions/` forks
    # a new DRAFT (v1 -> v2) and commits nothing, so deploy then fails with
    # "Committed version not found" and the pipeline is left dangling. Note
    # /commits/ is absent from the published OpenAPI spec; it is what the
    # platform actually uses, and what mcp__respan__commit_workflow calls.
    experiments._call("POST", f"/workflows/{workflow_id}/commits/",
                      {"description": "provisioned by scripts.setup_respan"})
    # Version omitted: deploys the latest committed one.
    experiments._call("POST", f"/workflows/{workflow_id}/deployments/", {})
    return workflow_id, True


def _write_env(values: dict[str, str]) -> list[str]:
    """Upsert keys into .env, leaving every other line untouched.

    Rewriting the file wholesale would drop the user's own keys, so existing
    assignments are replaced in place and only genuinely new ones are appended.
    """
    text = ENV_FILE.read_text() if ENV_FILE.is_file() else ""
    changed = []
    for key, value in values.items():
        pattern = re.compile(rf"^{re.escape(key)}=.*$", re.M)
        if pattern.search(text):
            if pattern.search(text).group(0) != f"{key}={value}":
                text = pattern.sub(f"{key}={value}", text)
                changed.append(key)
        else:
            if text and not text.endswith("\n"):
                text += "\n"
            text += f"{key}={value}\n"
            changed.append(key)
    if changed:
        ENV_FILE.write_text(text)
    return changed


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--apply", action="store_true",
                    help="actually create things (default: dry run)")
    args = ap.parse_args(argv)

    if not config.RESPAN_API_KEY:
        print("RESPAN_API_KEY is not set. Put it in .env first.", file=sys.stderr)
        return 1

    graders = json.loads(GRADERS_FILE.read_text())

    try:
        have_graders = _by_name("/evaluators/list/", {}, "id")
        have_pipelines = _by_name("/workflows/list/", {
            "filters": {"type": {"value": ["evaluators"], "operator": "eq"}}
        }, "workflow_id")
    except urllib.error.HTTPError as exc:
        print(f"Could not read the workspace: {exc}. Is RESPAN_API_KEY valid?",
              file=sys.stderr)
        return 1

    env: dict[str, str] = {}
    created = 0
    print(f"{'grader':<28} {'grader id':<12} {'pipeline'}")
    for grader in graders:
        gid, gid_new = _ensure_grader(grader, have_graders, args.apply)
        pid, pid_new = _ensure_pipeline(grader, gid, have_pipelines, args.apply)
        created += gid_new + pid_new

        suffix = grader["key"].upper()
        env[GRADER_ENV.format(suffix)] = gid
        env[PIPELINE_ENV.format(suffix)] = pid

        mark = lambda new: "CREATE" if new else "reuse "            # noqa: E731
        print(f"  {grader['name']:<26} {mark(gid_new)} {mark(pid_new)}  "
              f"{'' if args.apply or not (gid_new or pid_new) else '(dry run)'}")

    if not args.apply:
        if created:
            print(f"\n{created} object(s) would be created. Re-run with --apply.")
        else:
            print("\nEverything already exists. --apply would change nothing.")
        return 0

    changed = _write_env(env)
    print(f"\n{created} object(s) created.")
    print(f"{len(changed)} key(s) written to {ENV_FILE.name}"
          f"{': ' + ', '.join(changed) if changed else ' (already correct)'}")
    print("\nVerify with:  python -m scripts.run_experiment --name 'setup check'")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
