"use client";

import { cn, severityColor, formatRelativeTime } from "@/lib/utils";
import {
  Bell,
  BellOff,
  Plus,
  CheckCircle2,
  Clock,
} from "lucide-react";
import { useState } from "react";

const alerts = [
  { id: "1", rule: "CPU > 90%", severity: "critical", status: "firing", service: "api-gateway", message: "CPU usage at 94.2% for last 5 minutes", fired_at: new Date(Date.now() - 120000).toISOString() },
  { id: "2", rule: "Error rate > 5%", severity: "high", status: "firing", service: "payment-api", message: "Error rate at 8.3% (threshold: 5%)", fired_at: new Date(Date.now() - 600000).toISOString() },
  { id: "3", rule: "Memory > 85%", severity: "medium", status: "firing", service: "redis-cache", message: "Memory utilization at 87%", fired_at: new Date(Date.now() - 1200000).toISOString() },
  { id: "4", rule: "Disk > 90%", severity: "high", status: "firing", service: "elasticsearch", message: "Disk usage at 92.1% on data node", fired_at: new Date(Date.now() - 2400000).toISOString() },
  { id: "5", rule: "Pod restart count > 3", severity: "medium", status: "resolved", service: "order-worker", message: "Pod restarted 5 times in last hour", fired_at: new Date(Date.now() - 3600000).toISOString() },
  { id: "6", rule: "Response time > 1s", severity: "medium", status: "resolved", service: "user-service", message: "p95 latency at 1.2s", fired_at: new Date(Date.now() - 5400000).toISOString() },
];

export default function AlertsPage() {
  const [filter, setFilter] = useState("all");

  const filtered = alerts.filter((a) => {
    if (filter === "firing") return a.status === "firing";
    if (filter === "resolved") return a.status === "resolved";
    return true;
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Alerts</h1>
          <p className="text-sm text-muted-foreground mt-1">Active alerts and alert rule management</p>
        </div>
        <button className="flex items-center gap-2 rounded-lg bg-gradient-to-r from-pulse-primary to-purple-600 px-4 py-2 text-sm font-semibold text-white hover:shadow-lg hover:shadow-pulse-primary/25 transition-all">
          <Plus className="h-4 w-4" />
          New Rule
        </button>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-3 gap-4">
        <div className="glass rounded-xl p-4 flex items-center gap-3">
          <div className="rounded-lg bg-red-500/10 p-2.5"><Bell className="h-5 w-5 text-red-400" /></div>
          <div>
            <p className="text-2xl font-bold text-foreground">{alerts.filter(a => a.status === "firing").length}</p>
            <p className="text-xs text-muted-foreground">Firing</p>
          </div>
        </div>
        <div className="glass rounded-xl p-4 flex items-center gap-3">
          <div className="rounded-lg bg-emerald-500/10 p-2.5"><CheckCircle2 className="h-5 w-5 text-emerald-400" /></div>
          <div>
            <p className="text-2xl font-bold text-foreground">{alerts.filter(a => a.status === "resolved").length}</p>
            <p className="text-xs text-muted-foreground">Resolved</p>
          </div>
        </div>
        <div className="glass rounded-xl p-4 flex items-center gap-3">
          <div className="rounded-lg bg-orange-500/10 p-2.5"><Clock className="h-5 w-5 text-orange-400" /></div>
          <div>
            <p className="text-2xl font-bold text-foreground">{alerts.filter(a => a.severity === "critical").length}</p>
            <p className="text-xs text-muted-foreground">Critical</p>
          </div>
        </div>
      </div>

      {/* Filter tabs */}
      <div className="flex items-center gap-1 rounded-lg border border-border p-1 w-fit">
        {["all", "firing", "resolved"].map((s) => (
          <button
            key={s}
            onClick={() => setFilter(s)}
            className={cn(
              "rounded-md px-3 py-1.5 text-xs font-medium transition-colors capitalize",
              filter === s ? "bg-pulse-primary/15 text-pulse-primary" : "text-muted-foreground hover:text-foreground"
            )}
          >
            {s}
          </button>
        ))}
      </div>

      {/* Alert list */}
      <div className="space-y-2">
        {filtered.map((alert) => (
          <div key={alert.id} className="glass rounded-xl p-4 flex items-center gap-4 hover:border-muted-foreground/30 transition-colors animate-slide-up">
            <div className={cn(
              "h-2.5 w-2.5 rounded-full shrink-0",
              alert.status === "firing" ? "bg-red-400 animate-pulse" : "bg-emerald-400"
            )} />
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-semibold text-foreground">{alert.rule}</h3>
                <span className={cn("rounded-full border px-2 py-0.5 text-[10px] font-semibold uppercase", severityColor(alert.severity))}>
                  {alert.severity}
                </span>
              </div>
              <p className="text-xs text-muted-foreground mt-0.5">{alert.message}</p>
            </div>
            <div className="text-right shrink-0">
              <p className="text-xs font-mono text-foreground">{alert.service}</p>
              <p className="text-xs text-muted-foreground mt-0.5">{formatRelativeTime(alert.fired_at)}</p>
            </div>
            <button className="rounded-lg p-2 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors">
              {alert.status === "firing" ? <BellOff className="h-4 w-4" /> : <Bell className="h-4 w-4" />}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
