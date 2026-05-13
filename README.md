# PulseStack AI

> Autonomous AI-Powered Observability & Incident Intelligence Platform

![Next.js](https://img.shields.io/badge/Next.js-16-black?logo=next.js)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql)
![Elasticsearch](https://img.shields.io/badge/Elasticsearch-8-005571?logo=elasticsearch)
![Kafka](https://img.shields.io/badge/Kafka-3.7-231F20?logo=apachekafka)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)

## What is PulseStack AI?

PulseStack AI is an enterprise-grade AIOps platform that continuously ingests infrastructure logs, metrics, traces, and events from distributed systems. It uses AI agents and machine learning to understand failures, detect anomalies, identify root causes, and automate remediation — functioning like **autonomous SRE engineers**.

## Architecture

```
Frontend (Next.js 16) → API Gateway (FastAPI) → Core Services
                                                    ├── PostgreSQL (state)
                                                    ├── Elasticsearch (logs)
                                                    ├── Redis (cache + streaming)
                                                    ├── Kafka (event pipeline)
                                                    └── AI Agents (LangGraph)
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+
- Python 3.12+

### 1. Start Infrastructure
```bash
docker compose up -d postgres elasticsearch redis kafka
```

### 2. Start Backend
```bash
cd backend
python -m venv .venv
.venv/Scripts/activate  # Windows
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

### 3. Start Frontend
```bash
cd frontend
npm install
npm run dev
```

### 4. Access
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Project Structure

```
pulsestack/
├── frontend/          # Next.js 16 + TypeScript + TailwindCSS
├── backend/           # FastAPI + Python 3.12
├── ai/                # LangGraph AI agents (Phase 2+)
├── streaming/         # Kafka producers/consumers
├── infra/             # Docker, K8s, Terraform
├── tests/             # Backend, frontend, AI tests
└── docker-compose.yml # Local development stack
```

## Features

### Phase 1 (Current) — Core Platform
- ✅ JWT Authentication + RBAC
- ✅ Log ingestion pipeline (Elasticsearch)
- ✅ Log search with full-text + filters
- ✅ Real-time WebSocket streaming
- ✅ Incident management
- ✅ Alert rules engine
- ✅ Service registry & health monitoring
- ✅ Dashboard overview with charts
- ✅ Modern enterprise UI (dark theme, glassmorphism)

### Phase 2 — AI Intelligence
- 🔲 AI log summarization
- 🔲 Semantic search (pgvector)
- 🔲 Conversational AI assistant
- 🔲 Anomaly detection

### Phase 3 — AI Incident Investigation
- 🔲 LangGraph agent orchestrator
- 🔲 Root cause analysis
- 🔲 Failure timeline generation

### Phase 4 — Multi-Agent AIOps
- 🔲 Specialized AI agents
- 🔲 Agent collaboration
- 🔲 Runbook auto-generation

### Phase 5 — Autonomous Operations
- 🔲 K8s rollbacks
- 🔲 Auto-scaling
- 🔲 Predictive prevention

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16, TypeScript, TailwindCSS v4, Recharts, Zustand |
| Backend | FastAPI, Python 3.12, SQLAlchemy 2.0, Pydantic v2 |
| AI | LangGraph, OpenAI, Ollama, pgvector |
| Streaming | Kafka (KRaft), Redis Streams, Celery |
| Databases | PostgreSQL 16, Elasticsearch 8, Redis 7 |
| Infra | Docker, Kubernetes, Terraform, Prometheus, Grafana |

