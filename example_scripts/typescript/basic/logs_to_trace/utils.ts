/**
 * Trace Log Processing Utilities
 *
 * This module provides utilities for preprocessing trace logs to create new unique traces
 * while preserving exact relationships and timing between spans.
 *
 * Key Functions:
 * - deterministicStringMapper(): Maps strings deterministically while preserving length
 * - shiftTimestamp(): Shifts timestamps while preserving relative timing
 * - generateTraceData(): Main function to process a list of logs into a new trace
 */

import { createHash } from "crypto";

interface TraceLog {
  trace_unique_id?: string;
  span_unique_id?: string;
  span_parent_id?: string | null;
  start_time?: string;
  timestamp?: string;
  [key: string]: unknown;
}

/**
 * Create a deterministic mapping that preserves the original string length.
 *
 * This generic utility function maps any string to a new string of the same length
 * using SHA-256 hashing. It works for trace IDs, span IDs, or any other string
 * that needs consistent mapping.
 *
 * Key properties:
 * - Same input always produces same output (deterministic)
 * - Output has exactly the same length as input
 * - Different seeds produce different mappings
 * - Suitable for hex strings of any length
 *
 * @param originalString - The original string to be mapped
 * @param seed - Seed string that determines the mapping variant
 * @returns A deterministic hex string of the same length as originalString
 *
 * @example
 * deterministicStringMapper("abc123", "seed1")
 * // Returns '31ffc5' (same length as input)
 * deterministicStringMapper("4fd81b946f97464789a28b50dd253a90", "seed1")
 * // Returns '16aefa5bf5e1dd7ff07818352772a21b' (32 chars -> 32 chars)
 */
export function deterministicStringMapper(
  originalString: string,
  seed: string
): string {
  // Combine seed and original string for unique hashing input
  const combined = `${seed}:${originalString}`;

  // Generate SHA-256 hash
  const hash = createHash("sha256");
  hash.update(combined);
  let hexHash = hash.digest("hex");

  // If we need more characters than one hash provides, chain multiple hashes
  const targetLength = originalString.length;
  let result = hexHash;
  let counter = 0;

  while (result.length < targetLength) {
    counter++;
    const additionalHash = createHash("sha256");
    additionalHash.update(`${combined}:${counter}`);
    result += additionalHash.digest("hex");
  }

  // Return exactly the same length as the original string
  return result.slice(0, targetLength);
}

/**
 * Shift a timestamp while preserving its relative position in the trace timeline.
 *
 * This function calculates the time offset of the original timestamp relative to
 * a reference point, then applies that same offset to the new anchor time.
 * This preserves the exact timing relationships between all spans in the trace.
 *
 * @param originalTimestampStr - Original timestamp in ISO format (with 'Z' suffix)
 *                               e.g., "2025-09-08T07:46:18.037942Z"
 * @param anchorTime - The new anchor time (typically current time)
 *                     This becomes the new reference point for the trace
 * @param referenceTime - The original reference time (typically the first
 *                        log's timestamp in the original trace)
 * @returns Shifted timestamp in ISO format with 'Z' suffix
 *
 * @example
 * If original trace started at 07:46:00 and current log was at 07:46:05 (5s later),
 * and we anchor to 10:00:00, the new timestamp will be 10:00:05 (still 5s later).
 */
export function shiftTimestamp(
  originalTimestampStr: string,
  anchorTime: Date,
  referenceTime: Date
): string {
  // Parse the original timestamp
  const originalTime = new Date(originalTimestampStr);

  // Calculate how far this timestamp was from the reference point
  const timeOffset = originalTime.getTime() - referenceTime.getTime();

  // Apply the same offset to the new anchor time
  const newTime = new Date(anchorTime.getTime() + timeOffset);

  // Return in the same ISO format with 'Z' suffix
  return newTime.toISOString();
}

/**
 * Generate new trace data from existing logs while preserving all relationships.
 *
 * This is the main processing function that:
 * 1. Finds the earliest timestamp in the logs to use as a reference point
 * 2. Generates a new trace ID deterministically based on the original trace ID and timestamp
 * 3. Maps all span IDs and parent IDs consistently using the same seed
 * 4. Shifts all timestamps to be relative to the runTimestamp while preserving intervals
 * 5. Maintains all other log data (latency, costs, metadata, etc.) unchanged
 *
 * @param logList - List of log objects from the JSON file
 *                  Each object represents one span in the trace
 * @param runTimestamp - Timestamp used for both seed generation and anchoring
 *                       Different timestamps create different traces
 * @returns Processed log objects with:
 *          - New trace_unique_id (same for all logs)
 *          - New span_unique_id for each span
 *          - Updated span_parent_id references
 *          - Shifted timestamps preserving relative timing
 *          - All other fields unchanged
 */
export function generateTraceData(
  logList: TraceLog[],
  runTimestamp: Date
): TraceLog[] {
  if (!logList || logList.length === 0) {
    return logList;
  }

  // Find reference timestamp (earliest in the trace)
  let referenceTime: Date | null = null;

  // First, try to find a start_time (preferred as it's the actual start of operations)
  for (const log of logList) {
    if (log.start_time) {
      const timestamp = new Date(log.start_time);
      if (referenceTime === null || timestamp < referenceTime) {
        referenceTime = timestamp;
      }
    }
  }

  // If no start_time found, fall back to timestamp field
  if (referenceTime === null) {
    for (const log of logList) {
      if (log.timestamp) {
        const timestamp = new Date(log.timestamp);
        if (referenceTime === null || timestamp < referenceTime) {
          referenceTime = timestamp;
        }
      }
    }
  }

  // Generate seed from timestamp and create new trace ID
  const seed = runTimestamp.toISOString();
  const originalTraceId = logList[0]?.trace_unique_id ?? "default_trace";
  const newTraceId = deterministicStringMapper(originalTraceId, seed);

  // Process each log entry
  const processedLogs: TraceLog[] = [];

  for (const log of logList) {
    // Create a shallow copy to avoid modifying the original
    const processedLog: TraceLog = { ...log };

    // Update trace_unique_id (same for all spans in this trace)
    if (processedLog.trace_unique_id !== undefined) {
      processedLog.trace_unique_id = newTraceId;
    }

    // Update span_unique_id (unique for each span)
    if (processedLog.span_unique_id !== undefined) {
      const oldSpanId = processedLog.span_unique_id;
      processedLog.span_unique_id = deterministicStringMapper(oldSpanId, seed);
    }

    // Update span_parent_id (must match the new span_unique_id of the parent)
    if (processedLog.span_parent_id) {
      const oldParentId = processedLog.span_parent_id;
      processedLog.span_parent_id = deterministicStringMapper(oldParentId, seed);
    }

    // Update timestamps while preserving relative timing relationships
    if (referenceTime) {
      if (processedLog.start_time) {
        processedLog.start_time = shiftTimestamp(
          processedLog.start_time,
          runTimestamp,
          referenceTime
        );
      }

      if (processedLog.timestamp) {
        processedLog.timestamp = shiftTimestamp(
          processedLog.timestamp,
          runTimestamp,
          referenceTime
        );
      }
    }

    processedLogs.push(processedLog);
  }

  return processedLogs;
}
