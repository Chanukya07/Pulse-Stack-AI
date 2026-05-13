"use client";

import { useState } from "react";
import { Settings as SettingsIcon, User, Shield, Bell, Database, Bot, Save } from "lucide-react";
import { cn } from "@/lib/utils";

const tabs = [
  { id: "profile", icon: User, title: "Profile", desc: "Manage your account settings" },
  { id: "security", icon: Shield, title: "Security", desc: "Authentication and API keys" },
  { id: "ai", icon: Bot, title: "AI Configuration", desc: "LLM providers and agent settings" },
];

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState("profile");

  return (
    <div className="space-y-6 max-w-5xl">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Settings</h1>
        <p className="text-sm text-muted-foreground mt-1">Platform configuration and preferences</p>
      </div>

      <div className="flex flex-col md:flex-row gap-6">
        {/* Sidebar */}
        <div className="w-full md:w-64 space-y-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all text-left",
                activeTab === tab.id
                  ? "bg-pulse-primary/15 text-pulse-primary"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              )}
            >
              <tab.icon className="h-4 w-4" />
              {tab.title}
            </button>
          ))}
        </div>

        {/* Content Area */}
        <div className="flex-1 glass rounded-xl p-6 border border-border">
          {activeTab === "profile" && (
            <div className="space-y-4 animate-fade-in">
              <h2 className="text-lg font-semibold text-foreground border-b border-border pb-2 mb-4">Profile Settings</h2>
              <div className="grid gap-2">
                <label className="text-xs font-medium text-muted-foreground">Full Name</label>
                <input type="text" defaultValue="John Doe" className="w-full rounded-lg border border-border bg-background/50 px-3 py-2 text-sm text-foreground focus:border-pulse-primary focus:outline-none" />
              </div>
              <div className="grid gap-2">
                <label className="text-xs font-medium text-muted-foreground">Email Address</label>
                <input type="email" defaultValue="john@example.com" className="w-full rounded-lg border border-border bg-background/50 px-3 py-2 text-sm text-foreground focus:border-pulse-primary focus:outline-none" />
              </div>
            </div>
          )}

          {activeTab === "security" && (
            <div className="space-y-4 animate-fade-in">
              <h2 className="text-lg font-semibold text-foreground border-b border-border pb-2 mb-4">Security</h2>
              <div className="grid gap-2">
                <label className="text-xs font-medium text-muted-foreground">Current Password</label>
                <input type="password" placeholder="••••••••" className="w-full rounded-lg border border-border bg-background/50 px-3 py-2 text-sm text-foreground focus:border-pulse-primary focus:outline-none" />
              </div>
              <div className="grid gap-2">
                <label className="text-xs font-medium text-muted-foreground">New Password</label>
                <input type="password" placeholder="••••••••" className="w-full rounded-lg border border-border bg-background/50 px-3 py-2 text-sm text-foreground focus:border-pulse-primary focus:outline-none" />
              </div>
              <div className="pt-4 mt-4 border-t border-border">
                <h3 className="text-sm font-semibold text-foreground mb-2">API Keys</h3>
                <div className="bg-muted/30 border border-border rounded-lg p-3 text-sm text-muted-foreground font-mono flex justify-between items-center">
                  <span>ps_live_******************</span>
                  <button className="text-pulse-primary hover:underline text-xs">Revoke</button>
                </div>
              </div>
            </div>
          )}

          {activeTab === "ai" && (
            <div className="space-y-4 animate-fade-in">
              <h2 className="text-lg font-semibold text-foreground border-b border-border pb-2 mb-4">AI Configuration</h2>
              <div className="grid gap-2">
                <label className="text-xs font-medium text-muted-foreground">Primary LLM Provider</label>
                <select className="w-full rounded-lg border border-border bg-background/50 px-3 py-2 text-sm text-foreground focus:border-pulse-primary focus:outline-none">
                  <option>OpenRouter (poolside/laguna-xs.2)</option>
                  <option>OpenAI (gpt-4o)</option>
                  <option>Local (Ollama / Llama 3)</option>
                </select>
              </div>
              <div className="grid gap-2 mt-4">
                <label className="text-xs font-medium text-muted-foreground flex items-center gap-2">
                  <input type="checkbox" defaultChecked className="rounded border-border text-pulse-primary focus:ring-pulse-primary bg-background" />
                  Enable Autonomous Investigation (Autopilot)
                </label>
              </div>
              <div className="grid gap-2 mt-2">
                <label className="text-xs font-medium text-muted-foreground flex items-center gap-2">
                  <input type="checkbox" defaultChecked className="rounded border-border text-pulse-primary focus:ring-pulse-primary bg-background" />
                  Enable Live Anomaly Detection
                </label>
              </div>
            </div>
          )}

          <div className="mt-6 pt-4 border-t border-border flex justify-end">
            <button className="flex items-center gap-2 rounded-lg bg-pulse-primary px-4 py-2 text-sm font-semibold text-white hover:bg-pulse-primary/90 transition-all">
              <Save className="h-4 w-4" />
              Save Changes
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
