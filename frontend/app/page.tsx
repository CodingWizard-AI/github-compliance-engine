"use client";

import { FormEvent, useMemo, useState } from "react";
import {
  AnalyzeResponse,
  AnalysisResultsResponse,
  analyzeRepository,
  getAnalysisResults,
} from "../lib/api";

const defaultRepoUrl = "https://github.com/octocat/Hello-World";

export default function Home() {
  const [repoUrl, setRepoUrl] = useState(defaultRepoUrl);
  const [analysis, setAnalysis] = useState<AnalyzeResponse | null>(null);
  const [results, setResults] = useState<AnalysisResultsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const scorePercent = useMemo(() => {
    if (!results) {
      return "0%";
    }
    return `${Math.round(results.traceability_score * 100)}%`;
  }, [results]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setAnalysis(null);
    setResults(null);
    setIsSubmitting(true);

    try {
      const accepted = await analyzeRepository(repoUrl);
      setAnalysis(accepted);
      const completed = await getAnalysisResults(accepted.analysis_id);
      setResults(completed);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Analysis request failed");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="shell">
      <section className="workspace" aria-labelledby="page-title">
        <header className="header">
          <div>
            <p className="eyebrow">FEAT-SCAFFOLD-001</p>
            <h1 id="page-title">GitHub Compliance Engine</h1>
            <p className="summary">
              Submit a public GitHub repository URL and review the placeholder Golden Thread
              traceability report returned by the Python backend scaffold.
            </p>
          </div>
          <div className="score" aria-label="Traceability score">
            <span>{scorePercent}</span>
            <small>Traceability</small>
          </div>
        </header>

        <form className="analysis-form" onSubmit={handleSubmit}>
          <label htmlFor="repo-url">Repository URL</label>
          <div className="form-row">
            <input
              id="repo-url"
              name="repo-url"
              type="url"
              value={repoUrl}
              onChange={(event) => setRepoUrl(event.target.value)}
              placeholder="https://github.com/owner/repo"
              required
            />
            <button type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Analyzing" : "Analyze"}
            </button>
          </div>
        </form>

        {error ? <p className="error" role="alert">{error}</p> : null}

        <section className="status-grid" aria-label="Analysis status">
          <div>
            <span>Analysis ID</span>
            <strong>{analysis?.analysis_id ?? "Not submitted"}</strong>
          </div>
          <div>
            <span>Status</span>
            <strong>{results?.status ?? analysis?.status ?? "Idle"}</strong>
          </div>
          <div>
            <span>Backend route</span>
            <strong>REST-RESULTS-001</strong>
          </div>
        </section>

        <section className="results-layout" aria-label="Analysis results">
          <article>
            <h2>Graph</h2>
            <div className="graph-list">
              <div>
                <h3>Nodes</h3>
                <ul>
                  {(results?.graph.nodes ?? []).map((node) => (
                    <li key={node.id}>
                      <span>{node.type}</span>
                      {node.label}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h3>Edges</h3>
                <ul>
                  {(results?.graph.edges ?? []).map((edge) => (
                    <li key={`${edge.source}-${edge.target}-${edge.type}`}>
                      <span>{edge.type}</span>
                      {edge.source} to {edge.target}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </article>

          <article>
            <h2>Objective Mappings</h2>
            <ul className="records">
              {(results?.objective_mappings ?? []).map((mapping) => (
                <li key={`${mapping.interface}-${mapping.objective}`}>
                  <span>{mapping.interface}</span>
                  {mapping.objective}
                </li>
              ))}
            </ul>
          </article>

          <article>
            <h2>Orphaned Code Units</h2>
            {results && results.orphaned_code_units.length === 0 ? (
              <p className="empty">No orphaned code units in the placeholder response.</p>
            ) : (
              <p className="empty">Run an analysis to load placeholder orphan checks.</p>
            )}
          </article>
        </section>
      </section>
    </main>
  );
}
