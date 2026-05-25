#!/usr/bin/env python3
"""
Streaming — Stream responses from Dify.

Shows how to use `ResponseMode.STREAMING` with the wrapped client.
The exporter automatically collects the streamed chunks and logs them
to Respan when the stream finishes.
"""

import os
import uuid
import sys
from dotenv import load_dotenv
from dify_client.models import ChatRequest, ResponseMode
from respan_exporter_dify import create_client, flush_pending_exports

load_dotenv(override=True)

def main():
    respan_api_key = os.getenv("RESPAN_API_KEY", "your-respan-api-key")
    
    respan_client = create_client(
        api_key=respan_api_key,
        gateway_base_url=os.getenv("RESPAN_BASE_URL"),
        gateway_model=os.getenv("RESPAN_MODEL", "gpt-4o"),
    )

    user_id = f"user-{uuid.uuid4().hex[:8]}"
    print(f"Sending streaming request as {user_id}...")
    
    req = ChatRequest(
        query="Write a 3-paragraph story about a robot learning to paint.",
        user=user_id,
        response_mode=ResponseMode.STREAMING,
        inputs={},
    )
    
    try:
        response_stream = respan_client.chat_messages(req=req)
        
        print("\nStreaming Response:")
        for chunk in response_stream:
            if hasattr(chunk, "answer"):
                sys.stdout.write(chunk.answer)
                sys.stdout.flush()
                
        print("\n\nStream finished. Event logged to Respan.")
    except Exception as e:
        print(f"\nError calling gateway: {e}")
    finally:
        flush_pending_exports(timeout=20)

if __name__ == "__main__":
    main()
