#!/usr/bin/env python3
"""Compatibility alias for the streaming Dify chat example."""

from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).with_name("02_chat_streaming.py")), run_name="__main__")
