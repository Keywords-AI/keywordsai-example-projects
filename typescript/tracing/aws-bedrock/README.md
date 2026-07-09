# AWS Bedrock TypeScript tracing examples

These examples exercise `@respan/instrumentation-aws-bedrock` against the AWS
Bedrock Runtime TypeScript SDK surface.

They load `respan-example-projects/.env` from the repo root. Required:

- `RESPAN_API_KEY`

Optional:

- `RESPAN_BASE_URL`
- `RESPAN_EXAMPLE_RUN_ID`
- `AWS_BEDROCK_EXAMPLE_MODE=live`
- `AWS_REGION` or `AWS_DEFAULT_REGION`
- `AWS_BEDROCK_MODEL_ID`
- `AWS_BEDROCK_INVOKE_MODEL_ID`

By default the examples run in deterministic mock mode. Mock mode still uses the
real `@aws-sdk/client-bedrock-runtime` command classes and covers:

- `Converse`
- `InvokeModel`
- `ConverseStream`
- `InvokeModelWithResponseStream`
- a deterministic failure path with `error.message`

Run everything:

```bash
npm install
RESPAN_EXAMPLE_RUN_ID=aws-bedrock-ts-local npm run examples
```

Use live mode only when the repo-root `.env` has AWS credentials and Bedrock
model access:

```bash
AWS_BEDROCK_EXAMPLE_MODE=live npm run examples
```
