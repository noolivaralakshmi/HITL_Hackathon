# Change Impact Memory

**Human-in-the-Loop AI for Enterprise Decision Intelligence**

AI that reconstructs enterprise decision reasoning from fragmented evidence and preserves it as verified organizational knowledge — with human approval at every step.

> "AI proposes. Humans verify. Knowledge persists."

---

## Problem

Organizations lose decision context over time. When teams change, nobody remembers *why* a technology was chosen, what alternatives were rejected, or what risks were knowingly accepted. This institutional knowledge is scattered across emails, meeting notes, and people's heads — and eventually lost forever.

---

## Solution

Change Impact Memory is a Human-in-the-Loop AI system that:

1. **Reconstructs** decision reasoning from uploaded documents using Amazon Bedrock
2. **Enforces human validation** before anything becomes organizational truth
3. **Preserves** verified decisions as searchable knowledge with full evidence trails

---

## HITL Framework — 4 Core Layers

| Layer | What Happens |
|-------|-------------|
| 1. User Request | Contributor uploads relevant documents |
| 2. AI Draft | AI reconstructs reasoning — never auto-finalized |
| 3. Human Review | Reviewer approves, edits, or rejects |
| 4. Action Log | Immutable audit trail of every action |

---

## Key Features

### Risk Levels
Every AI-generated draft is labeled: **LOW** / **MEDIUM** / **HIGH** / **BLOCKED**
Based on AI confidence, missing information count, and guardrail flags.

### Role-Based Approval
- **Contributors** — Upload docs, review AI output, edit, send for approval
- **Reviewers** — Approve, reject, rollback verified knowledge

Contributors cannot approve their own work. Separation of duties enforced.

### AWS Bedrock Guardrails
- **PII Detection** — SSNs, credit cards, phone numbers auto-masked
- **Content Safety** — Harmful content blocked
- **Credential Protection** — AWS keys, passwords, private keys blocked at API level

### Undo / Rollback
- Reviewers can revert any verified memory back to draft
- Immediately removed from knowledge pool
- Full snapshot history preserved

### Duplicate Detection
- AI detects if similar verified memory already exists
- Option to merge new documents into existing memory
- Prevents duplicate knowledge entries

### Evidence Verification
- Original documents stored in AWS S3
- Evidence file names are clickable links (pre-signed URLs)
- Users can cross-verify AI claims against source documents

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, TailwindCSS, Framer Motion |
| Backend | FastAPI (Python) |
| AI Model | Amazon Bedrock — Nova 2 Lite (us.amazon.nova-2-lite-v1:0) |
| Guardrails | AWS Bedrock Guardrails (ID: ka5t8n9etx95) |
| Database | SQLite with FTS5 full-text search |
| Storage | AWS S3 (hitl-change-impact-memory-docs) |
| Auth | Role-based SSO-style login |

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                   FRONTEND (React + Vite)                  │
│   Login → Dashboard → Create Memory → Ask Knowledge       │
└─────────────────────────┬────────────────────────────────┘
                          │ REST API
┌─────────────────────────┴────────────────────────────────┐
│                  BACKEND (FastAPI / Python)                │
│   Routes → Services → Guardrails → Memory Management      │
└──────┬─────────────────┬──────────────────┬──────────────┘
       │                 │                  │
  ┌────┴────┐     ┌─────┴──────┐    ┌─────┴─────┐
  │ SQLite  │     │  Amazon    │    │  AWS S3    │
  │ + FTS5  │     │  Bedrock   │    │ (Documents)│
  └─────────┘     │  (Nova 2)  │    └───────────┘
                  └─────┬──────┘
                  ┌─────┴──────┐
                  │  Bedrock   │
                  │ Guardrails │
                  └────────────┘
```

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- AWS credentials configured (`~/.aws/credentials`)
- Bedrock model access enabled for `amazon.nova-2-lite-v1:0`

### Install & Run

```bash
# Backend dependencies
pip install fastapi uvicorn python-multipart pydantic boto3 python-docx PyPDF2 aiosqlite

# Frontend dependencies
cd frontend && npm install && cd ..

# Start both servers
./start.sh
```

Or start separately:

```bash
# Terminal 1: Backend
uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend && npm run dev
```

Open **http://localhost:5173**

---

## Demo Users

| Name | Email | Role |
|------|-------|------|
| Vara Lakshmi | vara.lakshmi@company.com | Contributor + Reviewer |
| Shanthi | shanthi@company.com | Contributor + Reviewer |
| Archana | archana@company.com | Contributor |
| Priyanka | priyanka@company.com | Contributor |

---

## Demo Scenario

### Cloud Migration (On-Prem → AWS)

Upload these 5 documents from the `demo/` folder:
1. `migration_proposal.txt` — Budget, timeline, current state
2. `architecture_review.txt` — ARB decision, alternatives rejected
3. `risk_assessment.txt` — 6 risks with owners and mitigations
4. `security_review.txt` — Network architecture, compliance
5. `executive_approval.txt` — CEO sign-off with conditions

### PII Guardrail Test

Upload `sensitive_document.txt` to see PII masking in action:
- SSNs → `###-##-####`
- Credit cards → `####-####-####-####`
- Passwords → `[PASSWORD MASKED]`
- AWS keys → blocked by Bedrock Guardrail

