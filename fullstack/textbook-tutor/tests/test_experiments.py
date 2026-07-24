"""Grading one answer as a Respan experiment (`experiments.evaluate_answer`).

The status contract drives the Inspect panel, so it has to distinguish "the span
isn't logged yet" (retrying works) from "no graders in this workspace" (retrying
never helps) from "the experiment ran but produced nothing" (a real failure).

The other thing worth pinning down is *what gets graded*: the prompt is taken
from the span, so the graders read exactly what the model read. If that ever
silently became something else — the answer alone, the whole message array — the
scores would stop being comparable to the regression baseline and nothing would
look wrong.
"""
import pytest

from backend import config, experiments


@pytest.fixture(autouse=True)
def configured(monkeypatch):
    monkeypatch.setattr(config, "RESPAN_API_KEY", "sk-respan-test")
    monkeypatch.setattr(config, "EXPERIMENTS_CONFIGURED", True)
    monkeypatch.setattr(config, "EVAL_PIPELINE_IDS",
                        {f"g{i}": f"pipeline-{i}" for i in range(5)})


PROMPT = "Excerpts (each labelled with its source and page):\n\n[Axler, p. 8]\n…\n\nQuestion: What is a vector?"
ANSWER = "A vector is an arrow from the origin [Axler, p. 8]."


def _span(prompt=PROMPT, answer=ANSWER):
    """Shaped like the gateway's stored generation log."""
    return {
        "full_request": {"messages": [
            {"role": "user", "content": "an earlier question"},
            {"role": "assistant", "content": "an earlier answer"},
            {"role": "user", "content": prompt},
        ]},
        "full_response": {"content": [
            {"type": "thinking", "thinking": "…"},
            {"type": "text", "text": answer},
        ]},
    }


def _wire(monkeypatch, *, span=None, scores=None, status="completed"):
    """Stub the whole platform round trip, capturing what got uploaded."""
    sent = {}
    monkeypatch.setattr(experiments, "fetch_answer_io",
                        lambda lid, attempts=4: None if span is None else
                        (span["full_request"]["messages"][-1]["content"],
                         span["full_response"]["content"][-1]["text"]))
    monkeypatch.setattr(experiments, "pipeline_versions",
                        lambda families: [f"v-{f}" for f in families])
    monkeypatch.setattr(experiments, "create_dataset", lambda n, d: "ds-1")
    monkeypatch.setattr(experiments, "add_rows",
                        lambda ds, rows: sent.setdefault("rows", rows) and 0 or len(rows))
    # grade_dataset runs one experiment per grader; record the bundles it used.
    def fake_grade(name, desc, ds, rows, pipes, on_progress=None):
        sent["pipelines"] = pipes
        sent.setdefault("bundles", []).append(list(pipes))
        if status != "completed":
            return [], []
        return ([{"scores": {k: {"evaluator_name": k, "numerical_value": v}
                             for k, v in (scores or {}).items()}}],
                ["exp-1"])
    monkeypatch.setattr(experiments, "grade_dataset", fake_grade)
    return sent


# --- what gets graded ---

def test_grades_the_prompt_the_model_actually_saw(monkeypatch):
    sent = _wire(monkeypatch, span=_span(), scores={"RAG · groundedness": 1.0})
    experiments.evaluate_answer("log-1", "What is a vector?")
    row = sent["rows"][0]
    assert row["input"] == PROMPT, "graders must see the composed prompt, not the bare question"
    assert row["output"] == ANSWER


def test_history_is_not_sent_to_the_graders(monkeypatch):
    sent = _wire(monkeypatch, span=_span(), scores={"RAG · groundedness": 1.0})
    experiments.evaluate_answer("log-1", "q")
    assert "an earlier question" not in sent["rows"][0]["input"]


def test_every_deployed_pipeline_is_attached(monkeypatch):
    sent = _wire(monkeypatch, span=_span(), scores={"RAG · groundedness": 1.0})
    experiments.evaluate_answer("log-1", "q")
    assert sorted(sent["pipelines"]) == sorted(f"v-{f}" for f in config.EVAL_PIPELINE_IDS.values())


# --- the status contract ---

def test_scores_are_returned_keyed_by_evaluator_name(monkeypatch):
    _wire(monkeypatch, span=_span(),
          scores={"RAG · context relevance": 0.33, "RAG · groundedness": 1.0})
    res = experiments.evaluate_answer("log-1", "q")
    assert res["status"] == "ready"
    assert res["scores"]["RAG · context relevance"]["score"] == 0.33
    assert res["experiment_id"] == "exp-1"


def test_pass_follows_the_display_threshold(monkeypatch):
    _wire(monkeypatch, span=_span(),
          scores={"low": experiments.PASS_THRESHOLD - 0.01,
                  "high": experiments.PASS_THRESHOLD})
    res = experiments.evaluate_answer("log-1", "q")
    assert res["scores"]["low"]["pass"] is False
    assert res["scores"]["high"]["pass"] is True


def test_span_not_ingested_yet_is_pending(monkeypatch):
    _wire(monkeypatch, span=None)
    assert experiments.evaluate_answer("log-1", "q")["status"] == "pending"


