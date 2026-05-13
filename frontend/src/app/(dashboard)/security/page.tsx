import { Shield, Lock, AlertOctagon, Key } from "lucide-react";

export default function SecurityPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Security Overview</h1>
        <p className="text-sm text-muted-foreground mt-1">Monitor IAM, API tokens, and suspicious network patterns</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="glass rounded-xl p-4 flex items-center gap-3">
          <div className="rounded-lg bg-emerald-500/10 p-2.5"><Shield className="h-5 w-5 text-emerald-400" /></div>
          <div>
            <p className="text-xs text-muted-foreground">System Status</p>
            <p className="text-lg font-bold text-emerald-400">Secure</p>
          </div>
        </div>
        <div className="glass rounded-xl p-4 flex items-center gap-3">
          <div className="rounded-lg bg-red-500/10 p-2.5"><AlertOctagon className="h-5 w-5 text-red-400" /></div>
          <div>
            <p className="text-xs text-muted-foreground">Active Threats</p>
            <p className="text-lg font-bold text-foreground">0</p>
          </div>
        </div>
        <div className="glass rounded-xl p-4 flex items-center gap-3">
          <div className="rounded-lg bg-pulse-primary/10 p-2.5"><Lock className="h-5 w-5 text-pulse-primary" /></div>
          <div>
            <p className="text-xs text-muted-foreground">Failed Logins (24h)</p>
            <p className="text-lg font-bold text-foreground">14</p>
          </div>
        </div>
        <div className="glass rounded-xl p-4 flex items-center gap-3">
          <div className="rounded-lg bg-blue-500/10 p-2.5"><Key className="h-5 w-5 text-blue-400" /></div>
          <div>
            <p className="text-xs text-muted-foreground">Active API Keys</p>
            <p className="text-lg font-bold text-foreground">8</p>
          </div>
        </div>
      </div>

      <div className="glass rounded-xl border border-border p-6">
        <h3 className="text-sm font-semibold mb-4 text-foreground">Recent Security Events</h3>
        <div className="text-sm text-muted-foreground py-8 text-center border border-dashed border-border/50 rounded-lg">
          No critical security events detected in the last 7 days.
        </div>
      </div>
    </div>
  );
}
