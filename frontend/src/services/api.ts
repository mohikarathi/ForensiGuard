/**
 * API Service Client for ForensiGuard REST backend
 */

import {
  HealthResponse,
  OverviewResponse,
  ModelsResponse,
  DemoSamplesResponse,
  AnalyzeResponse,
  AnalysisSummaryItem,
  EvaluationSummaryResponse,
  AblationsResponse,
  CurvesResponse,
} from '../types/api';

const BASE_URL = '/api';

export async function fetchHealth(): Promise<HealthResponse> {
  const res = await fetch(`${BASE_URL}/health`);
  if (!res.ok) throw new Error(`Health check failed with status ${res.status}`);
  return res.json();
}

export async function fetchOverview(): Promise<OverviewResponse> {
  const res = await fetch(`${BASE_URL}/overview`);
  if (!res.ok) throw new Error(`Failed to fetch overview: ${res.statusText}`);
  return res.json();
}

export async function fetchModels(): Promise<ModelsResponse> {
  const res = await fetch(`${BASE_URL}/models`);
  if (!res.ok) throw new Error(`Failed to fetch models: ${res.statusText}`);
  return res.json();
}

export async function fetchDemoSamples(): Promise<DemoSamplesResponse> {
  const res = await fetch(`${BASE_URL}/demo-samples`);
  if (!res.ok) throw new Error(`Failed to fetch demo samples: ${res.statusText}`);
  return res.json();
}

export async function analyzeUploadedFile(file: File): Promise<AnalyzeResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${BASE_URL}/analyze`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(errorData.detail || 'Analysis request failed');
  }

  return res.json();
}

export async function analyzeDemoSample(sampleId: string): Promise<AnalyzeResponse> {
  const formData = new FormData();
  formData.append('sample_id', sampleId);

  const res = await fetch(`${BASE_URL}/analyze`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(errorData.detail || 'Demo sample analysis failed');
  }

  return res.json();
}

export async function fetchAnalysesHistory(): Promise<AnalysisSummaryItem[]> {
  const res = await fetch(`${BASE_URL}/analyses`);
  if (!res.ok) throw new Error(`Failed to fetch analyses history: ${res.statusText}`);
  return res.json();
}

export async function fetchAnalysisById(analysisId: string): Promise<AnalyzeResponse> {
  const res = await fetch(`${BASE_URL}/analyses/${analysisId}`);
  if (!res.ok) throw new Error(`Failed to fetch analysis ${analysisId}: ${res.statusText}`);
  return res.json();
}

export async function clearAnalysesHistory(): Promise<{ message: string; cleared_count: number }> {
  const res = await fetch(`${BASE_URL}/analyses`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error(`Failed to clear history: ${res.statusText}`);
  return res.json();
}

export async function fetchEvaluationSummary(): Promise<EvaluationSummaryResponse> {
  const res = await fetch(`${BASE_URL}/evaluation/summary`);
  if (!res.ok) throw new Error(`Failed to fetch evaluation summary: ${res.statusText}`);
  return res.json();
}

export async function fetchEvaluationAblations(): Promise<AblationsResponse> {
  const res = await fetch(`${BASE_URL}/evaluation/ablations`);
  if (!res.ok) throw new Error(`Failed to fetch ablations: ${res.statusText}`);
  return res.json();
}

export async function fetchEvaluationCurves(): Promise<CurvesResponse> {
  const res = await fetch(`${BASE_URL}/evaluation/curves`);
  if (!res.ok) throw new Error(`Failed to fetch curves: ${res.statusText}`);
  return res.json();
}