def test_unprovisioned_workspace_is_unconfigured(monkeypatch):
    # Distinct from pending: retrying never helps until provisioning runs.
    monkeypatch.setattr(config, "EXPERIMENTS_CONFIGURED", False)
    assert experiments.evaluate_answer("log-1", "q")["status"] == "unconfigured"


def test_a_failed_experiment_is_an_error(monkeypatch):
    _wire(monkeypatch, span=_span(), scores={"g": 1.0}, status="failed")
    assert experiments.evaluate_answer("log-1", "q")["status"] == "error"


def test_completing_with_no_scores_is_an_error(monkeypatch):
    # The failure that produced a whole run of 0.00s: the experiment finishes,
    # but nothing was attached. Reporting that as "ready" with an empty panel
    # would look like a UI bug rather than a grading one.
    _wire(monkeypatch, span=_span(), scores={})
    res = experiments.evaluate_answer("log-1", "q")
    assert res["status"] == "error"


def test_a_row_that_never_lands_is_an_error(monkeypatch):
    _wire(monkeypatch, span=_span(), scores={"g": 1.0})
    monkeypatch.setattr(experiments, "add_rows", lambda ds, rows: 0)
    assert experiments.evaluate_answer("log-1", "q")["status"] == "error"


def test_each_grader_gets_its_own_experiment(monkeypatch):
    """Bundling graders into one experiment corrupts the scores.

    Only the first grader receives the answer as {{output}}; every one after it
    is handed the PREVIOUS grader's result JSON, so anything reading the output
    grades a JSON blob. Groundedness averaged 0.65 with 0.00s on well-grounded
    answers when bundled, and 1.00 on the same rows when run alone. §28.
    """
    bundles = []
    monkeypatch.setattr(experiments, "create_experiment",
                        lambda n, d, ds, pipes: bundles.append(list(pipes)) or f"exp{len(bundles)}")
    monkeypatch.setattr(experiments, "wait_for", lambda eid, on_progress=None: {"status": "completed"})
    monkeypatch.setattr(experiments, "collect_scores", lambda eid, rows, graders: [])

    experiments.grade_dataset("n", "d", "ds-1", 1, ["p1", "p2", "p3", "p4", "p5"])
    assert len(bundles) == 5, "one experiment per grader"
    assert all(len(b) == 1 for b in bundles), f"graders were bundled: {bundles}"


def test_progress_is_reported(monkeypatch):
    _wire(monkeypatch, span=_span(), scores={"g": 1.0})
    seen = []
    experiments.evaluate_answer("log-1", "q", on_progress=seen.append)
    assert seen, "the panel shows these while the experiment runs"


# --- a score is kept with its turn ---

def test_scores_are_stored_on_the_turn_that_produced_the_span(tmp_path, monkeypatch):
    """Grading costs an experiment run, so the result has to survive a reload."""
    from backend import chats
    monkeypatch.setattr(config, "CHATS_FILE", tmp_path / "chats.json")
    monkeypatch.setattr(config, "MESSAGES_DIR", tmp_path / "messages")

    chat = chats.create(None)["id"]
    chats.append(chat, {"role": "user", "content": "q"})
    chats.append(chat, {"role": "tutor", "content": "a", "trace": {"log_id": "span-1"}})
    chats.append(chat, {"role": "tutor", "content": "b", "trace": {"log_id": "span-2"}})

    assert chats.set_scores(chat, "span-2", {"g": {"score": 1.0, "pass": True}}, "exp-9")
    turns = chats.messages(chat)
    assert "scores" not in turns[1], "the wrong turn was scored"
    assert turns[2]["scores"]["g"]["score"] == 1.0
    assert turns[2]["experiment_id"] == "exp-9"


def test_scoring_an_unknown_span_changes_nothing(tmp_path, monkeypatch):
    from backend import chats
    monkeypatch.setattr(config, "CHATS_FILE", tmp_path / "chats.json")
    monkeypatch.setattr(config, "MESSAGES_DIR", tmp_path / "messages")
    chat = chats.create(None)["id"]
    chats.append(chat, {"role": "tutor", "content": "a", "trace": {"log_id": "span-1"}})
    assert chats.set_scores(chat, "nope", {"g": {}}, "exp-1") is False
    assert "scores" not in chats.messages(chat)[0]


# --- what a new workspace hits first ---

def test_a_bad_key_says_so_instead_of_reporting_pending(monkeypatch):
    """The commonest first-run failure must not look like ingestion lag.

    Resolving graders happens before the span fetch precisely so a 401/403 is
    reported as a key problem. Reversed, the same failure reads "not logged yet"
    and the user retries forever.
    """
    monkeypatch.setattr(experiments, "pipeline_versions", lambda families: [])
    monkeypatch.setattr(experiments, "fetch_answer_io",
                        lambda lid, attempts=4: pytest.fail("must not reach the span fetch"))
    res = experiments.evaluate_answer("log-1", "q")
    assert res["status"] == "error"
    assert "RESPAN_API_KEY" in res["detail"]


def test_auth_failure_resolving_graders_is_not_an_exception(monkeypatch):
    import urllib.error

    def forbidden(method, path, body=None, timeout=120):
        raise urllib.error.HTTPError(path, 403, "Forbidden", {}, None)

    monkeypatch.setattr(experiments, "_call", forbidden)
    assert experiments.pipeline_versions(["family-1"]) == []
