# Trace Structure Examples

This document shows the trace tree structure created by the example script.

## Example 1: E-Commerce Order Processing

**Total Spans:** 19 spans across 3 levels
**Models Used:** gpt-4o, gpt-4o-mini, gpt-3.5-turbo, claude-3-sonnet, gemini-1.5-flash

```
e-commerce_order_processing (root trace) [gpt-4o / openai]
│
├─ order_validation (Level 1) [gpt-4o / openai]
│  ├─ validate_inventory (Level 2) [gpt-4o / openai]
│  ├─ validate_payment (Level 2) [gpt-4o / openai]
│  └─ validate_shipping_address (Level 2) [gpt-4o / openai]
│
├─ order_processing (Level 1) [gpt-4o-mini / openai]
│  ├─ personalize_confirmation (Level 2) [gpt-4o-mini / openai]
│  │  ├─ openai.chat (Level 3) [gpt-4o / openai] - Email generation
│  │  └─ openai.chat (Level 3) [gpt-3.5-turbo / openai] - SMS generation
│  │
│  ├─ inventory_allocation (Level 2) [claude-3-sonnet-20240229 / anthropic]
│  │  ├─ reserve_item_A (Level 3) [claude-3-sonnet-20240229 / anthropic]
│  │  ├─ reserve_item_B (Level 3) [claude-3-sonnet-20240229 / anthropic]
│  │  └─ reserve_item_C (Level 3) [claude-3-sonnet-20240229 / anthropic]
│  │
│  └─ create_shipping_label (Level 2) [gpt-4o-mini / openai]
│     ├─ calculate_shipping_cost (Level 3) [gpt-4o-mini / openai]
│     └─ generate_label_pdf (Level 3) [gpt-4o-mini / openai]
│
└─ send_notifications (Level 1) [gemini-1.5-flash / google]
   ├─ send_email (Level 2) [gemini-1.5-flash / google]
   ├─ send_sms (Level 2) [gemini-1.5-flash / google]
   └─ send_push_notification (Level 2) [gemini-1.5-flash / google]
```

### Key Features:
- **3 top-level spans** (order_validation, order_processing, send_notifications)
- **Multiple children per parent** (e.g., order_processing has 3 children)
- **Deep nesting** (3 levels: trace → Level 1 → Level 2 → Level 3)
- **Multi-model workflow** - Uses OpenAI, Anthropic, and Google models
- **Model inheritance** - Children inherit parent's model unless overridden
- **ALL spans have model info** - No "unknown model" issues!

## Example 2: AI Assistant Conversation

**Total Spans:** 6 spans across 2 levels
**Models Used:** gpt-4o, gpt-3.5-turbo

```
ai_assistant_conversation (root trace) [gpt-4o / openai]
│
├─ conversation_turn_1 (Level 1) [gpt-4o / openai]
│  └─ openai.chat (Level 2) [gpt-4o / openai]
│
├─ conversation_turn_2 (Level 1) [gpt-4o / openai]
│  └─ openai.chat (Level 2) [gpt-4o / openai]
│
└─ conversation_turn_3 (Level 1) [gpt-4o / openai]
   └─ openai.chat (Level 2) [gpt-3.5-turbo / openai]
```

### Key Features:
- **3 conversation turns** (sequential spans)
- **LLM generation per turn** with different models
- **2-level nesting** (conversation turn → LLM call)
- **Model switching** - Last turn uses gpt-3.5-turbo instead of gpt-4o

## Creating Your Own Complex Traces

### Pattern 1: Parent with Multiple Children
```python
# Parent uses gpt-4o (default from env)
parent_span = trace.span(name="parent")

# Create multiple children (inherit parent's model by default)
child1 = parent_span.span(name="child_1")
child1.end()

child2 = parent_span.span(name="child_2")
child2.end()

child3 = parent_span.span(name="child_3")
child3.end()

parent_span.end()
```

### Pattern 2: Deep Nesting with Model Changes
```python
# Each level can have its own model
level1 = trace.span(name="level_1", model="gpt-4o", provider_id="openai")
level2 = level1.span(name="level_2", model="claude-3-sonnet-20240229", provider_id="anthropic")
level3 = level2.span(name="level_3", model="gemini-1.5-pro", provider_id="google")
level4 = level3.span(name="level_4", model="gpt-3.5-turbo", provider_id="openai")

# End from deepest to shallowest
level4.end()
level3.end()
level2.end()
level1.end()
```

### Pattern 3: Mixed LLM and Regular Spans (All with Models)
```python
# Workflow uses default model
workflow_span = trace.span(name="workflow")

# Regular span using default
prep_span = workflow_span.span(name="prepare_data")
prep_span.end()

# LLM generation with specific model
llm_gen = workflow_span.generation(
    name="openai.chat",
    model="gpt-4o",
    provider_id="openai"
)
llm_gen.end(output="Generated content")

# Post-processing with different model
post_span = workflow_span.span(
    name="post_process",
    model="gpt-3.5-turbo",
    provider_id="openai"
)
post_span.end()

workflow_span.end()
```

### Pattern 4: Multi-Model Workflow
```python
# Demonstrate using different AI providers in one trace
trace = langfuse.trace(name="multi_model_pipeline")

# Step 1: OpenAI GPT-4 for analysis
analysis = trace.span(
    name="analyze_requirements",
    model="gpt-4o",
    provider_id="openai"
)
analysis.end()

# Step 2: Anthropic Claude for content
content = trace.span(
    name="generate_content",
    model="claude-3-opus-20240229",
    provider_id="anthropic"
)
content.end()

# Step 3: Google Gemini for review
review = trace.span(
    name="review_quality",
    model="gemini-1.5-pro",
    provider_id="google"
)
review.end()

trace.end()
```

## Viewing in Keywords AI

After running the examples, go to:
**https://platform.keywordsai.co/ → Traces**

You'll see:
- ✅ Full trace tree with expandable nodes
- ✅ Parent-child relationships preserved
- ✅ Timing information for each span
- ✅ Input/output data at each level
- ✅ LLM calls properly tagged with model names

## Model Assignment Rules

### Default Behavior
- All spans use `DEFAULT_MODEL` and `DEFAULT_PROVIDER` from `.env`
- Set sensible defaults for your most common use case

### Override per Span
```python
span = trace.span(
    name="special_operation",
    model="claude-3-sonnet-20240229",  # Override default
    provider_id="anthropic"
)
```

### Available Models

**OpenAI (`provider_id="openai"`)**
- `gpt-4o` - Most capable, expensive
- `gpt-4o-mini` - Fast, cost-effective
- `gpt-4-turbo` - Previous generation flagship
- `gpt-3.5-turbo` - Fast, cheap, good for simple tasks

**Anthropic (`provider_id="anthropic"`)**
- `claude-3-opus-20240229` - Most capable Claude
- `claude-3-sonnet-20240229` - Balanced performance
- `claude-3-haiku-20240307` - Fast, lightweight

**Google (`provider_id="google"`)**
- `gemini-1.5-pro` - Most capable Gemini
- `gemini-1.5-flash` - Fast, efficient
- `gemini-pro` - Previous generation

## Tips for Complex Traces

1. **Always end child spans before parent spans**
2. **Use descriptive span names** (e.g., "validate_payment" not "step_2")
3. **Add input/output data** for better debugging
4. **Group related operations** under parent spans
5. **Specify models explicitly** for clarity (or rely on defaults)
6. **Mix models strategically** - use the right model for each task
7. **Keep nesting to 3-4 levels** for readability
8. **Use model inheritance** - set model on parent, children inherit
