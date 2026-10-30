import React, { useState } from 'react';
import {
  History,
  Trash2,
  FileSearch,
  CheckCircle,
  AlertTriangle,
  ArrowRight,
} from 'lucide-react';
import { AnalysisSummaryItem, AnalyzeResponse } from '../types/api';
import { fetchAnalysisById, clearAnalysesHistory } from '../services/api';

interface HistoryViewProps {
  history: AnalysisSummaryItem[];
  onSelectAnalysis: (analysis: AnalyzeResponse) => void;
  onClearHistory: () => void;
  onNavigateToAnalyze: () => void;
}

export const HistoryView: React.FC<HistoryViewProps> = ({
  history,
  onSelectAnalysis,
  onClearHistory,
  onNavigateToAnalyze,
}) => {
  const [loadingId, setLoadingId] = useState<string | null>(null);

  const handleInspect = async (id: string) => {
    setLoadingId(id);
    try {
      const fullAnalysis = await fetchAnalysisById(id);
      onSelectAnalysis(fullAnalysis);
    } catch (err) {
      console.error('Failed to load past analysis:', err);
    } finally {
      setLoadingId(null);
    }
  };

  const handleClear = async () => {
    if (window.confirm('Are you sure you want to clear the session analysis history?')) {
      try {
        await clearAnalysesHistory();
        onClearHistory();
      } catch (err) {
        console.error('Failed to clear history:', err);
      }
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-charcoal-900">Analysis Audit Log</h1>
          <p className="text-xs text-charcoal-500 mt-0.5">
            Audit trail of all digital evidence triage operations conducted during this session.
          </p>
        </div>
        {history.length > 0 && (
          <div className="flex items-center space-x-3">
            <button
              onClick={handleClear}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-border text-xs font-semibold text-charcoal-600 hover:text-red-700 hover:border-red-200 hover:bg-red-50/50 cursor-pointer transition-colors"
            >
              <Trash2 className="h-3.5 w-3.5" />
              <span>Clear Audit Log</span>
            </button>
          </div>
        )}
      </div>

      {history.length === 0 ? (
        <div className="rounded-xl border border-border bg-surface p-12 text-center space-y-4 shadow-xs">
          <History className="h-10 w-10 text-charcoal-400 mx-auto" />
          <div className="space-y-1">
            <h3 className="text-sm font-semibold text-charcoal-800">No Evidence Analyzed Yet</h3>
            <p className="text-xs text-charcoal-500 max-w-sm mx-auto">
              Run forensic analyses using either curated benchmark targets or custom uploaded files.
            </p>
          </div>
          <div>
            <button
              onClick={onNavigateToAnalyze}
              className="inline-flex items-center space-x-2 px-4 py-2 rounded-lg bg-olive-700 hover:bg-olive-800 text-white font-medium text-xs shadow-sm cursor-pointer transition-colors"
            >
              <span>Go to Evidence Analysis</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      ) : (
        <div className="rounded-xl border border-border bg-surface shadow-xs overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-surface-subtle text-charcoal-500 font-semibold uppercase text-[10px] tracking-wider border-b border-border">
                <tr>
                  <th className="py-3 px-4">Timestamp</th>
                  <th className="py-3 px-4">Evidence Artifact</th>
                  <th className="py-3 px-4">Size</th>
                  <th className="py-3 px-4">Triage Verdict</th>
                  <th className="py-3 px-4 text-right">Probability</th>
                  <th className="py-3 px-4">Attributed Technique</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {history.map((item) => (
                  <tr key={item.analysis_id} className="hover:bg-surface-subtle/50 transition-colors">
                    <td className="py-3 px-4 font-mono text-[11px] text-charcoal-500 whitespace-nowrap">
                      {new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                    </td>
                    <td className="py-3 px-4 font-mono font-medium text-charcoal-900 whitespace-nowrap">
                      {item.filename}
                    </td>
                    <td className="py-3 px-4 font-mono text-charcoal-500 whitespace-nowrap">
                      {(((item.file_size_bytes ?? 0) / 1024)).toFixed(1)} KB
                    </td>
                    <td className="py-3 px-4 whitespace-nowrap">
                      <span
                        className={`inline-flex items-center space-x-1.5 px-2 py-0.5 rounded-full text-[11px] font-semibold border ${
                          item.is_manipulated
                            ? 'bg-amber-50 text-amber-900 border-amber-200'
                            : 'bg-olive-50 text-olive-900 border-olive-200'
                        }`}
                      >
                        {item.is_manipulated ? (
                          <AlertTriangle className="h-3 w-3 text-amber-600" />
                        ) : (
                          <CheckCircle className="h-3 w-3 text-olive-600" />
                        )}
                        <span>{item.predicted_label}</span>
                      </span>
                    </td>
                    <td className="py-3 px-4 font-mono font-semibold text-right whitespace-nowrap">
                      {(((item.manipulation_probability ?? 0) * 100)).toFixed(1)}%
                    </td>
                    <td className="py-3 px-4 text-charcoal-700 capitalize whitespace-nowrap">
                      {(item.attributed_technique || 'N/A').replace(/_/g, ' ')}
                    </td>
                    <td className="py-3 px-4 text-right whitespace-nowrap">
                      <button
                        onClick={() => handleInspect(item.analysis_id)}
                        disabled={loadingId === item.analysis_id}
                        className="inline-flex items-center space-x-1 px-2.5 py-1 rounded bg-surface border border-border text-[11px] font-medium text-charcoal-700 hover:bg-surface-subtle hover:text-olive-800 cursor-pointer transition-colors"
                      >
                        {loadingId === item.analysis_id ? (
                          <span className="text-[10px]">Loading...</span>
                        ) : (
                          <>
                            <FileSearch className="h-3 w-3 text-olive-600" />
                            <span>Inspect</span>
                          </>
                        )}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
