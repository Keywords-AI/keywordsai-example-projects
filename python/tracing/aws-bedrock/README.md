# AWS Bedrock Runtime tracing examples

These examples trace `boto3` Bedrock Runtime calls with
`respan-instrumentation-aws-bedrock`.

They load environment variables from the repository root `.env`. If AWS
credentials are not present, the examples use `botocore.stub.Stubber` so the
Respan trace path can still be exercised locally.

## Run

```bash
python 01_invoke_model.py
python 02_converse.py
python 03_converse_stream.py
```

Set `AWS_BEDROCK_USE_STUBS=false` to force live Bedrock calls. For live calls,
configure AWS credentials and optionally set `AWS_REGION` and
`AWS_BEDROCK_MODEL_ID`.
