"""Langfuse to KeywordsAI Integration using @observe decorators."""

import os
from pathlib import Path
from langfuse import observe, get_client
from dotenv import load_dotenv

env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

import opentelemetry.exporter.otlp.proto.http.trace_exporter as otlp_module
import requests
import json
from datetime import datetime, timezone

original_export = otlp_module.OTLPSpanExporter.export

def patched_export(self, spans):
    """Transform and export spans to KeywordsAI."""
    keywordsai_endpoint = "https://api.keywordsai.co/api/v1/traces/ingest"
    api_key = os.getenv("KEYWORDSAI_API_KEY")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    batch_logs = []
    
    for span in spans:
        attributes = dict(span.attributes) if span.attributes else {}
        
        langfuse_type = attributes.get("langfuse.observation.type", "span")
        log_type_mapping = {
            "span": "workflow" if not span.parent else "tool",
            "generation": "generation"
        }
        log_type = log_type_mapping.get(langfuse_type, "custom")
        
        start_time_ns = span.start_time
        end_time_ns = span.end_time
        start_time_iso = datetime.fromtimestamp(start_time_ns / 1e9, tz=timezone.utc).isoformat()
        timestamp_iso = datetime.fromtimestamp(end_time_ns / 1e9, tz=timezone.utc).isoformat()
        latency = (end_time_ns - start_time_ns) / 1e9
        
        payload = {
            "trace_unique_id": format(span.context.trace_id, '032x'),
            "span_unique_id": format(span.context.span_id, '016x'),
            "span_parent_id": format(span.parent.span_id, '016x') if span.parent else None,
            "span_name": span.name,
            "span_workflow_name": attributes.get("langfuse.trace.name", span.name),
            "log_type": log_type,
            "customer_identifier": attributes.get("user.id"),
            "timestamp": timestamp_iso,
            "start_time": start_time_iso,
            "latency": latency,
        }
        
        if "langfuse.observation.input" in attributes:
            input_str = attributes["langfuse.observation.input"]
            payload["input"] = input_str if isinstance(input_str, str) else json.dumps(input_str)
        
        if "langfuse.observation.output" in attributes:
            output_str = attributes["langfuse.observation.output"]
            payload["output"] = output_str if isinstance(output_str, str) else json.dumps(output_str)
        
        if "langfuse.observation.model.name" in attributes:
            payload["model"] = attributes["langfuse.observation.model.name"]
        
        if "langfuse.observation.usage_details" in attributes:
            try:
                usage = json.loads(attributes["langfuse.observation.usage_details"])
                payload["usage"] = {
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0)
                }
            except:
                pass
        
        batch_logs.append(payload)
    
    if batch_logs:
        try:
            response = requests.post(keywordsai_endpoint, json=batch_logs, headers=headers, timeout=10)
            response.raise_for_status()
        except Exception as e:
            print(f"Warning: Failed to send batch to KeywordsAI. Error: {e}")
    
    from opentelemetry.sdk.trace.export import SpanExportResult
    return SpanExportResult.SUCCESS

otlp_module.OTLPSpanExporter.export = patched_export

keywordsai_api_key = os.getenv("KEYWORDSAI_API_KEY")
keywordsai_base_url = os.getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api")

if not keywordsai_api_key:
    raise ValueError("KEYWORDSAI_API_KEY environment variable is required")

os.environ["LANGFUSE_PUBLIC_KEY"] = os.getenv("LANGFUSE_PUBLIC_KEY", "")
os.environ["LANGFUSE_SECRET_KEY"] = os.getenv("LANGFUSE_SECRET_KEY", "")
os.environ["LANGFUSE_BASE_URL"] = os.getenv("KEYWORDSAI_BASE_URL", "")

langfuse = get_client()


@observe(as_type="generation")
def chat_completion(user_message: str, model: str = "gpt-4o-mini"):
    """Simulate chat completion."""
    response = f"Response to: {user_message}"
    return response


@observe()
def search_web(query: str, source: str):
    """Search web from source."""
    print(f"   🔍 Searching {source}...")
    return {
        "source": source,
        "results": f"Search results for '{query}' from {source}"
    }


