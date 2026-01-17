/**
 * Create Dataset Example
 *
 * This example demonstrates how to create and manage datasets in KeywordsAI.
 * Datasets are curated collections of logs (inputs/outputs + metadata) that you can
 * evaluate, annotate, and use to power Experiments.
 *
 * Documentation: https://docs.keywordsai.co/documentation/products/dataset
 */

import "dotenv/config";

const BASE_URL = process.env.KEYWORDSAI_BASE_URL || "https://api.keywordsai.co/api";
const API_KEY = process.env.KEYWORDSAI_API_KEY;

interface DatasetResponse {
  id?: string;
  dataset_id?: string;
  [key: string]: unknown;
}

interface DatasetLogResponse {
  id?: string;
  log_id?: string;
  [key: string]: unknown;
}

interface CreateDatasetOptions {
  name: string;
  description?: string;
  isEmpty?: boolean;
  datasetType?: string;
  sampling?: number;
  startTime?: string;
  endTime?: string;
  initialLogFilters?: Record<string, unknown>;
  [key: string]: unknown;
}

interface AddDatasetLogOptions {
  datasetId: string;
  inputData: Record<string, unknown>;
  outputData: Record<string, unknown>;
  metadata?: Record<string, unknown>;
  metrics?: Record<string, unknown>;
  [key: string]: unknown;
}

interface BulkAddLogsOptions {
  datasetId: string;
  startTime: string;
  endTime: string;
  filters?: Record<string, unknown>;
  samplingPercentage?: number;
  [key: string]: unknown;
}

interface EvalRunResponse {
  id?: string;
  report_id?: string;
  status?: string;
  [key: string]: unknown;
}

/**
 * Create a new dataset in Keywords AI.
 */
export async function createDataset(options: CreateDatasetOptions): Promise<DatasetResponse> {
  const {
    name,
    description = "",
    isEmpty = true,
    datasetType,
    sampling,
    startTime,
    endTime,
    initialLogFilters,
    ...kwargs
  } = options;

  const url = `${BASE_URL}/datasets/`;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${API_KEY}`,
  };

  const payload: Record<string, unknown> = {
    name,
    description,
    is_empty: isEmpty,
  };

  if (datasetType) {
    payload.type = datasetType;
  }
  if (sampling !== undefined) {
    payload.sampling = sampling;
  }
  if (startTime) {
    payload.start_time = startTime;
  }
  if (endTime) {
    payload.end_time = endTime;
  }
  if (initialLogFilters) {
    payload.initial_log_filters = initialLogFilters;
  }

  Object.assign(payload, kwargs);

  console.log("Creating dataset...");
  console.log(`  URL: ${url}`);
  console.log(`  Name: ${name}`);
  if (description) {
    console.log(`  Description: ${description}`);
  }
  console.log(`  Is Empty: ${isEmpty}`);
  console.log(`  Request Body: ${JSON.stringify(payload, null, 2)}`);

  const response = await fetch(url, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data: DatasetResponse = await response.json();
  console.log(`\n[OK] Dataset created successfully`);
  if (data.id) {
    console.log(`  Dataset ID: ${data.id}`);
  }
  if (data.dataset_id) {
    console.log(`  Dataset ID: ${data.dataset_id}`);
  }

  return data;
}

/**
 * Add a log entry to a dataset.
 */
export async function addDatasetLog(options: AddDatasetLogOptions): Promise<DatasetLogResponse> {
  const { datasetId, inputData, outputData, metadata, metrics, ...kwargs } = options;

  const url = `${BASE_URL}/datasets/${datasetId}/logs/`;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${API_KEY}`,
  };

  const payload: Record<string, unknown> = {
    input: inputData,
    output: outputData,
  };

  if (metadata) {
    payload.metadata = metadata;
  }
  if (metrics) {
    payload.metrics = metrics;
  }

  Object.assign(payload, kwargs);

  console.log("Adding dataset log...");
  console.log(`  URL: ${url}`);
  console.log(`  Dataset ID: ${datasetId}`);
  console.log(`  Request Body: ${JSON.stringify(payload, null, 2)}`);

  const response = await fetch(url, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data: DatasetLogResponse = await response.json();
  console.log(`\n[OK] Dataset log added successfully`);
  if (data.id) {
    console.log(`  Log ID: ${data.id}`);
  }

  return data;
}

