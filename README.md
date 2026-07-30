# Change Impact Memory

**AI that reconstructs enterprise decision reasoning from fragmented evidence and preserves it as verified organizational memory.**

A Human-in-the-Loop AI system demonstrating risk-labeled actions, role-based approval, guardrail checks, undo/rollback, and a complete audit trail.

---

## Quick Start

```bash
# Install backend dependencies
pip install fastapi uvicorn python-multipart pydantic boto3 python-docx PyPDF2 aiosqlite

# Install frontend dependencies
cd frontend && npm install && cd ..

# Start both servers
./start.sh
```

Or start them separately:

```bash
# Terminal 1: Backend
uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend && npm run dev
```

Then open **http://localhost:5173**

---

## Demo

Click **"Load Demo Scenario"** on the home page to load the Password → Passkeys migration demo with:
- 5 realistic enterprise documents
- Pre-generated AI analysis (96% confidence)
- Complete audit trail

Switch between user roles (Admin, Approver, Reviewer, Viewer) using the dropdown in the header to see role-based access controls in action.

---

## HITL Framework - Core Layers

| Layer | What happens |
|-------|-------------|
| 1. User Request | Upload documents, logged to action log |
| 2. AI Draft | Bedrock analyzes, generates reasoning (never auto-finalized) |
| 3. Human Review | Approve / Edit / Reject with role-based permissions |
| 4. Action Log | Complete immutable audit trail of all actions |

---

## Key Features

- **Risk Levels**: Every AI action labeled LOW / MEDIUM / HIGH / BLOCKED
- **Role-Based Approval**: Viewer → Reviewer → Approver → Admin hierarchy
- **Guardrail Checks**: PII detection, unsupported claims, harmful content detection
- **Undo/Rollback**: Admin can revert any approved memory back to draft
- **Verified-Only Answers**: Mode 2 queries ONLY approved memories, never hallucinates

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, TailwindCSS, Framer Motion |
| Backend | FastAPI (Python) |
| AI | Amazon Bedrock (Claude) |
| Database | SQLite with FTS5 |

---

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /api/documents/upload | Upload files |
| POST | /api/memory/generate | AI analysis |
| PATCH | /api/memory/{id}/approve | Role-gated approval |
| PATCH | /api/memory/{id}/reject | Rejection |
| POST | /api/memory/{id}/rollback | Admin rollback |
| POST | /api/chat/{id} | HITL conversation |
| POST | /api/query | Mode 2 verified knowledge |
| GET | /api/audit/{id} | Action log |
| GET | /api/demo/load | Load demo data |

Full API docs at http://localhost:8000/docs

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| AWS_REGION | us-east-1 | AWS region for Bedrock |
| BEDROCK_MODEL_ID | anthropic.claude-sonnet-4-20250514 | Bedrock model |

The app works without AWS credentials using built-in demo fallbacks.
