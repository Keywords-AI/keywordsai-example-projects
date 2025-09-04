from agents.tracing.processors import BatchTraceProcessor, BackendSpanExporter
from agents.tracing.traces import Trace
from agents.tracing.spans import Span
from typing import Any, Dict, Optional, Union
import httpx
import json
import os
import random
import time
import logging

logger = logging.getLogger(__name__)

class KeywordsAISpanExporter(BackendSpanExporter):
    """
    Custom exporter for Keywords AI that handles all span types and allows for dynamic endpoint configuration.
    """
    
    def __init__(
        self,
        api_key: str | None = None,
        organization: str | None = None,
        project: str | None = None,
        endpoint: str = "https://api.keywordsai.co/api/",
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
    ):
        """
        Initialize the Keywords AI exporter.
        
        Args:
            api_key: The API key for authentication. Defaults to os.environ["OPENAI_API_KEY"] if not provided.
            organization: The organization ID. Defaults to os.environ["OPENAI_ORG_ID"] if not provided.
            project: The project ID. Defaults to os.environ["OPENAI_PROJECT_ID"] if not provided.
            endpoint: The HTTP endpoint to which traces/spans are posted.
            max_retries: Maximum number of retries upon failures.
            base_delay: Base delay (in seconds) for the first backoff.
            max_delay: Maximum delay (in seconds) for backoff growth.
        """
        super().__init__(
            api_key=api_key,
            organization=organization,
            project=project,
            endpoint=endpoint,
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
        )
    
    def set_endpoint(self, endpoint: str) -> None:
        """
        Dynamically change the endpoint URL.
        
        Args:
            endpoint: The new endpoint URL to use for exporting spans.
        """
        self.endpoint = endpoint
        logger.info(f"Keywords AI exporter endpoint changed to: {endpoint}")
    
    def _keywordsai_export(self, item: Union[Trace, Span[Any]]) -> Optional[Dict[str, Any]]:
        """
        Process different span types and extract all JSON serializable attributes.
        
        Args:
            item: A Trace or Span object to export.
            
        Returns:
            A dictionary with all the JSON serializable attributes of the span,
            or None if the item cannot be exported.
        """
        # First try the native export method
        native_export = item.export()
        if not native_export:
            return None
        
        # Add additional metadata based on the type of span
        result = dict(native_export)  # Create a copy to avoid modifying the original
        
        # Add span_type field to help with identification on the Keywords AI side
        if isinstance(item, Trace):
            result["span_type"] = "trace"
        elif isinstance(item, Span):
            # Try to determine the specific span type based on span_data
            span_data_type = type(item.span_data).__name__ if hasattr(item, "span_data") else "unknown"
            result["span_type"] = span_data_type
            
            # Add any additional attributes that might be useful
            if hasattr(item, "span_id"):
                result["span_id"] = item.span_id
            if hasattr(item, "parent_id"):
                result["parent_id"] = item.parent_id
            if hasattr(item, "trace_id"):
                result["trace_id"] = item.trace_id
            
            # Extract span data attributes if available
            if hasattr(item, "span_data"):
                span_data = item.span_data
                # Add all attributes from span_data that are JSON serializable
                for attr_name in dir(span_data):
                    if not attr_name.startswith("_"):  # Skip private attributes
                        try:
                            attr_value = getattr(span_data, attr_name)
                            # Try to serialize to check if it's JSON serializable
                            json.dumps({"test": attr_value})
                            result[f"span_data_{attr_name}"] = attr_value
                        except (TypeError, OverflowError):
                            # Skip attributes that aren't JSON serializable
                            pass
        
        return result
    
    def export(self, items: list[Trace | Span[Any]]) -> None:
        """
        Export traces and spans to the Keywords AI backend.
        
        Args:
            items: List of Trace or Span objects to export.
        """
        if not items:
            return

        if not self.api_key:
            logger.warning("API key is not set, skipping trace export")
            return

        # Process each item with our custom exporter
        data = [self._keywordsai_export(item) for item in items]
        # Filter out None values
        data = [item for item in data if item]
        
        if not data:
            return
            
        payload = {"data": data}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "OpenAI-Beta": "traces=v1",
        }

        # Exponential backoff loop
        attempt = 0
        delay = self.base_delay
        while True:
            attempt += 1
            try:
                response = self._client.post(url=self.endpoint, headers=headers, json=payload)

                # If the response is successful, break out of the loop
                if response.status_code < 300:
                    logger.debug(f"Exported {len(data)} items to Keywords AI")
                    return

                # If the response is a client error (4xx), we won't retry
                if 400 <= response.status_code < 500:
                    logger.error(f"Keywords AI client error {response.status_code}: {response.text}")
                    return

                # For 5xx or other unexpected codes, treat it as transient and retry
                logger.warning(f"Server error {response.status_code}, retrying.")
            except httpx.RequestError as exc:
                # Network or other I/O error, we'll retry
                logger.warning(f"Request failed: {exc}")

            # If we reach here, we need to retry or give up
            if attempt >= self.max_retries:
                logger.error("Max retries reached, giving up on this batch.")
                return

            # Exponential backoff + jitter
            sleep_time = delay + random.uniform(0, 0.1 * delay)  # 10% jitter
            time.sleep(sleep_time)
            delay = min(delay * 2, self.max_delay)


class KeywordsProcessor(BatchTraceProcessor):
    """
    A processor that uses KeywordsAISpanExporter to send traces and spans to Keywords AI.
    """
    
    def __init__(
        self,
        api_key: str | None = None,
        organization: str | None = None,
        project: str | None = None,
        endpoint: str = "https://api.keywordsai.co/api/",
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
        max_queue_size: int = 8192,
        max_batch_size: int = 128,
        schedule_delay: float = 5.0,
        export_trigger_ratio: float = 0.7,
    ):
        """
        Initialize the Keywords AI processor.
        
        Args:
            api_key: The API key for authentication.
            organization: The organization ID.
            project: The project ID.
            endpoint: The HTTP endpoint to which traces/spans are posted.
            max_retries: Maximum number of retries upon failures.
            base_delay: Base delay (in seconds) for the first backoff.
            max_delay: Maximum delay (in seconds) for backoff growth.
            max_queue_size: The maximum number of spans to store in the queue.
            max_batch_size: The maximum number of spans to export in a single batch.
            schedule_delay: The delay between checks for new spans to export.
            export_trigger_ratio: The ratio of the queue size at which we will trigger an export.
        """
        # Create the exporter
        exporter = KeywordsAISpanExporter(
            api_key=api_key,
            organization=organization,
            project=project,
            endpoint=endpoint,
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
        )
        
        # Initialize the BatchTraceProcessor with our exporter
        super().__init__(
            exporter=exporter,
            max_queue_size=max_queue_size,
            max_batch_size=max_batch_size,
            schedule_delay=schedule_delay,
            export_trigger_ratio=export_trigger_ratio,
        )
        
        # Store the exporter for easy access
        self._keywords_exporter = exporter
    
    def set_endpoint(self, endpoint: str) -> None:
        """
        Dynamically change the endpoint URL.
        
        Args:
            endpoint: The new endpoint URL to use for exporting spans.
        """
        self._keywords_exporter.set_endpoint(endpoint)


