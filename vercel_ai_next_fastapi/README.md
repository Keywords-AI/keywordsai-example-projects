# AI SDK, Next.js, and FastAPI Examples with KeywordsAI Telemetry

These examples show you how to use the [AI SDK](https://ai-sdk.dev/docs) with [Next.js](https://nextjs.org), [FastAPI](https://fastapi.tiangolo.com), and [KeywordsAI](https://keywordsai.co) for comprehensive AI observability and tracing.

## How to use

Execute [`create-next-app`](https://github.com/vercel/next.js/tree/canary/packages/create-next-app) with [npm](https://docs.npmjs.com/cli/init), [Yarn](https://yarnpkg.com/lang/en/docs/cli/create/), or [pnpm](https://pnpm.io) to bootstrap the example:

```bash
npx create-next-app --example https://github.com/Keywords-AI/keywordsai-example-projects/tree/main/vercel_ai_next_fastapi next-fastapi-app
```

```bash
yarn create next-app --example https://github.com/Keywords-AI/keywordsai-example-projects/tree/main/vercel_ai_next_fastapi next-fastapi-app
```

```bash
pnpm create next-app --example https://github.com/Keywords-AI/keywordsai-example-projects/tree/main/vercel_ai_next_fastapi next-fastapi-app
```

You will also need [Python 3.6+](https://www.python.org/downloads) and [virtualenv](https://virtualenv.pypa.io/en/latest/installation.html) installed to run the FastAPI server.

## Setup Instructions

### 1. Get API Keys

1. **OpenAI**: Sign up at [OpenAI's Developer Platform](https://platform.openai.com/signup) and get your API key from [the dashboard](https://platform.openai.com/account/api-keys).
2. **KeywordsAI**: Sign up at [KeywordsAI](https://keywordsai.co) and get your API key from [API Keys page](https://platform.keywordsai.co/platform/api/api-keys).

### 2. Environment Configuration

Set the required environment variables as shown in [the example env file](./.env.local.example) but in a new file called `.env.local`:

```bash
cp .env.local.example .env.local
```

Then edit `.env.local` with your actual API keys:

```env
OPENAI_API_KEY=your_openai_api_key_here
KEYWORDSAI_API_KEY=your_keywordsai_api_key_here
KEYWORDSAI_BASE_URL=https://api.keywordsai.co/api
```

### 3. Python Environment Setup

```bash
# Create and activate virtual environment
virtualenv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies (includes keywordsai-tracing)
pip install -r requirements.txt
# OR if using Poetry:
poetry install
```

### 4. Node.js Dependencies

```bash
pnpm install
# OR
npm install
# OR
yarn install
```

### 5. Run the Application

```bash
pnpm dev
```

The application will be available at `http://localhost:3000`.

### Add Keywords AI telemetry to trace the LLM calls (`api/index.py`)

The FastAPI backend includes:

```python
from keywordsai_tracing import KeywordsAITelemetry, workflow, get_client

# Initialize telemetry
telemetry = KeywordsAITelemetry()

@workflow(name="stream_text")
async def stream_text(messages: List[ClientMessage], protocol: str = "data"):
    # Automatic tracing of LLM calls and tool usage
    keywordsai_client = get_client()
    keywordsai_client.update_current_span(
        keywordsai_params={
            "metadata": {
                "project": "keywordsai-fastapi-example"
            }
        }
    )
    # ... rest of the implementation
```

## Learn More

To learn more about the technologies used in this example:

- [AI SDK Docs](https://ai-sdk.dev/docs) - AI SDK documentation and reference
- [Vercel AI Playground](https://ai-sdk.dev/playground) - try different models and choose the best one for your use case
- [Next.js Docs](https://nextjs.org/docs) - learn about Next.js features and API
- [FastAPI Docs](https://fastapi.tiangolo.com) - learn about FastAPI features and API
- [KeywordsAI Docs](https://docs.keywordsai.co) - comprehensive AI observability and monitoring
- [KeywordsAI Tracing Guide](https://docs.keywordsai.co/features/monitoring/traces/traces) - detailed tracing setup and usage

## Troubleshooting

### Common Issues

1. **Missing API Keys**: Ensure both `OPENAI_API_KEY` and `KEYWORDSAI_API_KEY` are set in `.env.local`
2. **Python Environment**: Make sure you're using Python 3.6+ and have activated your virtual environment
3. **Dependencies**: Run `pip install -r requirements.txt` or `poetry install` to ensure all Python packages are installed
4. **Port Conflicts**: The default port is 3000; change it in `package.json` if needed

### Viewing Traces

1. Go to your [KeywordsAI Platform](https://platform.keywordsai.co/)
2. Navigate to the "Signals" -> "Traces" section
3. Look for traces with the project name "keywordsai-fastapi-example"
4. Click on individual traces to see detailed execution flows

### No Traces Appearing?

If you don't see traces in your KeywordsAI dashboard:

1. **Check API Key**: Verify your `KEYWORDSAI_API_KEY` is correct
2. **Check Base URL**: Ensure `KEYWORDSAI_BASE_URL` is set to `https://api.keywordsai.co/api`
3. **Network Issues**: Check if your application can reach the KeywordsAI API
4. **Wait a moment**: Traces may take a few seconds to appear in the dashboard
5. **Check Console**: Look for any error messages in your terminal or browser console

## Contributing

Feel free to contribute to this example by submitting issues or pull requests to improve the integration between AI SDK, FastAPI, and KeywordsAI telemetry.
