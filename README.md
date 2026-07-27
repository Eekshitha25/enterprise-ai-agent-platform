# Enterprise AI Agent Platform
### Multi-Agent RAG System for Enterprise Knowledge Automation

An "AI employee" that reads company documents, understands business questions,
searches internal knowledge bases, calls tools/APIs, and answers with citations
and a visible reasoning trace — built with a supervisor/specialist multi-agent
architecture on LangGraph.

**Example interaction it's built to handle:**

> **User:** "Why did our AWS bill increase last month?"
> **Agent:** Routes to the Finance agent → pulls the invoice line items →
> checks cloud usage deltas → cross-references the internal cost policy doc →
> explains the root cause (e.g. a runaway SageMaker job + cross-region data
> transfer) → suggests concrete optimizations → cites every source it used.

---

## 1. Architecture

```
                          ┌─────────────────────┐
                          │   React Dashboard    │
                          │  (chat + citations +  │
                          │   agent trace + docs)  │
                          └──────────┬───────────┘
                                     │ REST (FastAPI)
                          ┌──────────▼───────────┐
                          │      FastAPI API      │
                          │  /chat  /documents     │
                          └──────────┬───────────┘
                                     │
                          ┌──────────▼───────────┐
                          │   LangGraph Supervisor │
                          │   (routes each turn)   │
                          └───┬───────────────┬───┘
                              │               │
                  ┌───────────▼──┐     ┌──────▼────────┐
                  │ Research Agent│     │ Finance Agent  │
                  │ (RAG search)  │     │ (invoices +    │
                  │               │     │  cloud usage)  │
                  └───────┬───────┘     └──────┬────────┘
                          │                    │
              ┌───────────▼───────┐   ┌────────▼─────────┐
              │   Qdrant Vector DB │   │  AWS Cost APIs /  │
              │  (doc embeddings)  │   │  Invoice data      │
              └───────────┬───────┘   └───────────────────┘
                          │
              ┌───────────▼───────┐
              │  Ingestion pipeline│
              │ PDF / Confluence /│
              │ Notion / Email     │
              └───────────────────┘

        PostgreSQL persists conversations, messages, citations, and
        the agent trace for every turn (audit trail + conversation history).
```

**Why a supervisor/specialist pattern instead of one giant agent:** each
specialist (research, finance, and any future agent — compliance, ops, HR)
owns its own tools and system prompt, stays independently testable, and the
supervisor can be swapped for a smarter router (e.g. a classifier) without
touching specialist logic. This mirrors how real enterprise "AI employee"
platforms are structured.

## 2. Tech stack

| Layer | Tech |
|---|---|
| Orchestration | LangGraph (multi-agent state machine) + LangChain (tool-calling agents) |
| LLM | Claude (Anthropic) or GPT (OpenAI) — swappable via `.env` |
| Retrieval | RAG over Qdrant vector DB, OpenAI embeddings |
| Backend API | FastAPI |
| Persistence | PostgreSQL (conversations, messages, citations, agent trace) |
| Frontend | React + Vite + Tailwind (chat UI, citation cards, live agent trace, doc upload) |
| Infra | Docker Compose (local), Kubernetes manifests (production: HPA, ingress, secrets) |
| Cloud | AWS (Cost Explorer tool; mocked by default so the demo runs without live creds) |

## 3. Project layout

```
enterprise-ai-agent-platform/
├── backend/
│   ├── app/
│   │   ├── agents/        # LangGraph graph, supervisor, research & finance agents
│   │   ├── tools/         # knowledge search, invoice lookup, AWS cost/usage tools
│   │   ├── rag/           # embeddings, Qdrant client, ingestion pipeline, retriever
│   │   ├── db/            # SQLAlchemy models, session, Pydantic schemas
│   │   ├── api/           # /chat and /documents FastAPI routes
│   │   └── main.py
│   ├── seed_data/         # sample invoice, usage, and knowledge-base docs for demoing
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/    # Sidebar, ChatWindow, MessageBubble, CitationCard, AgentTrace
│   │   └── api/client.js
│   └── Dockerfile
├── infra/
│   ├── docker-compose.yml
│   └── k8s/                # namespace, postgres, qdrant, backend+HPA, frontend, ingress, secrets
└── README.md
```

