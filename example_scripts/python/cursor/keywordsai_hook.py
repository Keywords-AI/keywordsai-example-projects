#!/usr/bin/env python3
"""
Keywords AI Hook for Cursor

Real-time tracing - each hook sends its span immediately.
Spans with same trace_unique_id are grouped by Keywords AI server.

Hooks:
- beforeSubmitPrompt: Store user input + start time
- afterAgentThought: Send thinking span
- afterShellExecution: Send shell span
- afterFileEdit: Send file edit span
- afterMCPExecution: Send MCP tool span
- afterAgentResponse: Send root span with input + output
- stop: Cleanup

Usage:
    Copy to ~/.cursor/hooks/keywordsai_hook.py
    Configure hooks.json
    Set KEYWORDSAI_API_KEY and TRACE_TO_KEYWORDSAI=true
"""

import json
import os
import sys
import requests
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

# Configuration
LOG_FILE = Path.home() / ".cursor" / "state" / "keywordsai_hook.log"
STATE_FILE = Path.home() / ".cursor" / "state" / "keywordsai_state.json"
DEBUG = os.environ.get("CURSOR_KEYWORDSAI_DEBUG", "").lower() == "true"


def log(level: str, message: str) -> None:
    """Log to file."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} [{level}] {message}\n")


def debug(message: str) -> None:
    if DEBUG:
        log("DEBUG", message)


def load_state() -> Dict[str, Any]:
    """Load state."""
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except:
        return {}


def save_state(state: Dict[str, Any]) -> None:
    """Save state."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def read_hook_input() -> Optional[Dict[str, Any]]:
    """Read JSON input from Cursor via stdin."""
    try:
        data = sys.stdin.read()
        if not data.strip():
            return None
        return json.loads(data)
    except json.JSONDecodeError as e:
        debug(f"JSON parse error: {e}")
        return None
    except Exception as e:
        debug(f"Read error: {e}")
        return None


