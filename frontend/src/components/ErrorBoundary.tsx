import { Component, ErrorInfo, ReactNode } from 'react';
import { AlertOctagon, RotateCcw } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallbackTitle?: string;
  onReset?: () => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an unhandled rendering error:', error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div className="rounded-xl border border-red-200 bg-red-50/70 p-6 my-4 max-w-4xl mx-auto shadow-xs text-charcoal-800 space-y-4">
          <div className="flex items-start space-x-3">
            <AlertOctagon className="h-6 w-6 text-red-600 shrink-0 mt-0.5" />
            <div className="space-y-1 flex-1">
              <h3 className="text-base font-bold text-red-900">
                {this.props.fallbackTitle || 'A display error occurred while rendering this component'}
              </h3>
              <p className="text-xs text-red-700 leading-relaxed">
                The forensic analysis data was processed, but a visual formatting exception prevented rendering.
              </p>
              {this.state.error && (
                <div className="mt-2 p-2.5 rounded bg-white/80 border border-red-200 font-mono text-[11px] text-red-800 break-all">
                  {this.state.error.toString()}
                </div>
              )}
            </div>
          </div>
          <div className="flex justify-end pt-2">
            <button
              onClick={this.handleReset}
              className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-lg bg-red-700 hover:bg-red-800 text-white font-medium text-xs shadow-xs cursor-pointer transition-colors"
            >
              <RotateCcw className="h-3.5 w-3.5" />
              <span>Reset & Reload View</span>
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
