"use client";

import { useState, useMemo } from "react";
import { cn, severityColor, formatRelativeTime } from "@/lib/utils";
import {
  AlertTriangle,
  Search,
  Plus,
  Bot,
  Clock,
  User,
  ChevronRight,
} from "lucide-react";
import { Autopilot } from "@/components/agents/autopilot";

function generateIncidents() {
  const now = Date.now();
  return [
    { id: "INC-001", title: "Payment Service — 502 Bad Gateway errors spike across all regions", severity: "critical", status: "investigating", source: "automated", created_at: new Date(now - 300000).toISOString(), ai_summary: "Upstream payment provider API is timing out. Connection pool on api-gateway is saturating. Recommend: failover to secondary provider or enable circuit breaker.", ai_confidence: 0.92, services: ["payment-api", "checkout-service"], assigned_to: "Alex Chen" },
    { id: "INC-002", title: "Database connection pool exhausted — postgres-primary", severity: "high", status: "open", source: "alert", created_at: new Date(now - 900000).toISOString(), ai_summary: "Connection count reached max (100). Long-running queries from report-worker holding connections. Recommend: kill stale queries and increase pool size.", ai_confidence: 0.87, services: ["postgres-primary", "report-worker"], assigned_to: null },
    { id: "INC-003", title: "Auth service latency degradation — p99 > 2s", severity: "medium", status: "investigating", source: "ai-detected", created_at: new Date(now - 1800000).toISOString(), ai_summary: "Redis cache miss rate spiked to 40% after deployment v2.14.3. Session tokens not being cached properly. Root cause: Redis key prefix changed.", ai_confidence: 0.95, services: ["auth-service", "redis-cache"], assigned_to: "Sarah Kim" },
    { id: "INC-004", title: "Kubernetes pod CrashLoopBackOff — order-worker deployment", severity: "high", status: "open", source: "automated", created_at: new Date(now - 3600000).toISOString(), ai_summary: "OOMKilled — container memory limit 512Mi exceeded. Memory leak in v3.2.1 of order-processing library. Recommend: rollback to v3.2.0 or increase limits.", ai_confidence: 0.89, services: ["order-worker"], assigned_to: null },
    { id: "INC-005", title: "Elevated 5xx error rate on API Gateway", severity: "medium", status: "resolved", source: "alert", created_at: new Date(now - 7200000).toISOString(), ai_summary: "Traced to a misconfigured rate limiter deployed in v1.8.4. Fixed by config rollback. No data loss detected.", ai_confidence: 0.98, services: ["api-gateway"], assigned_to: "Mike Johnson" },
  ];
}

export default function IncidentsPage() {
  const [filter, setFilter] = useState("all");
  const [search, setSearch] = useState("");
   
  const incidents = useMemo(() => generateIncidents(), []);

  const filtered = incidents.filter((inc) => {
    if (filter !== "all" && inc.status !== filter) return false;
    if (search && !inc.title.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Incidents</h1>
          <p className="text-sm text-muted-foreground mt-1">AI-powered incident tracking and investigation</p>
        </div>
        <button className="flex items-center gap-2 rounded-lg bg-gradient-to-r from-pulse-primary to-purple-600 px-4 py-2 text-sm font-semibold text-white hover:shadow-lg hover:shadow-pulse-primary/25 transition-all">
          <Plus className="h-4 w-4" />
          New Incident
        </button>
      </div>

      {/* Filters */}
      <div className="glass rounded-xl p-4 flex flex-wrap gap-3">
        <div className="flex items-center gap-2 rounded-lg border border-border bg-background/50 px-3 py-2 flex-1 min-w-64">
          <Search className="h-4 w-4 text-muted-foreground" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search incidents..."
            className="flex-1 bg-transparent text-sm text-foreground placeholder:text-muted-foreground outline-none"
          />
        </div>
        <div className="flex items-center gap-1 rounded-lg border border-border p-1">
          {["all", "open", "investigating", "resolved"].map((s) => (
            <button
              key={s}
              onClick={() => setFilter(s)}
              className={cn(
                "rounded-md px-3 py-1 text-xs font-medium transition-colors capitalize",
                filter === s
                  ? "bg-pulse-primary/15 text-pulse-primary"
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Incident Cards */}
      <div className="space-y-3">
        {filtered.map((inc) => (
          <div
            key={inc.id}
            className="glass rounded-xl p-5 transition-all hover:border-muted-foreground/30 cursor-pointer group animate-slide-up"
          >
            <div className="flex items-start gap-4">
              <div className={cn(
                "mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg",
                inc.severity === "critical" ? "bg-red-500/15" :
                inc.severity === "high" ? "bg-orange-500/15" :
                "bg-yellow-500/15"
              )}>
                <AlertTriangle className={cn(
                  "h-4 w-4",
                  inc.severity === "critical" ? "text-red-400" :
                  inc.severity === "high" ? "text-orange-400" :
                  "text-yellow-400"
                )} />
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-mono text-muted-foreground">{inc.id}</span>
                      <span className={cn("rounded-full border px-2 py-0.5 text-[10px] font-semibold uppercase", severityColor(inc.severity))}>
                        {inc.severity}
                      </span>
                      <span className={cn(
                        "rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase",
                        inc.status === "resolved" ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" :
                        inc.status === "investigating" ? "bg-blue-500/10 text-blue-400 border border-blue-500/20" :
                        "bg-zinc-500/10 text-zinc-400 border border-zinc-500/20"
                      )}>
                        {inc.status}
                      </span>
                    </div>
                    <h3 className="text-sm font-semibold text-foreground group-hover:text-white transition-colors">{inc.title}</h3>
                  </div>
                  <ChevronRight className="h-4 w-4 text-muted-foreground group-hover:text-foreground transition-colors shrink-0 mt-1" />
                </div>

                {/* AI Summary */}
                {inc.ai_summary && (
                  <div className="mt-3 rounded-lg border border-pulse-primary/20 bg-pulse-primary/5 p-3">
                    <div className="flex items-center gap-1.5 mb-1">
                      <Bot className="h-3.5 w-3.5 text-pulse-primary" />
                      <span className="text-xs font-semibold text-pulse-primary">AI Analysis</span>
                      <span className="ml-auto text-[10px] text-muted-foreground">
                        Confidence: {Math.round(inc.ai_confidence! * 100)}%
                      </span>
                    </div>
                    <p className="text-xs text-muted-foreground leading-relaxed">{inc.ai_summary}</p>
                  </div>
                )}

                {/* Meta */}
                <div className="mt-3 flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
                  <span className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {formatRelativeTime(inc.created_at)}
                  </span>
                  {inc.assigned_to && (
                    <span className="flex items-center gap-1">
                      <User className="h-3 w-3" />
                      {inc.assigned_to}
                    </span>
                  )}
                  <span className="flex items-center gap-1">
                    {inc.services.map((s) => (
                      <span key={s} className="rounded bg-muted px-1.5 py-0.5 font-mono text-[10px]">{s}</span>
                    ))}
                  </span>
                  {inc.source === "ai-detected" && (
                    <span className="flex items-center gap-1 text-pulse-secondary">
                      <Bot className="h-3 w-3" />
                      AI Detected
                    </span>
                  )}
                </div>
                
                {/* Autopilot Investigation */}
                <Autopilot incidentId={inc.id} query={inc.title} />

              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