/**
 * List logs in a dataset.
 */
export async function listDatasetLogs(
  datasetId: string,
  page: number = 1,
  pageSize: number = 10
): Promise<Record<string, unknown>> {
  const url = `${BASE_URL}/datasets/${datasetId}/logs/list/`;
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${API_KEY}`,
  };

  console.log("Listing dataset logs...");
  console.log(`  URL: ${url}`);
  console.log(`  Dataset ID: ${datasetId}`);
  console.log(`  Page: ${page}, Page Size: ${pageSize}`);

  const response = await fetch(`${url}?${params}`, {
    method: "GET",
    headers,
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  const logs = Array.isArray(data) ? data : data.logs || data.results || [];

  console.log(`\n[OK] Found ${logs.length} log(s)`);
  logs.forEach((log: Record<string, unknown>, i: number) => {
    const logId = log.id || log.log_id || "N/A";
    console.log(`  ${i + 1}. Log ID: ${logId}`);
  });

  return data;
}

/**
 * Bulk add logs to a dataset using filters and time range.
 */
export async function bulkAddLogs(options: BulkAddLogsOptions): Promise<Record<string, unknown>> {
  const { datasetId, startTime, endTime, filters, samplingPercentage, ...kwargs } = options;

  const url = `${BASE_URL}/datasets/${datasetId}/logs/bulk/`;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${API_KEY}`,
  };

  const payload: Record<string, unknown> = {
    start_time: startTime,
    end_time: endTime,
  };

  if (filters) {
    payload.filters = filters;
  }
  if (samplingPercentage !== undefined) {
    payload.sampling_percentage = samplingPercentage;
  }

  Object.assign(payload, kwargs);

  console.log("Bulk adding logs to dataset...");
  console.log(`  URL: ${url}`);
  console.log(`  Dataset ID: ${datasetId}`);
  console.log(`  Time Range: ${startTime} to ${endTime}`);
  if (filters) {
    console.log(`  Filters: ${JSON.stringify(filters, null, 2)}`);
  }
  if (samplingPercentage) {
    console.log(`  Sampling: ${samplingPercentage}%`);
  }
  console.log(`  Request Body: ${JSON.stringify(payload, null, 2)}`);

  const response = await fetch(url, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  console.log(`\n[OK] Bulk add operation initiated`);
  console.log(`  Note: This runs in the background. Use listDatasetLogs() to check when logs appear.`);

  return data;
}

/**
 * Run evaluators on all logs in a dataset.
 */