## 4. Running it locally

```bash
cp backend/.env.example backend/.env
# edit backend/.env and add OPENAI_API_KEY (embeddings) and ANTHROPIC_API_KEY or OPENAI_API_KEY (chat model)

cd infra
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend docs (Swagger): http://localhost:8000/docs
- Qdrant dashboard: http://localhost:6333/dashboard

**Try the demo flow:**
1. Upload a PDF (or rely on the seeded `sample_docs/` text already used by the
   knowledge tool) via the sidebar upload button.
2. Ask: *"What's our cost optimization policy for SageMaker jobs?"* → routes
   to the Research agent, cites the policy doc.
3. Ask: *"Why did our AWS bill increase last month?"* → routes to the Finance
   agent, which pulls `2026-06` invoice + usage data (seeded in
   `backend/seed_data/`), explains the SageMaker + data-transfer spike, and
   suggests optimizations.

`USE_MOCK_AWS_TOOL=true` (default) uses the seeded usage data so the whole
flow works with zero AWS credentials. Flip it to `false` and provide AWS keys
with `ce:GetCostAndUsage` permission to hit live Cost Explorer.

## 5. Deploying to Kubernetes

```bash
kubectl apply -f infra/k8s/namespace.yaml
kubectl apply -f infra/k8s/secrets.example.yaml   # copy & fill in real values first
kubectl apply -f infra/k8s/postgres.yaml
kubectl apply -f infra/k8s/qdrant.yaml
kubectl apply -f infra/k8s/backend-deployment.yaml
kubectl apply -f infra/k8s/frontend-deployment.yaml
kubectl apply -f infra/k8s/ingress.yaml
```

The backend Deployment ships with a `HorizontalPodAutoscaler` (2–10 replicas
on 70% CPU) since agent calls are I/O-bound on LLM/tool latency, not CPU —
this is a starting point to tune once you have real traffic patterns.

## 6. Extending it

- **New specialist agent:** add a node (`app/agents/<name>_agent.py`) with its
  own tools + prompt, register it in `app/agents/graph.py`, and teach the
  supervisor prompt about the new route.
- **New data source:** add a loader in `app/rag/ingestion.py` (Confluence and
  Notion stubs are already there with the exact LangChain loader classes to
  wire in) and a corresponding upload/sync endpoint.
- **Swap vector DB:** `app/rag/vector_store.py` is the only file that talks to
  Qdrant — implement the same three methods against Pinecone or Weaviate and
  nothing else in the codebase changes.
- **Streaming responses:** LangGraph supports `.stream()` — swap the `/chat`
  route to a `StreamingResponse` for token-by-token UI updates.

## 7. Resume framing

**Title:** *Built an Autonomous AI Agent Platform for Enterprise Knowledge Automation*

Suggested bullets (edit numbers to match what you actually measure once deployed):

- Architected a multi-agent RAG platform (LangGraph + LangChain + Qdrant) that
  routes natural-language business questions to specialist agents, cutting
  manual document/invoice lookup time by an estimated **60–70%** in the demo
  workflow.
- Built a supervisor/specialist agent orchestration pattern in LangGraph,
  enabling independent tool-calling agents (RAG research, FinOps cost
  analysis) to be added without modifying existing agent logic.
- Designed a RAG ingestion pipeline (PDF/Confluence/Notion/email → chunking →
  embeddings → Qdrant) with citation tracking end-to-end from retrieval to UI.
- Shipped a production-shaped deployment: Dockerized FastAPI + React services,
  Kubernetes manifests with HPA and ingress, PostgreSQL for conversation/audit
  history.
- Built the React dashboard (chat UI, live agent reasoning trace, inline
  citation cards, document upload) consumed by the agent platform's API.

## 8. Notes on scope

This is a complete, runnable reference implementation, not a fully managed
SaaS. To take it from "portfolio project" to "production," you'd add: auth
(the API is currently open), rate limiting, streaming responses, retries/
circuit breakers around tool calls, evaluation harness for agent answer
quality, and real Confluence/Notion/email connectors (stubs are in
`ingestion.py` with the exact LangChain classes to plug in).
