#!/usr/bin/env python3
"""
Keywords AI Hook for Claude Code

Sends Claude Code conversation traces to Keywords AI after each response.
Uses Claude Code's Stop hook to capture transcripts and convert them to Keywords AI spans.

Usage:
    Copy this file to ~/.claude/hooks/keywordsai_hook.py
    Configure in ~/.claude/settings.json (see .claude/settings.json.example)
    Enable per-project in .claude/settings.local.json (see .claude/settings.local.json.example)
"""

import json
import os
import sys
import requests
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Configuration
LOG_FILE = Path.home() / ".claude" / "state" / "keywordsai_hook.log"
STATE_FILE = Path.home() / ".claude" / "state" / "keywordsai_state.json"
DEBUG = os.environ.get("CC_KEYWORDSAI_DEBUG", "").lower() == "true"


def log(level: str, message: str) -> None:
    """Log a message to the log file."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} [{level}] {message}\n")


def debug(message: str) -> None:
    """Log a debug message (only if DEBUG is enabled)."""
    if DEBUG:
        log("DEBUG", message)


def load_state() -> Dict[str, Any]:
    """Load the state file containing session tracking info."""
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, IOError):
        return {}


def save_state(state: Dict[str, Any]) -> None:
    """Save the state file."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def get_content(msg: Dict[str, Any]) -> Any:
    """Extract content from a message."""
    if isinstance(msg, dict):
        if "message" in msg:
            return msg["message"].get("content")
        return msg.get("content")
    return None


def is_tool_result(msg: Dict[str, Any]) -> bool:
    """Check if a message contains tool results."""
    content = get_content(msg)
    if isinstance(content, list):
        return any(
            isinstance(item, dict) and item.get("type") == "tool_result"
            for item in content
        )
    return False


