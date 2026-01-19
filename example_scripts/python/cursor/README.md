# Keywords AI Cursor Integration

Real-time tracing of Cursor AI agent conversations using [Cursor Hooks](https://cursor.com/docs/agent/hooks).

## How It Works

Cursor hooks provide **structured JSON via stdin** for each event. We send spans **immediately in real-time** as events occur:

```
┌─────────────────────────────────────────────────────────────────┐
│                        Cursor Agent                              │
├─────────────────────────────────────────────────────────────────┤
│  User Query → Thinking → Tool Calls → File Edits → Response     │
│       ↓          ↓           ↓            ↓            ↓        │
│    [hooks fire with JSON input via stdin]                       │
└─────────────────────────────────────────────────────────────────┘
       │          │           │            │            │
       ↓          ↓           ↓            ↓            ↓
  ┌─────────┬─────────┬─────────────┬──────────┬──────────────┐
  │ Store   │ Send    │ Send        │ Send     │ Send Root    │
  │ Prompt  │ Thinking│ Shell/MCP/  │ File     │ Span with    │
  │         │ Span    │ File Spans  │ Edit     │ User I/O     │
  └─────────┴─────────┴─────────────┴──────────┴──────────────┘
       │          │           │            │            │
       └──────────┴───────────┴────────────┴────────────┘
                            ↓
                   Keywords AI Groups by
                   trace_unique_id on server
```

## Hooks Used

| Hook | JSON Input | Purpose |
|------|------------|---------|
| `beforeSubmitPrompt` | `{ prompt, attachments }` | **Store** user input for root span |
| `afterAgentThought` | `{ text, duration_ms }` | **Send** thinking span immediately |
| `afterShellExecution` | `{ command, output, duration }` | **Send** shell command span immediately |
| `afterFileEdit` | `{ file_path, edits }` | **Send** file edit span immediately |
| `afterMCPExecution` | `{ tool_name, tool_input, result_json, duration }` | **Send** MCP tool span immediately |
| `afterAgentResponse` | `{ text }` | **Send** root span with user input + agent output |
| `stop` | `{ status, loop_count }` | **Cleanup** state file |

**Common fields** (all hooks): `conversation_id`, `generation_id`, `model`, `cursor_version`

**Real-time Architecture**: Each hook sends its span immediately. Keywords AI groups spans with the same `trace_unique_id` on the server side into a hierarchical trace.

## Installation

### 1. Set Environment Variables

**Bash/Zsh:**
```bash
export KEYWORDSAI_API_KEY="your-api-key"
export TRACE_TO_KEYWORDSAI="true"
export CURSOR_KEYWORDSAI_DEBUG="true"  # Optional
```

**PowerShell:**
```powershell
$env:KEYWORDSAI_API_KEY = "your-api-key"
$env:TRACE_TO_KEYWORDSAI = "true"
```

### 2. Install Hook Script

```bash
mkdir -p ~/.cursor/hooks
cp keywordsai_hook.py ~/.cursor/hooks/
```

### 3. Configure Cursor Hooks

Copy `hooks.json.example` to `~/.cursor/hooks.json`:

```json
{
  "version": 1,
  "hooks": {
    "beforeSubmitPrompt": [
      { "command": "python ~/.cursor/hooks/keywordsai_hook.py" }
    ],
    "afterAgentThought": [
      { "command": "python ~/.cursor/hooks/keywordsai_hook.py" }
    ],
    "afterAgentResponse": [
      { "command": "python ~/.cursor/hooks/keywordsai_hook.py" }
    ],
    "afterShellExecution": [
      { "command": "python ~/.cursor/hooks/keywordsai_hook.py" }
    ],
    "afterFileEdit": [
      { "command": "python ~/.cursor/hooks/keywordsai_hook.py" }
    ],
    "afterMCPExecution": [
      { "command": "python ~/.cursor/hooks/keywordsai_hook.py" }
    ],
    "stop": [
      { "command": "python ~/.cursor/hooks/keywordsai_hook.py" }
    ]
  }
}
```

### 4. Restart Cursor

Restart to apply hooks.

## Trace Structure

Each agent response creates a trace with hierarchical spans:

```
Agent Response (root)
├── Thinking 1
├── Thinking 2
├── MCP: tool_name
├── Shell: command
├── Edit: filename
└── ...
```

**IDs:**
- `trace_unique_id` = `{conversation_id}_{generation_id}` (unique per turn)
- `span_parent_id` = root span ID (for children)
- `thread_identifier` = `conversation_id` (links all turns)

## Data Flow

1. **Store User Input**: `beforeSubmitPrompt` saves user prompt to state file (needed for root span later)
2. **Send Child Spans**: `afterAgentThought`, `afterShellExecution`, `afterFileEdit`, `afterMCPExecution` each send their span immediately
3. **Send Root Span**: `afterAgentResponse` sends root span with user input + agent output
4. **Cleanup**: State cleared after root span is sent
5. **Fallback**: `stop` hook cleans up any remaining state

**Key Point**: Spans are sent immediately as they occur, not batched. The Keywords AI server groups them by `trace_unique_id`.

## Debugging

```bash
# Watch logs
tail -f ~/.cursor/state/keywordsai_hook.log

# Check state
cat ~/.cursor/state/keywordsai_state.json

# Clear state (reprocess)
rm ~/.cursor/state/keywordsai_state.json
```

**PowerShell:**
```powershell
Get-Content "$env:USERPROFILE\.cursor\state\keywordsai_hook.log" -Tail 50 -Wait
```

## Common Issues

| Issue | Solution |
|-------|----------|
| No logs | Check `TRACE_TO_KEYWORDSAI=true` is set and environment variables are loaded |
| API errors (403) | Verify `KEYWORDSAI_API_KEY` is valid and not expired |
| Only root span | Ensure **all 7 hooks** are configured in `hooks.json` |
| Missing user input in root span | Verify `beforeSubmitPrompt` hook is configured and running |
| Missing thinking | Ensure `afterAgentThought` hook is active |
| Spans not grouping | All spans must have same `trace_unique_id` format: `{conversation_id}_{generation_id}` |

## Example Files

### Hook Input Example
See `example_transcript.json` for what **Cursor sends to the hook** via stdin for each event.

### Trace Output Example
See `example_trace_output.json` for how the **final trace appears in Keywords AI** after all spans are grouped.

## Files

| File | Purpose |
|------|---------|
| `keywordsai_hook.py` | Main hook script that processes events |
| `hooks.json.example` | Cursor hooks configuration template |
| `example_transcript.json` | Example of hook input data (what Cursor sends) |
| `example_trace_output.json` | Example of final trace structure (what appears in Keywords AI) |
| `requirements.txt` | Python dependencies (requests) |
| `README.md` | Documentation |

## References

- [Cursor Hooks Documentation](https://cursor.com/docs/agent/hooks)
- [Keywords AI Traces Ingest](https://docs.keywordsai.co/api-endpoints/observe/traces/traces-ingest-from-logs)
