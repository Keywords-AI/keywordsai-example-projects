"""Seed the scorecard UI with a redacted demo run (no API keys needed).

    python3 eval/make_sample.py

Writes results/sample.json and web/data/results.json. A real run of
`eval/redteam.py` overwrites web/data/results.json with measured data of the
same shape.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import attacks  # noqa: E402
import _synth  # noqa: E402


def main() -> None:
    with open(os.path.join(HERE, "config.json")) as f:
        cfg = json.load(f)
    with open(os.path.join(HERE, "behaviors.json")) as f:
        behaviors = json.load(f)["behaviors"]

    results = _synth.synth_results(
        targets=cfg["targets"],
        behaviors=behaviors,
        attack_order=attacks.ORDER,
        judge=cfg["judge"]["primary"],
        gateway=os.environ.get("RESPAN_BASE_URL", "https://api.respan.ai/api"),
        trace_group=os.environ.get("RESPAN_TRACE_GROUP", "redteam-demo"),
    )

    for path in (
        os.path.join(ROOT, "results", "sample.json"),
        os.path.join(ROOT, "web", "data", "results.json"),
    ):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(results, f, indent=2)
        print("wrote", os.path.relpath(path, ROOT))


if __name__ == "__main__":
    main()
