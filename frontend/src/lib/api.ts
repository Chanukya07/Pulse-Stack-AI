const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_V1 = `${API_BASE}/api/v1`;

type FetchOptions = RequestInit & {
  token?: string;
};

async function apiFetch<T = unknown>(
  endpoint: string,
  options: FetchOptions = {}
): Promise<T> {
  const { token, headers: customHeaders, ...rest } = options;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((customHeaders as Record<string, string>) || {}),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_V1}${endpoint}`, {
    headers,
    ...rest,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `API Error: ${res.status}`);
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

// ── Auth ────────────────────────────────────────────────────
export const authApi = {
  register: (data: { email: string; password: string; full_name: string }) =>
    apiFetch<{ access_token: string; refresh_token: string }>("/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  login: (data: { email: string; password: string }) =>
    apiFetch<{ access_token: string; refresh_token: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  refresh: (refresh_token: string) =>
    apiFetch<{ access_token: string; refresh_token: string }>("/auth/refresh", {
      method: "POST",
      body: JSON.stringify({ refresh_token }),
    }),
};

// ── Dashboard ──────────────────────────────────────────────
export const dashboardApi = {
  getOverview: (token: string) =>
    apiFetch<DashboardOverview>("/dashboard/overview", { token }),
};

// ── Logs ───────────────────────────────────────────────────
export const logsApi = {
  search: (token: string, params?: Record<string, string>) => {
    const query = params ? `?${new URLSearchParams(params)}` : "";
    return apiFetch<LogSearchResponse>(`/logs/search${query}`, { token });
  },

  ingest: (token: string, logs: LogEntry[]) =>
    apiFetch("/logs/ingest", {
      method: "POST",
      body: JSON.stringify({ logs }),
      token,
    }),
};

// ── Incidents ──────────────────────────────────────────────
export const incidentsApi = {
  list: (token: string, params?: Record<string, string>) => {
    const query = params ? `?${new URLSearchParams(params)}` : "";
    return apiFetch<IncidentResponse[]>(`/incidents${query}`, { token });
  },

  get: (token: string, id: string) =>
    apiFetch<IncidentResponse>(`/incidents/${id}`, { token }),

  create: (token: string, data: IncidentCreate) =>
    apiFetch<IncidentResponse>("/incidents", {
      method: "POST",
      body: JSON.stringify(data),
      token,
    }),

  update: (token: string, id: string, data: Partial<IncidentCreate>) =>
    apiFetch<IncidentResponse>(`/incidents/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
      token,
    }),
};

// ── Services ───────────────────────────────────────────────
export const servicesApi = {
  list: (token: string) =>
    apiFetch<ServiceResponse[]>("/services", { token }),

  create: (token: string, data: { name: string; service_type?: string; environment?: string }) =>
    apiFetch<ServiceResponse>("/services", {
      method: "POST",
      body: JSON.stringify(data),
      token,
    }),
};

// ── Alerts ─────────────────────────────────────────────────
export const alertsApi = {
  list: (token: string, params?: Record<string, string>) => {
    const query = params ? `?${new URLSearchParams(params)}` : "";
    return apiFetch<AlertResponse[]>(`/alerts${query}`, { token });
  },

  listRules: (token: string) =>
    apiFetch<AlertRuleResponse[]>("/alerts/rules", { token }),

    createRule: (token: string, data: AlertRuleCreate) =>
    apiFetch<AlertRuleResponse>("/alerts/rules", {
      method: "POST",
      body: JSON.stringify(data),
      token,
    }),
};

// ── Agents / AI ────────────────────────────────────────────
export const agentsApi = {
  chat: (token: string, messages: Record<string, unknown>[], model?: string) =>
    apiFetch<{ content: string; model: string; tokens_used: number }>("/ai/chat", {
      method: "POST",
      body: JSON.stringify({ messages, model, stream: false }),
      token,
    }),

  investigate: (token: string, query: string, incidentId?: string) =>
    apiFetch<InvestigationResult>("/ai/investigate", {
      method: "POST",
      body: JSON.stringify({ query, incident_id: incidentId }),
      token,
    }),
};

// ── Types ──────────────────────────────────────────────────
export interface DashboardOverview {
  total_services: number;
  healthy_services: number;
  degraded_services: number;
  open_incidents: number;
  critical_incidents: number;
  active_alerts: number;
  logs_ingested_24h: number;
  ai_sessions_24h: number;
  recent_incidents: IncidentResponse[];
  recent_alerts: AlertResponse[];
}

export interface LogEntry {
  timestamp?: string;
  service: string;
  level: string;
  message: string;
  source?: string;
  host?: string;
  environment?: string;
  trace_id?: string;
  metadata?: Record<string, unknown>;
}

export interface LogSearchResponse {
  total: number;
  logs: Record<string, unknown>[];
  took_ms: number;
}

export interface IncidentResponse {
  id: string;
  org_id: string;
  title: string;
  description: string | null;
  severity: string;
  status: string;
  source: string | null;
  ai_summary: string | null;
  ai_root_cause: string | null;
  ai_confidence: number | null;
  assigned_to: string | null;
  resolved_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface IncidentCreate {
  title: string;
  description?: string;
  severity: string;
  source?: string;
  service_ids?: string[];
}

export interface ServiceResponse {
  id: string;
  org_id: string;
  name: string;
  service_type: string | null;
  environment: string | null;
  status: string;
  created_at: string;
}

export interface AlertResponse {
  id: string;
  org_id: string;
  service_id: string | null;
  incident_id: string | null;
  rule_name: string;
  severity: string;
  status: string;
  message: string | null;
  fired_at: string;
  resolved_at: string | null;
}

export interface AlertRuleResponse {
  id: string;
  org_id: string;
  name: string;
  condition: Record<string, unknown>;
  severity: string;
  channels: Record<string, unknown>[];
  is_active: boolean;
  created_at: string;
}

export interface AlertRuleCreate {
  name: string;
  condition: Record<string, unknown>;
  severity?: string;
  channels?: Record<string, unknown>[];
}

export interface InvestigationResult {
  report: string;
  analysis: string;
  root_cause: string;
  confidence: number;
  steps_taken: string[];
  duration_ms: number;
  incident_id: string | null;
}
