"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  ScrollText,
  AlertTriangle,
  Bell,
  Server,
  Settings,
  Bot,
  Shield,
  LogOut,
  Zap,
} from "lucide-react";
import { useAuthStore } from "@/stores/auth";

const navigation = [
  { name: "Overview", href: "/overview", icon: LayoutDashboard },
  { name: "Logs", href: "/logs", icon: ScrollText },
  { name: "Incidents", href: "/incidents", icon: AlertTriangle },
  { name: "Alerts", href: "/alerts", icon: Bell },
  { name: "Services", href: "/services", icon: Server },
  { name: "AI Agents", href: "/agents", icon: Bot },
  { name: "Security", href: "/security", icon: Shield },
  { name: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const { logout, user } = useAuthStore();

  return (
    <aside className="fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r border-border bg-card">
      {/* Logo */}
      <div className="flex h-16 items-center gap-2 px-6 border-b border-border">
        <div className="relative flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-pulse-primary to-pulse-secondary">
          <Zap className="h-4 w-4 text-white" />
          <div className="absolute inset-0 rounded-lg bg-pulse-glow/20 animate-pulse-glow" />
        </div>
        <div>
          <h1 className="text-sm font-bold tracking-tight text-foreground">
            PulseStack
          </h1>
          <p className="text-[10px] font-medium text-pulse-secondary uppercase tracking-widest">
            AI Platform
          </p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4 overflow-y-auto">
        {navigation.map((item) => {
          const isActive = pathname === item.href || pathname?.startsWith(item.href + "/");
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200",
                isActive
                  ? "bg-pulse-primary/15 text-pulse-primary shadow-sm shadow-pulse-primary/10"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              )}
            >
              <item.icon className={cn("h-4 w-4 shrink-0", isActive && "text-pulse-primary")} />
              {item.name}
              {item.name === "Incidents" && (
                <span className="ml-auto flex h-5 min-w-5 items-center justify-center rounded-full bg-red-500/20 px-1.5 text-[10px] font-bold text-red-400">
                  4
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* User footer */}
      <div className="border-t border-border p-4">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-pulse-primary to-pulse-secondary text-xs font-bold text-white">
            {user?.full_name?.[0] || "U"}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-foreground truncate">
              {user?.full_name || "User"}
            </p>
            <p className="text-xs text-muted-foreground truncate">
              {user?.role || "viewer"}
            </p>
          </div>
          <button
            onClick={logout}
            className="rounded-lg p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
            title="Sign out"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}
