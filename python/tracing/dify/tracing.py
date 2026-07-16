#!/usr/bin/env python3
"""Compatibility alias for the blocking Dify chat tracing example."""

from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).with_name("01_chat_blocking.py")), run_name="__main__")
