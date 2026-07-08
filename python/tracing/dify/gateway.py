#!/usr/bin/env python3
"""Compatibility alias for the workflow/API Dify tracing example."""

from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).with_name("04_workflow_and_api.py")), run_name="__main__")
