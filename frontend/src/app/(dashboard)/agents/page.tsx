import { Bot, Workflow, Zap } from "lucide-react";

export default function AgentsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">AI Agents</h1>
        <p className="text-sm text-muted-foreground mt-1">Manage autonomous LangGraph agents monitoring your infrastructure</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Incident Investigator Agent */}
        <div className="glass rounded-xl p-5 border border-pulse-primary/30 relative overflow-hidden">
          <div className="absolute top-0 right-0 p-4">
            <div className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span className="text-xs font-medium text-emerald-400">Active</span>
            </div>
          </div>
          <Bot className="h-8 w-8 text-pulse-primary mb-4" />
          <h3 className="text-lg font-semibold text-foreground">Incident Investigator</h3>
          <p className="text-sm text-muted-foreground mt-2 mb-4">
            Automatically triggers on CRITICAL alerts. Gathers logs, clusters anomalies, and generates root cause reports using LangGraph.
          </p>
          <div className="flex gap-2">
            <span className="text-xs bg-muted px-2 py-1 rounded">LangGraph</span>
            <span className="text-xs bg-muted px-2 py-1 rounded">Log Analysis</span>
          </div>
        </div>

        {/* Anomaly Detector Agent */}
        <div className="glass rounded-xl p-5 border border-border relative overflow-hidden opacity-80">
          <div className="absolute top-0 right-0 p-4">
            <div className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-emerald-400"></span>
              <span className="text-xs font-medium text-emerald-400">Active</span>
            </div>
          </div>
          <Zap className="h-8 w-8 text-yellow-500 mb-4" />
          <h3 className="text-lg font-semibold text-foreground">Anomaly Watcher</h3>
          <p className="text-sm text-muted-foreground mt-2 mb-4">
            Continuously monitors real-time log streams to detect statistical deviations and unusual error spikes before alerts fire.
          </p>
          <div className="flex gap-2">
            <span className="text-xs bg-muted px-2 py-1 rounded">TF-IDF</span>
            <span className="text-xs bg-muted px-2 py-1 rounded">Streaming</span>
          </div>
        </div>

        {/* Auto-Remediation Agent */}
        <div className="glass rounded-xl p-5 border border-border relative overflow-hidden opacity-60">
          <div className="absolute top-0 right-0 p-4">
            <div className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-zinc-500"></span>
              <span className="text-xs font-medium text-zinc-400">Paused</span>
            </div>
          </div>
          <Workflow className="h-8 w-8 text-blue-400 mb-4" />
          <h3 className="text-lg font-semibold text-foreground">Auto-Remediator</h3>
          <p className="text-sm text-muted-foreground mt-2 mb-4">
            Executes predefined runbooks (e.g., clearing Redis cache, scaling pods) based on high-confidence AI root cause analysis.
          </p>
          <div className="flex gap-2">
            <span className="text-xs bg-muted px-2 py-1 rounded">Runbooks</span>
            <span className="text-xs bg-muted px-2 py-1 rounded">Actionable</span>
          </div>
        </div>
      </div>
    </div>
  );
}
