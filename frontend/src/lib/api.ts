import type {
  AnalysisResponse as TypedAnalysisResponse,
  AnalysisRequest,
  ProgressResponse,
  ReportResponse,
  FullReport,
  AnalysisStatus,
  ModuleStatus,
} from "./types";

const API_URL = "";

export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public detail?: string,
  ) {
    super(message);
    this.name = "APIError";
  }
}

async function fetchAPI<T>(
  endpoint: string,
  options?: RequestInit,
): Promise<T> {
  const url = `${API_URL}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new APIError(
      error.detail || `API Error: ${response.status}`,
      response.status,
      error.detail,
    );
  }

  return response.json();
}

export interface AnalysisResponse {
  id: string;
  status: AnalysisStatus;
}

export interface AnalysisOptions {
  description?: string;
  industry?: string;
  email?: string;
}

export async function startAnalysis(
  url: string,
  options?: AnalysisOptions,
): Promise<AnalysisResponse> {
  return fetchAPI<AnalysisResponse>("/api/v1/analyze", {
    method: "POST",
    body: JSON.stringify({ url, ...options }),
  });
}

export interface AnalysisProgress {
  id: string;
  status: AnalysisStatus;
  modules: Record<string, ModuleStatus>;
  completion_percentage: number;
  overall_score?: number;
  completed?: boolean;
  error?: string;
}

export async function getAnalysisProgress(
  id: string,
): Promise<AnalysisProgress> {
  return fetchAPI<AnalysisProgress>(`/api/v1/analysis/${id}/progress`);
}

export interface ReportData {
  id: string;
  url: string;
  overall_score: number;
  scores: Record<string, number>;
  report: FullReport;
}

export async function getReport(id: string): Promise<ReportData> {
  return fetchAPI<ReportData>(`/api/v1/analysis/${id}/report`);
}

export function getPDFUrl(id: string): string {
  return `${API_URL}/api/v1/analysis/${id}/pdf`;
}

export const submitAnalysis = startAnalysis;

export async function getAnalysisStatus(id: string) {
  return fetchAPI<TypedAnalysisResponse>(`/api/v1/analysis/${id}`);
}

export type {
  FullReport,
  AnalysisStatus,
  ModuleStatus,
  ProgressResponse,
  ReportResponse,
};

export * from "./types";
