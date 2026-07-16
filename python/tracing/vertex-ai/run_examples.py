from __future__ import annotations

import importlib.util
from pathlib import Path


EXAMPLE_FILES = (
    "01_generate_content.py",
    "02_chat_streaming.py",
)


def _load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load example module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    for filename in EXAMPLE_FILES:
        module = _load_module(base_dir / filename)
        respan = module.Respan(instrumentations=[module.VertexAIInstrumentor()])
        try:
            module.run_example()
        finally:
            respan.flush()


if __name__ == "__main__":
    main()
