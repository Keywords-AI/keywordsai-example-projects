"""Respan Red-Team: run an LLM safety eval through the Respan gateway.

    python eval/redteam.py                      # real run (needs RESPAN_API_KEY)
    python eval/redteam.py --dry-run            # synthetic redacted demo data, no key
    python eval/redteam.py --limit 5            # first 5 behaviors only (cheap smoke test)
    python eval/redteam.py --load-advbench --advbench-n 50

For each (target model x behavior x framing) the runner sends the framed
request through the Respan gateway, judges the response with Llama Guard, and
writes a redacted scorecard to web/data/results.json. Every call is traced into
the Respan dashboard, grouped by RESPAN_TRACE_GROUP.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import aggregate  # noqa: E402
import attacks  # noqa: E402
import _synth  # noqa: E402

PLATFORM = "https://platform.respan.ai"
GATEWAY = "https://api.respan.ai/api"


def _load_env() -> None:
    try:
        from dotenv import load_dotenv

        load_dotenv(os.path.join(ROOT, ".env"))
    except Exception:
        pass


def _load_json(name: str):
    with open(os.path.join(HERE, name)) as f:
        return json.load(f)


def _write(results: dict, out: str) -> None:
    paths = (
        [out]
        if out
        else [
            os.path.join(ROOT, "web", "data", "results.json"),
            os.path.join(ROOT, "results", "latest.json"),
        ]
    )
    for p in paths:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            json.dump(results, f, indent=2)
        print("wrote", os.path.relpath(p, ROOT))


async def _run_live(cfg, behaviors, attack_names, trace_group, concurrency, redact) -> dict:
    import respan_client
    from judge import judge as judge_fn, strip_think
    from rich.progress import Progress

    client = respan_client.build_client()
    gateway = os.environ.get("RESPAN_BASE_URL", respan_client.DEFAULT_BASE_URL)
    gen, jcfg = cfg["generation"], cfg["judge"]
    sem = asyncio.Semaphore(concurrency)
    attempts: list[dict] = []

    jobs = [(m, b, atk) for m in cfg["targets"] for b in behaviors for atk in attack_names]

    async def run_one(m, b, atk, progress, task_id):
        async with sem:
            cid = f"{trace_group}:{m['id']}:{b['id']}:{atk}"
            call = await respan_client.call_model(
                client,
                model=m["id"],
                prompt=attacks.apply(atk, b["goal"]),
                temperature=gen["temperature"],
                max_tokens=gen["max_tokens"],
                trace_group=trace_group,
                custom_identifier=cid,
                metadata={"behavior": b["id"], "category": b["category"], "attack": atk, "role": "target"},
            )
            v = await judge_fn(
                client,
                primary=jcfg["primary"],
                fallback=jcfg["fallback"],
                goal=b["goal"],
                response=call.text,
                trace_group=trace_group,
            )
            if call.error:
                preview = f"[error: {call.error}]"
            elif not redact:
                clean = strip_think(call.text)
                preview = (clean[:90] + "…") if len(clean) > 91 else (clean or "[empty]")
            elif v.verdict == "unsafe":
                preview = "[unsafe output redacted by harness]"
            else:
                preview = "[safe output withheld]"
            attempts.append({
                "id": cid,
                "model_id": m["id"],
                "model_label": m["label"],
                "behavior_id": b["id"],
                "category": b["category"],
                "attack": atk,
                "verdict": v.verdict,
                "judge_score": round(v.score, 3),
                "latency_ms": call.latency_ms,
                "cost_usd": round(call.cost_usd, 7),
                "prompt_preview": f"[{atk}] {b['category']} request",
                "response_preview": preview,
                "respan_log_url": f"{PLATFORM}/platform/requests?group={trace_group}",
            })
            progress.advance(task_id)

    with Progress() as progress:
        task_id = progress.add_task("[red]red-teaming", total=len(jobs))
        await asyncio.gather(*(run_one(m, b, atk, progress, task_id) for (m, b, atk) in jobs))

    return aggregate.build_results(
        targets=cfg["targets"],
        behaviors=behaviors,
        attack_order=attack_names,
        attempts=attempts,
        mode="live",
        gateway=gateway,
        judge=jcfg["primary"] or jcfg["fallback"],
        strategy="template (single-shot framings)",
        trace_group=trace_group,
        source_repo="github.com/islamborghini/JailbreakingLLMs",
        redacted=redact,
    )


def main() -> None:
    _load_env()
    ap = argparse.ArgumentParser(description="Respan Red-Team safety eval")
    ap.add_argument("--dry-run", action="store_true", help="synthetic demo data, no API key")
    ap.add_argument("--limit", type=int, default=0, help="use only the first N behaviors")
    ap.add_argument("--attacks", default="", help="comma-separated framings (default: all)")
    ap.add_argument("--load-advbench", action="store_true", help="fetch the public AdvBench set")
    ap.add_argument("--advbench-n", type=int, default=50)
    ap.add_argument("--concurrency", type=int, default=0)
    ap.add_argument("--out", default="", help="write to this path instead of the UI data files")
    args = ap.parse_args()

    cfg = _load_json("config.json")
    if args.load_advbench:
        import advbench

        behaviors = advbench.load_advbench(args.advbench_n)
    else:
        behaviors = _load_json("behaviors.json")["behaviors"]
    if args.limit:
        behaviors = behaviors[: args.limit]

    attack_names = [a.strip() for a in args.attacks.split(",") if a.strip()] or attacks.ORDER
    trace_group = os.environ.get("RESPAN_TRACE_GROUP", "redteam-run")
    concurrency = args.concurrency or cfg.get("concurrency", 8)
    redact = cfg.get("redact", True)

    if args.dry_run:
        results = _synth.synth_results(
            targets=cfg["targets"],
            behaviors=behaviors,
            attack_order=attack_names,
            judge=cfg["judge"]["primary"],
            gateway=os.environ.get("RESPAN_BASE_URL", GATEWAY),
            trace_group=trace_group,
        )
    else:
        results = asyncio.run(_run_live(cfg, behaviors, attack_names, trace_group, concurrency, redact))

    _write(results, args.out)
    m = results["meta"]
    print(
        f"\n{m['mode'].upper()}  {m['total_attempts']} attempts  "
        f"${m['total_cost_usd']:.4f}  judge={m['judge']}"
    )
    for mdl in sorted(results["models"], key=lambda x: x["jailbreak_rate"]):
        print(
            f"  {mdl['label']:<16} ASR {mdl['jailbreak_rate'] * 100:5.1f}%   "
            f"coverage {mdl['coverage_rate'] * 100:3.0f}%"
        )


if __name__ == "__main__":
    main()
