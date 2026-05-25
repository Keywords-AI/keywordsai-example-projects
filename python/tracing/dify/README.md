# Dify AI Tracing Examples

This directory contains examples of how to integrate Respan observability with
the Dify Python SDK request/response models using the local unpublished
`respan-exporter-dify` compatibility layer.

These examples run through the Respan gateway with only `RESPAN_API_KEY`.
No `DIFY_API_KEY` is required.

## Setup

1. Copy `.env.example` to `.env` and fill in your Respan credentials:
   ```bash
   cp .env.example .env
   ```

2. Install dependencies via poetry:
   ```bash
   poetry install
   ```

3. Run an example:
   ```bash
   poetry run python hello_world.py
   ```

## Notes

- `RESPAN_BASE_URL` defaults to `https://api.respan.ai/api`
- `RESPAN_MODEL` defaults to `gpt-4o-mini`
- The local SDK translates Dify request objects such as `ChatRequest` into
  OpenAI-compatible gateway calls under the hood