@observe()
def extract_information(search_result: dict):
    """Extract information from results."""
    source = search_result["source"]
    print(f"      📄 Extracting info from {source}...")
    return {
        "source": source,
        "extracted_info": f"Key facts from {source}",
        "relevance_score": 0.85
    }


@observe()
def validate_source(extracted_info: dict):
    """Validate source reliability."""
    source = extracted_info["source"]
    print(f"         ✓ Validating {source}...")
    return {
        "source": source,
        "is_valid": True,
        "confidence": 0.9
    }


@observe()
def research_topic(topic: str, source: str):
    """Research topic from source."""
    search_result = search_web(topic, source)
    extracted = extract_information(search_result)
    validated = validate_source(extracted)
    return validated


@observe()
def gather_research(query: str):
    """Gather research from multiple sources."""
    print(f"  📚 Gathering research from multiple sources...")
    sources = ["Wikipedia", "ArXiv", "Google Scholar"]
    results = []
    
    for source in sources:
        result = research_topic(query, source)
        results.append(result)
    
    return results


@observe(as_type="generation")
def synthesize_answer(query: str, research_results: list):
    """Synthesize answer from research."""
    print(f"  🧠 Synthesizing answer...")
    valid_sources = [r["source"] for r in research_results if r["is_valid"]]
    answer = f"Based on research from {', '.join(valid_sources)}, here's the answer about {query}..."
    return answer


@observe(as_type="generation")
def evaluate_answer(query: str, answer: str):
    """Evaluate answer quality."""
    print(f"  ⚖️  Evaluating answer quality...")
    return {
        "quality_score": 0.92,
        "completeness": 0.88,
        "accuracy": 0.95,
        "feedback": "High quality answer with good coverage"
    }


@observe()
def multi_step_workflow(query: str):
    """Multi-level research workflow."""
    print(f"\n🚀 Starting deep research workflow for: '{query}'\n")
    
    research_results = gather_research(query)
    answer = synthesize_answer(query, research_results)
    evaluation = evaluate_answer(query, answer)
    
    print(f"\n✅ Research complete!")
    print(f"   Quality Score: {evaluation['quality_score']}")
    
    return {
        "answer": answer,
        "evaluation": evaluation,
        "sources_used": len(research_results)
    }


@observe()
def simple_chat_example():
    """Simple chat example."""
    result = chat_completion("Hello, how are you?")
    print(f"\n📝 Created trace: simple-chat")
    print(f"🤖 Output: {result}\n")
    return result


def main():
    """Run Langfuse to KeywordsAI integration examples."""
    print("🚀 Initializing Langfuse with KeywordsAI base_url...\n")
    print(f"✅ Langfuse initialized with base_url: {keywordsai_base_url}")
    print(f"🔑 Using API Key: {keywordsai_api_key[:10]}...\n")
    
    print("=" * 60)
    print("Example 1: Simple Trace with LLM Generation")
    print("=" * 60)
    simple_chat_example()
    
    print("=" * 60)
    print("Example 2: Deep Research Workflow (Multi-Level Tree)")
    print("=" * 60)
    print("\nThis creates a deep trace tree with:")
    print("  - 3 parallel research branches (Wikipedia, ArXiv, Google Scholar)")
    print("  - Each branch has 3 levels: Search → Extract → Validate")
    print("  - Plus synthesis and evaluation steps")
    print("  - Total: ~13 spans across 4 levels\n")
    
    result2 = multi_step_workflow("What is quantum computing?")
    print(f"\n📝 Created deep trace: multi-step-workflow")
    print(f"🤖 Answer preview: {result2['answer'][:80]}...")
    print(f"   Sources: {result2['sources_used']}, Quality: {result2['evaluation']['quality_score']}\n")
    
    print("=" * 60)
    print("Flushing traces to KeywordsAI...")
    print("=" * 60)
    langfuse.flush()
    
    print("\n✅ All traces flushed!")
    print("\n📊 Check your KeywordsAI dashboard:")
    print("   https://platform.keywordsai.co/")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
