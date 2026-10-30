import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { Sidebar, TabId } from './components/Sidebar';
import { ErrorBoundary } from './components/ErrorBoundary';
import { OverviewView } from './views/OverviewView';
import { AnalyzeView } from './views/AnalyzeView';
import { HistoryView } from './views/HistoryView';
import { EvaluationView } from './views/EvaluationView';
import {
  HealthResponse,
  OverviewResponse,
  DemoSampleItem,
  AnalysisSummaryItem,
  AnalyzeResponse,
  EvaluationSummaryResponse,
  AblationsResponse,
  CurvesResponse,
} from './types/api';
import {
  fetchHealth,
  fetchOverview,
  fetchDemoSamples,
  fetchAnalysesHistory,
  fetchEvaluationSummary,
  fetchEvaluationAblations,
  fetchEvaluationCurves,
} from './services/api';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabId>('analyze');
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [overview, setOverview] = useState<OverviewResponse | null>(null);
  const [demoSamples, setDemoSamples] = useState<DemoSampleItem[]>([]);
  const [history, setHistory] = useState<AnalysisSummaryItem[]>([]);
  const [currentAnalysis, setCurrentAnalysis] = useState<AnalyzeResponse | null>(null);
  const [evaluation, setEvaluation] = useState<EvaluationSummaryResponse | null>(null);
  const [ablations, setAblations] = useState<AblationsResponse | null>(null);
  const [curves, setCurves] = useState<CurvesResponse | null>(null);
  const [initialLoading, setInitialLoading] = useState<boolean>(true);

  // Load initial application data
  useEffect(() => {
    async function loadData() {
      try {
        const [
          healthData,
          overviewData,
          demosData,
          historyData,
          evalData,
          ablationsData,
          curvesData,
        ] = await Promise.allSettled([
          fetchHealth(),
          fetchOverview(),
          fetchDemoSamples(),
          fetchAnalysesHistory(),
          fetchEvaluationSummary(),
          fetchEvaluationAblations(),
          fetchEvaluationCurves(),
        ]);

        if (healthData.status === 'fulfilled') setHealth(healthData.value);
        if (overviewData.status === 'fulfilled') setOverview(overviewData.value);
        if (demosData.status === 'fulfilled') setDemoSamples(demosData.value.samples);
        if (historyData.status === 'fulfilled') setHistory(historyData.value);
        if (evalData.status === 'fulfilled') setEvaluation(evalData.value);
        if (ablationsData.status === 'fulfilled') setAblations(ablationsData.value);
        if (curvesData.status === 'fulfilled') setCurves(curvesData.value);
      } catch (err) {
        console.error('Initial data fetch error:', err);
      } finally {
        setInitialLoading(false);
      }
    }

    loadData();
  }, []);

  const handleAnalysisSuccess = (analysis: AnalyzeResponse) => {
    // Add to local history list
    const summaryItem: AnalysisSummaryItem = {
      analysis_id: analysis.analysis_id,
      filename: analysis.evidence_provenance?.filename || 'evidence_artifact',
      file_size_bytes: analysis.evidence_provenance?.file_size_bytes || 0,
      declared_extension:
        analysis.observed_physical_facts?.declared_extension ||
        analysis.evidence_provenance?.declared_extension ||
        '',
      predicted_label: analysis.final_prediction?.predicted_label || 'Triage Complete',
      is_manipulated: Boolean(analysis.final_prediction?.is_manipulated),
      manipulation_probability: analysis.final_prediction?.manipulation_probability || 0,
      attributed_technique: analysis.final_prediction?.attributed_technique || 'N/A',
      timestamp: analysis.timestamp || new Date().toISOString(),
    };
    setHistory((prev) => [summaryItem, ...prev.filter((p) => p.analysis_id !== analysis.analysis_id)]);
  };

  const handleSelectAnalysis = (analysis: AnalyzeResponse) => {
    setCurrentAnalysis(analysis);
    setActiveTab('analyze');
  };

  const handleClearHistory = () => {
    setHistory([]);
  };

  return (
    <div className="min-h-screen bg-background flex flex-col font-sans text-charcoal-800">
      <Navbar health={health} activeTab={activeTab} />

      <div className="flex-1 flex">
        <Sidebar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          analysesCount={history.length}
        />

        <main className="flex-1 p-8 overflow-y-auto max-h-[calc(100vh-65px)]">
          {initialLoading ? (
            <div className="flex flex-col items-center justify-center h-64 space-y-3">
              <div className="h-6 w-6 border-2 border-olive-700 border-t-transparent rounded-full animate-spin" />
              <p className="text-xs text-charcoal-500 font-mono">
                Initializing ForensiGuard pipeline & loading checkpoints...
              </p>
            </div>
          ) : (
            <ErrorBoundary
              fallbackTitle="Component Display Exception"
              onReset={() => setCurrentAnalysis(null)}
            >
              {activeTab === 'overview' && (
                <OverviewView
                  overview={overview}
                  onNavigateToAnalyze={() => setActiveTab('analyze')}
                />
              )}

              {activeTab === 'analyze' && (
                <AnalyzeView
                  demoSamples={demoSamples}
                  currentAnalysis={currentAnalysis}
                  setCurrentAnalysis={setCurrentAnalysis}
                  onAnalysisSuccess={handleAnalysisSuccess}
                />
              )}

              {activeTab === 'history' && (
                <HistoryView
                  history={history}
                  onSelectAnalysis={handleSelectAnalysis}
                  onClearHistory={handleClearHistory}
                  onNavigateToAnalyze={() => setActiveTab('analyze')}
                />
              )}

              {activeTab === 'evaluation' && (
                <EvaluationView
                  evaluation={evaluation}
                  ablations={ablations}
                  curves={curves}
                />
              )}
            </ErrorBoundary>
          )}
        </main>
      </div>
    </div>
  );
};
export default App;