def get_timestamp() -> str:
    """Get current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def send_span(span: Dict, api_key: str, base_url: str) -> bool:
    """Send a single span to Keywords AI."""
    try:
        url = f"{base_url}/v1/traces/ingest"
        debug(f"Sending span '{span.get('span_name')}' to {url}")
        
        response = requests.post(
            url,
            json=[span],  # API expects array
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=10,
        )
        
        if response.status_code >= 400:
            log("ERROR", f"API error: {response.status_code} - {response.text}")
            return False
        
        debug(f"Span sent: {response.status_code}")
        return True
        
    except Exception as e:
        log("ERROR", f"Send failed: {e}")
        return False


def get_trace_id(hook_input: Dict) -> str:
    """Get trace ID from hook input."""
    conversation_id = hook_input.get("conversation_id", "unknown")
    generation_id = hook_input.get("generation_id", "unknown")
    return f"{conversation_id}_{generation_id}"


def get_root_span_id(hook_input: Dict) -> str:
    """Get root span ID for parent reference."""
    generation_id = hook_input.get("generation_id", "unknown")
    return f"{generation_id}_root"


def handle_before_submit_prompt(hook_input: Dict, state: Dict, api_key: str, base_url: str):
    """Store user input and start time for later use."""
    generation_id = hook_input.get("generation_id", "unknown")
    prompt = hook_input.get("prompt", "")
    attachments = hook_input.get("attachments", [])
    
    # Store for later when we create root span
    state[generation_id] = {
        "user_prompt": prompt,
        "attachments": len(attachments),
        "start_time": get_timestamp(),
        "child_count": 0,
    }
    
    save_state(state)
    debug(f"Stored user prompt for generation {generation_id}: {prompt[:50]}...")


def handle_after_agent_thought(hook_input: Dict, state: Dict, api_key: str, base_url: str):
    """Send thinking span immediately."""
    generation_id = hook_input.get("generation_id", "unknown")
    text = hook_input.get("text", "")
    duration_ms = hook_input.get("duration_ms", 100)
    
    # Update child count
    gen_state = state.get(generation_id, {"child_count": 0})
    gen_state["child_count"] = gen_state.get("child_count", 0) + 1
    child_idx = gen_state["child_count"]
    state[generation_id] = gen_state
    save_state(state)
    
    now = datetime.now(timezone.utc)
    latency_sec = duration_ms / 1000.0
    start_time = now - timedelta(seconds=latency_sec)
    
    span = {
        "trace_unique_id": get_trace_id(hook_input),
        "span_unique_id": f"{generation_id}_thinking_{child_idx}",
        "span_parent_id": get_root_span_id(hook_input),
        "span_name": f"Thinking {child_idx}",
        "log_type": "generation",
        "span_workflow_name": f"cursor_{hook_input.get('conversation_id', 'unknown')}",
        "span_path": f"thinking_{child_idx}",
        "input": json.dumps({"type": "reasoning"}),
        "output": text[:2000],
        "model": hook_input.get("model", "claude-3.5-sonnet"),
        "provider_id": "anthropic",
        "start_time": start_time.isoformat().replace("+00:00", "Z"),
        "timestamp": now.isoformat().replace("+00:00", "Z"),
        "latency": latency_sec,
        "metadata": {
            "duration_ms": duration_ms,
            "index": child_idx,
        },
    }
    
    send_span(span, api_key, base_url)
    log("INFO", f"Sent thinking span {child_idx}")


def handle_after_shell_execution(hook_input: Dict, state: Dict, api_key: str, base_url: str):
    """Send shell command span immediately."""
    generation_id = hook_input.get("generation_id", "unknown")
    command = hook_input.get("command", "")
    output = hook_input.get("output", "")
    duration = hook_input.get("duration", 100)
    
    # Update child count
    gen_state = state.get(generation_id, {"child_count": 0})
    gen_state["child_count"] = gen_state.get("child_count", 0) + 1
    child_idx = gen_state["child_count"]
    state[generation_id] = gen_state
    save_state(state)
    
    now = datetime.now(timezone.utc)
    latency_sec = duration / 1000.0
    start_time = now - timedelta(seconds=latency_sec)
    
    span = {
        "trace_unique_id": get_trace_id(hook_input),
        "span_unique_id": f"{generation_id}_shell_{child_idx}",
        "span_parent_id": get_root_span_id(hook_input),
        "span_name": f"Shell: {command[:30]}",
        "log_type": "tool",
        "span_workflow_name": f"cursor_{hook_input.get('conversation_id', 'unknown')}",
        "span_path": f"shell_{child_idx}",
        "input": json.dumps({"command": command}),
        "output": output[:1000],
        "start_time": start_time.isoformat().replace("+00:00", "Z"),
        "timestamp": now.isoformat().replace("+00:00", "Z"),
        "latency": latency_sec,
        "metadata": {
            "command": command,
            "duration_ms": duration,
        },
    }
    
    send_span(span, api_key, base_url)
    log("INFO", f"Sent shell span: {command[:30]}")


def format_edits_output(edits: list, max_length: int = 4000) -> str:
    """Format edits array into readable output with size limit."""
    if not edits:
        return "No edits"
    
    output_parts = []
    total_length = 0
    
    for i, edit in enumerate(edits):
        # Handle different edit formats from Cursor
        if isinstance(edit, dict):
            # Try to extract meaningful info from edit object
            old_text = edit.get("oldText", edit.get("old", ""))
            new_text = edit.get("newText", edit.get("new", ""))
            start_line = edit.get("startLine", edit.get("start", {}).get("line", "?"))
            end_line = edit.get("endLine", edit.get("end", {}).get("line", "?"))
            
            if old_text or new_text:
                # Show diff-style output
                edit_str = f"[Edit {i+1}] Lines {start_line}-{end_line}\n"
                if old_text:
                    # Truncate long text
                    old_preview = old_text[:500] + "..." if len(old_text) > 500 else old_text
                    edit_str += f"- {old_preview}\n"
                if new_text:
                    new_preview = new_text[:500] + "..." if len(new_text) > 500 else new_text
                    edit_str += f"+ {new_preview}"
            else:
                # Fallback: dump the edit object
                edit_str = f"[Edit {i+1}]: {json.dumps(edit)[:300]}"
        elif isinstance(edit, str):
            edit_str = f"[Edit {i+1}]: {edit[:300]}"
        else:
            edit_str = f"[Edit {i+1}]: {str(edit)[:300]}"
        
        # Check if we'd exceed max length
        if total_length + len(edit_str) + 10 > max_length:
            remaining = len(edits) - i
            output_parts.append(f"\n... and {remaining} more edit(s)")
            break
        
        output_parts.append(edit_str)
        total_length += len(edit_str) + 2  # +2 for separator
    
    return "\n\n".join(output_parts)


def handle_after_file_edit(hook_input: Dict, state: Dict, api_key: str, base_url: str):
    """Send file edit span immediately."""
    generation_id = hook_input.get("generation_id", "unknown")
    file_path = hook_input.get("file_path", "")
    edits = hook_input.get("edits", [])
    
    # Update child count
    gen_state = state.get(generation_id, {"child_count": 0})
    gen_state["child_count"] = gen_state.get("child_count", 0) + 1
    child_idx = gen_state["child_count"]
    state[generation_id] = gen_state
    save_state(state)
    
    now = datetime.now(timezone.utc)
    latency_sec = 0.1  # File edits don't have duration from Cursor
    start_time = now - timedelta(seconds=latency_sec)
    file_name = Path(file_path).name
    
    # Format edits for better visibility
    edits_output = format_edits_output(edits)
    
    # Also store raw edits in metadata (truncated)
    edits_preview = []
    for edit in edits[:5]:  # First 5 edits for metadata
        if isinstance(edit, dict):
            edits_preview.append({
                "old": str(edit.get("oldText", edit.get("old", "")))[:200],
                "new": str(edit.get("newText", edit.get("new", "")))[:200],
                "startLine": edit.get("startLine", edit.get("start", {}).get("line")),
                "endLine": edit.get("endLine", edit.get("end", {}).get("line")),
            })
    
    span = {
        "trace_unique_id": get_trace_id(hook_input),
        "span_unique_id": f"{generation_id}_file_{child_idx}",
        "span_parent_id": get_root_span_id(hook_input),
        "span_name": f"Edit: {file_name}",
        "log_type": "tool",
        "span_workflow_name": f"cursor_{hook_input.get('conversation_id', 'unknown')}",
        "span_path": f"file_{child_idx}",
        "input": json.dumps({"file": file_path, "edit_count": len(edits)}),
        "output": edits_output,
        "start_time": start_time.isoformat().replace("+00:00", "Z"),
        "timestamp": now.isoformat().replace("+00:00", "Z"),
        "latency": latency_sec,
        "metadata": {
            "file_path": file_path,
            "edit_count": len(edits),
            "edits_preview": edits_preview,
        },
    }
    
    send_span(span, api_key, base_url)
    log("INFO", f"Sent file edit span: {file_name} ({len(edits)} edits)")


def handle_after_mcp_execution(hook_input: Dict, state: Dict, api_key: str, base_url: str):
    """Send MCP tool span immediately."""
    generation_id = hook_input.get("generation_id", "unknown")
    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", "{}")
    result_json = hook_input.get("result_json", "{}")
    duration = hook_input.get("duration", 100)
    
    # Update child count
    gen_state = state.get(generation_id, {"child_count": 0})
    gen_state["child_count"] = gen_state.get("child_count", 0) + 1
    child_idx = gen_state["child_count"]
    state[generation_id] = gen_state
    save_state(state)
    
    now = datetime.now(timezone.utc)
    latency_sec = duration / 1000.0
    start_time = now - timedelta(seconds=latency_sec)
    
    span = {
        "trace_unique_id": get_trace_id(hook_input),
        "span_unique_id": f"{generation_id}_mcp_{child_idx}",
        "span_parent_id": get_root_span_id(hook_input),
        "span_name": f"MCP: {tool_name}",
        "log_type": "tool",
        "span_workflow_name": f"cursor_{hook_input.get('conversation_id', 'unknown')}",
        "span_path": f"mcp_{child_idx}",
        "input": tool_input,
        "output": result_json[:1000],
        "start_time": start_time.isoformat().replace("+00:00", "Z"),
        "timestamp": now.isoformat().replace("+00:00", "Z"),
        "latency": latency_sec,
        "metadata": {
            "tool_name": tool_name,
            "duration_ms": duration,
        },
    }
    
    send_span(span, api_key, base_url)
    log("INFO", f"Sent MCP span: {tool_name}")


def handle_after_agent_response(hook_input: Dict, state: Dict, api_key: str, base_url: str):
    """Send root span with user input and agent output."""
    generation_id = hook_input.get("generation_id", "unknown")
    conversation_id = hook_input.get("conversation_id", "unknown")
    response_text = hook_input.get("text", "")
    
    # Get stored state (user prompt, start time)
    gen_state = state.get(generation_id, {})
    user_prompt = gen_state.get("user_prompt", "[No prompt captured]")
    start_time = gen_state.get("start_time", get_timestamp())
    child_count = gen_state.get("child_count", 0)
    
    now = get_timestamp()
    
    # Build messages for chat format
    prompt_messages = [{"role": "user", "content": user_prompt}]
    completion_message = {"role": "assistant", "content": response_text}
    
    span = {
        "trace_unique_id": get_trace_id(hook_input),
        "span_unique_id": get_root_span_id(hook_input),
        "span_parent_id": None,  # Root span has no parent
        "span_name": f"cursor_{generation_id}",
        "log_type": "agent",
        "span_workflow_name": f"cursor_{conversation_id}",
        "span_path": "",
        "thread_identifier": f"cursor_{conversation_id}",
        "input": json.dumps(prompt_messages),
        "output": json.dumps(completion_message),
        "prompt_messages": prompt_messages,
        "completion_message": completion_message,
        "model": hook_input.get("model", "claude-3.5-sonnet"),
        "provider_id": "anthropic",
        "start_time": start_time,
        "timestamp": now,
        "latency": 0,  # Will be calculated from timestamps
        "metadata": {
            "child_count": child_count,
            "cursor_version": hook_input.get("cursor_version", ""),
        },
    }
    
    send_span(span, api_key, base_url)
    log("INFO", f"Sent root span with {child_count} children")
    
    # Clean up state for this generation
    if generation_id in state:
        del state[generation_id]
        save_state(state)


def handle_stop(hook_input: Dict, state: Dict, api_key: str, base_url: str):
    """Clean up any remaining state."""
    status = hook_input.get("status", "unknown")
    debug(f"Stop hook - status: {status}")
    
    # If there's any generation with stored prompt but no response sent,
    # we could send a partial trace here, but for now just clean up
    generation_id = hook_input.get("generation_id", "")
    if generation_id and generation_id in state:
        debug(f"Cleaning up state for {generation_id}")
        del state[generation_id]
        save_state(state)


def main():
    debug("Hook started")
    
    # Check if enabled
    if os.environ.get("TRACE_TO_KEYWORDSAI", "").lower() != "true":
        debug("Tracing disabled")
        sys.exit(0)
    
    # Get config
    api_key = os.getenv("KEYWORDSAI_API_KEY")
    # Default: api.keywordsai.co | Enterprise: endpoint.keywordsai.co (set KEYWORDSAI_BASE_URL)
    base_url = os.getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api")
    
    if not api_key:
        log("ERROR", "KEYWORDSAI_API_KEY not set")
        sys.exit(0)
    
    # Read hook input
    hook_input = read_hook_input()
    if not hook_input:
        debug("No input received")
        sys.exit(0)
    
    hook_name = hook_input.get("hook_event_name", "")
    debug(f"Hook: {hook_name}")
    
    # Load state
    state = load_state()
    
    # Route to handler
    handlers = {
        "beforeSubmitPrompt": handle_before_submit_prompt,
        "afterAgentThought": handle_after_agent_thought,
        "afterAgentResponse": handle_after_agent_response,
        "afterShellExecution": handle_after_shell_execution,
        "afterFileEdit": handle_after_file_edit,
        "afterMCPExecution": handle_after_mcp_execution,
        "stop": handle_stop,
    }
    
    handler = handlers.get(hook_name)
    if handler:
        try:
            handler(hook_input, state, api_key, base_url)
        except Exception as e:
            log("ERROR", f"Handler {hook_name} failed: {e}")
            import traceback
            debug(traceback.format_exc())
    else:
        debug(f"No handler for hook: {hook_name}")
    
    sys.exit(0)


if __name__ == "__main__":
    main()
