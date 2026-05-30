# Respan Red-Team: LLM Safety Scorecard

An open-source LLM safety red-teaming eval that runs entirely through the
[Respan](https://respan.ai) gateway and renders a polished **Safety Scorecard**.
Every model call is routed and judged through Respan, so the whole run is traced
in your dashboard. Harmful model outputs are redacted by default.

This example ports a
[PAIR jailbreaking replication](https://github.com/islamborghini/JailbreakingLLMs)
onto Respan's gateway and evals. It is authorized, defensive evaluation research
on public benchmarks.

## What it does

1. Takes a set of harmful **behaviors** (a tame default set ships in
   `eval/behaviors.json`; the full public **AdvBench** set loads on demand).
2. Wraps each behavior in a library of published **attack framings** (roleplay,
   hypothetical, persona, formatting, plus a `direct` control).
3. Sends every `(target model x behavior x framing)` through the **Respan
   gateway** (OpenAI-compatible, `https://api.respan.ai/api`), tagged with a
   shared trace group.
4. Judges each response with **Llama Guard 4** through the same gateway (a strict
   JSON judge is the fallback).
5. Aggregates everything into a scorecard: a model leaderboard ranked by
   attack-success rate, a category-by-model threat matrix, attack-vector
   effectiveness, and a filterable trace log.

Targets and judge come from the source capstone: Llama 3.1 8B, Llama 4 Scout,
Qwen3 32B, Kimi K2, judged by `meta-llama/llama-guard-4-12b`.

## Quickstart (demo, no API key)

```bash
python3 eval/make_sample.py            # seed redacted demo data
cd web && npm install && npm run dev   # open http://localhost:3000
```

## Real run (through Respan)

```bash
cp .env.example .env                   # add your RESPAN_API_KEY
pip install -r eval/requirements.txt
python eval/redteam.py                 # routes + judges through the gateway
```

Then refresh the web app to see the live scorecard. Useful flags:

```bash
python eval/redteam.py --dry-run            # synthetic data, no key
python eval/redteam.py --limit 3            # first 3 behaviors (cheap smoke test)
python eval/redteam.py --load-advbench --advbench-n 50
python eval/redteam.py --attacks direct,roleplay
```

A full default run is small and cheap: 4 models x 10 behaviors x 5 framings is
200 calls.

## How it works

- **Gateway.** `eval/respan_client.py` wraps the OpenAI SDK against
  `https://api.respan.ai/api`. Every call carries a `trace_group_identifier`, a
  `custom_identifier`, and `metadata`, so the run is grouped and filterable in
  the Respan dashboard.
- **Judge.** `eval/judge.py` classifies each response with Llama Guard. If Llama
  Guard is unavailable or unparseable, a strict JSON judge takes over. Both strip
  `<think>` blocks first (a lesson from the source PAIR run).
- **Aggregation.** `eval/aggregate.py` turns the flat attempt records into the
  scorecard JSON. The live runner and the demo generator share this one code
  path, so they cannot drift apart.
- **Redaction.** With `redact: true` (the default), unsafe outputs are stored as
  a placeholder, never the payload. The scorecard shows verdicts, not harmful
  text.

## Configuration

Edit `eval/config.json` to change targets, the judge, generation params, and
concurrency. Model ids route verbatim through the gateway; if a target returns
404, check the exact id in the Respan dashboard and adjust the provider prefix.

## Responsible use

This is authorized, defensive evaluation (replicating Chao et al., 2023, on
public benchmarks) for measuring and reporting refusal robustness. The repo ships
only tame, abstracted behavior goals; AdvBench is fetched at runtime, never
vendored. Harmful outputs are redacted by default. The iterative PAIR attacker is
a documented extension point, not shipped: bring your own.

## Structure

```
eval/                python eval engine
  config.json        targets, judge, generation params
  behaviors.json     tame default red-team set
  attacks.py         attack framings (+ PAIR extension point)
  respan_client.py   gateway client
  judge.py           Llama Guard + JSON-judge fallback
  aggregate.py       attempts -> scorecard JSON (shared by live + demo)
  redteam.py         async runner / CLI
  advbench.py        optional public AdvBench loader
  make_sample.py     seed demo data (no key)
web/                 next.js + tailwind scorecard
  app/ components/ lib/ data/results.json
```

## Credits

PAIR (Chao et al., 2023). AdvBench (Zou et al., 2023). Llama Guard (Meta). Built
on [Respan](https://respan.ai).
