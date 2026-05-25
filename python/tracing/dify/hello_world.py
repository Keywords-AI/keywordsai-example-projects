#!/usr/bin/env python3
"""
Hello World — Simple Dify integration example.

Bare minimum sanity check — does this integration work?
Shows how to use the local unpublished Dify compatibility layer to send
a Dify-style request through the Respan gateway with only `RESPAN_API_KEY`.
"""

import os
import uuid
from dotenv import load_dotenv
from dify_client.models import ChatRequest, ResponseMode
from respan_exporter_dify import create_client, flush_pending_exports

# Load environment variables from .env
load_dotenv(override=True)

def main():
    respan_api_key = os.getenv("RESPAN_API_KEY", "your-respan-api-key")
    respan_client = create_client(
        api_key=respan_api_key,
        gateway_base_url=os.getenv("RESPAN_BASE_URL"),
        gateway_model=os.getenv("RESPAN_MODEL"),
    )

    user_id = f"user-{uuid.uuid4().hex[:8]}"
    print(f"Sending message as {user_id}...")
    
    req = ChatRequest(
        query="Hello! What's the capital of France?",
        user=user_id,
        response_mode=ResponseMode.BLOCKING,
        inputs={},
    )
    
    try:
        response = respan_client.chat_messages(req=req)
        print("\nResponse from Respan Gateway:")
        print(response.answer)
    except Exception as e:
        print(f"\nError calling gateway: {e}")
    finally:
        flush_pending_exports(timeout=20)

if __name__ == "__main__":
    main()
