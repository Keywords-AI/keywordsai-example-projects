# Hugging Face Respan Examples

These examples demonstrate Hugging Face Transformers tracing with
`respan-instrumentation-huggingface`. They load credentials from the repository
root `.env`.

## Setup

Install from local source while developing:

```bash
uv venv /tmp/respan-huggingface-example-venv
/tmp/respan-huggingface-example-venv/bin/python -m pip install \
  -e ../../../../respan/python-sdks/respan-sdk \
  -e ../../../../respan/python-sdks/respan-tracing \
  -e ../../../../respan/python-sdks/respan \
  -e ../../../../respan/python-sdks/instrumentations/respan-instrumentation-huggingface \
  -r requirements.txt
```

Run the full set:

```bash
python run_all.py
```

## Examples

| Script | Workflow name | Coverage |
| --- | --- | --- |
| `01_text_generation_pipeline.py` | `huggingface_01_text_generation_pipeline` | Single `TextGenerationPipeline.__call__`, model metadata, generation parameters, prompt, and completion |
| `02_batch_prompts.py` | `huggingface_02_batch_prompts` | Batch prompt indexing and multiple generated completions |
| `03_trace_content_disabled.py` | `huggingface_03_trace_content_disabled` | `TRACELOOP_TRACE_CONTENT=false` privacy mode with metadata-only generation spans |
