"use client";

import { useMemo } from "react";
import {
  Server,
  AlertTriangle,
  Bell,
  ScrollText,
  Bot,
  TrendingUp,
  TrendingDown,
  ArrowUpRight,
  Activity,
  ShieldAlert,
  Zap,
} from "lucide-react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";
import { cn, severityColor, formatRelativeTime } from "@/lib/utils";

// Seeded deterministic chart data (no Math.random to avoid hydration mismatch)
const logVolumeData = [
  { hour: "0:00", logs: 2100, errors: 45 }, { hour: "1:00", logs: 1800, errors: 32 },
  { hour: "2:00", logs: 1500, errors: 28 }, { hour: "3:00", logs: 1200, errors: 22 },
  { hour: "4:00", logs: 1400, errors: 35 }, { hour: "5:00", logs: 2200, errors: 48 },
  { hour: "6:00", logs: 3100, errors: 62 }, { hour: "7:00", logs: 4200, errors: 95 },
  { hour: "8:00", logs: 5100, errors: 120 }, { hour: "9:00", logs: 4800, errors: 105 },
  { hour: "10:00", logs: 4500, errors: 88 }, { hour: "11:00", logs: 4300, errors: 76 },
  { hour: "12:00", logs: 3900, errors: 68 }, { hour: "13:00", logs: 4100, errors: 82 },
  { hour: "14:00", logs: 4600, errors: 91 }, { hour: "15:00", logs: 5200, errors: 110 },
  { hour: "16:00", logs: 5500, errors: 130 }, { hour: "17:00", logs: 5000, errors: 115 },
  { hour: "18:00", logs: 4200, errors: 85 }, { hour: "19:00", logs: 3600, errors: 65 },
  { hour: "20:00", logs: 3100, errors: 52 }, { hour: "21:00", logs: 2800, errors: 42 },
  { hour: "22:00", logs: 2500, errors: 38 }, { hour: "23:00", logs: 2200, errors: 35 },
];

const severityData = [
  { name: "Critical", count: 3, fill: "#ef4444" },
  { name: "High", count: 7, fill: "#f97316" },
  { name: "Medium", count: 12, fill: "#eab308" },
  { name: "Low", count: 24, fill: "#3b82f6" },
];

const services = [
  { name: "api-gateway", status: "healthy", uptime: "99.98%", latency: "12ms" },
  { name: "payment-api", status: "degraded", uptime: "98.2%", latency: "340ms" },
  { name: "auth-service", status: "degraded", uptime: "99.1%", latency: "2100ms" },
  { name: "user-service", status: "healthy", uptime: "99.99%", latency: "8ms" },
  { name: "order-worker", status: "down", uptime: "94.5%", latency: "—" },
  { name: "postgres-primary", status: "degraded", uptime: "99.5%", latency: "45ms" },
];

function generateTimedData() {
  const now = Date.now();
  return {
    recentIncidents: [
      { id: "1", title: "Payment Service — 502 errors spike", severity: "critical", status: "investigating", time: new Date(now - 300000).toISOString(), service: "payment-api" },
      { id: "2", title: "Database connection pool exhausted", severity: "high", status: "open", time: new Date(now - 900000).toISOString(), service: "postgres-primary" },
      { id: "3", title: "Auth service latency >2s", severity: "medium", status: "investigating", time: new Date(now - 1800000).toISOString(), service: "auth-service" },
      { id: "4", title: "K8s pod CrashLoopBackOff — order-worker", severity: "high", status: "open", time: new Date(now - 3600000).toISOString(), service: "order-worker" },
    ],
    recentAlerts: [
      { rule: "CPU > 90%", severity: "critical", service: "api-gateway", time: new Date(now - 120000).toISOString() },
      { rule: "Error rate > 5%", severity: "high", service: "payment-api", time: new Date(now - 600000).toISOString() },
      { rule: "Memory > 85%", severity: "medium", service: "redis-cache", time: new Date(now - 1200000).toISOString() },
      { rule: "Disk > 90%", severity: "high", service: "elasticsearch", time: new Date(now - 2400000).toISOString() },
    ],
  };
}

