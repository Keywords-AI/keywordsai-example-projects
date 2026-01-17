#!/usr/bin/env python3
"""
Span Buffering Example - KeywordsAI Tracing SDK

Manual control over span creation, buffering, and batch processing.
Note: This demonstrates the concept - actual API may vary in the Python SDK.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the same directory as this script
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path, override=True)

from keywordsai_tracing import KeywordsAITelemetry
from keywordsai_tracing.instruments import Instruments

# Initialize telemetry (block instruments without installed OpenTelemetry packages)
keywords_ai = KeywordsAITelemetry(
    app_name="span-buffering-demo",
    api_key=os.getenv("KEYWORDSAI_API_KEY", "demo-key"),
    base_url=os.getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api"),
    block_instruments={Instruments.ANTHROPIC, Instruments.REQUESTS, Instruments.URLLIB3},
)


class SpanBuffer:
    """Simple span buffer implementation for demonstration."""
    
    def __init__(self, trace_id: str):
        self.trace_id = trace_id
        self.spans = []
    
    def create_span(self, name: str, attributes: dict = None):
        """Create a span and add it to the buffer."""
        span = {
            "name": name,
            "trace_id": self.trace_id,
            "attributes": attributes or {},
        }
        self.spans.append(span)
        return span
    
    def get_all_spans(self):
        """Get all spans in the buffer."""
        return self.spans
    
    def clear_spans(self):
        """Clear all spans from the buffer."""
        self.spans = []


class SpanBufferManager:
    """Manager for span buffers."""
    
    def __init__(self):
        self.buffers = {}
    
    def create_buffer(self, trace_id: str) -> SpanBuffer:
        """Create a new span buffer for a trace."""
        buffer = SpanBuffer(trace_id)
        self.buffers[trace_id] = buffer
        return buffer
    
    def process_spans(self, spans: list) -> bool:
        """Process (export) spans - in a real implementation this would send to the backend."""
        print(f"   Processing {len(spans)} spans...")
        for span in spans:
            print(f"     - {span['name']}: {span.get('attributes', {})}")
        return True


def run_span_buffering_demo():
    """Demonstrate span buffering and manual span management."""
    print("Starting Span Buffering Demo\n")
    
    # Check if the SDK has a span buffer manager
    # Note: The actual API may differ in the Python SDK
    try:
        if hasattr(keywords_ai, 'get_span_buffer_manager'):
            manager = keywords_ai.get_span_buffer_manager()
        else:
            print("Using demonstration SpanBufferManager")
            manager = SpanBufferManager()
    except Exception:
        print("Using demonstration SpanBufferManager")
        manager = SpanBufferManager()
    
    trace_id = "manual-trace-123"
    buffer = manager.create_buffer(trace_id)
    print(f"Created buffer for trace: {trace_id}")
    
    # Create spans manually in buffer
    print("Creating spans manually in buffer...")
    buffer.create_span("initial_step", {
        "status": "completed",
        "duration_ms": 150,
        "step.type": "init"
    })
    
    buffer.create_span("processing_step", {
        "status": "completed",
        "duration_ms": 450,
        "step.type": "compute",
        "complexity": "high"
    })
    
    buffer.create_span("final_step", {
        "status": "completed",
        "duration_ms": 50,
        "step.type": "cleanup"
    })
    
    spans = buffer.get_all_spans()
    print(f"Total spans in buffer: {len(spans)}")
    print("   Span names:", ", ".join(s["name"] for s in spans))
    
    # Decide whether to export or discard
    should_export = True
    if should_export:
        print("\nManually processing (exporting) spans...")
        success = manager.process_spans(spans)
        print(f"Processing {'succeeded' if success else 'failed'}")
    else:
        print("Clearing spans without exporting...")
        buffer.clear_spans()
    
    print("\nSpan buffering demo completed.")


if __name__ == "__main__":
    run_span_buffering_demo()
