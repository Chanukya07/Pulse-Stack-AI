import { useState } from "react";
import { Bot, Loader2, Sparkles, CheckCircle2, AlertCircle } from "lucide-react";
import { agentsApi, InvestigationResult } from "@/lib/api";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface AutopilotProps {
  incidentId: string;
  query: string;
  onComplete?: (result: InvestigationResult) => void;
}

export function Autopilot({ incidentId, query, onComplete }: AutopilotProps) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<InvestigationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const runInvestigation = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // Pass a dummy token for local dev
      const res = await agentsApi.investigate("dummy-token", query, incidentId);
      setResult(res);
      if (onComplete) {
        onComplete(res);
      }
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to run investigation");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mt-4 rounded-xl border border-pulse-primary/20 bg-pulse-primary/5 p-4 overflow-hidden relative">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Bot className="h-5 w-5 text-pulse-primary" />
          <h4 className="font-semibold text-foreground">LangGraph Autopilot</h4>
        </div>
        {!loading && !result && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              runInvestigation();
            }}
            className="flex items-center gap-2 rounded-lg bg-pulse-primary px-3 py-1.5 text-xs font-semibold text-white shadow-lg shadow-pulse-primary/25 hover:bg-pulse-primary/90 transition-all"
          >
            <Sparkles className="h-3.5 w-3.5" />
            Investigate Root Cause
          </button>
        )}
      </div>

      {loading && (
        <div className="space-y-4 py-4">
          <div className="flex items-center gap-3 text-sm text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin text-pulse-primary" />
            <span className="animate-pulse">Gathering logs, clustering, and analyzing...</span>
          </div>
          
          {/* Skeleton loading animation */}
          <div className="space-y-2">
            <div className="h-2 rounded bg-pulse-primary/20 w-3/4 animate-pulse"></div>
            <div className="h-2 rounded bg-pulse-primary/20 w-full animate-pulse"></div>
            <div className="h-2 rounded bg-pulse-primary/20 w-5/6 animate-pulse"></div>
          </div>
        </div>
      )}

      {error && (
        <div className="flex items-start gap-2 text-sm text-red-400 bg-red-500/10 p-3 rounded-lg border border-red-500/20">
          <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
          <p>{error}</p>
        </div>
      )}

      {result && (
        <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-500">
          <div className="flex items-center justify-between border-b border-border/50 pb-2">
            <div className="flex items-center gap-2 text-sm">
              <CheckCircle2 className="h-4 w-4 text-emerald-400" />
              <span className="text-emerald-400 font-medium">Investigation Complete</span>
            </div>
            <span className="text-xs text-muted-foreground">
              Confidence: {Math.round(result.confidence * 100)}% | Took {result.duration_ms}ms
            </span>
          </div>
          
          <div className="space-y-3">
            <div>
              <div className="prose prose-sm prose-invert max-w-none text-muted-foreground prose-headings:text-foreground prose-a:text-pulse-primary hover:prose-a:text-pulse-primary/80">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {result.root_cause || result.analysis}
                </ReactMarkdown>
              </div>
            </div>
            
            <div className="pt-2 border-t border-border/50">
              <h5 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">Steps Taken by AI</h5>
              <ul className="list-disc list-inside text-xs text-muted-foreground space-y-1">
                {result.steps_taken.map((step, idx) => (
                  <li key={idx}>{step}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
      
      {/* Decorative background glow */}
      <div className="absolute -top-10 -right-10 w-32 h-32 bg-pulse-primary/10 rounded-full blur-2xl pointer-events-none"></div>
    </div>
  );
}
