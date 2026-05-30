# Respan Red-Team 🔴🛡️

An open-source **LLM safety red-teaming eval** that runs entirely through the
[Respan](https://www.respan.ai) gateway and renders a polished **Safety
Scorecard**. Every model call is traced into your Respan dashboard; harmful
outputs are redacted by default.

> Ported from a [PAIR jailbreaking replication](https://github.com/islamborghini/JailbreakingLLMs).
> Authorized, defensive eval research on public benchmarks.

**📋 See [PLAN.md](./PLAN.md) for the full roadmap and design.**

## Quickstart (demo, no API key)

```bash
python3 eval/make_sample.py      # seed redacted demo data
cd web && npm install && npm run dev   # view the scorecard   [M3]
```

## Real run

```bash
cp .env.example .env             # add your RESPAN_API_KEY
pip install -r eval/requirements.txt
python3 -m eval.redteam          # runs through the Respan gateway   [M1]
```

Status: **M0 (scaffold) complete** — see PLAN.md.
