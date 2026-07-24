---
name: setup-respan
description: Connect this app to a Respan workspace — install the Respan MCP server, provision the five RAG evaluators and their pipelines, and write the pipeline ids into .env so `scripts/run_experiment.py` can grade the tutor. Use when setting the project up for the first time, when run_experiment says it isn't configured, or when moving the app to a different Respan org.
---

# Set up Respan for Ask the Textbook

The tutor itself only needs `RESPAN_API_KEY` — upload, ask, cite and solve all
work through the gateway with nothing else configured.

The **Inspect panel's evaluator scores** need more: five graders that live in
*your* Respan workspace. Their ids can't ship in the repo, so this skill creates
them and writes the ids into `.env`.

Do the steps in order. Stop and report if any step fails; a half-provisioned
workspace is worse than none.

---

## Step 1 — Respan API key

Ask the user for their Respan API key if `RESPAN_API_KEY` isn't already
resolvable (`platform.respan.ai` → Settings → API keys). Check first:

```bash
cd <project root> && ./.venv/bin/python -c "from backend import config; print('key set:', bool(config.RESPAN_API_KEY))"
```

`config.py` loads every `.env` from the project directory upward, nearest first,
so the key may legitimately live in a parent directory. If it's already set,
don't ask for it again.

If it isn't set, write it to the project's own `.env` (git-ignored):

```
RESPAN_API_KEY=sk-respan-...
```

## Step 2 — Install the Respan MCP server

Check whether it's already connected — the tools appear as `mcp__respan__*`. If
they aren't available, add it:

```bash
claude mcp add --transport http respan https://mcp.respan.ai/mcp \
  --header "Authorization: Bearer <THE USER'S RESPAN KEY>"
```

Use `--scope user` to make it available across projects, or `--scope project` to
commit it for the team. **Never hard-code a key into a committed file** — with
project scope the header belongs in an env var, not the config.

The connection only takes effect on the next Claude Code session, so if you just
added it, tell the user to restart and re-run this skill rather than trying to
push on without the tools.

## Step 3 — Create the five graders

Read `graders.json` in this directory. It holds the exact, verified definition
of each grader: four LLM judges and one code grader.

For each entry, call `mcp__respan__create_evaluator` with its `name`,
`description`, `type`, `score_value_type`, `score_config`,
`passing_conditions`, and either `llm_config` or `code_config`. Then call
`mcp__respan__commit_evaluator` on the returned id.

**Committing is not optional.** `create_evaluator` leaves a draft, and
`POST /evaluators/{id}/run/` keeps serving the last *committed* version — so an
uncommitted grader silently scores with nothing behind it. Commit, then record
the id.

Why these graders are shaped the way they are: each derives its score from a
count (`(N−U)/N`, `R/C`, `P/A`, `D/N`) rather than picking from a list of rubric
anchors. An earlier anchored version emitted only 0.0 / 0.75 / 1.0 across 150
real scores — a near-binary signal that can't show drift. Don't "simplify" these
prompts back into an anchor list.

## Step 4 — Wrap each grader in a deployed pipeline

A grader only appears on the Evaluators page, and is only usable by online-eval
automations, once it's wrapped in a committed + deployed pipeline. For each
grader:

1. `mcp__respan__create_evaluation_pipeline` with `steps: [{grader_id: <id>}]`
   and `combine: "single"`, named after the grader (e.g. `RAG · groundedness`).
2. `mcp__respan__commit_workflow` on the returned `workflow_id`.
3. `mcp__respan__deploy_workflow` on the same `workflow_id`.

Verify each ends up `deployed_version == version`, `type: "evaluators"`,
`trigger_event_type: "eval_only"`, `is_enabled: true`.

## Step 5 — Write the pipeline ids into .env

Append to the project's `.env` (git-ignored — never commit these):

```
EVAL_PIPELINE_CONTEXT_RELEVANCE=<pipeline id>
EVAL_PIPELINE_CONTEXT_COMPLETENESS=<pipeline id>
EVAL_PIPELINE_GROUNDEDNESS=<pipeline id>
EVAL_PIPELINE_CONTEXT_UTILIZATION=<pipeline id>
EVAL_PIPELINE_CITATION_VALIDITY=<pipeline id>
```

These are each pipeline's **`workflow_id`** — the stable family id — NOT the
`id` field and NOT the grader ids from Step 3.

That distinction matters and is easy to get backwards. `evaluator_workflow_ids`
does want a WorkflowVersion id, but every commit mints a new one, so pinning the
`id` you see today freezes the grader at today's version: you can edit it, commit
it, deploy it, watch `deployed_version` climb, and every run keeps scoring with
the old logic. The app pins the family and resolves the current version per run
(`experiments.pipeline_versions`).