function StatCard({
  title,
  value,
  change,
  changeType,
  icon: Icon,
  iconColor,
}: {
  title: string;
  value: string | number;
  change: string;
  changeType: "up" | "down" | "neutral";
  icon: React.ElementType;
  iconColor: string;
}) {
  return (
    <div className="glass rounded-xl p-5 animate-slide-up transition-transform hover:scale-[1.02]">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          <p className="mt-2 text-3xl font-bold tracking-tight text-foreground">{value}</p>
        </div>
        <div className={cn("rounded-lg p-2.5", iconColor)}>
          <Icon className="h-5 w-5" />
        </div>
      </div>
      <div className="mt-3 flex items-center gap-1.5">
        {changeType === "up" && <TrendingUp className="h-3.5 w-3.5 text-emerald-400" />}
        {changeType === "down" && <TrendingDown className="h-3.5 w-3.5 text-red-400" />}
        <span
          className={cn(
            "text-xs font-medium",
            changeType === "up" ? "text-emerald-400" : changeType === "down" ? "text-red-400" : "text-muted-foreground"
          )}
        >
          {change}
        </span>
        <span className="text-xs text-muted-foreground">vs last 24h</span>
      </div>
    </div>
  );
}

export default function OverviewPage() {
   
  const { recentIncidents, recentAlerts } = useMemo(() => generateTimedData(), []);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-foreground">
          Infrastructure Overview
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Real-time observability across all monitored services
        </p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Services"
          value={18}
          change="+2"
          changeType="up"
          icon={Server}
          iconColor="bg-blue-500/10 text-blue-400"
        />
        <StatCard
          title="Open Incidents"
          value={4}
          change="+1"
          changeType="down"
          icon={AlertTriangle}
          iconColor="bg-red-500/10 text-red-400"
        />
        <StatCard
          title="Active Alerts"
          value={6}
          change="-3"
          changeType="up"
          icon={Bell}
          iconColor="bg-orange-500/10 text-orange-400"
        />
        <StatCard
          title="Logs (24h)"
          value="1.2M"
          change="+15%"
          changeType="up"
          icon={ScrollText}
          iconColor="bg-emerald-500/10 text-emerald-400"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Log Volume Chart */}
        <div className="glass rounded-xl p-5 lg:col-span-2 animate-slide-up">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold text-foreground">Log Volume</h3>
              <p className="text-xs text-muted-foreground">Ingested logs over the last 24 hours</p>
            </div>
            <div className="flex items-center gap-4 text-xs">
              <span className="flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-pulse-primary" />
                Total
              </span>
              <span className="flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-red-400" />
                Errors
              </span>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <AreaChart data={logVolumeData}>
              <defs>
                <linearGradient id="logGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#7c3aed" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#7c3aed" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="errGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
              <XAxis dataKey="hour" tick={{ fontSize: 11, fill: "#71717a" }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: "#71717a" }} axisLine={false} tickLine={false} />
              <Tooltip
                contentStyle={{ backgroundColor: "#18181b", border: "1px solid #3f3f46", borderRadius: "8px", fontSize: "12px" }}
                labelStyle={{ color: "#fafafa" }}
              />
              <Area type="monotone" dataKey="logs" stroke="#7c3aed" fill="url(#logGrad)" strokeWidth={2} />
              <Area type="monotone" dataKey="errors" stroke="#ef4444" fill="url(#errGrad)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Incident Severity Distribution */}
        <div className="glass rounded-xl p-5 animate-slide-up">
          <h3 className="text-sm font-semibold text-foreground mb-1">Alert Severity</h3>
          <p className="text-xs text-muted-foreground mb-4">Active alert distribution</p>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={severityData} layout="vertical" barSize={16}>
              <CartesianGrid strokeDasharray="3 3" stroke="#27272a" horizontal={false} />
              <XAxis type="number" tick={{ fontSize: 11, fill: "#71717a" }} axisLine={false} tickLine={false} />
              <YAxis dataKey="name" type="category" tick={{ fontSize: 11, fill: "#a1a1aa" }} axisLine={false} tickLine={false} width={60} />
              <Tooltip contentStyle={{ backgroundColor: "#18181b", border: "1px solid #3f3f46", borderRadius: "8px", fontSize: "12px" }} />
              <Bar dataKey="count" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Bottom Row: Incidents + Alerts + Services */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Recent Incidents */}
        <div className="glass rounded-xl p-5 animate-slide-up">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-foreground">Recent Incidents</h3>
            <a href="/incidents" className="text-xs font-medium text-pulse-primary hover:underline flex items-center gap-0.5">
              View all <ArrowUpRight className="h-3 w-3" />
            </a>
          </div>
          <div className="space-y-3">
            {recentIncidents.map((inc) => (
              <div
                key={inc.id}
                className="flex items-start gap-3 rounded-lg border border-border bg-background/50 p-3 transition-colors hover:border-muted-foreground/30"
              >
                <ShieldAlert className={cn("h-4 w-4 mt-0.5 shrink-0", inc.severity === "critical" ? "text-red-400" : inc.severity === "high" ? "text-orange-400" : "text-yellow-400")} />
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium text-foreground truncate">{inc.title}</p>
                  <div className="mt-1 flex items-center gap-2 text-xs text-muted-foreground">
                    <span className={cn("rounded-full border px-2 py-0.5 text-[10px] font-semibold uppercase", severityColor(inc.severity))}>
                      {inc.severity}
                    </span>
                    <span>{formatRelativeTime(inc.time)}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Alerts */}
        <div className="glass rounded-xl p-5 animate-slide-up">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-foreground">Recent Alerts</h3>
            <a href="/alerts" className="text-xs font-medium text-pulse-primary hover:underline flex items-center gap-0.5">
              View all <ArrowUpRight className="h-3 w-3" />
            </a>
          </div>
          <div className="space-y-3">
            {recentAlerts.map((alert, i) => (
              <div
                key={i}
                className="flex items-center gap-3 rounded-lg border border-border bg-background/50 p-3 transition-colors hover:border-muted-foreground/30"
              >
                <Bell className={cn("h-4 w-4 shrink-0", alert.severity === "critical" ? "text-red-400" : alert.severity === "high" ? "text-orange-400" : "text-yellow-400")} />
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium text-foreground">{alert.rule}</p>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    {alert.service} · {formatRelativeTime(alert.time)}
                  </p>
                </div>
                <span className={cn("rounded-full border px-2 py-0.5 text-[10px] font-semibold uppercase shrink-0", severityColor(alert.severity))}>
                  {alert.severity}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Service Health */}
        <div className="glass rounded-xl p-5 animate-slide-up">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-foreground">Service Health</h3>
            <a href="/services" className="text-xs font-medium text-pulse-primary hover:underline flex items-center gap-0.5">
              View all <ArrowUpRight className="h-3 w-3" />
            </a>
          </div>
          <div className="space-y-2">
            {services.map((svc) => (
              <div
                key={svc.name}
                className="flex items-center gap-3 rounded-lg border border-border bg-background/50 p-3 transition-colors hover:border-muted-foreground/30"
              >
                <div className={cn("h-2.5 w-2.5 rounded-full shrink-0",
                  svc.status === "healthy" ? "bg-emerald-400" :
                  svc.status === "degraded" ? "bg-yellow-400 animate-pulse" :
                  "bg-red-400 animate-pulse"
                )} />
                <span className="text-sm font-medium text-foreground flex-1 truncate font-mono">{svc.name}</span>
                <span className="text-xs text-muted-foreground tabular-nums">{svc.latency}</span>
                <span className="text-xs text-muted-foreground tabular-nums w-14 text-right">{svc.uptime}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* AI Agent Status Banner */}
      <div className="glass rounded-xl p-5 animate-slide-up">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-pulse-primary to-pulse-secondary">
              <Bot className="h-5 w-5 text-white" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-foreground">AI Agents — Active</h3>
              <p className="text-xs text-muted-foreground">
                3 agents monitoring · 2 investigating incidents · Last analysis 30s ago
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex -space-x-2">
              {["A", "R", "T"].map((letter, i) => (
                <div
                  key={i}
                  className="flex h-7 w-7 items-center justify-center rounded-full border-2 border-card bg-gradient-to-br from-pulse-primary to-pulse-secondary text-[10px] font-bold text-white"
                >
                  {letter}
                </div>
              ))}
            </div>
            <button className="rounded-lg bg-pulse-primary/10 px-3 py-1.5 text-xs font-medium text-pulse-primary hover:bg-pulse-primary/20 transition-colors border border-pulse-primary/20">
              <Zap className="mr-1 inline h-3 w-3" />
              Ask AI
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
