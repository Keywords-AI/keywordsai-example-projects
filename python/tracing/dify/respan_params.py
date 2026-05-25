#!/usr/bin/env python3
"""
Respan Params — Add customer identifiers, metadata, and custom tags.

Shows how to pass `RespanParams` to the Dify client to attach business context
to your LLM calls, such as user IDs or custom metadata.
"""

import os
import uuid
from dotenv import load_dotenv
from dify_client.models import ChatRequest, ResponseMode
from respan_exporter_dify import create_client, flush_pending_exports
from respan_sdk.respan_types import RespanParams

load_dotenv(override=True)

def main():
    respan_api_key = os.getenv("RESPAN_API_KEY", "your-respan-api-key")
    
    respan_client = create_client(
        api_key=respan_api_key,
        gateway_base_url=os.getenv("RESPAN_BASE_URL"),
        gateway_model=os.getenv("RESPAN_MODEL"),
    )

    user_id = f"user-{uuid.uuid4().hex[:8]}"
    print(f"Sending message for customer {user_id}...")
    
    req = ChatRequest(
        query="What is observability in software engineering?",
        user=user_id,
        response_mode=ResponseMode.BLOCKING,
        inputs={},
    )
    
    # Create RespanParams to attach custom context
    params = RespanParams(
        customer_identifier=user_id,
        metadata={
            "feature": "search_assistant",
            "environment": "production",
            "tier": "enterprise"
        },
        session_identifier=f"session-{uuid.uuid4().hex[:8]}",
    )
    
    try:
        response = respan_client.chat_messages(req=req, respan_params=params)
        print("\nResponse:")
        print(response.answer)
    except Exception as e:
        print(f"\nError calling gateway: {e}")
    finally:
        flush_pending_exports(timeout=20)

if __name__ == "__main__":
    main()
