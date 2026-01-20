/**
 * Create Dataset Example
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

interface CreateDatasetOptions {
  name: string;
  description?: string;
  isEmpty?: boolean;
  [key: string]: unknown;
}

interface AddDatasetLogOptions {
  datasetId: string;
  inputData: Record<string, unknown>;
  outputData: Record<string, unknown>;
  metadata?: Record<string, unknown>;
  metrics?: Record<string, unknown>;
}

export async function createDataset(options: CreateDatasetOptions): Promise<DatasetResponse> {
  const { name, description = "", isEmpty = true, ...kwargs } = options;

  const url = `${BASE_URL}/datasets/`;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${API_KEY}`,
  };

  const payload: Record<string, unknown> = { name, description, is_empty: isEmpty };
  Object.assign(payload, kwargs);

  const response = await fetch(url, { method: "POST", headers, body: JSON.stringify(payload) });
  if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

  const data: DatasetResponse = await response.json();
  console.log(`[OK] Dataset created: ${data.id || data.dataset_id}`);
  return data;
}

export async function addDatasetLog(options: AddDatasetLogOptions): Promise<Record<string, unknown>> {
  const { datasetId, inputData, outputData, metadata, metrics } = options;

  const url = `${BASE_URL}/datasets/${datasetId}/logs/`;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${API_KEY}`,
  };

  const payload: Record<string, unknown> = { input: inputData, output: outputData };
  if (metadata) payload.metadata = metadata;
  if (metrics) payload.metrics = metrics;

  const response = await fetch(url, { method: "POST", headers, body: JSON.stringify(payload) });
  if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

  const data = await response.json();
  console.log(`[OK] Log added to dataset`);
  return data;
}

export async function listDatasetLogs(datasetId: string): Promise<Record<string, unknown>> {
  const url = `${BASE_URL}/datasets/${datasetId}/logs/list/`;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${API_KEY}`,
  };

  const response = await fetch(url, { method: "GET", headers });
  if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

  const data = await response.json();
  const logs = Array.isArray(data) ? data : data.logs || data.results || [];
  console.log(`[OK] Found ${logs.length} log(s)`);
  return data;
}

export async function updateDataset(
  datasetId: string,
  options: { name?: string; description?: string }
): Promise<DatasetResponse> {
  const url = `${BASE_URL}/datasets/${datasetId}/`;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${API_KEY}`,
  };

  const response = await fetch(url, { method: "PATCH", headers, body: JSON.stringify(options) });
  if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

  const data: DatasetResponse = await response.json();
  console.log(`[OK] Dataset updated`);
  return data;
}

async function main() {
  console.log("Create Dataset Example\n");

  // Create dataset
  console.log("[1] Creating dataset");
  const dataset = await createDataset({
    name: "Demo Dataset (via API)",
    description: "Created from docs tutorial",
  });
  const datasetId = dataset.id || dataset.dataset_id;

  if (datasetId) {
    // Add logs
    console.log("\n[2] Adding logs");
    await addDatasetLog({
      datasetId,
      inputData: { question: "What is 2+2?" },
      outputData: { answer: "4" },
      metadata: { model: "gpt-4o-mini" },
    });

    await addDatasetLog({
      datasetId,
      inputData: { question: "What is the capital of France?" },
      outputData: { answer: "Paris" },
      metadata: { model: "gpt-4o-mini" },
    });

    // List logs
    console.log("\n[3] Listing logs");
    await listDatasetLogs(datasetId);

    // Update dataset
    console.log("\n[4] Updating dataset");
    await updateDataset(datasetId, { name: "Updated Demo Dataset" });
  }

  console.log("\nDone.");
}

const isMainModule = import.meta.url === `file://${process.argv[1]}`;
if (isMainModule) {
  main().catch(console.error);
}
