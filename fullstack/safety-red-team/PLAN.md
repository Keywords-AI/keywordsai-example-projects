# Respan Red-Team — Project Plan

> An open-source **LLM safety red-teaming eval** that runs entirely through the
> **Respan gateway** and renders a polished **Safety Scorecard** web UI. Ported
> from my PAIR jailbreaking capstone. Ships as an example PR to
> `respanai/respan-example-projects` **and** a deployed demo + write-up.

This is my standout artifact for the **Respan Frontend SWE Intern** application.

---

## Why this wins the application

| The role wants | This project shows |
| --- | --- |
| Frontend (React, **Next.js**, Tailwind) | A polished scorecard UI in their exact stack, deployed to Vercel |
| Their product (observability + **evals**) | A real eval built on their gateway; every call traces into their dashboard |
| "Vibe coding" with AI tools | Built in ~1 day with Claude Code — the workflow they hire for |
| Something memorable | My **AI-safety / jailbreak** niche — nobody else in the pool has this angle |
| Real contribution | A **mergeable PR** into their example repo, not just a toy demo |

Distribution: deployed demo + 60-sec Loom + short Medium post + DM to the founders (Raymond/Andy).

---

## What it does

1. Pulls a set of harmful **behaviors** (tame defaults shipped; full public **AdvBench** loadable on demand).
2. Wraps each behavior in a library of published **attack framings** (roleplay, hypothetical, persona, formatting, + a `direct` control).
3. Sends every `(target model × behavior × framing)` through the **Respan gateway** (OpenAI-compatible, `https://api.respan.ai/api`). Every call auto-traces into Respan and is tagged with a shared `trace_group` + `metadata`.
4. **Judges** each response with **Llama Guard 4** via the gateway (JSON LLM-judge fallback), mirroring my capstone. Strips Qwen3 `<think>` tags (the bug from my blog post).
5. Aggregates into a **Safety Scorecard** and writes `web/data/results.json`.
6. The **Next.js UI** renders the scorecard: leaderboard, category×model heatmap, attack-effectiveness, attempts drill-down, auto-generated findings.

Targets & judge come straight from my capstone (`github.com/islamborghini/JailbreakingLLMs`):
Llama-3.1-8B (`llama-3.1-8b-instant`), Llama-4-Scout (`meta-llama/llama-4-scout-17b-16e-instruct`),
Qwen3-32B (`qwen/qwen3-32b`), Kimi-K2 (`moonshotai/kimi-k2-instruct`); judge `meta-llama/llama-guard-4-12b`.

---

## Architecture

```
behaviors.json ─┐
attacks.py ─────┤
                ▼
          eval/redteam.py ──(OpenAI SDK)──► Respan Gateway ──► target model
                │                                 │
                │◄──────── judged via ◄───────────┘ (Llama Guard through same gateway)
                ▼
        web/data/results.json ──► Next.js Scorecard (web/) ──► Vercel
                                          ▲
                       traces + scores ───┘ surface in the Respan dashboard
```

**Responsible-use posture (built in, and itself a selling point):**
- Harmful model outputs are **redacted by default** (`"redacted": true`); the UI shows verdicts, not payloads.
- Shipped behaviors are tame/abstracted; the two most acute categories are placeholders. Full AdvBench is *loaded*, never transcribed into the repo.
- Attack framings are generic and non-optimized. The iterative **PAIR** attacker is a documented *pluggable extension*, not shipped — you bring your own.
- This is authorized, defensive eval research (replicating Chao et al. 2023 on public benchmarks).

---

## Repository layout

```
respan/                         (this repo)
├── PLAN.md                     ← you are here
├── README.md                   PR-ready writeup (TODO: full version in M5)
├── eval/                       Python eval engine
│   ├── config.json             targets, judge, generation params
│   ├── behaviors.json          tame default red-team set (+ AdvBench loader)
│   ├── attacks.py              attack framings (+ PAIR extension point)
│   ├── judge.py                Llama Guard + JSON-judge fallback   [M1]
│   ├── respan_client.py        gateway client + best-effort score logging  [M1]
│   ├── redteam.py              async runner / CLI                  [M1]
│   ├── _synth.py               redacted demo-data generator (stdlib only) ✅
│   └── make_sample.py          seeds the UI without keys ✅
├── results/sample.json         committed redacted demo run ✅
└── web/                        Next.js scorecard                   [M3]
    └── data/results.json       data the UI renders ✅ (demo)
```

---

## Milestones (fits the ~8-hour budget)

- [x] **M0 — Repo + scaffold** · _done_
      git repo, config/behaviors/attacks, synthetic data engine, sample data, UI data contract.
- [ ] **M1 — Eval engine** · ~2h
      `redteam.py` async runner through the gateway; `judge.py` (Llama Guard + fallback, `<think>` strip);
      `respan_client.py` (trace grouping, metadata, best-effort Scores API); `--dry-run`, `--load-advbench`, `--limit`.
- [ ] **M2 — Finalize metrics** · ~20m · _decision below_
      Switch headline to **ASR** (attempt-level) for differentiation; keep coverage, queries-per-success, first-try.
- [ ] **M3 — Scorecard UI** · ~3h
      Next.js + Tailwind. Leaderboard · category×model heatmap · attack-effectiveness · attempts drill-down ·
      findings · run-meta with Respan trace links. Use the `frontend-design` skill. Deploy to Vercel.
- [ ] **M4 — Live run** · ~30m
      Run with my Respan key (4×10×5 = 200 calls, well under $1). Swap demo→live data. Capture screenshots +
      Respan dashboard trace links.
- [ ] **M5 — Ship** · ~1h
      Full README. Fork + PR to `respanai/respan-example-projects` (`fullstack/safety-red-team/`).
      60-sec Loom, short Medium post, DM the founders.

---

## Open decisions (need your call)

1. **Project / demo name** — working title is "Respan Red-Team." Alternatives: *RedScore*, *Guardrail Scorecard*, *SafeScan*.
2. **Live run now or later** — do you have a Respan API key handy (free credits at platform.respan.ai), or build UI on demo data first and run live in M4?
3. **PR target** — `fullstack/safety-red-team/` in their example repo (my default), or keep it a standalone repo we just link to them?

## Status
M0 complete. Awaiting go-ahead on M1 (and the decisions above).