---

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /api/users/login | SSO-style login by email |
| GET | /api/users/{id}/dashboard | Role-based dashboard data |
| POST | /api/documents/upload | Upload files (S3 + text extraction) |
| POST | /api/memory/generate | AI analysis with Bedrock |
| PATCH | /api/memory/{id}/submit-for-review | Send to reviewer |
| PATCH | /api/memory/{id}/approve | Reviewer approves |
| PATCH | /api/memory/{id}/reject | Reviewer rejects |
| PATCH | /api/memory/{id}/edit | Edit reasoning |
| PATCH | /api/memory/{id}/discard | Contributor discards |
| POST | /api/memory/{id}/rollback | Reviewer rollback |
| POST | /api/memory/{id}/merge | Merge duplicate into existing |
| POST | /api/chat/{id} | HITL chat with AI |
| POST | /api/query | Query verified knowledge only |
| GET | /api/audit/{id} | Action log timeline |

Full API docs: http://localhost:8000/docs

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| AWS_REGION | us-east-1 | AWS region |
| BEDROCK_MODEL_ID | us.amazon.nova-2-lite-v1:0 | Bedrock model inference profile |
| BEDROCK_GUARDRAIL_ID | ka5t8n9etx95 | Bedrock Guardrail ID |
| BEDROCK_GUARDRAIL_VERSION | 5 | Guardrail version |
| S3_BUCKET | hitl-change-impact-memory-docs | S3 bucket for documents |

---

## Limitations

- AI confidence is self-assessed (human review compensates)
- Change type matching is broad (two "Authentication" changes treated as same)
- SQLite doesn't handle concurrent writes (use PostgreSQL in production)
- English documents only
- Notifications are simulated (no email/Slack integration)
- Bedrock Guardrail required tuning (5 versions) to avoid false positives on security docs

---

## Disclosure: Pre-existing Components & Third-Party Services

### Third-Party / Proprietary Services Used

| Component | Provider | Purpose |
|-----------|----------|---------|
| Amazon Bedrock (Nova 2 Lite) | AWS | AI model for document analysis and reasoning |
| AWS Bedrock Guardrails | AWS | PII anonymization, content safety, credential blocking |
| AWS S3 | AWS | Document storage with pre-signed download URLs |

### Open-Source Libraries

| Library | Purpose |
|---------|---------|
| React 18 | Frontend UI framework |
| Vite | Build tool and dev server |
| TailwindCSS | Utility-first CSS styling |
| Framer Motion | Page transitions and animations |
| FastAPI | Python backend framework |
| SQLite + FTS5 | Database with full-text search |
| Boto3 | AWS SDK for Python |
| Axios | HTTP client |
| Lucide React | Icon library |
| React Router | Client-side routing |
| React Dropzone | File upload drag-and-drop |
| PyPDF2 / python-docx | PDF and DOCX text extraction |

### Original Work (Built During Hackathon)

- HITL workflow engine (upload → AI draft → human review → approve/reject → verified knowledge)
- Role-based approval system (contributor vs contributor+reviewer separation)
- Document analysis prompts and decision reasoning reconstruction
- Risk assessment algorithm (confidence × missing info × guardrail flags)
- Duplicate detection and memory merge flow
- Reviewer assignment and send-for-approval workflow
- HITL chat interface (reviewer asks AI questions grounded in evidence)
- Action log / immutable audit trail
- Rollback system with snapshot preservation
- Local PII masking layer (regex-based, runs before Bedrock)
- AWS Bedrock Guardrail configuration and integration (5 iterations)
- S3 upload with pre-signed URL evidence linking
- Dashboard with role-based tabs and stats
- Login system with role-based access control

---

## Hackathon Judging Coverage

| Criteria | Weight | How We Address It |
|----------|--------|-------------------|
| Problem & Usefulness | 25% | Real enterprise knowledge loss problem |
| Working Prototype | 25% | End-to-end flow with real Bedrock AI calls |
| Data & AI Quality | 15% | AI reconstructs reasoning, detects change types, flags gaps |
| Trust & Safety | 15% | AWS Guardrails, PII masking, role separation, rollback, audit trail |
| Architecture Clarity | 10% | Clear 3-tier with guardrail layer |
| Demo & Storytelling | 10% | "AI proposes. Humans verify. Knowledge persists." |