def get_tool_calls(msg: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract tool use blocks from a message."""
    content = get_content(msg)
    if isinstance(content, list):
        return [
            item for item in content
            if isinstance(item, dict) and item.get("type") == "tool_use"
        ]
    return []


def get_text_content(msg: Dict[str, Any]) -> str:
    """Extract text content from a message."""
    content = get_content(msg)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text_parts.append(item.get("text", ""))
            elif isinstance(item, str):
                text_parts.append(item)
        return "\n".join(text_parts)
    return ""


def format_tool_input(tool_name: str, tool_input: Any, max_length: int = 4000) -> str:
    """Format tool input for better readability."""
    if not tool_input:
        return ""
    
    # Handle Write/Edit tool - show file path and content preview
    if tool_name in ("Write", "Edit", "MultiEdit"):
        if isinstance(tool_input, dict):
            file_path = tool_input.get("file_path", tool_input.get("path", ""))
            content = tool_input.get("content", "")
            
            result = f"File: {file_path}\n"
            if content:
                content_preview = content[:2000] + "..." if len(content) > 2000 else content
                result += f"Content:\n{content_preview}"
            return result[:max_length]
    
    # Handle Read tool
    if tool_name == "Read":
        if isinstance(tool_input, dict):
            file_path = tool_input.get("file_path", tool_input.get("path", ""))
            return f"File: {file_path}"
    
    # Handle Bash/Shell tool
    if tool_name in ("Bash", "Shell"):
        if isinstance(tool_input, dict):
            command = tool_input.get("command", "")
            return f"Command: {command}"
    
    # Default: JSON dump with truncation
    try:
        result = json.dumps(tool_input, indent=2)
        if len(result) > max_length:
            result = result[:max_length] + "\n... (truncated)"
        return result
    except (TypeError, ValueError):
        return str(tool_input)[:max_length]


def format_tool_output(tool_name: str, tool_output: Any, max_length: int = 4000) -> str:
    """Format tool output for better readability."""
    if not tool_output:
        return ""
    
    # Handle string output directly
    if isinstance(tool_output, str):
        if len(tool_output) > max_length:
            return tool_output[:max_length] + "\n... (truncated)"
        return tool_output
    
    # Handle list of content blocks (common in Claude Code tool results)
    if isinstance(tool_output, list):
        parts = []
        total_length = 0
        
        for item in tool_output:
            if isinstance(item, dict):
                # Text content block
                if item.get("type") == "text":
                    text = item.get("text", "")
                    if total_length + len(text) > max_length:
                        remaining = max_length - total_length
                        if remaining > 100:
                            parts.append(text[:remaining] + "... (truncated)")
                        break
                    parts.append(text)
                    total_length += len(text)
                # Image or other type
                elif item.get("type") == "image":
                    parts.append("[Image output]")
                else:
                    # Try to extract any text-like content
                    text = str(item)[:500]
                    parts.append(text)
                    total_length += len(text)
            elif isinstance(item, str):
                if total_length + len(item) > max_length:
                    remaining = max_length - total_length
                    if remaining > 100:
                        parts.append(item[:remaining] + "... (truncated)")
                    break
                parts.append(item)
                total_length += len(item)
        
        return "\n".join(parts)
    
    # Handle dict output
    if isinstance(tool_output, dict):
        # Special handling for Write tool success/error
        if "success" in tool_output:
            return f"Success: {tool_output.get('success')}\n{tool_output.get('message', '')}"
        
        # Default JSON formatting
        try:
            result = json.dumps(tool_output, indent=2)
            if len(result) > max_length:
                result = result[:max_length] + "\n... (truncated)"
            return result
        except (TypeError, ValueError):
            return str(tool_output)[:max_length]
    
    return str(tool_output)[:max_length]


def merge_assistant_parts(parts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge multiple assistant message parts into one."""
    if not parts:
        return {}
    
    merged_content = []
    for part in parts:
        content = get_content(part)
        if isinstance(content, list):
            merged_content.extend(content)
        elif content:
            merged_content.append({"type": "text", "text": str(content)})
    
    # Use the structure from the first part
    result = parts[0].copy()
    if "message" in result:
        result["message"] = result["message"].copy()
        result["message"]["content"] = merged_content
    else:
        result["content"] = merged_content
    
    return result


def find_latest_transcript() -> Optional[Tuple[str, Path]]:
    """Find the most recently modified transcript file.
    
    Claude Code stores transcripts as *.jsonl files directly in the project directory.
    Main conversation files have UUID names, agent files have agent-*.jsonl names.
    The session ID is stored inside each JSON line.
    """
    projects_dir = Path.home() / ".claude" / "projects"
    
    if not projects_dir.exists():
        debug(f"Projects directory not found: {projects_dir}")
        return None
    
    latest_file = None
    latest_mtime = 0
    
    for project_dir in projects_dir.iterdir():
        if not project_dir.is_dir():
            continue
        
        # Look for all .jsonl files directly in the project directory
        for transcript_file in project_dir.glob("*.jsonl"):
            mtime = transcript_file.stat().st_mtime
            if mtime > latest_mtime:
                latest_mtime = mtime
                latest_file = transcript_file
    
    if latest_file:
        # Extract session ID from the first line of the file
        try:
            first_line = latest_file.read_text(encoding="utf-8").split("\n")[0]
            if first_line:
                first_msg = json.loads(first_line)
                session_id = first_msg.get("sessionId", latest_file.stem)
                debug(f"Found transcript: {latest_file}, session: {session_id}")
                return (session_id, latest_file)
        except (json.JSONDecodeError, IOError, IndexError, UnicodeDecodeError) as e:
            debug(f"Error reading transcript {latest_file}: {e}")
            return None
    
    debug("No transcript files found")
    return None


def parse_timestamp(ts_str: str) -> Optional[datetime]:
    """Parse ISO timestamp string to datetime."""
    try:
        # Handle both with and without timezone
        if ts_str.endswith("Z"):
            ts_str = ts_str[:-1] + "+00:00"
        return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def create_keywordsai_spans(
    session_id: str,
    turn_num: int,
    user_msg: Dict[str, Any],
    assistant_msgs: List[Dict[str, Any]],
    tool_results: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Create Keywords AI span logs for a single turn with all available metadata."""
    spans = []
    
    # Extract user text and timestamp
    user_text = get_text_content(user_msg)
    user_timestamp = user_msg.get("timestamp")
    user_time = parse_timestamp(user_timestamp) if user_timestamp else None
    
    # Extract final assistant text and get timing from first assistant message
    final_output = ""
    first_assistant_msg = None
    if assistant_msgs:
        final_output = get_text_content(assistant_msgs[-1])
        first_assistant_msg = assistant_msgs[0]
    
    # Get model, usage, and timing info from first assistant message
    model = "claude"
    usage = None
    request_id = None
    stop_reason = None
    assistant_timestamp = None
    assistant_time = None
    
    if first_assistant_msg and isinstance(first_assistant_msg, dict) and "message" in first_assistant_msg:
        msg_obj = first_assistant_msg["message"]
        model = msg_obj.get("model", "claude")
        usage = msg_obj.get("usage")
        request_id = msg_obj.get("requestId")
        stop_reason = msg_obj.get("stop_reason")
        assistant_timestamp = first_assistant_msg.get("timestamp")
        assistant_time = parse_timestamp(assistant_timestamp) if assistant_timestamp else None
    
    # Calculate timing
    start_time_str = user_timestamp if user_timestamp else (assistant_timestamp if assistant_timestamp else datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    timestamp_str = assistant_timestamp if assistant_timestamp else datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    
    # Calculate latency if we have both timestamps
    latency = None
    if user_time and assistant_time:
        latency = (assistant_time - user_time).total_seconds()
    
    # Extract messages for chat span
    prompt_messages = []
    if user_text:
        prompt_messages.append({"role": "user", "content": user_text})
    
    completion_message = None
    if final_output:
        completion_message = {"role": "assistant", "content": final_output}
    
    # Create trace ID for this turn
    trace_unique_id = f"{session_id}_turn_{turn_num}"
    
    # Naming convention: claudecode_{session_id} for workflow, claudecode_{trace_id} for root span
    workflow_name = f"claudecode_{session_id}"
    root_span_name = f"claudecode_{trace_unique_id}"
    thread_id = f"claudecode_{session_id}"
    
    # Build metadata with additional info
    metadata = {
        "claude_code_turn": turn_num,
    }
    if request_id:
        metadata["request_id"] = request_id
    if stop_reason:
        metadata["stop_reason"] = stop_reason
    
    # Build usage object with cache details
    usage_obj = None
    if usage:
        usage_obj = {
            "prompt_tokens": usage.get("input_tokens", 0),
            "completion_tokens": usage.get("output_tokens", 0),
        }
        total_tokens = usage_obj["prompt_tokens"] + usage_obj["completion_tokens"]
        if total_tokens > 0:
            usage_obj["total_tokens"] = total_tokens
        
        # Add cache details
        prompt_tokens_details = {}
        cache_creation = usage.get("cache_creation_input_tokens", 0)
        cache_read = usage.get("cache_read_input_tokens", 0)
        if cache_creation > 0:
            prompt_tokens_details["cache_creation_tokens"] = cache_creation
            usage_obj["cache_creation_prompt_tokens"] = cache_creation
        if cache_read > 0:
            prompt_tokens_details["cached_tokens"] = cache_read
        
        if prompt_tokens_details:
            usage_obj["prompt_tokens_details"] = prompt_tokens_details
        
        # Add service tier to metadata
        service_tier = usage.get("service_tier")
        if service_tier:
            metadata["service_tier"] = service_tier
    
    # Create chat span (root)
    chat_span_id = f"turn_{turn_num}_chat"
    chat_span = {
        "trace_unique_id": trace_unique_id,
        "thread_identifier": thread_id,
        "span_unique_id": chat_span_id,
        "span_parent_id": None,
        "span_name": root_span_name,
        "span_workflow_name": workflow_name,
        "log_type": "agent",
        "input": json.dumps(prompt_messages) if prompt_messages else "",
        "output": json.dumps(completion_message) if completion_message else "",
        "prompt_messages": prompt_messages,
        "completion_message": completion_message,
        "model": model,
        "timestamp": timestamp_str,
        "start_time": start_time_str,
        "metadata": metadata,
    }
    
    # Add usage if available
    if usage_obj:
        chat_span["prompt_tokens"] = usage_obj["prompt_tokens"]
        chat_span["completion_tokens"] = usage_obj["completion_tokens"]
        if "total_tokens" in usage_obj:
            chat_span["total_tokens"] = usage_obj["total_tokens"]
        if "cache_creation_prompt_tokens" in usage_obj:
            chat_span["cache_creation_prompt_tokens"] = usage_obj["cache_creation_prompt_tokens"]
        if "prompt_tokens_details" in usage_obj:
            chat_span["prompt_tokens_details"] = usage_obj["prompt_tokens_details"]
    
    # Add latency if calculated
    if latency is not None:
        chat_span["latency"] = latency
    
    spans.append(chat_span)
    
    # Extract thinking blocks and create spans for them
    thinking_spans = []
    for idx, assistant_msg in enumerate(assistant_msgs):
        if isinstance(assistant_msg, dict) and "message" in assistant_msg:
            content = assistant_msg["message"].get("content", [])
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "thinking":
                        thinking_text = item.get("thinking", "")
                        if thinking_text:
                            thinking_span_id = f"turn_{turn_num}_thinking_{len(thinking_spans) + 1}"
                            thinking_timestamp = assistant_msg.get("timestamp", timestamp_str)
                            thinking_spans.append({
                                "trace_unique_id": trace_unique_id,
                                "span_unique_id": thinking_span_id,
                                "span_parent_id": chat_span_id,
                                "span_name": f"Thinking {len(thinking_spans) + 1}",
                                "span_workflow_name": workflow_name,
                                "log_type": "generation",
                                "input": "",
                                "output": thinking_text,
                                "timestamp": thinking_timestamp,
                                "start_time": thinking_timestamp,
                            })
    
    spans.extend(thinking_spans)
    
    # Collect all tool calls and results with metadata
    tool_call_map = {}
    for assistant_msg in assistant_msgs:
        tool_calls = get_tool_calls(assistant_msg)
        for tool_call in tool_calls:
            tool_name = tool_call.get("name", "unknown")
            tool_input = tool_call.get("input", {})
            tool_id = tool_call.get("id", "")
            tool_call_map[tool_id] = {
                "name": tool_name,
                "input": tool_input,
                "id": tool_id,
                "timestamp": assistant_msg.get("timestamp") if isinstance(assistant_msg, dict) else None,
            }
    
    # Find matching tool results with metadata
    for tr in tool_results:
        tr_content = get_content(tr)
        tool_result_metadata = {}
        
        # Extract tool result metadata
        if isinstance(tr, dict):
            tool_use_result = tr.get("toolUseResult", {})
            if tool_use_result:
                if "durationMs" in tool_use_result:
                    tool_result_metadata["duration_ms"] = tool_use_result["durationMs"]
                if "numFiles" in tool_use_result:
                    tool_result_metadata["num_files"] = tool_use_result["numFiles"]
                if "filenames" in tool_use_result:
                    tool_result_metadata["filenames"] = tool_use_result["filenames"]
                if "truncated" in tool_use_result:
                    tool_result_metadata["truncated"] = tool_use_result["truncated"]
        
        if isinstance(tr_content, list):
            for item in tr_content:
                if isinstance(item, dict) and item.get("type") == "tool_result":
                    tool_use_id = item.get("tool_use_id")
                    if tool_use_id in tool_call_map:
                        tool_call_map[tool_use_id]["output"] = item.get("content")
                        tool_call_map[tool_use_id]["result_metadata"] = tool_result_metadata
                        tool_call_map[tool_use_id]["result_timestamp"] = tr.get("timestamp")
    
    # Create tool spans (children)
    tool_num = 0
    for tool_id, tool_data in tool_call_map.items():
        tool_num += 1
        tool_span_id = f"turn_{turn_num}_tool_{tool_num}"
        
        # Use tool result timestamp if available, otherwise use tool call timestamp
        tool_timestamp = tool_data.get("result_timestamp") or tool_data.get("timestamp") or timestamp_str
        tool_start_time = tool_data.get("timestamp") or start_time_str
        
        # Format input and output for better readability
        formatted_input = format_tool_input(tool_data['name'], tool_data["input"])
        formatted_output = format_tool_output(tool_data['name'], tool_data.get("output"))
        
        tool_span = {
            "trace_unique_id": trace_unique_id,
            "span_unique_id": tool_span_id,
            "span_parent_id": chat_span_id,
            "span_name": f"Tool: {tool_data['name']}",
            "span_workflow_name": workflow_name,
            "log_type": "tool",
            "input": formatted_input,
            "output": formatted_output,
            "timestamp": tool_timestamp,
            "start_time": tool_start_time,
        }
        
        # Add tool result metadata if available
        if tool_data.get("result_metadata"):
            tool_span["metadata"] = tool_data["result_metadata"]
            # Calculate latency if duration_ms is available
            duration_ms = tool_data["result_metadata"].get("duration_ms")
            if duration_ms:
                tool_span["latency"] = duration_ms / 1000.0  # Convert ms to seconds
        
        spans.append(tool_span)
    
    return spans


def process_transcript(
    session_id: str,
    transcript_file: Path,
    state: Dict[str, Any],
    api_key: str,
    base_url: str,
) -> int:
    """Process a transcript file and create traces for new turns."""
    # Get previous state for this session
    session_state = state.get(session_id, {})
    last_line = session_state.get("last_line", 0)
    turn_count = session_state.get("turn_count", 0)
    
    # Read transcript - need ALL messages to build conversation history
    lines = transcript_file.read_text(encoding="utf-8").strip().split("\n")
    total_lines = len(lines)
    
    if last_line >= total_lines:
        debug(f"No new lines to process (last: {last_line}, total: {total_lines})")
        return 0
    
    # Parse new messages
    new_messages = []
    for i in range(last_line, total_lines):
        try:
            if lines[i].strip():
                msg = json.loads(lines[i])
                new_messages.append(msg)
        except json.JSONDecodeError:
            continue
    
    if not new_messages:
        return 0
    
    debug(f"Processing {len(new_messages)} new messages")
    
    # Group messages into turns (user -> assistant(s) -> tool_results)
    turns_processed = 0
    current_user = None
    current_assistants = []
    current_assistant_parts = []
    current_msg_id = None
    current_tool_results = []
    
    for msg in new_messages:
        role = msg.get("type") or (msg.get("message", {}).get("role"))
        
        if role == "user":
            # Check if this is a tool result
            if is_tool_result(msg):
                current_tool_results.append(msg)
                continue
            
            # New user message - finalize previous turn
            if current_msg_id and current_assistant_parts:
                merged = merge_assistant_parts(current_assistant_parts)
                current_assistants.append(merged)
                current_assistant_parts = []
                current_msg_id = None
            
            if current_user and current_assistants:
                turns_processed += 1
                turn_num = turn_count + turns_processed
                spans = create_keywordsai_spans(
                    session_id, turn_num, current_user, current_assistants, current_tool_results
                )
                
                # Send spans to Keywords AI
                try:
                    response = requests.post(
                        f"{base_url}/v1/traces/ingest",
                        json=spans,
                        headers={"Authorization": f"Bearer {api_key}"},
                    )
                    response.raise_for_status()
                    debug(f"Sent {len(spans)} spans for turn {turn_num}")
                except Exception as e:
                    log("ERROR", f"Failed to send spans for turn {turn_num}: {e}")
            
            # Start new turn
            current_user = msg
            current_assistants = []
            current_assistant_parts = []
            current_msg_id = None
            current_tool_results = []
            
        elif role == "assistant":
            msg_id = None
            if isinstance(msg, dict) and "message" in msg:
                msg_id = msg["message"].get("id")
            
            if not msg_id:
                # No message ID, treat as continuation
                current_assistant_parts.append(msg)
            elif msg_id == current_msg_id:
                # Same message ID, add to current parts
                current_assistant_parts.append(msg)
            else:
                # New message ID - finalize previous message
                if current_msg_id and current_assistant_parts:
                    merged = merge_assistant_parts(current_assistant_parts)
                    current_assistants.append(merged)
                
                # Start new assistant message
                current_msg_id = msg_id
                current_assistant_parts = [msg]
    
    # Process final turn
    if current_msg_id and current_assistant_parts:
        merged = merge_assistant_parts(current_assistant_parts)
        current_assistants.append(merged)
    
    if current_user and current_assistants:
        turns_processed += 1
        turn_num = turn_count + turns_processed
        spans = create_keywordsai_spans(
            session_id, turn_num, current_user, current_assistants, current_tool_results
        )
        
        # Send spans to Keywords AI
        try:
            response = requests.post(
                f"{base_url}/v1/traces/ingest",
                json=spans,
                headers={"Authorization": f"Bearer {api_key}"},
            )
            response.raise_for_status()
            debug(f"Sent {len(spans)} spans for turn {turn_num}")
        except Exception as e:
            log("ERROR", f"Failed to send spans for turn {turn_num}: {e}")
    
    # Update state
    state[session_id] = {
        "last_line": total_lines,
        "turn_count": turn_count + turns_processed,
        "updated": datetime.now(timezone.utc).isoformat(),
    }
    save_state(state)
    
    return turns_processed


def main():
    script_start = datetime.now()
    debug("Hook started")
    
    # Check if tracing is enabled
    if os.environ.get("TRACE_TO_KEYWORDSAI", "").lower() != "true":
        debug("Tracing disabled (TRACE_TO_KEYWORDSAI != true)")
        sys.exit(0)
    
    # Check for required environment variables
    api_key = os.getenv("KEYWORDSAI_API_KEY")
    # Default: api.keywordsai.co | Enterprise: endpoint.keywordsai.co (set KEYWORDSAI_BASE_URL)
    base_url = os.getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api")
    
    if not api_key:
        log("ERROR", "Keywords AI API key not set (KEYWORDSAI_API_KEY)")
        sys.exit(0)
    
    # Load state
    state = load_state()
    
    # Find the most recently modified transcript
    result = find_latest_transcript()
    if not result:
        debug("No transcript file found")
        sys.exit(0)
    
    session_id, transcript_file = result
    
    if not transcript_file:
        debug("No transcript file found")
        sys.exit(0)
    
    debug(f"Processing session: {session_id}")
    
    # Process the transcript
    try:
        turns = process_transcript(session_id, transcript_file, state, api_key, base_url)
        
        # Log execution time
        duration = (datetime.now() - script_start).total_seconds()
        log("INFO", f"Processed {turns} turns in {duration:.1f}s")
        
        if duration > 180:
            log("WARN", f"Hook took {duration:.1f}s (>3min), consider optimizing")
            
    except Exception as e:
        log("ERROR", f"Failed to process transcript: {e}")
        import traceback
        debug(traceback.format_exc())
    
    sys.exit(0)


if __name__ == "__main__":
    main()
