import React from 'react';
import {
  SearchCode,
  Workflow,
  History,
  BarChart3,
  ShieldCheck,
} from 'lucide-react';

export type TabId = 'analyze' | 'overview' | 'history' | 'evaluation';

interface SidebarProps {
  activeTab: TabId;
  setActiveTab: (tab: TabId) => void;
  analysesCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  setActiveTab,
  analysesCount,
}) => {
  const navItems = [
    {
      id: 'analyze' as TabId,
      label: 'Analyze File',
      subtitle: 'Scan for anti-forensic tampering',
      icon: SearchCode,
    },
    {
      id: 'overview' as TabId,
      label: 'How It Works',
      subtitle: 'Multi-modal detection flow',
      icon: Workflow,
    },
    {
      id: 'history' as TabId,
      label: 'Audit Log',
      subtitle: 'Session scan history',
      icon: History,
      badge: analysesCount > 0 ? analysesCount : undefined,
    },
    {
      id: 'evaluation' as TabId,
      label: 'Benchmarks',
      subtitle: 'Accuracy & ROC curves',
      icon: BarChart3,
    },
  ];

  return (
    <aside className="w-64 shrink-0 border-r border-border bg-surface flex flex-col justify-between h-[calc(100vh-61px)] sticky top-[61px]">
      <div className="p-3.5 space-y-4">
        <div>
          <span className="px-3 text-[10px] font-bold uppercase tracking-wider text-charcoal-400">
            Workspace
          </span>
          <nav className="mt-2 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-start space-x-3 px-3 py-2.5 rounded-lg text-left transition-all cursor-pointer ${
                    isActive
                      ? 'bg-olive-50 text-olive-900 border border-olive-200/80 shadow-xs'
                      : 'text-charcoal-600 hover:bg-surface-subtle hover:text-charcoal-900 border border-transparent'
                  }`}
                >
                  <Icon
                    className={`h-4 w-4 mt-0.5 shrink-0 transition-colors ${
                      isActive ? 'text-olive-700' : 'text-charcoal-400'
                    }`}
                  />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className={`text-xs font-semibold truncate ${isActive ? 'text-olive-900' : 'text-charcoal-800'}`}>
                        {item.label}
                      </span>
                      {item.badge !== undefined && (
                        <span className="ml-2 inline-flex items-center px-1.5 py-0.2 rounded-full text-[10px] font-semibold bg-olive-100 text-olive-800">
                          {item.badge}
                        </span>
                      )}
                    </div>
                    <p className="text-[10px] text-charcoal-400 truncate mt-0.5">
                      {item.subtitle}
                    </p>
                  </div>
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Footer Info */}
      <div className="p-3.5 border-t border-border bg-surface-subtle/50 text-[11px] text-charcoal-500 space-y-1">
        <div className="flex items-center space-x-1.5 text-charcoal-600 font-medium">
          <ShieldCheck className="h-3.5 w-3.5 text-olive-600" />
          <span>Non-Destructive Triage</span>
        </div>
        <p className="text-[10px] text-charcoal-400 leading-tight">
          Analyzes file copies without altering timestamps or inode records.
        </p>
      </div>
    </aside>
  );
};
