# Model Information in Every Span

## Overview

**Every span now includes model and provider information** - no more "unknown model" in Keywords AI!

## How It Works

### 1. Default Model from Environment
Set defaults in your `.env` file:
```bash
DEFAULT_MODEL=gpt-4o
DEFAULT_PROVIDER=openai
```

All spans will automatically use these values unless you specify otherwise.

### 2. Span-Specific Models
Override the default for specific spans:
```python
# This span uses gpt-4o-mini instead of the default
span = trace.span(
    name="fast_processing",
    model="gpt-4o-mini",
    provider_id="openai"
)
```

### 3. Hierarchical Model Inheritance
**Children automatically inherit their parent's model** - no need to specify repeatedly!

```python
# Parent uses Claude
parent = trace.span(
    name="main_workflow",
    model="claude-3-sonnet-20240229",
    provider_id="anthropic"
)

# Child 1 inherits Claude from parent
child1 = parent.span(name="step_1")  # Uses claude-3-sonnet-20240229

# Child 2 also inherits Claude from parent
child2 = parent.span(name="step_2")  # Uses claude-3-sonnet-20240229

# Child 3 overrides to use GPT-4
child3 = parent.span(
    name="step_3",
    model="gpt-4o",
    provider_id="openai"
)  # Uses gpt-4o

parent.end()
```

**Inheritance Priority:**
1. Explicit `model` in span creation → highest priority
2. Parent's model → inherits if not specified
3. DEFAULT_MODEL from env → fallback if no parent

## Benefits

✅ **No "unknown model" errors** - Every span is properly identified
✅ **Flexible** - Use defaults or specify per-span
✅ **Clear attribution** - See exactly which model handled each operation
✅ **Multi-model workflows** - Mix GPT-4, Claude, Gemini in one trace

## Example: Multi-Model Workflow

```python
from langfuse_to_keywordsai import LangfuseToKeywordsAI

langfuse = LangfuseToKeywordsAI()
trace = langfuse.trace(name="multi_model_workflow")

# Use GPT-4o for initial analysis (default from env)
analysis = trace.span(name="analyze_input")
analysis.end()

# Use Claude for content generation
generation = trace.span(
    name="generate_content",
    model="claude-3-opus-20240229",
    provider_id="anthropic"
)
generation.end()

# Use Gemini for final review
review = trace.span(
    name="review_output",
    model="gemini-1.5-pro",
    provider_id="google"
)
review.end()

trace.end()
langfuse.flush()
```

## What You'll See in Keywords AI

When you view this trace in Keywords AI:
- ✅ `analyze_input` → **gpt-4o** (from DEFAULT_MODEL)
- ✅ `generate_content` → **claude-3-opus-20240229**
- ✅ `review_output` → **gemini-1.5-pro**

Each span is properly tagged with its model!

## Supported Models

### OpenAI
- `gpt-4o`
- `gpt-4-turbo`
- `gpt-4o-mini`
- `gpt-3.5-turbo`

### Anthropic
- `claude-3-opus-20240229`
- `claude-3-sonnet-20240229`
- `claude-3-haiku-20240307`

### Google
- `gemini-pro`
- `gemini-1.5-pro`
- `gemini-1.5-flash`

### Cohere
- `command-r-plus`
- `command-r`

## Best Practices

1. **Set sensible defaults** in `.env` for your most common model
2. **Override when needed** for specific operations
3. **Use the right model** for each task (e.g., GPT-4 for complex, GPT-3.5 for simple)
4. **Group related operations** under parent spans for clarity

## Migration from Old Code

If you have existing code without model info:

**Before:**
```python
span = trace.span(name="processing")  # Would show "unknown model"
```

**After:**
```python
# Option 1: Set DEFAULT_MODEL in .env (recommended)
span = trace.span(name="processing")  # Uses DEFAULT_MODEL

# Option 2: Specify per-span
span = trace.span(
    name="processing",
    model="gpt-4o",
    provider_id="openai"
)
```

## Result

🎉 **100% of spans now have model information!**

No more "unknown model" - every operation in Keywords AI is properly attributed to its model.

## Real-World Example: Model Inheritance in Action

```python
from langfuse_to_keywordsai import LangfuseToKeywordsAI

langfuse = LangfuseToKeywordsAI()
trace = langfuse.trace(name="order_processing")

# Level 1: Default model (gpt-4o from env)
validation = trace.span(name="validation")
payment = validation.span(name="check_payment")  # Inherits gpt-4o
payment.end()
validation.end()

# Level 1: Override to use Claude
inventory = trace.span(
    name="inventory_management",
    model="claude-3-sonnet-20240229",
    provider_id="anthropic"
)

# Level 2: All children inherit Claude automatically
reserve_a = inventory.span(name="reserve_item_A")  # Uses claude-3-sonnet
reserve_a.end()

reserve_b = inventory.span(name="reserve_item_B")  # Uses claude-3-sonnet
reserve_b.end()

reserve_c = inventory.span(name="reserve_item_C")  # Uses claude-3-sonnet
reserve_c.end()

inventory.end()

# Level 1: Override to use Gemini
notifications = trace.span(
    name="notifications",
    model="gemini-1.5-flash",
    provider_id="google"
)

# Level 2: All children inherit Gemini
email = notifications.span(name="send_email")  # Uses gemini-1.5-flash
email.end()

sms = notifications.span(name="send_sms")  # Uses gemini-1.5-flash
sms.end()

notifications.end()
trace.end()
langfuse.flush()
```

### Result Hierarchy:
```
order_processing [gpt-4o]
├─ validation [gpt-4o]  ← inherited from trace
│  └─ check_payment [gpt-4o]  ← inherited from validation
├─ inventory_management [claude-3-sonnet]  ← explicit override
│  ├─ reserve_item_A [claude-3-sonnet]  ← inherited from inventory_management
│  ├─ reserve_item_B [claude-3-sonnet]  ← inherited from inventory_management
│  └─ reserve_item_C [claude-3-sonnet]  ← inherited from inventory_management
└─ notifications [gemini-1.5-flash]  ← explicit override
   ├─ send_email [gemini-1.5-flash]  ← inherited from notifications
   └─ send_sms [gemini-1.5-flash]  ← inherited from notifications
```

**Benefits:**
- ✅ Set model once at parent level
- ✅ All children automatically use same model
- ✅ Override only when needed
- ✅ Clear, consistent model usage per workflow section
