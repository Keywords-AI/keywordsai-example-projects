# SageMaker Respan Tracing Examples

These examples cover Respan's SageMaker Runtime instrumentation package.

```bash
cd /home/yuyang/KeywordsAI/respan-example-projects/python/tracing/sagemaker
pip install -r requirements.txt
python run_all.py
```

For local package development, install from source instead:

```bash
pip install -e /home/yuyang/KeywordsAI/respan/python-sdks/respan \
            -e /home/yuyang/KeywordsAI/respan/python-sdks/respan-sdk \
            -e /home/yuyang/KeywordsAI/respan/python-sdks/respan-tracing \
            -e /home/yuyang/KeywordsAI/respan/python-sdks/instrumentations/respan-instrumentation-sagemaker \
            boto3 python-dotenv
```

The scripts load `/home/yuyang/KeywordsAI/respan-example-projects/.env`.
When `SAGEMAKER_ENDPOINT_NAME` is absent, they run in boto3 `Stubber` mode so
the instrumentation can be validated without an AWS endpoint. Set
`SAGEMAKER_EXAMPLE_MODE=live` and `SAGEMAKER_ENDPOINT_NAME` to exercise a real
SageMaker Runtime endpoint.

Set `SAGEMAKER_MODEL_ID` to the Respan-recognized model name you want attached
to the trace for pricing. The examples fall back to `RESPAN_MODEL`, then
`gpt-4o-mini`. This value is sent as SageMaker `CustomAttributes`
(`respan_model=<model>`) so example request bodies stay compatible with real
endpoints.

## Scripts

| Script | Coverage |
| --- | --- |
| `01_invoke_endpoint_text.py` | `InvokeEndpoint` with text generation payloads and token usage |
| `02_invoke_endpoint_chat_tools.py` | `InvokeEndpoint` two-turn tool flow with a model tool call, decorated local tool execution, tool-result follow-up, and final answer |
| `03_invoke_endpoint_stream.py` | `InvokeEndpointWithResponseStream` with event-stream output |
| `04_invoke_endpoint_async.py` | `InvokeEndpointAsync` request and output-location metadata |
