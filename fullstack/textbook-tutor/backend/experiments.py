"""Grading on Respan, by running an experiment.

One implementation, two callers: `scripts/run_experiment.py` grades a fixed
question set for regression, and the Inspect panel's **Evaluate** button grades a
single answer on demand. Both do the same thing — build dataset rows, run an
experiment over them with the five deployed pipelines, wait, read the scores —
so a per-answer score is directly comparable to the baseline.

Why an experiment rather than a direct grader call: `POST /evaluators/{id}/run/`
answers with `{"id": "", "environment": "test"}`. It computes a score, bills for
it, and stores nothing, so the number exists nowhere but the caller's memory. An
experiment persists, and shows up on the Experiments page.
"""
import json
import time
from concurrent.futures import ThreadPoolExecutor
import urllib.error
import urllib.request

from . import config

API = "https://api.respan.ai/api"

POLL_SECONDS = 4
POLL_LIMIT = 60

# Display-only. The graders carry their own `passing_conditions` on the platform,
# which are authoritative; this is just what colours a chip red in the panel.
PASS_THRESHOLD = 0.7


def _call(method: str, path: str, body: dict | None = None, timeout: int = 120) -> dict:
    req = urllib.request.Request(
        f"{API}{path}",
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": f"Bearer {config.RESPAN_API_KEY}",
                 "Content-Type": "application/json"},
        method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read()
        # DELETE answers 204 with an empty body; json.load would raise on it.
        return json.loads(body) if body else {}


# --- the span an answer came from -------------------------------------------

def fetch_answer_io(log_id: str, attempts: int = 4) -> tuple[str, str] | None:
    """The exact prompt and answer of one generation span, or None.

    Taken from the span rather than from anything the app kept, so the graders
    read precisely what the model read — the same string
    `scripts/run_experiment.py` uploads, which is what makes the two comparable.

    Retried: cold reads of `/request-logs/{id}/` have been measured between 1.5s
    and 22.8s, and a fresh answer may not be ingested for a few seconds yet.
    """
    for i in range(attempts):
        try:
            span = _call("GET", f"/request-logs/{log_id}/", timeout=45)
            break
        except urllib.error.HTTPError as e:
            if e.code != 404:
                return None
            time.sleep(3)          # not ingested yet
        except Exception:
            time.sleep(3)          # slow cold read; try again
    else:
        return None

    messages = (span.get("full_request") or {}).get("messages") or []
    user = [m for m in messages if m.get("role") == "user"]
    if not user or not isinstance(user[-1].get("content"), str):
        return None                # solve-mode turns send a list (image + text)
    answer = "".join(
        b.get("text", "") for b in (span.get("full_response") or {}).get("content", [])
        if b.get("type") == "text").strip()
    if not answer:
        return None
    return user[-1]["content"], answer


def pipeline_versions(families: list[str]) -> list[str]:
    """Resolve pipeline family ids to the version PKs an experiment needs.

    `evaluator_workflow_ids` wants WorkflowVersion ids, and every commit mints a
    new one. Pinning the PK therefore freezes the grader: you can edit it, commit
    it and deploy it, watch `deployed_version` go up, and still have every run
    scored by the version whose id you wrote down. Which is exactly what happened
    to the groundedness and citation fixes.

    So the config pins the stable family id and this resolves it per run.
    Unresolvable families are dropped rather than passed through: a stale id is
    accepted by the API and silently scores with old logic, which is worse than
    one fewer grader.
    """
    try:
        listing = _call("GET", "/workflows/list/?page_size=100").get("results") or []
    except urllib.error.HTTPError as e:
        # 401/403 here is the commonest first-run failure: a key that is missing,
        # wrong, or from another workspace. Returning [] lets the caller say that
        # in words rather than surfacing "HTTPError" in the panel.
        if e.code in (401, 403):
            return []
        raise
    current = {w.get("workflow_id"): w.get("id") for w in listing
               if w.get("type") == "evaluators"}
    return [current[f] for f in families if current.get(f)]


# --- dataset + experiment ----------------------------------------------------

