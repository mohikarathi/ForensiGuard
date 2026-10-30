import React, { useState, useEffect } from 'react';
import {
  UploadCloud,
  FileCheck2,
  AlertTriangle,
  CheckCircle,
  ArrowRight,
  Download,
  Copy,
  Sparkles,
} from 'lucide-react';
import {
  DemoSampleItem,
  AnalyzeResponse,
} from '../types/api';
import {
  analyzeUploadedFile,
  analyzeDemoSample,
} from '../services/api';

const formatTimestamp = (ts?: number, str?: string): string => {
  if (str) return str;
  if (typeof ts === 'number' && !isNaN(ts) && ts > 0) {
    try {
      return new Date(ts * 1000).toISOString().slice(0, 19).replace('T', ' ') + ' UTC';
    } catch {
      return String(ts);
    }
  }
  return 'N/A';
};

interface AnalyzeViewProps {
  demoSamples: DemoSampleItem[];
  currentAnalysis: AnalyzeResponse | null;
  setCurrentAnalysis: (analysis: AnalyzeResponse | null) => void;
  onAnalysisSuccess: (analysis: AnalyzeResponse) => void;
}

export const AnalyzeView: React.FC<AnalyzeViewProps> = ({
  demoSamples,
  currentAnalysis,
  setCurrentAnalysis,
  onAnalysisSuccess,
}) => {
  const [mode, setMode] = useState<'demo' | 'upload'>('demo');
  const [selectedDemoId, setSelectedDemoId] = useState<string>('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [loadingStage, setLoadingStage] = useState<string>('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [copiedHash, setCopiedHash] = useState<string | null>(null);

  // Set default demo sample if available
  useEffect(() => {
    if (demoSamples.length > 0 && !selectedDemoId) {
      setSelectedDemoId(demoSamples[0].sample_id);
    }
  }, [demoSamples, selectedDemoId]);

  const activeDemo = demoSamples.find((s) => s.sample_id === selectedDemoId);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.size > 25 * 1024 * 1024) {
        setErrorMessage('File exceeds maximum upload limit of 25 MB.');
        return;
      }
      setSelectedFile(file);
      setErrorMessage(null);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (file.size > 25 * 1024 * 1024) {
        setErrorMessage('File exceeds maximum upload limit of 25 MB.');
        return;
      }
      setSelectedFile(file);
      setErrorMessage(null);
    }
  };

  const handleExecuteAnalysis = async () => {
    setLoading(true);
    setErrorMessage(null);
    setLoadingStage('Inspecting file and computing cryptographic hashes...');

    try {
      let result: AnalyzeResponse;
      if (mode === 'demo') {
        if (!selectedDemoId) {
          throw new Error('Please select a sample to analyze.');
        }
        setTimeout(() => setLoadingStage('Extracting MACB timestamps & headers...'), 350);
        setTimeout(() => setLoadingStage('Evaluating multimodal detectors & explainability...'), 700);
        result = await analyzeDemoSample(selectedDemoId);
      } else {
        if (!selectedFile) {
          throw new Error('Please select a file to analyze.');
        }
        setTimeout(() => setLoadingStage('Extracting metadata and byte statistics...'), 400);
        setTimeout(() => setLoadingStage('Running detection models & feature attributions...'), 800);
        result = await analyzeUploadedFile(selectedFile);
      }

      setCurrentAnalysis(result);
      onAnalysisSuccess(result);
    } catch (err: any) {
      setErrorMessage(err.message || 'An error occurred during analysis.');
    } finally {
      setLoading(false);
      setLoadingStage('');
    }
  };

  const copyToClipboard = (text: string, type: string) => {
    navigator.clipboard.writeText(text);
    setCopiedHash(type);
    setTimeout(() => setCopiedHash(null), 2000);
  };

  const exportJsonReport = () => {
    if (!currentAnalysis) return;
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(currentAnalysis, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', `ForensiGuard_Report_${currentAnalysis.analysis_id}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-12">
      {/* Evidence Selection Header Card */}
      <div className="rounded-xl border border-border bg-surface p-6 shadow-xs space-y-5">
        <div>
          <h1 className="text-xl font-bold text-charcoal-900">Evidence File Analysis</h1>
          <p className="text-xs text-charcoal-500 mt-0.5">
            Scan files to detect timestomping, hidden payloads, or disguised file types.
          </p>
        </div>

        {/* Input Mode Selector */}
        <div className="flex border-b border-border">
          <button
            onClick={() => {
              setMode('demo');
              setErrorMessage(null);
            }}
            className={`pb-3 px-4 text-xs font-semibold border-b-2 transition-all cursor-pointer ${
              mode === 'demo'
                ? 'border-olive-700 text-olive-900'
                : 'border-transparent text-charcoal-500 hover:text-charcoal-800'
            }`}
          >
            Sample Test Files ({demoSamples.length})
          </button>
          <button
            onClick={() => {
              setMode('upload');
              setErrorMessage(null);
            }}
            className={`pb-3 px-4 text-xs font-semibold border-b-2 transition-all cursor-pointer ${
              mode === 'upload'
                ? 'border-olive-700 text-olive-900'
                : 'border-transparent text-charcoal-500 hover:text-charcoal-800'
            }`}
          >
            Upload Local File
          </button>
        </div>

        {/* Mode 1: Sample Files */}
        {mode === 'demo' && (
          <div className="space-y-3">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
              {demoSamples.map((sample) => {
                const isSelected = selectedDemoId === sample.sample_id;
                return (
                  <button
                    key={sample.sample_id}
                    onClick={() => setSelectedDemoId(sample.sample_id)}
                    className={`p-3 rounded-lg text-left border transition-all cursor-pointer flex flex-col justify-between ${
                      isSelected
                        ? 'border-olive-600 bg-olive-50/70 shadow-xs ring-1 ring-olive-600/30'
                        : 'border-border bg-surface-subtle/50 hover:bg-surface-subtle hover:border-border-strong'
                    }`}
                  >
                    <div>
                      <div className="flex items-center justify-between">
                        <span className="font-mono text-[11px] font-semibold text-charcoal-800 truncate">
                          {sample.filename}
                        </span>
                      </div>
                      <div className="text-[11px] text-charcoal-600 font-medium capitalize mt-1">
                        {sample.technique.replace(/_/g, ' ')}
                      </div>
                      <div className="text-[10px] text-charcoal-400 capitalize">
                        {sample.subtype.replace(/_/g, ' ')}
                      </div>
                    </div>
                    <div className="mt-2 text-[10px] font-mono text-charcoal-500 flex justify-between border-t border-border/60 pt-1.5">
                      <span>{sample.declared_extension}</span>
                      <span>{(((sample.file_size_bytes ?? 0) / 1024)).toFixed(1)} KB</span>
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Active Demo Description */}
            {activeDemo && (
              <div className="p-3 rounded-lg border border-border bg-surface-subtle text-xs space-y-1">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-charcoal-800">
                    Selected: <span className="font-mono text-olive-700">{activeDemo.filename}</span>
                  </span>
                  <span className="font-mono text-[11px] text-charcoal-500">
                    MIME: {activeDemo.detected_mime_type}
                  </span>
                </div>
                <p className="text-charcoal-600 text-[11px] leading-relaxed">
                  {activeDemo.description}
                </p>
              </div>
            )}
          </div>
        )}

        {/* Mode 2: Custom File Upload */}
        {mode === 'upload' && (
          <div className="space-y-4">
            <div
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              className={`border-2 border-dashed rounded-xl p-8 text-center transition-all ${
                dragActive
                  ? 'border-olive-600 bg-olive-50/50'
                  : 'border-border bg-surface-subtle/40 hover:bg-surface-subtle'
              }`}
            >
              <UploadCloud className="h-10 w-10 text-charcoal-400 mx-auto mb-3" />
              <div className="space-y-1">
                <p className="text-sm font-semibold text-charcoal-800">
                  Drag and drop a digital evidence file here
                </p>
                <p className="text-xs text-charcoal-500">
                  Supports Images (.png, .jpg, .jpeg) and general documents. Max 25 MB.
                </p>
              </div>
              <div className="mt-4">
                <label className="inline-flex items-center px-4 py-2 rounded-lg bg-surface border border-border-strong text-xs font-semibold text-charcoal-800 hover:bg-surface-subtle shadow-xs cursor-pointer transition-colors">
                  <span>Browse Local File</span>
                  <input
                    type="file"
                    className="hidden"
                    onChange={handleFileChange}
                  />
                </label>
              </div>
            </div>

            {selectedFile && (
              <div className="flex items-center justify-between p-3.5 rounded-lg border border-olive-200 bg-olive-50/60 text-xs">
                <div className="flex items-center space-x-2.5">
                  <FileCheck2 className="h-4 w-4 text-olive-700" />
                  <span className="font-mono font-semibold text-charcoal-900">{selectedFile.name}</span>
                  <span className="text-charcoal-500">
                    ({(((selectedFile?.size ?? 0) / 1024)).toFixed(1)} KB)
                  </span>
                </div>
                <button
                  onClick={() => setSelectedFile(null)}
                  className="text-xs text-charcoal-500 hover:text-charcoal-900 font-medium cursor-pointer"
                >
                  Remove
                </button>
              </div>
            )}
          </div>
        )}

        {/* Error Alert */}
        {errorMessage && (
          <div className="p-3 rounded-lg border border-red-200 bg-red-50 text-red-800 text-xs flex items-center space-x-2">
            <AlertTriangle className="h-4 w-4 text-red-600 shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}

        {/* Execution Trigger Button */}
        <div className="flex justify-end pt-1">
          <button
            onClick={handleExecuteAnalysis}
            disabled={loading || (mode === 'upload' && !selectedFile)}
            className={`inline-flex items-center space-x-2 px-6 py-2.5 rounded-lg font-medium text-sm transition-all shadow-sm ${
              loading || (mode === 'upload' && !selectedFile)
                ? 'bg-charcoal-300 text-charcoal-500 cursor-not-allowed'
                : 'bg-olive-700 hover:bg-olive-800 text-white cursor-pointer'
            }`}
          >
            {loading ? (
              <>
                <div className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Scanning File...</span>
              </>
            ) : (
              <>
                <span>Run Analysis</span>
                <ArrowRight className="h-4 w-4" />
              </>
            )}
          </button>
        </div>

        {/* Live Loading Stage Tracker */}
        {loading && (
          <div className="p-3 rounded-lg bg-surface-subtle border border-border text-xs text-charcoal-600 flex items-center space-x-3 animate-pulse">
            <div className="h-2 w-2 rounded-full bg-olive-600" />
            <span className="font-mono text-[11px]">{loadingStage}</span>
          </div>
        )}
      </div>

      {/* Analysis Results View */}
      {currentAnalysis && (
        <div className="space-y-6">
          {/* Main Top Verdict Card */}
          <div
            className={`rounded-xl border p-6 shadow-xs space-y-4 transition-all ${
              currentAnalysis.final_prediction?.is_manipulated
                ? 'border-red-300 bg-gradient-to-br from-red-50/70 to-surface'
                : 'border-olive-200 bg-gradient-to-br from-olive-50/50 to-surface'
            }`}
          >
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="flex items-start space-x-3.5">
                <div
                  className={`p-2.5 rounded-lg ${
                    currentAnalysis.final_prediction?.is_manipulated
                      ? 'bg-red-600 text-white'
                      : 'bg-olive-700 text-white'
                  }`}
                >
                  {currentAnalysis.final_prediction?.is_manipulated ? (
                    <AlertTriangle className="h-6 w-6" />
                  ) : (
                    <CheckCircle className="h-6 w-6" />
                  )}
                </div>
                <div>
                  <div className="text-xs uppercase tracking-wider font-semibold text-charcoal-500">
                    Verdict
                  </div>
                  <h2
                    className={`text-xl font-bold mt-0.5 ${
                      currentAnalysis.final_prediction?.is_manipulated
                        ? 'text-red-700'
                        : 'text-charcoal-900'
                    }`}
                  >
                    {currentAnalysis.final_prediction?.is_manipulated
                      ? 'Tampering Detected'
                      : 'Clean / Unmodified'}
                  </h2>
                  <p className="text-xs text-charcoal-600 mt-1 max-w-2xl leading-relaxed">
                    {currentAnalysis.final_prediction?.threshold_explanation || ''}
                  </p>
                </div>
              </div>

              {/* Manipulation Probability Gauge / Metric */}
              <div className="flex items-center space-x-6 md:border-l md:border-border md:pl-6 shrink-0">
                <div className="text-right">
                  <div className="text-xs text-charcoal-500 font-medium">Tamper Probability</div>
                  <div
                    className={`text-2xl font-bold font-mono ${
                      currentAnalysis.final_prediction?.is_manipulated
                        ? 'text-red-700'
                        : 'text-charcoal-900'
                    }`}
                  >
                    {((currentAnalysis.final_prediction?.manipulation_probability ?? 0) * 100).toFixed(1)}%
                  </div>
                </div>

                <div className="text-right">
                  <div className="text-xs text-charcoal-500 font-medium">Detected Technique</div>
                  <div className="text-sm font-bold text-olive-800">
                    {currentAnalysis.final_prediction?.attributed_technique || 'None'}
                  </div>
                  <div className="text-[10px] text-charcoal-400">
                    Confidence: {((currentAnalysis.final_prediction?.confidence ?? 0) * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
            </div>

            {/* Attribution Probabilities Bar */}
            {currentAnalysis.final_prediction?.attribution_probabilities &&
              Object.keys(currentAnalysis.final_prediction.attribution_probabilities).length > 0 && (
              <div className="pt-3 border-t border-border/80 space-y-2">
                <div className="flex justify-between text-xs text-charcoal-600 font-medium">
                  <span>Technique Likelihood</span>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-2 text-xs">
                  {Object.entries(currentAnalysis.final_prediction.attribution_probabilities).map(([cls, prob]) => (
                    <div key={cls} className="p-2 rounded bg-surface border border-border space-y-1">
                      <div className="flex justify-between text-[11px]">
                        <span className="capitalize text-charcoal-600 truncate">{cls.replace(/_/g, ' ')}</span>
                        <span className="font-mono font-semibold text-charcoal-900">{((prob ?? 0) * 100).toFixed(1)}%</span>
                      </div>
                      <div className="w-full h-1.5 rounded-full bg-surface-subtle overflow-hidden">
                        <div
                          className="h-full bg-olive-600 rounded-full"
                          style={{ width: `${Math.min(100, Math.max(2, (prob ?? 0) * 100))}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* 5-Component Breakdown Cards */}
          <div className="space-y-3">
            <h3 className="text-sm font-bold text-charcoal-900">Multi-Modal Signals</h3>
            <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
              {/* Metadata Classifier */}
              <div className="p-3.5 rounded-lg border border-border bg-surface space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-charcoal-800">Timestamps</span>
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-olive-50 text-olive-800 border border-olive-200">
                    Metadata
                  </span>
                </div>
                <div className="text-xl font-bold font-mono text-charcoal-900">
                  {currentAnalysis.component_breakdown?.metadata_classifier?.score_display ||
                    `${((currentAnalysis.component_breakdown?.metadata_classifier?.probability ?? 0) * 100).toFixed(1)}%`}
                </div>
                <p className="text-[11px] text-charcoal-500 leading-tight">
                  {currentAnalysis.component_breakdown?.metadata_classifier?.interpretation ||
                    currentAnalysis.component_breakdown?.metadata_classifier?.contribution_description ||
                    'Nominal filesystem chronology'}
                </p>
              </div>

              {/* Image CNN */}
              <div className="p-3.5 rounded-lg border border-border bg-surface space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-charcoal-800">Steganography</span>
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-surface-subtle text-charcoal-600 border border-border">
                    Pixel Noise
                  </span>
                </div>
                <div className="text-xl font-bold font-mono text-charcoal-900">
                  {currentAnalysis.component_breakdown?.image_cnn?.ran
                    ? (currentAnalysis.component_breakdown?.image_cnn?.score_display ||
                        `${((currentAnalysis.component_breakdown?.image_cnn?.probability ?? 0) * 100).toFixed(1)}%`)
                    : 'Bypassed'}
                </div>
                <p className="text-[11px] text-charcoal-500 leading-tight">
                  {currentAnalysis.component_breakdown?.image_cnn?.interpretation ||
                    currentAnalysis.component_breakdown?.image_cnn?.contribution_description ||
                    'Spatial residual scan'}
                </p>
              </div>

              {/* Anomaly Detector */}
              <div className="p-3.5 rounded-lg border border-border bg-surface space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-charcoal-800">Anomaly Check</span>
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-surface-subtle text-charcoal-600 border border-border">
                    Outlier
                  </span>
                </div>
                <div className="text-xl font-bold font-mono text-charcoal-900">
                  {currentAnalysis.component_breakdown?.anomaly_detector?.score_display ||
                    `${((currentAnalysis.component_breakdown?.anomaly_detector?.probability ?? 0) * 100).toFixed(1)}%`}
                </div>
                <p className="text-[11px] text-charcoal-500 leading-tight">
                  {currentAnalysis.component_breakdown?.anomaly_detector?.interpretation ||
                    currentAnalysis.component_breakdown?.anomaly_detector?.contribution_description ||
                    'Within nominal cluster'}
                </p>
              </div>

              {/* Signature Verifier */}
              <div className="p-3.5 rounded-lg border border-border bg-surface space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-charcoal-800">File Signature</span>
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-surface-subtle text-charcoal-600 border border-border">
                    Magic Bytes
                  </span>
                </div>
                <div className="text-xl font-bold font-mono text-charcoal-900">
                  {currentAnalysis.component_breakdown?.signature_verifier?.score_display ||
                    (currentAnalysis.observed_physical_facts?.is_signature_mismatch ? 'MISMATCH' : 'VALID')}
                </div>
                <p className="text-[11px] text-charcoal-500 leading-tight">
                  {currentAnalysis.component_breakdown?.signature_verifier?.interpretation ||
                    currentAnalysis.component_breakdown?.signature_verifier?.contribution_description ||
                    'Header signature check'}
                </p>
              </div>

              {/* Late Fusion */}
              <div className="p-3.5 rounded-lg border border-olive-200 bg-olive-50/60 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-olive-900">Combined Result</span>
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-olive-200 text-olive-900">
                    Fusion
                  </span>
                </div>
                <div className="text-xl font-bold font-mono text-olive-800">
                  {currentAnalysis.component_breakdown?.late_fusion?.score_display ||
                    `${((currentAnalysis.component_breakdown?.late_fusion?.probability ?? 0) * 100).toFixed(1)}%`}
                </div>
                <p className="text-[11px] text-olive-800 leading-tight">
                  {currentAnalysis.component_breakdown?.late_fusion?.interpretation ||
                    currentAnalysis.component_breakdown?.late_fusion?.contribution_description ||
                    'Combined score from all detectors.'}
                </p>
              </div>
            </div>
          </div>

          {/* Key Influencing Factors */}
          {currentAnalysis.feature_attributions && currentAnalysis.feature_attributions.length > 0 && (
            <div className="rounded-xl border border-border bg-surface p-6 shadow-xs space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold text-charcoal-900">Key Decision Factors (TreeSHAP)</h3>
                  <p className="text-xs text-charcoal-500">
                    File properties that contributed most toward flagging or clearing this file.
                  </p>
                </div>
                <span className="text-xs font-mono text-charcoal-500">
                  Top {currentAnalysis.feature_attributions.length} Factors
                </span>
              </div>

              <div className="space-y-2.5 pt-2">
                {(() => {
                  const attributions = currentAnalysis.feature_attributions || [];
                  const maxAbsShap = Math.max(
                    ...attributions.map((a) => Math.abs(a.shap_value || 0)),
                    1.0
                  );

                  return attributions.map((attr) => {
                    const shapVal = attr.shap_value || 0;
                    const isPushingManip = shapVal > 0;
                    const barWidth = Math.min(100, (Math.abs(shapVal) / maxAbsShap) * 100);

                    return (
                      <div key={attr.feature} className="space-y-1 text-xs">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <span className="font-mono text-charcoal-800 font-medium">
                              {attr.feature_label || attr.feature}
                            </span>
                            <span className="text-[11px] font-mono text-charcoal-400">
                              (value: {typeof attr.value === 'number' ? attr.value.toFixed(2) : String(attr.value ?? '')})
                            </span>
                          </div>
                          <div className="flex items-center space-x-2 font-mono text-xs">
                            <span
                              className={`font-semibold ${
                                isPushingManip ? 'text-amber-700' : 'text-olive-700'
                              }`}
                            >
                              {shapVal > 0 ? '+' : ''}
                              {shapVal.toFixed(3)}
                            </span>
                            <span className="text-[10px] text-charcoal-400">
                              {isPushingManip ? 'Pushes Tampered' : 'Pushes Clean'}
                            </span>
                          </div>
                        </div>
                        {/* Visual bar */}
                        <div className="w-full h-2 rounded-full bg-surface-subtle overflow-hidden flex">
                          <div
                            className={`h-full rounded-full ${
                              isPushingManip ? 'bg-amber-600' : 'bg-olive-600'
                            }`}
                            style={{ width: `${barWidth}%` }}
                          />
                        </div>
                      </div>
                    );
                  });
                })()}
              </div>
            </div>
          )}

          {/* File Metadata & Checksums */}
          <div className="rounded-xl border border-border bg-surface p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-charcoal-900">File Metadata & Checksums</h3>
                <p className="text-xs text-charcoal-500">
                  Extracted timestamps, header signatures, and file identifiers.
                </p>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={exportJsonReport}
                  className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded bg-surface border border-border text-xs font-semibold text-charcoal-700 hover:bg-surface-subtle cursor-pointer transition-colors"
                >
                  <Download className="h-3.5 w-3.5 text-olive-600" />
                  <span>Download Report</span>
                </button>
              </div>
            </div>

            {/* Cryptographic Hashes */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
              <div className="p-3 rounded-lg bg-surface-subtle border border-border flex items-center justify-between">
                <div>
                  <span className="text-[10px] uppercase font-bold text-charcoal-400">SHA-256 Checksum</span>
                  <div className="font-mono text-charcoal-800 break-all text-[11px] mt-0.5">
                    {currentAnalysis.evidence_provenance?.sha256 || 'N/A'}
                  </div>
                </div>
                {currentAnalysis.evidence_provenance?.sha256 && (
                  <button
                    onClick={() => copyToClipboard(currentAnalysis.evidence_provenance.sha256, 'sha256')}
                    className="p-1.5 rounded hover:bg-surface text-charcoal-400 hover:text-charcoal-700 cursor-pointer ml-2 shrink-0"
                    title="Copy SHA-256"
                  >
                    {copiedHash === 'sha256' ? (
                      <CheckCircle className="h-3.5 w-3.5 text-olive-600" />
                    ) : (
                      <Copy className="h-3.5 w-3.5" />
                    )}
                  </button>
                )}
              </div>

              <div className="p-3 rounded-lg bg-surface-subtle border border-border flex items-center justify-between">
                <div>
                  <span className="text-[10px] uppercase font-bold text-charcoal-400">MD5 Checksum</span>
                  <div className="font-mono text-charcoal-800 break-all text-[11px] mt-0.5">
                    {currentAnalysis.evidence_provenance?.md5 || 'N/A'}
                  </div>
                </div>
                {currentAnalysis.evidence_provenance?.md5 && (
                  <button
                    onClick={() => copyToClipboard(currentAnalysis.evidence_provenance.md5, 'md5')}
                    className="p-1.5 rounded hover:bg-surface text-charcoal-400 hover:text-charcoal-700 cursor-pointer ml-2 shrink-0"
                    title="Copy MD5"
                  >
                    {copiedHash === 'md5' ? (
                      <CheckCircle className="h-3.5 w-3.5 text-olive-600" />
                    ) : (
                      <Copy className="h-3.5 w-3.5" />
                    )}
                  </button>
                )}
              </div>
            </div>

            {/* Physical Facts Matrix */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs pt-2">
              <div className="p-3 rounded-lg border border-border bg-surface-subtle space-y-1">
                <span className="text-[10px] font-bold text-charcoal-400 uppercase">Inode Times</span>
                <div className="text-[11px] font-mono text-charcoal-700 space-y-0.5">
                  <div>mtime: {formatTimestamp(currentAnalysis.observed_physical_facts?.mtime, currentAnalysis.observed_physical_facts?.mtime_str)}</div>
                  <div>ctime: {formatTimestamp(currentAnalysis.observed_physical_facts?.ctime, currentAnalysis.observed_physical_facts?.ctime_str)}</div>
                  <div>atime: {formatTimestamp(currentAnalysis.observed_physical_facts?.atime, currentAnalysis.observed_physical_facts?.atime_str)}</div>
                </div>
              </div>

              <div className="p-3 rounded-lg border border-border bg-surface-subtle space-y-1">
                <span className="text-[10px] font-bold text-charcoal-400 uppercase">Subsecond Precision</span>
                <div className="text-[11px] font-mono text-charcoal-700 space-y-0.5">
                  <div>subsecond: {typeof currentAnalysis.observed_physical_facts?.mtime_subsecond === 'number' ? `${currentAnalysis.observed_physical_facts.mtime_subsecond.toFixed(6)}s` : 'N/A'}</div>
                  <div className={currentAnalysis.observed_physical_facts?.mtime_subsecond_is_zero ? 'text-amber-700 font-bold' : 'text-olive-700'}>
                    zeroed: {currentAnalysis.observed_physical_facts?.mtime_subsecond_is_zero ? 'TRUE (Anomalous)' : 'FALSE'}
                  </div>
                </div>
              </div>

              <div className="p-3 rounded-lg border border-border bg-surface-subtle space-y-1">
                <span className="text-[10px] font-bold text-charcoal-400 uppercase">Timestamp Deltas</span>
                <div className="text-[11px] font-mono text-charcoal-700 space-y-0.5">
                  <div>mtime - ctime: {typeof currentAnalysis.observed_physical_facts?.delta_mtime_ctime === 'number' ? `${currentAnalysis.observed_physical_facts.delta_mtime_ctime.toFixed(2)}s` : 'N/A'}</div>
                  <div>atime - mtime: {typeof currentAnalysis.observed_physical_facts?.delta_atime_mtime === 'number' ? `${currentAnalysis.observed_physical_facts.delta_atime_mtime.toFixed(2)}s` : 'N/A'}</div>
                  <div>ctime - atime: {typeof currentAnalysis.observed_physical_facts?.delta_ctime_atime === 'number' ? `${currentAnalysis.observed_physical_facts.delta_ctime_atime.toFixed(2)}s` : 'N/A'}</div>
                </div>
              </div>

              <div className="p-3 rounded-lg border border-border bg-surface-subtle space-y-1">
                <span className="text-[10px] font-bold text-charcoal-400 uppercase">MIME vs Extension</span>
                <div className="text-[11px] font-mono text-charcoal-700 space-y-0.5">
                  <div>ext: {currentAnalysis.observed_physical_facts?.declared_extension || currentAnalysis.evidence_provenance?.declared_extension || 'N/A'}</div>
                  <div>mime: {currentAnalysis.observed_physical_facts?.detected_mime_type || 'N/A'}</div>
                  <div className={currentAnalysis.observed_physical_facts?.is_signature_mismatch ? 'text-red-700 font-bold' : 'text-olive-700'}>
                    mismatch: {currentAnalysis.observed_physical_facts?.is_signature_mismatch ? 'TRUE' : 'FALSE'}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Summary Findings */}
          <div className="rounded-xl border border-border bg-surface p-6 shadow-xs space-y-3">
            <div className="flex items-center space-x-2 text-charcoal-900 font-bold text-sm">
              <Sparkles className="h-4 w-4 text-olive-600" />
              <span>Summary Findings</span>
            </div>
            <div className="space-y-2 text-xs text-charcoal-700">
              {(currentAnalysis.investigator_narrative || []).map((point, idx) => (
                <div key={idx} className="flex items-start space-x-2">
                  <span className="text-olive-700 font-bold mt-0.5">&bull;</span>
                  <p className="leading-relaxed">{point}</p>
                </div>
              ))}
            </div>

            {currentAnalysis.warnings && currentAnalysis.warnings.length > 0 && (
              <div className="mt-4 pt-3 border-t border-border space-y-1.5">
                <span className="text-[11px] font-bold text-amber-800 uppercase tracking-wide">
                  Observations & Notes:
                </span>
                {currentAnalysis.warnings.map((warn, idx) => (
                  <p key={idx} className="text-[11px] text-charcoal-500 italic">
                    &bull; {warn}
                  </p>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
