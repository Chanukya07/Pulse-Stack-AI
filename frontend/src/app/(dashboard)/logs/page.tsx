"use client";

import { useState, useMemo } from "react";
import {
  Search,
  Filter,
  Download,
  RefreshCw,
  AlertCircle,
  Info,
  AlertTriangle,
  XCircle,
  Bug,
} from "lucide-react";
import { cn } from "@/lib/utils";

const levels = ["all", "info", "warn", "error", "debug", "fatal"] as const;

const levelIcon: Record<string, React.ElementType> = {
  info: Info,
  warn: AlertTriangle,
  error: XCircle,
  fatal: AlertCircle,
  debug: Bug,
};

const levelColor: Record<string, string> = {
  info: "text-blue-400",
  warn: "text-yellow-400",
  error: "text-red-400",
  fatal: "text-red-500",
  debug: "text-zinc-400",
};

const logMessages = [
  { msg: "Request processed successfully — 200 OK", lvl: "info" },
  { msg: "Connection pool nearing capacity — 85% utilized", lvl: "warn" },
  { msg: "Failed to authenticate user: invalid token", lvl: "error" },
  { msg: "Database query timeout after 30000ms", lvl: "error" },
  { msg: "Health check passed", lvl: "info" },
  { msg: "Retrying failed request — attempt 3/5", lvl: "debug" },
  { msg: "Rate limit exceeded for client 10.0.3.42", lvl: "warn" },
  { msg: "Pod restarted due to OOMKilled", lvl: "fatal" },
  { msg: "TLS handshake completed in 12ms", lvl: "debug" },
];
const serviceNames = ["api-gateway", "payment-api", "auth-service", "user-service", "order-worker"];

function generateDemoLogs() {
  return Array.from({ length: 50 }, (_, i) => {
    const entry = logMessages[i % logMessages.length];
    return {
      id: `log-${i}`,
      timestamp: new Date(Date.now() - i * 15000).toISOString(),
      level: entry.lvl,
      service: serviceNames[i % serviceNames.length],
      message: entry.msg,
      host: `node-${(i % 3) + 1}.prod.internal`,
      trace_id: `trace-${i.toString(36).padStart(8, "0")}`,
    };
  });
}

export default function LogsPage() {
  const [selectedLevel, setSelectedLevel] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [autoRefresh, setAutoRefresh] = useState(true);
   
  const demoLogs = useMemo(() => generateDemoLogs(), []);

  const filtered = demoLogs.filter((log) => {
    if (selectedLevel !== "all" && log.level !== selectedLevel) return false;
    if (searchQuery && !log.message.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Log Explorer</h1>
          <p className="text-sm text-muted-foreground mt-1">Search and analyze logs across all services</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={cn(
              "flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-medium transition-colors",
              autoRefresh
                ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-400"
                : "border-border text-muted-foreground hover:text-foreground"
            )}
          >
            <RefreshCw className={cn("h-3 w-3", autoRefresh && "animate-spin")} style={autoRefresh ? { animationDuration: "3s" } : {}} />
            {autoRefresh ? "Live" : "Paused"}
          </button>
          <button onClick={() => alert("Log export feature is disabled in demo mode.")} className="rounded-lg border border-border px-3 py-1.5 text-xs font-medium text-muted-foreground hover:text-foreground transition-colors">
            <Download className="h-3 w-3 inline mr-1" />
            Export
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="glass rounded-xl p-4">
        <div className="flex flex-wrap gap-3">
          <div className="flex items-center gap-2 rounded-lg border border-border bg-background/50 px-3 py-2 flex-1 min-w-64">
            <Search className="h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search log messages..."
              className="flex-1 bg-transparent text-sm text-foreground placeholder:text-muted-foreground outline-none"
            />
          </div>
          <div className="flex items-center gap-1 rounded-lg border border-border p-1">
            {levels.map((level) => (
              <button
                key={level}
                onClick={() => setSelectedLevel(level)}
                className={cn(
                  "rounded-md px-2.5 py-1 text-xs font-medium transition-colors capitalize",
                  selectedLevel === level
                    ? "bg-pulse-primary/15 text-pulse-primary"
                    : "text-muted-foreground hover:text-foreground"
                )}
              >
                {level}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Log Table */}
      <div className="glass rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border">
                <th className="px-4 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider w-44">Timestamp</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider w-20">Level</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider w-36">Service</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">Message</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider w-36">Host</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/50">
              {filtered.map((log) => {
                const Icon = levelIcon[log.level] || Info;
                return (
                  <tr key={log.id} className="hover:bg-muted/30 transition-colors cursor-pointer group">
                    <td className="px-4 py-2.5 text-xs font-mono text-muted-foreground tabular-nums">
                      {new Date(log.timestamp).toLocaleTimeString("en-US", { hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit", fractionalSecondDigits: 3 })}
                    </td>
                    <td className="px-4 py-2.5">
                      <span className={cn("flex items-center gap-1.5 text-xs font-semibold uppercase", levelColor[log.level])}>
                        <Icon className="h-3.5 w-3.5" />
                        {log.level}
                      </span>
                    </td>
                    <td className="px-4 py-2.5 text-xs font-mono text-foreground">{log.service}</td>
                    <td className="px-4 py-2.5 text-sm text-foreground group-hover:text-white transition-colors">{log.message}</td>
                    <td className="px-4 py-2.5 text-xs font-mono text-muted-foreground">{log.host}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        <div className="border-t border-border px-4 py-3 text-xs text-muted-foreground flex justify-between">
          <span>Showing recent {filtered.length} logs matching filters</span>
          <span className="text-pulse-primary cursor-pointer hover:underline">Load older logs...</span>
        </div>
      </div>
    </div>
  );
}
