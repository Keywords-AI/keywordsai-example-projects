import subprocess
import sys
from pathlib import Path

EXAMPLES = (
    "01_basic_completion.py",
    "02_streaming_completion.py",
    "03_respan_attributes.py",
    "04_tool_calling.py",
    "05_expected_error.py",
    "06_async_completion.py",
    "07_async_streaming.py",
)


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    for script_name in EXAMPLES:
        print(f"\n=== {script_name} ===")
        subprocess.run([sys.executable, str(base_dir / script_name)], check=True)


if __name__ == "__main__":
    main()
