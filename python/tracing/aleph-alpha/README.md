# Aleph Alpha tracing examples

Examples for tracing the official Aleph Alpha Python SDK with Respan.

The scripts load environment variables from the repository root `.env`. If
`ALEPH_ALPHA_API_KEY` is set, they call the configured Aleph Alpha host directly.
If it is not set, they start a local Aleph-compatible mock server so the examples
still exercise the real `aleph-alpha-client` request paths and export real Respan
spans.

## Run

```bash
pip install -r requirements.txt
python run_all.py
```

Useful environment variables:

- `RESPAN_API_KEY`: Respan API key used for trace export.
- `RESPAN_BASE_URL`: Respan API base URL. Defaults to `https://api.respan.ai/api`.
- `ALEPH_ALPHA_API_KEY`: Optional direct Aleph Alpha API key.
- `ALEPH_ALPHA_HOST`: Optional Aleph Alpha API host.
- `ALEPH_ALPHA_MODEL`: Optional model id. Defaults to `pharia-1-chat`.