export async function runEvalOnDataset(
  datasetId: string,
  evaluatorSlugs: string[]
): Promise<Record<string, unknown>> {
  const url = `${BASE_URL}/datasets/${datasetId}/eval-reports/create`;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${API_KEY}`,
  };

  const payload = {
    evaluator_slugs: evaluatorSlugs,
  };

  console.log("Running eval on dataset...");
  console.log(`  URL: ${url}`);
  console.log(`  Dataset ID: ${datasetId}`);
  console.log(`  Evaluator Slugs: ${evaluatorSlugs.join(", ")}`);
  console.log(`  Request Body: ${JSON.stringify(payload, null, 2)}`);

  const response = await fetch(url, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  console.log(`\n[OK] Eval run initiated`);
  if (data.id) {
    console.log(`  Eval Report ID: ${data.id}`);
  }
  if (data.report_id) {
    console.log(`  Report ID: ${data.report_id}`);
  }

  return data;
}

/**
 * List all eval runs for a dataset.
 */
export async function listEvalRuns(datasetId: string): Promise<EvalRunResponse[]> {
  const url = `${BASE_URL}/datasets/${datasetId}/eval-reports/list/`;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${API_KEY}`,
  };

  console.log("Listing eval runs...");
  console.log(`  URL: ${url}`);
  console.log(`  Dataset ID: ${datasetId}`);

  const response = await fetch(url, {
    method: "GET",
    headers,
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  const runs: EvalRunResponse[] = Array.isArray(data) ? data : data.runs || data.results || [];

  console.log(`\n[OK] Found ${runs.length} eval run(s)`);
  runs.forEach((run, i) => {
    const runId = run.id || run.report_id || "N/A";
    const status = run.status || "N/A";
    console.log(`  ${i + 1}. Run ID: ${runId}, Status: ${status}`);
  });

  return runs;
}

/**
 * Update dataset metadata.
 */
export async function updateDataset(
  datasetId: string,
  options: { name?: string; description?: string; [key: string]: unknown }
): Promise<DatasetResponse> {
  const { name, description, ...kwargs } = options;

  const url = `${BASE_URL}/datasets/${datasetId}/`;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${API_KEY}`,
  };

  const payload: Record<string, unknown> = {};
  if (name) {
    payload.name = name;
  }
  if (description) {
    payload.description = description;
  }

  Object.assign(payload, kwargs);

  console.log("Updating dataset...");
  console.log(`  URL: ${url}`);
  console.log(`  Dataset ID: ${datasetId}`);
  console.log(`  Request Body: ${JSON.stringify(payload, null, 2)}`);

  const response = await fetch(url, {
    method: "PATCH",
    headers,
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data: DatasetResponse = await response.json();
  console.log(`\n[OK] Dataset updated successfully`);

  return data;
}

/**
 * Delete logs from a dataset.
 */
export async function deleteDatasetLogs(
  datasetId: string,
  options: { filters?: Record<string, unknown>; deleteAll?: boolean }
): Promise<Record<string, unknown>> {
  const { filters, deleteAll } = options;

  const url = `${BASE_URL}/datasets/${datasetId}/logs/delete/`;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${API_KEY}`,
  };

  const payload: Record<string, unknown> = {};
  if (deleteAll) {
    payload.delete_all = true;
  } else if (filters) {
    payload.filters = filters;
  } else {
    throw new Error("Either filters or deleteAll must be provided");
  }

  console.log("Deleting dataset logs...");
  console.log(`  URL: ${url}`);
  console.log(`  Dataset ID: ${datasetId}`);
  if (deleteAll) {
    console.log(`  WARNING: Deleting ALL logs!`);
  } else {
    console.log(`  Filters: ${JSON.stringify(filters, null, 2)}`);
  }
  console.log(`  Request Body: ${JSON.stringify(payload, null, 2)}`);

  const response = await fetch(url, {
    method: "DELETE",
    headers,
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = response.headers.get("content-length") !== "0" ? await response.json() : {};
  console.log(`\n[OK] Logs deleted successfully`);

  return data;
}

/**
 * Delete a dataset.
 */
export async function deleteDataset(datasetId: string): Promise<boolean> {
  const url = `${BASE_URL}/datasets/${datasetId}/`;

  const headers: Record<string, string> = {
    Authorization: `Bearer ${API_KEY}`,
  };

  console.log("Deleting dataset...");
  console.log(`  URL: ${url}`);
  console.log(`  Dataset ID: ${datasetId}`);
  console.log(`  WARNING: This will permanently delete the dataset!`);

  const response = await fetch(url, {
    method: "DELETE",
    headers,
  });

  if (response.status === 204) {
    console.log(`\n[OK] Dataset deleted successfully`);
    return true;
  }

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return false;
}

async function main() {
  console.log("=".repeat(80));
  console.log("KeywordsAI Create Dataset Example");
  console.log("=".repeat(80));

  // Example 1: Create an empty dataset
  console.log("\n[Example 1] Creating an empty dataset");
  console.log("-".repeat(80));

  const dataset1 = await createDataset({
    name: "Demo Dataset (via API)",
    description: "Created from docs tutorial",
    isEmpty: true,
  });
  const dataset1Id = dataset1.id || dataset1.dataset_id;

  // Example 2: Add a dataset log
  console.log("\n[Example 2] Adding a dataset log");
  console.log("-".repeat(80));

  if (dataset1Id) {
    await addDatasetLog({
      datasetId: dataset1Id,
      inputData: {
        question: "What is 2+2?",
        context: { source: "docs_tutorial" },
      },
      outputData: {
        answer: "4",
        explanation: "2 + 2 = 4.",
      },
      metadata: {
        custom_identifier: "dataset-tutorial-log-1",
        model: "gpt-4o-mini",
      },
      metrics: {
        cost: 0.0,
        latency: 0.0,
      },
    });

    // Add another log
    await addDatasetLog({
      datasetId: dataset1Id,
      inputData: {
        question: "What is the capital of France?",
        context: { source: "docs_tutorial" },
      },
      outputData: {
        answer: "Paris",
        explanation: "Paris is the capital and largest city of France.",
      },
      metadata: {
        custom_identifier: "dataset-tutorial-log-2",
        model: "gpt-4o-mini",
      },
      metrics: {
        cost: 0.0,
        latency: 0.0,
      },
    });
  }

  // Example 3: List dataset logs
  console.log("\n[Example 3] Listing dataset logs");
  console.log("-".repeat(80));

  if (dataset1Id) {
    await listDatasetLogs(dataset1Id, 1, 10);
  }

  // Example 4: Update dataset metadata
  console.log("\n[Example 4] Updating dataset metadata");
  console.log("-".repeat(80));

  if (dataset1Id) {
    await updateDataset(dataset1Id, {
      name: "Updated Demo Dataset",
      description: "Updated via API",
    });
  }

  // Example 5: Create another dataset for eval demonstration
  console.log("\n[Example 5] Creating another dataset for eval");
  console.log("-".repeat(80));

  const dataset2 = await createDataset({
    name: "Eval Test Dataset",
    description: "Dataset for testing evaluators",
    isEmpty: true,
  });
  const dataset2Id = dataset2.id || dataset2.dataset_id;

  if (dataset2Id) {
    // Add a log to the second dataset
    await addDatasetLog({
      datasetId: dataset2Id,
      inputData: {
        question: "What is machine learning?",
        context: { source: "eval_test" },
      },
      outputData: {
        answer: "Machine learning is a subset of AI that enables systems to learn from data.",
        explanation: "It uses algorithms to identify patterns and make decisions.",
      },
      metadata: {
        custom_identifier: "eval-test-log-1",
        model: "gpt-4o",
      },
      metrics: {
        cost: 0.001,
        latency: 0.5,
      },
    });

    // Example 6: Run eval on dataset (if evaluators exist)
    console.log("\n[Example 6] Running eval on dataset");
    console.log("-".repeat(80));
    console.log("Note: This requires existing evaluators. If you don't have evaluators,");
    console.log("      create them first using create_evaluator.ts");
    console.log("-".repeat(80));

    // Uncomment and replace with actual evaluator slugs if you have them
    // const evalResult = await runEvalOnDataset(dataset2Id, ["response_quality"]);

    // Example 7: List eval runs
    console.log("\n[Example 7] Listing eval runs");
    console.log("-".repeat(80));

    await listEvalRuns(dataset2Id);
  }

  // Example 8: Delete logs from dataset (by filter)
  console.log("\n[Example 8] Deleting logs from dataset (by filter)");
  console.log("-".repeat(80));
  console.log("Note: Skipping actual deletion to preserve test data.");
  console.log("      Uncomment the code below to test deletion.");
  console.log("-".repeat(80));

  // Uncomment to test deletion
  // if (dataset1Id) {
  //   await deleteDatasetLogs(dataset1Id, {
  //     filters: { "metadata.custom_identifier": "dataset-tutorial-log-1" },
  //   });
  // }

  console.log("\n" + "=".repeat(80));
  console.log("All examples completed successfully!");
  console.log("=".repeat(80));
  console.log("\nTips:");
  console.log("   - You can view your datasets on the KeywordsAI platform");
  console.log("   - Use datasets to power Experiments and compare prompt versions");
  console.log("   - Run evaluators on datasets to assess quality at scale");
  console.log(`\nCreated Dataset IDs:`);
  if (dataset1Id) {
    console.log(`   - Dataset 1: ${dataset1Id}`);
  }
  if (dataset2Id) {
    console.log(`   - Dataset 2: ${dataset2Id}`);
  }

  return {
    dataset_1: dataset1,
    dataset_2: dataset2,
  };
}

// Run main only if this is the entry point (not imported)
const isMainModule = import.meta.url === `file://${process.argv[1]}`;
if (isMainModule) {
  main().catch(console.error);
}