def create_dataset(name: str, description: str) -> str:
    return _call("POST", "/datasets/",
                 {"name": name, "description": description, "is_empty": True,
                  "type": "sampling"})["id"]


def add_rows(dataset_id: str, rows: list[dict]) -> int:
    """Insert the rows and return how many actually landed.

    `/logs/bulk/` takes the `{"logs": [...]}` array; the singular `/logs/`
    endpoint takes ONE bare `{input, output, ...}` object. Sending the array to
    the singular endpoint yields a row with no `input`, and the graders then
    score an empty string.

    The insert is asynchronous, so the count is read back rather than assumed —
    grading one row and reporting it as twelve would be worse than failing.
    """
    for i in range(0, len(rows), 50):
        _call("POST", f"/datasets/{dataset_id}/logs/bulk/", {"logs": rows[i:i + 50]})
    landed = 0
    for _ in range(30):
        time.sleep(2)
        landed = _call("GET", f"/datasets/{dataset_id}/logs/list/?page_size=200").get("count") or 0
        if landed >= len(rows):
            break
    return landed


def grade_dataset(name: str, description: str, dataset_id: str, rows: int,
                  pipeline_ids: list[str], on_progress=None) -> tuple[list[dict], list[str]]:
    """Grade a dataset, running ONE grader per experiment.

    Attaching several evaluator pipelines to a single experiment corrupts the
    result: only the first grader to run receives the answer as `{{output}}`, and
    every one after it is handed the *previous grader's result JSON* instead —
    despite each task's config saying `data_source: "original_event"`. Graders
    that read the output then score a JSON blob, which is why well-grounded
    answers came back 0.00 and why the affected grader changed between identical
    runs. Verified: groundedness averaged 0.65 with 0.00s when bundled, and 1.00
    across the same 12 rows when run alone.

    One experiment per grader, run concurrently over a shared dataset. Same
    number of grader calls, five experiment wrappers instead of one.
    """
    def one(pid):
        eid = create_experiment(f"{name} · {pid[:8]}", description, dataset_id, [pid])
        wait_for(eid)
        return eid, collect_scores(eid, rows, 1)

    with ThreadPoolExecutor(max_workers=len(pipeline_ids)) as pool:
        results = list(pool.map(one, pipeline_ids))

    # Merge per row, matching on the input the graders were given.
    merged: dict[str, dict] = {}
    for _, spans in results:
        for span in spans:
            key = span.get("input") or ""
            row = merged.setdefault(key, {"input": key, "output": span.get("output"), "scores": {}})
            row["scores"].update(span.get("scores") or {})
    if on_progress:
        on_progress(f"graded by {len(results)} graders")
    return list(merged.values()), [eid for eid, _ in results]


def create_experiment(name: str, description: str, dataset_id: str,
                      pipeline_ids: list[str]) -> str:
    """Create and start the experiment.

    Note `/v2/experiments/`, not `/testsets/`. `/testsets/` is a different
    resource — the spreadsheet on the Experiments page — and posting this body
    there creates a spreadsheet, not a run.
    """
    return _call("POST", "/v2/experiments/", {
        "name": name,
        "description": description,
        "dataset_id": dataset_id,
        # No generation step — the answers are already in the dataset.
        "workflow": [{"type": "duplicate", "config": {"name": "passthrough"}}],
        "evaluator_workflow_ids": pipeline_ids,
    })["id"]


def spans(experiment_id: str) -> list[dict]:
    out, page = [], 1
    while True:
        d = _call("GET", f"/v2/experiments/{experiment_id}/logs/list/?page={page}&page_size=50")
        out.extend(d.get("results") or [])
        if not d.get("next"):
            return out
        page += 1


def wait_for(experiment_id: str, on_progress=None) -> dict:
    for _ in range(POLL_LIMIT):
        exp = _call("GET", f"/v2/experiments/{experiment_id}/")
        if (exp.get("status") or "") in ("completed", "failed", "cancelled"):
            return exp
        if on_progress:
            meta = exp.get("metadata") or {}
            on_progress(exp.get("status") or "starting",
                        meta.get("eval_workflow_run_completed_count") or 0)
        time.sleep(POLL_SECONDS)
    return _call("GET", f"/v2/experiments/{experiment_id}/")