## Step 6 — Verify

```bash
python -m scripts.run_experiment --subject "<a subject with books>" --name "setup check"
```

Expect five per-evaluator averages at the end. If it says it isn't configured,
`EXPERIMENTS_CONFIGURED` is false — check all five `EVAL_PIPELINE_*` ids are
present and the key resolves.

Sanity-check the numbers, don't just accept them. All five at exactly 0.00, or
identical min and max across a varied question set, means the graders are
scoring an empty row rather than your answers — see the `/logs/bulk/` trap
below.

---

## Not needed — online-eval automations

The app does not grade anything. Quality is measured by running the five graders
as an **experiment** over a fixed question set, where one run is comparable to
the next. A score for a single live answer has nothing to compare it to.

So there should be **no enabled automation** pointing at these pipelines. Check:

```
filter_workflows { "type": { "value": ["automations"], "operator": "eq" } }
```

Anything named `RAG · … — online eval` with `is_enabled: true` is scoring every
span in the background. Turn it off with
`DELETE /api/workflows/{workflow_id}/deployments/`.

Note the two are separate objects and only one is the switch. The **pipelines**
(`type: evaluators`, `trigger_event_type: eval_only`) do not fire on their own —
they are invoked, by an experiment or by an automation. The **automations**
(`type: automations`, `trigger_event_type: request_log`) are what fires on every
log. Undeploying the pipelines does *not* stop background scoring and is not the
lever; undeploying the automations is. Leave the pipelines deployed — experiments
run fine either way, but deployed is their normal state.

## Gotchas, learned the hard way

- **`graders.json` goes stale every time a grader is improved.** The next person
  to run this skill then provisions the old one, silently. Check before trusting
  it, and after any grader change:

  ```bash
  python -m scripts.check_graders          # exits 1 on drift
  python -m scripts.check_graders --sync   # pull live definitions in, then commit
  ```

- **Read the OpenAPI spec before guessing at an endpoint.** It lives at
  `respan-docs/fern/apis/openapi/openapi.json` and documents all 116 routes.
  Guessing cost a day of debugging that a two-minute read would have prevented,
  and produced two "platform bugs" that were nothing of the kind.
- **`/datasets/{id}/logs/` takes ONE log, as a bare object** — `{input, output,
  metadata, metrics}`, `input` required. The `{"logs": [...]}` array shape
  belongs to **`/datasets/{id}/logs/bulk/`**, which is what you want for a
  question set: one request for N rows, returning `{success_count}`. Send the
  array to the singular endpoint and you get a row with no input, which the
  graders then score as an empty string.
- **`POST /testsets/` does not create an experiment.** `/api/testsets/` is a
  separate resource — the spreadsheet on the Experiments page — taking `name`,
  `description`, `column_definitions`, `starred`. Experiments are
  **`POST /api/v2/experiments/`** (`dataset_id` + `workflow` required); read
  spans back from `GET /api/v2/experiments/{id}/logs/list/`.
- **An experiment's `status: completed` precedes its last score.** Poll the
  spans until every one carries a full set of scores, or you will average over
  whichever graders happened to have landed.
- **Never attach more than one evaluator pipeline to an experiment.** Only the
  first grader to run receives the answer as `{{output}}`; every one after it is
  handed the *previous grader's result JSON*, despite each task's config saying
  `data_source: "original_event"`. Any grader reading the output then scores a
  JSON blob. Measured: groundedness averaged 0.65 with 0.00s on well-grounded
  answers when bundled with four others, and 1.00 across the same 12 rows run
  alone. `experiments.grade_dataset` fans out one grader per experiment; do the
  same anywhere else.

- **Pipelines embed a snapshot of the grader, not a live reference.** Updating a
  grader does *not* change what its pipeline runs. Re-run
  `update_evaluation_pipeline` to re-snapshot, then commit and deploy.
- **Forking a draft resets workflow metadata.** `POST /workflows/{id}/versions/`
  returns a draft with `type` reset to `automations` and `trigger_event_type`
  cleared. Restore both to `evaluators` / `eval_only` before committing.
- **`is_enabled` can't be set on a draft** — `commit_workflow` restores it.
- **Editing an existing setup** (rather than creating fresh) means: PATCH the
  evaluator → `commit_evaluator` → fork the pipeline draft →
  `update_evaluation_pipeline` → `update_workflow` (restore name/type/trigger) →
  `commit_workflow` → `deploy_workflow`.
