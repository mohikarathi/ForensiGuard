import React from 'react';
import {
  ShieldAlert,
  ArrowRight,
  Clock,
  EyeOff,
  FileType,
  Layers,
} from 'lucide-react';
import { OverviewResponse } from '../types/api';

interface OverviewViewProps {
  overview: OverviewResponse | null;
  onNavigateToAnalyze: () => void;
}

export const OverviewView: React.FC<OverviewViewProps> = ({
  overview,
  onNavigateToAnalyze,
}) => {
  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-12">
      {/* Hero Section */}
      <div className="rounded-xl border border-border bg-gradient-to-br from-surface via-surface to-surface-subtle p-6 sm:p-8 shadow-xs">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <h1 className="text-2xl font-bold tracking-tight text-charcoal-900 leading-snug">
              Multi-Modal Evidence Inspection Pipeline
            </h1>
            <p className="text-xs sm:text-sm text-charcoal-600 leading-relaxed">
              ForensiGuard inspects digital files across multiple independent signals—filesystem timestamp chronology, high-frequency pixel noise residuals, and binary magic bytes—to detect anti-forensic tampering and explain the decision factors.
            </p>
          </div>
          <div className="shrink-0">
            <button
              onClick={onNavigateToAnalyze}
              className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-lg bg-olive-700 hover:bg-olive-800 text-white font-medium text-xs sm:text-sm shadow-sm transition-colors cursor-pointer"
            >
              <span>Analyze a File</span>
              <ArrowRight className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Highlight Stats Row */}
        <div className="mt-6 grid grid-cols-2 sm:grid-cols-4 gap-3 pt-5 border-t border-border">
          <div className="p-3 rounded-lg bg-surface-subtle/80 border border-border">
            <div className="text-[11px] font-medium text-charcoal-500">Benchmark Scale</div>
            <div className="text-lg font-bold font-mono text-charcoal-900 mt-0.5">
              {overview?.total_artifacts ?? 812} <span className="text-[11px] font-normal text-charcoal-500">Files</span>
            </div>
            <div className="text-[10px] text-charcoal-400">140 unique sources</div>
          </div>
          <div className="p-3 rounded-lg bg-surface-subtle/80 border border-border">
            <div className="text-[11px] font-medium text-charcoal-500">Overall Accuracy</div>
            <div className="text-lg font-bold font-mono text-olive-700 mt-0.5">
              78.6%
            </div>
            <div className="text-[10px] text-charcoal-400">88.1% test recall</div>
          </div>
          <div className="p-3 rounded-lg bg-surface-subtle/80 border border-border">
            <div className="text-[11px] font-medium text-charcoal-500">Discriminative Power</div>
            <div className="text-lg font-bold font-mono text-charcoal-900 mt-0.5">
              0.895
            </div>
            <div className="text-[10px] text-charcoal-400">ROC-AUC score</div>
          </div>
          <div className="p-3 rounded-lg bg-surface-subtle/80 border border-border">
            <div className="text-[11px] font-medium text-charcoal-500">False Alarm Rate</div>
            <div className="text-lg font-bold font-mono text-charcoal-900 mt-0.5">
              4.8%
            </div>
            <div className="text-[10px] text-charcoal-400">Clean false positives</div>
          </div>
        </div>
      </div>

      {/* Interactive Pipeline Architecture Diagram */}
      <div className="space-y-3">
        <div>
          <h2 className="text-base font-bold text-charcoal-900">How Evidence is Processed</h2>
          <p className="text-xs text-charcoal-500">
            5-stage non-destructive pipeline from physical file ingest to explainable report.
          </p>
        </div>

        <div className="rounded-xl border border-border bg-surface p-5 shadow-xs">
          <div className="grid grid-cols-1 sm:grid-cols-5 gap-3">
            {/* Step 1: Ingestion */}
            <div className="p-3.5 rounded-lg bg-surface-subtle border border-border space-y-1.5">
              <div className="flex items-center space-x-2 text-charcoal-800 font-semibold text-xs">
                <span className="w-4 h-4 rounded-full bg-charcoal-800 text-white flex items-center justify-center text-[10px]">1</span>
                <span>File Ingest</span>
              </div>
              <p className="text-[11px] text-charcoal-500 leading-snug">
                Read-only buffer access. Computes SHA-256/MD5 and extracts binary magic bytes.
              </p>
            </div>

            {/* Step 2: Feature Extraction */}
            <div className="p-3.5 rounded-lg bg-surface-subtle border border-border space-y-1.5">
              <div className="flex items-center space-x-2 text-charcoal-800 font-semibold text-xs">
                <span className="w-4 h-4 rounded-full bg-charcoal-800 text-white flex items-center justify-center text-[10px]">2</span>
                <span>Extraction</span>
              </div>
              <p className="text-[11px] text-charcoal-500 leading-snug">
                Parses MACB inode times, subsecond precision, deltas, and image pixel residuals.
              </p>
            </div>

            {/* Step 3: Base Classifiers */}
            <div className="p-3.5 rounded-lg bg-olive-50/70 border border-olive-200/80 space-y-1.5">
              <div className="flex items-center space-x-2 text-olive-900 font-semibold text-xs">
                <span className="w-4 h-4 rounded-full bg-olive-700 text-white flex items-center justify-center text-[10px]">3</span>
                <span>Scoring</span>
              </div>
              <p className="text-[11px] text-olive-800 leading-snug">
                Evaluates metadata classifier, spatial residual CNN, isolation forest, and file signature.
              </p>
            </div>

            {/* Step 4: Late Fusion */}
            <div className="p-3.5 rounded-lg bg-surface-subtle border border-border space-y-1.5">
              <div className="flex items-center space-x-2 text-charcoal-800 font-semibold text-xs">
                <span className="w-4 h-4 rounded-full bg-charcoal-800 text-white flex items-center justify-center text-[10px]">4</span>
                <span>Late Fusion</span>
              </div>
              <p className="text-[11px] text-charcoal-500 leading-snug">
                Calibrated meta-model weights all modality signals at operating threshold &tau; = 0.500.
              </p>
            </div>

            {/* Step 5: Explainability */}
            <div className="p-3.5 rounded-lg bg-surface-subtle border border-border space-y-1.5">
              <div className="flex items-center space-x-2 text-charcoal-800 font-semibold text-xs">
                <span className="w-4 h-4 rounded-full bg-charcoal-800 text-white flex items-center justify-center text-[10px]">5</span>
                <span>TreeSHAP</span>
              </div>
              <p className="text-[11px] text-charcoal-500 leading-snug">
                Computes feature contributions explaining exactly why the file was flagged or cleared.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Anti-Forensic Manipulation Types */}
      <div className="rounded-xl border border-border bg-surface p-5 space-y-3">
        <div className="flex items-center space-x-2 text-charcoal-800 font-bold text-sm">
          <ShieldAlert className="h-4 w-4 text-olive-600" />
          <span>Supported Tampering Types</span>
        </div>
        <p className="text-xs text-charcoal-500">
          ForensiGuard identifies four common anti-forensic techniques:
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5 pt-1 text-xs">
          <div className="p-3 rounded-lg border border-border bg-surface-subtle space-y-1">
            <div className="flex items-center space-x-1.5 font-semibold text-charcoal-800">
              <Clock className="h-3.5 w-3.5 text-ochre-600" />
              <span>Timestomping</span>
            </div>
            <p className="text-[11px] text-charcoal-500 leading-tight">
              Altering modification, access, or creation timestamps to fake event order.
            </p>
          </div>

          <div className="p-3 rounded-lg border border-border bg-surface-subtle space-y-1">
            <div className="flex items-center space-x-1.5 font-semibold text-charcoal-800">
              <EyeOff className="h-3.5 w-3.5 text-olive-600" />
              <span>Steganography</span>
            </div>
            <p className="text-[11px] text-charcoal-500 leading-tight">
              Hiding covert data inside pixel noise residuals of image files.
            </p>
          </div>

          <div className="p-3 rounded-lg border border-border bg-surface-subtle space-y-1">
            <div className="flex items-center space-x-1.5 font-semibold text-charcoal-800">
              <FileType className="h-3.5 w-3.5 text-blue-600" />
              <span>File-Type Obfuscation</span>
            </div>
            <p className="text-[11px] text-charcoal-500 leading-tight">
              Mislabeled file extensions hiding the true file format (e.g. PDF renamed to .png).
            </p>
          </div>

          <div className="p-3 rounded-lg border border-border bg-surface-subtle space-y-1">
            <div className="flex items-center space-x-1.5 font-semibold text-charcoal-800">
              <Layers className="h-3.5 w-3.5 text-purple-600" />
              <span>Compound Attacks</span>
            </div>
            <p className="text-[11px] text-charcoal-500 leading-tight">
              Combined alterations (e.g. timestomped carrier containing steganographic payload).
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
