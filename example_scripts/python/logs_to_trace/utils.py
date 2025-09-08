"""
Trace Log Processing Utilities

This module provides utilities for preprocessing trace logs to create new unique traces
while preserving exact relationships and timing between spans.

Key Functions:
- deterministic_string_mapper(): Maps strings deterministically while preserving length
- shift_timestamp(): Shifts timestamps while preserving relative timing
- generate_trace_data(): Main function to process a list of logs into a new trace
"""

import hashlib
from datetime import datetime, timezone
from typing import List, Dict, Any


def deterministic_string_mapper(original_string: str, seed: str) -> str:
    """
    Create a deterministic mapping that preserves the original string length.

    This generic utility function maps any string to a new string of the same length
    using SHA-256 hashing. It works for trace IDs, span IDs, or any other string
    that needs consistent mapping.

    Key properties:
    - Same input always produces same output (deterministic)
    - Output has exactly the same length as input
    - Different seeds produce different mappings
    - Suitable for hex strings of any length

    Args:
        original_string (str): The original string to be mapped
        seed (str): Seed string that determines the mapping variant

    Returns:
        str: A deterministic hex string of the same length as original_string

    Example:
        >>> deterministic_string_mapper("abc123", "seed1")
        '31ffc5'  # Same length as input
        >>> deterministic_string_mapper("4fd81b946f97464789a28b50dd253a90", "seed1")
        '16aefa5bf5e1dd7ff07818352772a21b'  # 32 chars -> 32 chars
    """
    # Combine seed and original string for unique hashing input
    combined = f"{seed}:{original_string}"

    # Generate SHA-256 hash
    hash_obj = hashlib.sha256(combined.encode("utf-8"))
    hex_hash = hash_obj.hexdigest()

    # If we need more characters than one hash provides, chain multiple hashes
    target_length = len(original_string)
    result = hex_hash
    counter = 0

    while len(result) < target_length:
        counter += 1
        additional_hash = hashlib.sha256(
            f"{combined}:{counter}".encode("utf-8")
        ).hexdigest()
        result += additional_hash

    # Return exactly the same length as the original string
    return result[:target_length]


def shift_timestamp(
    original_timestamp_str: str, anchor_time: datetime, reference_time: datetime
) -> str:
    """
    Shift a timestamp while preserving its relative position in the trace timeline.

    This function calculates the time offset of the original timestamp relative to
    a reference point, then applies that same offset to the new anchor time.
    This preserves the exact timing relationships between all spans in the trace.

    Args:
        original_timestamp_str (str): Original timestamp in ISO format (with 'Z' suffix)
                                     e.g., "2025-09-08T07:46:18.037942Z"
        anchor_time (datetime): The new anchor time (typically current time)
                               This becomes the new reference point for the trace
        reference_time (datetime): The original reference time (typically the first
                                  log's timestamp in the original trace)

    Returns:
        str: Shifted timestamp in ISO format with 'Z' suffix

    Example:
        If original trace started at 07:46:00 and current log was at 07:46:05 (5s later),
        and we anchor to 10:00:00, the new timestamp will be 10:00:05 (still 5s later).
    """
    # Parse the original timestamp, handling the 'Z' UTC indicator
    original_time = datetime.fromisoformat(
        original_timestamp_str.replace("Z", "+00:00")
    )

    # Calculate how far this timestamp was from the reference point
    time_offset = original_time - reference_time

    # Apply the same offset to the new anchor time
    new_time = anchor_time + time_offset

    # Return in the same ISO format with 'Z' suffix
    return new_time.isoformat().replace("+00:00", "Z")


def generate_trace_data(
    log_list: List[Dict[str, Any]], run_timestamp: datetime
) -> List[Dict[str, Any]]:
    """
    Generate new trace data from existing logs while preserving all relationships.

    This is the main processing function that:
    1. Finds the earliest timestamp in the logs to use as a reference point
    2. Generates a new trace ID deterministically based on the original trace ID and timestamp
    3. Maps all span IDs and parent IDs consistently using the same seed
    4. Shifts all timestamps to be relative to the run_timestamp while preserving intervals
    5. Maintains all other log data (latency, costs, metadata, etc.) unchanged

    Args:
        log_list (List[Dict[str, Any]]): List of log dictionaries from the JSON file
                                        Each dict represents one span in the trace
        run_timestamp (datetime): Timestamp used for both seed generation and anchoring
                                 Different timestamps create different traces

    Returns:
        List[Dict[str, Any]]: Processed log dictionaries with:
                             - New trace_unique_id (same for all logs)
                             - New span_unique_id for each span
                             - Updated span_parent_id references
                             - Shifted timestamps preserving relative timing
                             - All other fields unchanged

    Raises:
        ValueError: If log_list is empty or contains no valid timestamps
    """
    if not log_list:
        return log_list

    # Find reference timestamp (earliest in the trace)
    reference_time = None

    # First, try to find a start_time (preferred as it's the actual start of operations)
    for log in log_list:
        if "start_time" in log and log["start_time"]:
            timestamp = datetime.fromisoformat(log["start_time"].replace("Z", "+00:00"))
            if reference_time is None or timestamp < reference_time:
                reference_time = timestamp

    # If no start_time found, fall back to timestamp field
    if reference_time is None:
        for log in log_list:
            if "timestamp" in log and log["timestamp"]:
                timestamp = datetime.fromisoformat(
                    log["timestamp"].replace("Z", "+00:00")
                )
                if reference_time is None or timestamp < reference_time:
                    reference_time = timestamp

    # Generate seed from timestamp and create new trace ID
    seed = run_timestamp.isoformat()
    original_trace_id = log_list[0].get("trace_unique_id", "default_trace")
    new_trace_id = deterministic_string_mapper(original_trace_id, seed)

    # Process each log entry
    processed_logs = []
    for log in log_list:
        # Create a shallow copy to avoid modifying the original
        processed_log = log.copy()

        # Update trace_unique_id (same for all spans in this trace)
        if "trace_unique_id" in processed_log:
            processed_log["trace_unique_id"] = new_trace_id

        # Update span_unique_id (unique for each span)
        if "span_unique_id" in processed_log:
            old_span_id = processed_log["span_unique_id"]
            processed_log["span_unique_id"] = deterministic_string_mapper(
                old_span_id, seed
            )

        # Update span_parent_id (must match the new span_unique_id of the parent)
        if "span_parent_id" in processed_log and processed_log["span_parent_id"]:
            old_parent_id = processed_log["span_parent_id"]
            processed_log["span_parent_id"] = deterministic_string_mapper(
                old_parent_id, seed
            )

        # Update timestamps while preserving relative timing relationships
        if reference_time:
            if "start_time" in processed_log and processed_log["start_time"]:
                processed_log["start_time"] = shift_timestamp(
                    processed_log["start_time"], run_timestamp, reference_time
                )

            if "timestamp" in processed_log and processed_log["timestamp"]:
                processed_log["timestamp"] = shift_timestamp(
                    processed_log["timestamp"], run_timestamp, reference_time
                )

        processed_logs.append(processed_log)

    return processed_logs
