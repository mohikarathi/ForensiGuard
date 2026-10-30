import React from 'react';
import { Shield, CheckCircle2, AlertTriangle, Cpu } from 'lucide-react';
import { HealthResponse } from '../types/api';

interface NavbarProps {
  health: HealthResponse | null;
  activeTab: string;
}

export const Navbar: React.FC<NavbarProps> = ({ health }) => {
  return (
    <header className="sticky top-0 z-30 border-b border-border bg-surface/95 backdrop-blur-sm px-6 py-3 transition-all">
      <div className="flex items-center justify-between">
        {/* Left: Branding & Tagline */}
        <div className="flex items-center space-x-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-olive-700 text-white shadow-sm ring-1 ring-olive-800/20">
            <Shield className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-mono text-base font-bold tracking-tight text-charcoal-900">ForensiGuard</span>
              <span className="rounded-full bg-olive-50 px-2 py-0.5 text-[10px] font-semibold text-olive-700 border border-olive-200/60 uppercase tracking-wide">
                Evidence Inspector
              </span>
            </div>
            <p className="text-[11px] text-charcoal-500 font-medium">
              Multi-Modal Digital Evidence Anti-Forensic Triage
            </p>
          </div>
        </div>

        {/* Right: Operational Status & System Info */}
        <div className="flex items-center space-x-3 text-xs">
          <div className="flex items-center space-x-1.5 px-3 py-1 rounded-md border border-border bg-surface-subtle">
            <span className="text-charcoal-500">Threshold:</span>
            <span className="font-mono font-semibold text-charcoal-800">&tau; = 0.500</span>
          </div>

          <div
            className={`flex items-center space-x-1.5 px-3 py-1 rounded-md border font-medium ${
              health?.models_loaded
                ? 'bg-olive-50 text-olive-800 border-olive-200'
                : 'bg-amber-50 text-amber-800 border-amber-200'
            }`}
          >
            {health?.models_loaded ? (
              <>
                <CheckCircle2 className="h-3.5 w-3.5 text-olive-600" />
                <span>Pipeline Ready</span>
              </>
            ) : (
              <>
                <AlertTriangle className="h-3.5 w-3.5 text-amber-600" />
                <span>Loading Pipeline</span>
              </>
            )}
            {health?.device && (
              <span className="inline-flex items-center space-x-1 font-mono text-[10px] text-charcoal-500 ml-1 pl-1 border-l border-olive-200">
                <Cpu className="h-3 w-3 inline text-charcoal-400" />
                <span>{health.device.toUpperCase()}</span>
              </span>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
