"""Backward-compatible entry point for the basic CrewAI example."""

from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).with_name("01_basic_crew.py")), run_name="__main__")
