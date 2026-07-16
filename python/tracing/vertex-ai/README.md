# Vertex AI tracing examples

These examples trace Vertex AI `GenerativeModel` and `ChatSession` calls with
`respan-instrumentation-vertexai`.

They load environment variables from the repository root `.env`. If
`GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, and Google application
credentials are available, the scripts use the real Vertex AI SDK. Otherwise
they install a small local compatibility stub so the tracing pipeline can be run
and verified without GCP credentials.

## Run

```bash
python run_examples.py
```

Every script sets an explicit workflow name:

- `vertexai_generate_content_example`
- `vertexai_chat_streaming_example`