def collect_scores(experiment_id: str, expected_rows: int, graders: int) -> list[dict]:
    """Every span's scores, once each span carries a full set.

    `status: completed` arrives before the last grader's score is attached, so
    this waits rather than reporting whichever ones happened to have landed.
    """
    found = []
    for _ in range(POLL_LIMIT):
        found = spans(experiment_id)
        if len(found) >= expected_rows and all(len(s.get("scores") or {}) >= graders for s in found):
            break
        time.sleep(POLL_SECONDS)
    return found


def averages(found: list[dict]) -> dict[str, list[float]]:
    out: dict[str, list[float]] = {}
    for span in found:
        for entry in (span.get("scores") or {}).values():
            v = entry.get("numerical_value")
            if v is not None:
                out.setdefault(entry["evaluator_name"], []).append(float(v))
    return out


def averages_by(found: list[dict], meta_for, bucket) -> dict[str, dict[str, list[float]]]:
    """Scores split into buckets: {evaluator_name: {bucket: [values]}}.

    A whole-set average hides the thing worth seeing: easy questions sit at the
    ceiling and drown out the hard ones, so a retrieval change barely moves the
    mean even when it clearly helped the hard slice. `meta_for(span)` returns the
    row metadata for a graded span (or None to drop it); `bucket(meta)` names the
    slice.
    """
    out: dict[str, dict[str, list[float]]] = {}
    for span in found:
        meta = meta_for(span)
        if meta is None:
            continue
        b = bucket(meta)
        if b is None:
            continue
        for entry in (span.get("scores") or {}).values():
            v = entry.get("numerical_value")
            if v is not None:
                out.setdefault(entry["evaluator_name"], {}).setdefault(b, []).append(float(v))
    return out


# --- grading one answer, for the Inspect panel -------------------------------

def evaluate_answer(log_id: str, label: str, on_progress=None) -> dict:
    """Run the five graders over a single answer as a one-row experiment.

    Returns {status, scores, experiment_id}. `scores` is keyed by evaluator name
    so the panel can render whatever the workspace has deployed, rather than a
    list this module has to keep in step.
    """
    if not config.EXPERIMENTS_CONFIGURED:
        return {"status": "unconfigured", "scores": {}}

    def step(msg):
        if on_progress:
            on_progress(msg)

    # Graders resolved first, deliberately: a missing or wrong key fails here,
    # with a message about the key. Left until after the span fetch, the same
    # failure surfaces as "not logged yet" and sends the user to retry forever.
    pipelines = pipeline_versions(list(config.EVAL_PIPELINE_IDS.values()))
    if not pipelines:
        return {"status": "error", "scores": {},
                "detail": "no graders resolved — check RESPAN_API_KEY and the "
                          "EVAL_PIPELINE_* ids in .env, then run /setup-respan"}

    step("reading the span")
    io = fetch_answer_io(log_id)
    if io is None:
        return {"status": "pending", "scores": {}}
    prompt, answer = io

    name = f"textbook-tutor · {label[:60]}"
    step("uploading")
    dataset_id = create_dataset(name, "Single answer graded from the Inspect panel.")
    landed = add_rows(dataset_id, [{"input": prompt, "output": answer,
                                    "metadata": {"log_id": log_id, "source": "inspect"}}])
    if not landed:
        return {"status": "error", "scores": {},
                "detail": "the row never landed in the dataset"}

    step(f"grading with {len(pipelines)} graders")
    found, experiment_ids = grade_dataset(name, "Graded from the Inspect panel.",
                                          dataset_id, 1, pipelines, on_progress=step)
    experiment_id = experiment_ids[0] if experiment_ids else ""

    scores = {}
    for evaluator, vals in averages(found).items():
        score = vals[0]
        scores[evaluator] = {"score": score, "pass": score >= PASS_THRESHOLD}
    if not scores:
        return {"status": "error", "scores": {}, "experiment_id": experiment_id,
                "detail": "the experiment completed but attached no scores"}
    return {"status": "ready", "scores": scores, "experiment_id": experiment_id}
