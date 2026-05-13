"use client";

import { cn } from "@/lib/utils";
import { Server, Plus, Activity, Clock, HardDrive, Cpu, MemoryStick, ArrowUpRight } from "lucide-react";

const services = [
  { name: "api-gateway", type: "api", env: "production", status: "healthy", uptime: "99.98%", latency: "12ms", cpu: "23%", memory: "45%", requests: "12.4k/min" },
  { name: "payment-api", type: "api", env: "production", status: "degraded", uptime: "98.2%", latency: "340ms", cpu: "78%", memory: "62%", requests: "3.2k/min" },
  { name: "auth-service", type: "api", env: "production", status: "degraded", uptime: "99.1%", latency: "2100ms", cpu: "45%", memory: "71%", requests: "8.1k/min" },
  { name: "user-service", type: "api", env: "production", status: "healthy", uptime: "99.99%", latency: "8ms", cpu: "12%", memory: "34%", requests: "5.6k/min" },
  { name: "order-worker", type: "worker", env: "production", status: "down", uptime: "94.5%", latency: "—", cpu: "0%", memory: "0%", requests: "0/min" },
  { name: "postgres-primary", type: "database", env: "production", status: "degraded", uptime: "99.5%", latency: "45ms", cpu: "67%", memory: "82%", requests: "2.1k/min" },
  { name: "redis-cache", type: "cache", env: "production", status: "degraded", uptime: "99.99%", latency: "1ms", cpu: "15%", memory: "87%", requests: "45k/min" },
  { name: "elasticsearch", type: "database", env: "production", status: "healthy", uptime: "99.9%", latency: "23ms", cpu: "56%", memory: "73%", requests: "1.8k/min" },
];

const statusConfig: Record<string, { dot: string; bg: string; text: string }> = {
  healthy: { dot: "bg-emerald-400", bg: "bg-emerald-500/10", text: "text-emerald-400" },
  degraded: { dot: "bg-yellow-400 animate-pulse", bg: "bg-yellow-500/10", text: "text-yellow-400" },
  down: { dot: "bg-red-400 animate-pulse", bg: "bg-red-500/10", text: "text-red-400" },
};

export default function ServicesPage() {
  const healthy = services.filter(s => s.status === "healthy").length;
  const degraded = services.filter(s => s.status === "degraded").length;
  const down = services.filter(s => s.status === "down").length;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Services</h1>
          <p className="text-sm text-muted-foreground mt-1">Monitored infrastructure services and health status</p>
        </div>
        <button className="flex items-center gap-2 rounded-lg bg-gradient-to-r from-pulse-primary to-purple-600 px-4 py-2 text-sm font-semibold text-white hover:shadow-lg hover:shadow-pulse-primary/25 transition-all">
          <Plus className="h-4 w-4" />
          Add Service
        </button>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-3 gap-4">
        <div className="glass rounded-xl p-4 flex items-center gap-3">
          <div className="h-3 w-3 rounded-full bg-emerald-400" />
          <div>
            <p className="text-2xl font-bold text-foreground">{healthy}</p>
            <p className="text-xs text-muted-foreground">Healthy</p>
          </div>
        </div>
        <div className="glass rounded-xl p-4 flex items-center gap-3">
          <div className="h-3 w-3 rounded-full bg-yellow-400 animate-pulse" />
          <div>
            <p className="text-2xl font-bold text-foreground">{degraded}</p>
            <p className="text-xs text-muted-foreground">Degraded</p>
          </div>
        </div>
        <div className="glass rounded-xl p-4 flex items-center gap-3">
          <div className="h-3 w-3 rounded-full bg-red-400 animate-pulse" />
          <div>
            <p className="text-2xl font-bold text-foreground">{down}</p>
            <p className="text-xs text-muted-foreground">Down</p>
          </div>
        </div>
      </div>

      {/* Service Cards Grid */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {services.map((svc) => {
          const cfg = statusConfig[svc.status] || statusConfig.healthy;
          return (
            <div key={svc.name} className={cn("glass rounded-xl p-5 hover:border-muted-foreground/30 transition-all cursor-pointer group animate-slide-up relative overflow-hidden", svc.status === "down" ? "border-red-500/50 shadow-lg shadow-red-500/10" : "")}>
              {svc.status === "down" && (
                <div className="absolute top-0 left-0 right-0 h-1 bg-red-500 animate-pulse"></div>
              )}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="rounded-lg bg-muted p-2">
                    <Server className="h-4 w-4 text-foreground" />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-foreground font-mono group-hover:text-white transition-colors">{svc.name}</h3>
                    <p className="text-xs text-muted-foreground">{svc.type} · {svc.env}</p>
                  </div>
                </div>
                <span className={cn("flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-semibold capitalize", cfg.bg, cfg.text, `border-${cfg.text.replace('text-', '')}/20`)}>
                  <span className={cn("h-1.5 w-1.5 rounded-full", cfg.dot)} />
                  {svc.status}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-lg bg-background/50 p-2.5">
                  <p className="text-[10px] uppercase text-muted-foreground font-medium flex items-center gap-1"><Activity className="h-3 w-3" />Latency</p>
                  <p className="text-sm font-bold text-foreground mt-0.5 tabular-nums">{svc.latency}</p>
                </div>
                <div className="rounded-lg bg-background/50 p-2.5">
                  <p className="text-[10px] uppercase text-muted-foreground font-medium flex items-center gap-1"><Clock className="h-3 w-3" />Uptime</p>
                  <p className="text-sm font-bold text-foreground mt-0.5 tabular-nums">{svc.uptime}</p>
                </div>
                <div className="rounded-lg bg-background/50 p-2.5">
                  <p className="text-[10px] uppercase text-muted-foreground font-medium flex items-center gap-1"><Cpu className="h-3 w-3" />CPU</p>
                  <p className="text-sm font-bold text-foreground mt-0.5 tabular-nums">{svc.cpu}</p>
                </div>
                <div className="rounded-lg bg-background/50 p-2.5">
                  <p className="text-[10px] uppercase text-muted-foreground font-medium flex items-center gap-1"><HardDrive className="h-3 w-3" />Memory</p>
                  <p className="text-sm font-bold text-foreground mt-0.5 tabular-nums">{svc.memory}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
