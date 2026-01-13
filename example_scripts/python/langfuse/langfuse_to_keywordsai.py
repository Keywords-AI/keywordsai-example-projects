#!/usr/bin/env python3
"""
Langfuse to Keywords AI Integration

Simple script that sends Langfuse traces to Keywords AI automatically.
This intercepts Langfuse SDK calls and forwards them to Keywords AI's trace ingest endpoint.

Setup:
    pip install langfuse requests python-dotenv
    
Environment Variables:
    KEYWORDSAI_API_KEY - Your Keywords AI API key (required)
    KEYWORDSAI_BASE_URL - Keywords AI base URL (optional, defaults to https://api.keywordsai.co/api)
    LANGFUSE_PUBLIC_KEY - Langfuse public key (optional, for dual logging)
    LANGFUSE_SECRET_KEY - Langfuse secret key (optional, for dual logging)
    LANGFUSE_HOST - Langfuse host (optional)

Usage:
    # All spans and generations include model information
    # Either specify explicitly or use defaults from environment
    
    # Using default model (from DEFAULT_MODEL and DEFAULT_PROVIDER env vars)
    span = trace.span(name="data_processing")
    
    # Specifying a custom model for a span
    span = trace.span(
        name="data_processing",
        model="gpt-4o-mini",
        provider_id="openai"
    )
    
    # LLM generations with specific models
    generation = trace.generation(
        name="openai.chat",
        model="gpt-4o",
        provider_id="openai"
    )
"""

import os
import json
import requests
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

load_dotenv(override=True)

try:
    from langfuse import Langfuse
except ImportError:
    raise ImportError("langfuse is required. Install with: pip install langfuse")


