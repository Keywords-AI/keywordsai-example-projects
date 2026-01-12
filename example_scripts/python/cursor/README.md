# Keywords AI Cursor Integration

Real-time tracing of Cursor AI agent conversations using [Cursor Hooks](https://cursor.com/docs/agent/hooks).

## How It Works

Cursor hooks provide **structured JSON via stdin** for each event. We use this to build traces in real-time:

```
┌─────────────────────────────────────────────────────────────────┐
│                        Cursor Agent                              │
├─────────────────────────────────────────────────────────────────┤
│  User Query → Thinking → Tool Calls → File Edits → Response     │
│                   ↓          ↓            ↓            ↓        │
│              [hooks fire with JSON input via stdin]             │
└─────────────────────────────────────────────────────────────────┘
                                │
    ┌───────────────────────────┼───────────────────────────┐
    ↓                           ↓                           ↓
┌─────────┐              ┌─────────────┐             ┌──────────┐
│Thinking │              │Shell/MCP/   │             │ Response │
│ Hooks   │  accumulate  │File Hooks   │  accumulate │  Hook    │
│         │ ──────────→  │             │ ──────────→ │          │
└─────────┘              └─────────────┘             └──────────┘
                                                          │
                                                          ↓
                                                   ┌─────────────┐
                                                   │ Batch Send  │
                                                   │ All Spans   │
                                                   └─────────────┘
```

## Hooks Used

| Hook | JSON Input | Purpose |
|------|------------|---------|
| `afterAgentThought` | `{ text, duration_ms }` | Accumulate thinking blocks |
| `afterShellExecution` | `{ command, output, duration }` | Accumulate shell commands |
| `afterFileEdit` | `{ file_path, edits }` | Accumulate file edits |
| `afterMCPExecution` | `{ tool_name, tool_input, result_json, duration }` | Accumulate MCP tool calls |
| `afterAgentResponse` | `{ text }` | **Trigger**: Creates root span + sends all accumulated children |
| `stop` | `{ status, loop_count }` | **Fallback**: Flush any unsent data |

**Common fields** (all hooks): `conversation_id`, `generation_id`, `model`, `cursor_version`

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

1. **Accumulate Phase**: `afterAgentThought`, `afterShellExecution`, `afterFileEdit`, `afterMCPExecution` hooks store data in state file
2. **Send Phase**: `afterAgentResponse` creates root span + all child spans, sends batch to Keywords AI
3. **Cleanup**: State cleared after successful send
4. **Fallback**: `stop` hook flushes any remaining data

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
| No logs | Check `TRACE_TO_KEYWORDSAI=true` is set |
| API errors | Verify `KEYWORDSAI_API_KEY` |
| Only root span | Check other hooks are configured |
| Missing thinking | Ensure `afterAgentThought` hook is active |

## Files

| File | Purpose |
|------|---------|
| `keywordsai_hook.py` | Main hook script |
| `hooks.json.example` | Cursor hooks configuration |
| `README.md` | Documentation |

## References

- [Cursor Hooks Documentation](https://cursor.com/docs/agent/hooks)
- [Keywords AI Traces Ingest](https://docs.keywordsai.co/api-endpoints/observe/traces/traces-ingest-from-logs)
