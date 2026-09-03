const backendBaseUrl = process.env.NEXT_PUBLIC_BACKEND_BASE_URL ?? "http://localhost:8000";

export interface AnalyzeResponse {
  analysis_id: string;
  status: "accepted";
  repo_url: string;
}

export interface GraphNode {
  id: string;
  label: string;
  type: string;
}

export interface GraphEdge {
  source: string;
  target: string;
  type: string;
}

export interface ObjectiveMapping {
  interface: string;
  objective: string;
}

export interface AnalysisResultsResponse {
  analysis_id: string;
  status: "complete";
  graph: {
    nodes: GraphNode[];
    edges: GraphEdge[];
  };
  objective_mappings: ObjectiveMapping[];
  orphaned_code_units: Record<string, unknown>[];
  traceability_score: number;
}

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${backendBaseUrl}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`Backend request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function analyzeRepository(repoUrl: string): Promise<AnalyzeResponse> {
  return requestJson<AnalyzeResponse>("/api/analyze", {
    method: "POST",
    body: JSON.stringify({ repo_url: repoUrl }),
  });
}

export function getAnalysisResults(analysisId: string): Promise<AnalysisResultsResponse> {
  return requestJson<AnalysisResultsResponse>(`/api/analyze/${analysisId}/results`);
}