class LangfuseToKeywordsAI:
    """Simple wrapper that forwards Langfuse traces to Keywords AI."""
    
    def __init__(self):
        # Keywords AI configuration
        self.keywordsai_api_key = os.getenv("KEYWORDSAI_API_KEY")
        self.keywordsai_base_url = os.getenv("KEYWORDSAI_BASE_URL", "https://api.keywordsai.co/api")
        
        if not self.keywordsai_api_key:
            raise ValueError("KEYWORDSAI_API_KEY is required")
        
        # Default model configuration
        self.default_model = os.getenv("DEFAULT_MODEL", "gpt-4o")
        self.default_provider = os.getenv("DEFAULT_PROVIDER", "openai")
        
        # Trace configuration
        self.batch_size = int(os.getenv("TRACE_BATCH_SIZE", "10"))
        self.flush_interval = float(os.getenv("TRACE_FLUSH_INTERVAL", "5.0"))
        self.request_timeout = int(os.getenv("TRACE_REQUEST_TIMEOUT", "10"))
        
        # Debug configuration
        self.debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
        self.print_traces = os.getenv("PRINT_TRACES", "false").lower() == "true"
        
        # Initialize Langfuse client (optional - can be disabled if no keys provided)
        try:
            self.langfuse = Langfuse()
            print("langfuse client initialized")
        except:
            self.langfuse = None
            print("langfuse client not initialized")
        
        self.logs_batch: List[Dict[str, Any]] = []
        self.trace_data: Dict[str, Any] = {}
        
        if self.debug_mode:
            print(f"✓ Langfuse to Keywords AI integration initialized")
            print(f"  Default Model: {self.default_model}")
            print(f"  Default Provider: {self.default_provider}")
            print(f"  Batch Size: {self.batch_size}")
            print(f"  Flush Interval: {self.flush_interval}s")
        else:
            print("✓ Langfuse to Keywords AI integration initialized")
    
    def _convert_to_keywordsai_log(self, trace_id: str, span_id: str, span_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert span data to Keywords AI log format."""
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        
        log = {
            "trace_unique_id": trace_id,
            "span_unique_id": span_id,
            "span_name": span_data.get("name", "span"),
            "span_parent_id": span_data.get("parent_id"),
            "start_time": span_data.get("start_time", now),
            "timestamp": span_data.get("end_time", now),
        }
        
        # Add model and provider info (important for Keywords AI to recognize LLM calls)
        if span_data.get("model"):
            log["model"] = span_data["model"]
        if span_data.get("provider_id"):
            log["provider_id"] = span_data["provider_id"]
        else:
            log["provider_id"] = ""  # Empty string for non-LLM spans
        
        if span_data.get("input"):
            log["input"] = json.dumps(span_data["input"]) if not isinstance(span_data["input"], str) else span_data["input"]
        if span_data.get("output"):
            log["output"] = json.dumps(span_data["output"]) if not isinstance(span_data["output"], str) else span_data["output"]
        if span_data.get("metadata"):
            log["metadata"] = span_data["metadata"]
        
        return log
    
    def _send_to_keywordsai(self):
        """Send accumulated logs to Keywords AI."""
        if not self.logs_batch:
            return
        
        # Print traces if debug mode enabled
        if self.print_traces:
            print("\n📦 Trace Data Being Sent:")
            print("=" * 60)
            import json
            print(json.dumps(self.logs_batch, indent=2))
            print("=" * 60)
        
        try:
            response = requests.post(
                f"{self.keywordsai_base_url}/v1/traces/ingest",
                json=self.logs_batch,
                headers={
                    "Authorization": f"Bearer {self.keywordsai_api_key}",
                    "Content-Type": "application/json"
                },
                timeout=self.request_timeout
            )
            if response.status_code == 200:
                print(f"✓ Sent {len(self.logs_batch)} logs to Keywords AI")
                if self.debug_mode:
                    print(f"  Response: {response.text[:100]}")
            else:
                print(f"✗ Failed to send logs: {response.status_code}")
                if self.debug_mode:
                    print(f"  Response: {response.text}")
        except Exception as e:
            print(f"✗ Error sending logs: {e}")
            if self.debug_mode:
                import traceback
                traceback.print_exc()
        finally:
            self.logs_batch = []
    
    def trace(self, name: str, **kwargs):
        """
        Create a trace that sends to Keywords AI.
        
        Args:
            name: Name of the trace
            user_id: User identifier (optional)
            metadata: Trace metadata (optional)
            model: Default model for this trace's spans (optional)
            provider_id: Default provider for this trace's spans (optional)
            **kwargs: Additional trace parameters
        """
        trace_id = self.langfuse.create_trace_id() if self.langfuse else str(id(self))
        self.trace_data[trace_id] = {
            "name": name,
            "user_id": kwargs.get("user_id"),
            "metadata": kwargs.get("metadata", {}),
            "start_time": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }
        return TraceWrapper(trace_id, name, self, self.langfuse, **kwargs)
    
    def flush(self):
        """Flush logs to both Langfuse and Keywords AI."""
        if len(self.logs_batch) >= self.batch_size or self.logs_batch:
            self._send_to_keywordsai()
        if self.langfuse:
            self.langfuse.flush()


class TraceWrapper:
    """Wrapper for trace that captures data for Keywords AI."""
    
    def __init__(self, trace_id: str, name: str, client: LangfuseToKeywordsAI, langfuse_client, **kwargs):
        self._client = client
        self._langfuse = langfuse_client
        self.id = trace_id
        self.name = name
        self._start_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self._metadata = kwargs.get("metadata", {})
        self._user_id = kwargs.get("user_id")
        
        # Trace-level model defaults (can be overridden per span)
        self.model = kwargs.get("model", client.default_model)
        self.provider_id = kwargs.get("provider_id", client.default_provider)
    
    def span(self, name: str, **kwargs):
        """
        Create a span within this trace.
        
        Children inherit trace's model/provider unless explicitly overridden.
        
        Args:
            name: Name of the span
            model: Model name (optional, inherits from trace if not specified)
            provider_id: Provider ID (optional, inherits from trace if not specified)
            **kwargs: Additional span parameters
        """
        return SpanWrapper(
            self.id, 
            name, 
            self._client, 
            self._langfuse, 
            parent_id=None,
            parent_model=self.model,  # Pass trace's model to child
            parent_provider=self.provider_id,  # Pass trace's provider to child
            **kwargs
        )
    
    def generation(self, name: str, **kwargs):
        """
        Create a generation within this trace.
        
        Children inherit trace's model/provider unless explicitly overridden.
        """
        return GenerationWrapper(
            self.id, 
            name, 
            self._client, 
            self._langfuse, 
            parent_id=None,
            parent_model=self.model,  # Pass trace's model to child
            parent_provider=self.provider_id,  # Pass trace's provider to child
            **kwargs
        )
    
    def end(self, **kwargs):
        """End the trace."""
        # Add trace as root span with model info
        self._client.logs_batch.append(
            self._client._convert_to_keywordsai_log(
                self.id,
                f"trace_{self.id}",
                {
                    "name": self.name,
                    "parent_id": None,
                    "start_time": self._start_time,
                    "end_time": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                    "metadata": {**self._metadata, **kwargs.get("metadata", {})},
                    "model": self.model,  # Use trace's model
                    "provider_id": self.provider_id,  # Use trace's provider
                }
            )
        )


class SpanWrapper:
    """Wrapper for span that captures data for Keywords AI."""
    
    def __init__(self, trace_id: str, name: str, client: LangfuseToKeywordsAI, langfuse_client, parent_id: Optional[str] = None, parent_model: Optional[str] = None, parent_provider: Optional[str] = None, **kwargs):
        self._client = client
        self._langfuse = langfuse_client
        self._trace_id = trace_id
        self.id = str(id(self))
        self.name = name
        
        # Model info - priority: explicit kwargs > parent model > client default
        self.model = kwargs.get("model") or parent_model or client.default_model
        self.provider_id = kwargs.get("provider_id") or parent_provider or client.default_provider
        
        self._data = {
            "name": name,
            "parent_id": parent_id,
            "start_time": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "input": kwargs.get("input"),
            "metadata": kwargs.get("metadata", {}),
            "model": self.model,
            "provider_id": self.provider_id,
        }
    
    def span(self, name: str, **kwargs):
        """
        Create a child span within this span.
        
        Children inherit parent's model/provider unless explicitly overridden.
        
        Args:
            name: Name of the span
            model: Model name (optional, inherits from parent if not specified)
            provider_id: Provider ID (optional, inherits from parent if not specified)
            **kwargs: Additional span parameters
        """
        return SpanWrapper(
            self._trace_id, 
            name, 
            self._client, 
            self._langfuse, 
            parent_id=self.id,
            parent_model=self.model,  # Pass parent's model to child
            parent_provider=self.provider_id,  # Pass parent's provider to child
            **kwargs
        )
    
    def generation(self, name: str, **kwargs):
        """
        Create a generation within this span.
        
        Children inherit parent's model/provider unless explicitly overridden.
        """
        return GenerationWrapper(
            self._trace_id, 
            name, 
            self._client, 
            self._langfuse, 
            parent_id=self.id,
            parent_model=self.model,  # Pass parent's model to child
            parent_provider=self.provider_id,  # Pass parent's provider to child
            **kwargs
        )
    
    def update(self, **kwargs):
        """Update the span."""
        if "output" in kwargs:
            self._data["output"] = kwargs["output"]
        if "input" in kwargs:
            self._data["input"] = kwargs["input"]
        if "metadata" in kwargs:
            self._data["metadata"] = kwargs.get("metadata", {})
        return self
    
    def end(self, **kwargs):
        """End the span and send to Keywords AI."""
        self._data["end_time"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        if kwargs.get("output"):
            self._data["output"] = kwargs["output"]
        
        # Add to batch
        self._client.logs_batch.append(
            self._client._convert_to_keywordsai_log(self._trace_id, self.id, self._data)
        )


class GenerationWrapper:
    """Wrapper for generation that captures data for Keywords AI."""
    
    def __init__(self, trace_id: str, name: str, client: LangfuseToKeywordsAI, langfuse_client, parent_id: Optional[str] = None, parent_model: Optional[str] = None, parent_provider: Optional[str] = None, **kwargs):
        self._client = client
        self._langfuse = langfuse_client
        self._trace_id = trace_id
        self.id = str(id(self))
        self.name = name
        
        # Model info - priority: explicit kwargs > parent model > client default
        self.model = kwargs.get("model") or parent_model or client.default_model
        self.provider_id = kwargs.get("provider_id") or parent_provider or client.default_provider
        
        self._data = {
            "name": name,
            "parent_id": parent_id,
            "start_time": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "input": kwargs.get("input"),
            "metadata": kwargs.get("metadata", {}),
            # LLM-specific fields
            "model": self.model,
            "provider_id": self.provider_id,
        }
    
    def end(self, **kwargs):
        """End the generation and send to Keywords AI."""
        self._data["end_time"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self._data["output"] = kwargs.get("output")
        
        # Update model/provider if provided in end()
        if kwargs.get("model"):
            self._data["model"] = kwargs["model"]
        if kwargs.get("provider_id"):
            self._data["provider_id"] = kwargs["provider_id"]
        
        # Add to batch
        self._client.logs_batch.append(
            self._client._convert_to_keywordsai_log(self._trace_id, self.id, self._data)
        )


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Langfuse to Keywords AI Integration - Example")
    print("=" * 60 + "\n")
    
    # Check if API key is set
    if not os.getenv("KEYWORDSAI_API_KEY"):
        print("❌ ERROR: KEYWORDSAI_API_KEY not set!")
        print("\nPlease set it in your .env file:")
        print("  KEYWORDSAI_API_KEY=your_api_key_here")
        exit(1)
    
    # Initialize the integration
    langfuse = LangfuseToKeywordsAI()
    
    # Example 1: Deep nested trace tree with multiple children
    print("Creating complex trace with deep nesting and multiple children...")
    trace = langfuse.trace(name="e-commerce_order_processing", user_id="customer_789")
    
    # Level 1: Main order validation (using default model from env)
    validation_span = trace.span(name="order_validation")
    validation_span.update(input={"order_id": "ORD-12345", "items": 3, "total": 299.99})
    
    # Level 2: Child 1 - Validate inventory (child of validation_span)
    inventory_span = validation_span.span(name="validate_inventory")
    inventory_span.update(
        input={"items": ["ITEM-A", "ITEM-B", "ITEM-C"]},
        output={"all_in_stock": True, "warehouse": "WH-001"}
    )
    inventory_span.end()
    
    # Level 2: Child 2 - Validate payment (child of validation_span)
    payment_span = validation_span.span(name="validate_payment")
    payment_span.update(
        input={"amount": 299.99, "method": "credit_card"},
        output={"authorized": True, "transaction_id": "TXN-9876"}
    )
    payment_span.end()
    
    # Level 2: Child 3 - Validate shipping address (child of validation_span)
    address_span = validation_span.span(name="validate_shipping_address")
    address_span.update(
        input={"address": "123 Main St", "city": "San Francisco", "zip": "94102"},
        output={"valid": True, "deliverable": True}
    )
    address_span.end()
    
    validation_span.update(output={"valid": True, "validation_time": "45ms"})
    validation_span.end()
    
    # Level 1: Order processing with LLM (specify custom model for this workflow)
    processing_span = trace.span(name="order_processing", model="gpt-4o-mini", provider_id="openai")
    processing_span.update(input={"order_id": "ORD-12345"})
    
    # Level 2: Generate personalized message with LLM (child of processing_span)
    personalization_span = processing_span.span(name="personalize_confirmation")
    personalization_span.update(input={"customer_name": "Alice", "order_total": 299.99})
    
    # Level 3: LLM generation for email (child of personalization_span)
    email_generation = personalization_span.generation(
        name="openai.chat",
        model="gpt-4o",
        provider_id="openai"
    )
    email_generation.end(
        output=[{"role": "assistant", "content": "Dear Alice, thank you for your order!"}]
    )
    
    # Level 3: LLM generation for SMS (child of personalization_span)
    sms_generation = personalization_span.generation(
        name="openai.chat",
        model="gpt-3.5-turbo",
        provider_id="openai"
    )
    sms_generation.end(
        output=[{"role": "assistant", "content": "Alice, your order #ORD-12345 is confirmed!"}]
    )
    
    personalization_span.update(output={"email_sent": True, "sms_sent": True})
    personalization_span.end()
    
    # Level 2: Allocate inventory (child of processing_span, using Claude)
    allocation_span = processing_span.span(
        name="inventory_allocation",
        model="claude-3-sonnet-20240229",
        provider_id="anthropic"
    )
    allocation_span.update(input={"warehouse": "WH-001", "items": 3})
    
    # Level 3: Reserve item A (child of allocation_span)
    reserve_a = allocation_span.span(name="reserve_item_A")
    reserve_a.update(
        input={"item": "ITEM-A", "quantity": 1},
        output={"reserved": True, "location": "A-12-3"}
    )
    reserve_a.end()
    
    # Level 3: Reserve item B (child of allocation_span)
    reserve_b = allocation_span.span(name="reserve_item_B")
    reserve_b.update(
        input={"item": "ITEM-B", "quantity": 1},
        output={"reserved": True, "location": "B-05-7"}
    )
    reserve_b.end()
    
    # Level 3: Reserve item C (child of allocation_span)
    reserve_c = allocation_span.span(name="reserve_item_C")
    reserve_c.update(
        input={"item": "ITEM-C", "quantity": 1},
        output={"reserved": True, "location": "C-18-2"}
    )
    reserve_c.end()
    
    allocation_span.update(output={"allocated": True, "picking_list_id": "PICK-567"})
    allocation_span.end()
    
    # Level 2: Create shipping label (child of processing_span)
    shipping_span = processing_span.span(name="create_shipping_label")
    shipping_span.update(input={"carrier": "UPS", "service": "Ground"})
    
    # Level 3: Calculate shipping cost (child of shipping_span)
    cost_calc = shipping_span.span(name="calculate_shipping_cost")
    cost_calc.update(
        input={"weight": 5.2, "distance": 450},
        output={"cost": 12.99, "estimated_days": 3}
    )
    cost_calc.end()
    
    # Level 3: Generate label PDF (child of shipping_span)
    pdf_gen = shipping_span.span(name="generate_label_pdf")
    pdf_gen.update(
        input={"format": "PDF", "size": "4x6"},
        output={"url": "https://labels.example.com/LABEL-8899.pdf"}
    )
    pdf_gen.end()
    
    shipping_span.update(output={"label_id": "LABEL-8899", "tracking": "1Z999AA1234567890"})
    shipping_span.end()
    
    processing_span.update(output={"status": "completed", "time": "2.5s"})
    processing_span.end()
    
    # Level 1: Final notification (using Gemini for notification logic)
    notification_span = trace.span(
        name="send_notifications",
        model="gemini-1.5-flash",
        provider_id="google"
    )
    notification_span.update(input={"channels": ["email", "sms", "push"]})
    
    # Level 2: Send email notification (child of notification_span)
    email_notif = notification_span.span(name="send_email")
    email_notif.update(
        input={"to": "alice@example.com", "template": "order_confirmation"},
        output={"sent": True, "message_id": "MSG-EMAIL-123"}
    )
    email_notif.end()
    
    # Level 2: Send SMS notification (child of notification_span)
    sms_notif = notification_span.span(name="send_sms")
    sms_notif.update(
        input={"to": "+1234567890", "message": "Order confirmed"},
        output={"sent": True, "message_id": "MSG-SMS-456"}
    )
    sms_notif.end()
    
    # Level 2: Send push notification (child of notification_span)
    push_notif = notification_span.span(name="send_push_notification")
    push_notif.update(
        input={"device_token": "DEV-ABC123", "title": "Order Confirmed"},
        output={"sent": True, "message_id": "MSG-PUSH-789"}
    )
    push_notif.end()
    
    notification_span.update(output={"sent": 3, "failed": 0})
    notification_span.end()
    
    trace.end()
    
    # Example 2: AI Assistant conversation with multiple turns
    print("Creating AI assistant trace with conversation turns...")
    trace2 = langfuse.trace(name="ai_assistant_conversation", user_id="user_456")
    
    # Turn 1
    turn1_span = trace2.span(name="conversation_turn_1")
    turn1_span.update(input={"user_query": "What's the weather like?"})
    
    turn1_gen = turn1_span.generation(
        name="openai.chat",
        model="gpt-4o",
        provider_id="openai"
    )
    turn1_gen.end(
        output=[{"role": "assistant", "content": "I'll check the weather for you."}]
    )
    
    turn1_span.update(output={"response": "I'll check the weather for you."})
    turn1_span.end()
    
    # Turn 2
    turn2_span = trace2.span(name="conversation_turn_2")
    turn2_span.update(input={"user_query": "Make it a poem"})
    
    turn2_gen = turn2_span.generation(
        name="openai.chat",
        model="gpt-4o",
        provider_id="openai"
    )
    turn2_gen.end(
        output=[{"role": "assistant", "content": "The sky is clear and bright..."}]
    )
    
    turn2_span.update(output={"response": "The sky is clear and bright..."})
    turn2_span.end()
    
    # Turn 3
    turn3_span = trace2.span(name="conversation_turn_3")
    turn3_span.update(input={"user_query": "Translate to Spanish"})
    
    turn3_gen = turn3_span.generation(
        name="openai.chat",
        model="gpt-3.5-turbo",
        provider_id="openai"
    )
    turn3_gen.end(
        output=[{"role": "assistant", "content": "El cielo está despejado..."}]
    )
    
    turn3_span.update(output={"response": "El cielo está despejado..."})
    turn3_span.end()
    
    trace2.end()
    
    # Flush all logs to Keywords AI
    print("\nFlushing logs to Keywords AI...")
    langfuse.flush()
    
    print("\n" + "=" * 60)
    print("✓ Done! Check your traces at:")
    print("  https://platform.keywordsai.co/")
    print("\n📊 Created traces:")
    print("  1. E-commerce Order Processing (19 spans, 3 levels deep)")
    print("     Models used: gpt-4o (default), gpt-4o-mini, gpt-3.5-turbo,")
    print("                  claude-3-sonnet, gemini-1.5-flash")
    print("  2. AI Assistant Conversation (6 spans, 2 levels)")
    print("     Models used: gpt-4o, gpt-3.5-turbo")
    print("\n✨ All spans include model information (no 'unknown model'!)")
    print("=" * 60 + "\n")
