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

### Groundedness Verification (NEW)
- Every AI claim is independently verified against source documents
- Direct quotes cited as evidence for each claim
- Groundedness score (e.g., 87% — 7 of 8 claims supported)
- Unsupported claims flagged as "critical gaps" for reviewer attention
- Re-verify on demand after edits via `/verify-groundedness` endpoint

### Semantic Search (NEW)
- Verified memories indexed using Amazon Titan Embeddings (1024-dim vectors)
- Natural language queries find relevant memories by meaning, not keywords
- Top-5 semantic results passed to AI for answer synthesis
- Scales to thousands of memories (replaces full-prompt-stuffing approach)
- Bootstrap index via `POST /api/query/reindex`

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, TailwindCSS, Framer Motion |
| Backend | FastAPI (Python) |
| AI Model | Amazon Bedrock — Nova 2 Lite (us.amazon.nova-2-lite-v1:0) |
| Embeddings | Amazon Bedrock — Titan Embeddings v2 (1024-dim vectors) |
| Guardrails | AWS Bedrock Guardrails (ID: ka5t8n9etx95, v5) |
| Database | SQLite with FTS5 full-text search + vector embeddings |
| Storage | AWS S3 (hitl-change-impact-memory-docs) |
| Testing | pytest (81 tests) |
| Auth | Role-based SSO-style login |

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                   FRONTEND (React + Vite)                  │
│   Login → Dashboard → Create Memory → Ask Knowledge       │
│   + Groundedness Panel + Guardrail Alerts                 │
└─────────────────────────┬────────────────────────────────┘
                          │ REST API
┌─────────────────────────┴────────────────────────────────┐
│                  BACKEND (FastAPI / Python)                │
│   Routes → Services → Guardrails → Memory Management      │
│   + Groundedness Verification + Embedding Service         │
└──────┬─────────────────┬──────────────────┬──────────────┘
       │                 │                  │
  ┌────┴────┐     ┌─────┴──────┐    ┌─────┴─────┐
  │ SQLite  │     │  Amazon    │    │  AWS S3    │
  │ + FTS5  │     │  Bedrock   │    │ (Documents)│
  │ + Vector│     │  ├ Nova 2  │    └───────────┘
  │   Index │     │  ├ Titan   │
  └─────────┘     │  │ Embed   │
                  │  └ Guard-  │
                  │    rails   │
                  └────────────┘
```

---

## Deployment Model

### Architecture Overview

The system is designed for a single-region AWS deployment with the following topology:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        AWS Region (us-east-1)                        │
│                                                                     │
│  ┌─────────────┐    ┌──────────────────┐    ┌───────────────────┐  │
│  │  Frontend   │    │  Backend (EC2 /  │    │  Amazon Bedrock   │  │
│  │  (S3 +     │───▶│  ECS Fargate /   │───▶│  ├─ Nova 2 Lite   │  │
│  │  CloudFront)│    │  Lambda)         │    │  ├─ Guardrails    │  │
│  └─────────────┘    └────────┬─────────┘    │  └─ Titan Embed   │  │
│                              │              └───────────────────┘  │
│                    ┌─────────┼─────────┐                           │
│                    │         │         │                           │
│              ┌─────┴──┐ ┌───┴────┐ ┌──┴──────┐                   │
│              │ RDS /  │ │  S3    │ │CloudWatch│                   │
│              │ Aurora │ │(Docs)  │ │ (Logs)   │                   │
│              └────────┘ └────────┘ └──────────┘                   │
└─────────────────────────────────────────────────────────────────────┘
```

### Deployment Options

| Environment | Compute | Database | Cost Profile |
|-------------|---------|----------|-------------|
| Development | Local uvicorn | SQLite | Free (Bedrock pay-per-use) |
| Staging | ECS Fargate (1 task) | RDS PostgreSQL (db.t3.micro) | ~$50/month + Bedrock |
| Production | ECS Fargate (2+ tasks, ALB) | Aurora PostgreSQL Serverless v2 | ~$200/month + Bedrock |

### Production Deployment Checklist

1. **Compute**: Deploy backend as Docker container on ECS Fargate behind an ALB
2. **Database**: Replace SQLite with Aurora PostgreSQL Serverless v2 (handles concurrent writes)
3. **Frontend**: Build static assets (`npm run build`), host on S3 + CloudFront
4. **Secrets**: Store AWS credentials and config in AWS Secrets Manager, inject via ECS task role
5. **Networking**: VPC with private subnets for backend/DB, public subnet for ALB
6. **IAM**: Task execution role with least-privilege access to Bedrock, S3, and Secrets Manager
7. **Monitoring**: CloudWatch logs + X-Ray tracing for Bedrock call latency
8. **Scaling**: Auto-scale ECS tasks based on CPU/memory; Bedrock handles scaling automatically

### IAM Permissions Required

```json
{
  "Effect": "Allow",
  "Action": [
    "bedrock:InvokeModel",
    "bedrock:ApplyGuardrail",
    "s3:PutObject",
    "s3:GetObject",
    "s3:DeleteObject"
  ],
  "Resource": [
    "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-2-lite-v1:0",
    "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v2:0",
    "arn:aws:bedrock:us-east-1:*:guardrail/ka5t8n9etx95",
    "arn:aws:s3:::hitl-change-impact-memory-docs/*"
  ]
}
```

---

## AWS Bedrock Guardrail Configuration

### Guardrail Details

| Property | Value |
|----------|-------|
| Guardrail ID | `ka5t8n9etx95` |
| Version | 5 (iterated 5 times to reduce false positives) |
| Region | us-east-1 |
| Attached To | Every `bedrock:InvokeModel` call via Converse API |

### Guardrail Policies Configured

| Policy | Action | Scope |
|--------|--------|-------|
| PII Anonymization | ANONYMIZE (replace with placeholders) | SSN, credit card, email, phone, DOB, address |
| Credential Detection | BLOCK | Passwords, AWS access keys, API secrets, private keys |
| Content Filtering | BLOCK | Hate speech, violence, sexual content, insults |
| Denied Topics | BLOCK | Instructions to bypass safety, jailbreak attempts |

### How Guardrails Attach to Model Calls

```python
# Every Bedrock call includes guardrailConfig:
response = client.converse(
    modelId="us.amazon.nova-2-lite-v1:0",
    messages=[...],
    guardrailConfig={
        "guardrailIdentifier": "ka5t8n9etx95",
        "guardrailVersion": "5",
        "trace": "enabled",  # Captures which policy triggered
    },
)
```

### Guardrail Behavior

1. **PII Anonymization** — Bedrock replaces detected PII with `{TYPE}` placeholders (e.g., `{US_SOCIAL_SECURITY_NUMBER}`). Our backend converts these to user-friendly masks (`###-##-####`).

2. **Credential Blocking** — If credentials are detected in the input or output, Bedrock returns `stopReason: "guardrail_intervened"`. The backend raises `GuardrailBlockedException` and the memory is marked as BLOCKED.

3. **Content Filtering** — Same blocking behavior for harmful content. The blocked message from the guardrail trace is surfaced to the user.

### Multi-Layer PII Protection

```
Document Upload
     │
     ▼
┌─────────────────────────┐
│ Layer 1: Local Masking   │  Regex-based PII detection (13 patterns)
│ (guardrail_service.py)   │  Redacts BEFORE sending to Bedrock
└───────────┬─────────────┘
            │ (pre-masked text)
            ▼
┌─────────────────────────┐
│ Layer 2: Bedrock Guard   │  AWS-managed detection with ML models
│ (Converse API guardrail) │  ANONYMIZE for PII, BLOCK for credentials
└───────────┬─────────────┘
            │ (anonymized output)
            ▼
┌─────────────────────────┐
│ Layer 3: Display Masking │  Convert {PLACEHOLDER} → user-friendly masks
│ (replace_pii_placeholders)│ Render as ###-##-#### in the UI
└─────────────────────────┘
```

### Tuning History (5 Versions)

| Version | Change | Reason |
|---------|--------|--------|
| 1 | Initial setup with all filters on BLOCK | Blocked legitimate security documents |
| 2 | Changed PII to ANONYMIZE instead of BLOCK | Security reviews discuss PII by category, not value |
| 3 | Added exception for business context names | Decision-maker names are legitimate content |
| 4 | Tuned content filter sensitivity from HIGH to MEDIUM | Risk assessment docs flagged as "harmful" |
| 5 | Final — credentials BLOCK, PII ANONYMIZE, content MEDIUM | Balanced: blocks real threats, passes legitimate docs |

---

## LLM Reasoning & Decision Baselines

### Model Selection

| Model | Use Case | Why |
|-------|----------|-----|
| Amazon Nova 2 Lite (`us.amazon.nova-2-lite-v1:0`) | Document analysis, reasoning, chat | Fast inference, good structured output, low cost |
| Amazon Titan Embeddings v2 (`amazon.titan-embed-text-v2:0`) | Semantic search | 1024-dim vectors, normalized, optimized for retrieval |

### Inference Parameters

```python
{
    "maxTokens": 4096,       # Sufficient for full reasoning structure
    "temperature": 0.1,      # Low temperature for deterministic, factual output
}
```

**Why temperature 0.1**: The system reconstructs factual reasoning from documents — it must not be creative or speculative. Low temperature ensures consistent, reproducible outputs across multiple runs of the same input.

### Reasoning Baselines — What the AI Produces

For every set of uploaded documents, the AI generates a structured reasoning record:

| Field | Description | Verification Method |
|-------|-------------|-------------------|
| `what_changed` | Before → After description | Groundedness check against source |
| `business_objective` | Why from business perspective | Citation to source document required |
| `technical_objective` | Why from technical perspective | Citation to source document required |
| `alternatives_considered` | Rejected options with reasons | Each must cite a source |
| `risks_accepted` | Known risks acknowledged | Must appear in source documents |
| `assumptions` | Stated assumptions | Flagged if unsupported |
| `evidence` | Document → claim mapping | Used as ground truth for verification |
| `decision_makers` | Who was involved | Extracted from document signatures/names |
| `timeline` | When things happened | Dates must match source documents |
| `confidence` | 0-100% self-assessment | Cross-validated by risk service |

### Groundedness Verification Pipeline

The AI's reasoning is independently verified against source documents:

```
AI Reasoning Record          Source Documents
       │                           │
       ▼                           ▼
┌──────────────────────────────────────────┐
│  Groundedness Verification (Separate Call) │
│  For each claim:                          │
│    1. Find supporting quote in source     │
│    2. Classify: SUPPORTED / PARTIAL / UNSUPPORTED │
│    3. Attach citation (doc name + quote)  │
└────────────────────┬─────────────────────┘
                     ▼
┌──────────────────────────────────────────┐
│  Groundedness Score                       │
│  e.g., "7/8 claims supported (87%)"      │
│  Critical gaps surfaced to reviewer       │
└──────────────────────────────────────────┘
```

### Risk Assessment Algorithm

```
if guardrail.should_block → BLOCKED (cannot proceed)
if any critical flag → HIGH
if confidence < 50 OR missing_info > 5 → HIGH
if confidence < 75 OR missing_info > 2 → MEDIUM
if any warning flag → MEDIUM
else → LOW
```

### Semantic Search for Knowledge Retrieval

When querying verified memory (Mode 2), the system uses vector similarity:

1. User question → embedded via Titan Embeddings (1024-dim)
2. Cosine similarity against all stored memory embeddings
3. Top-5 results above 0.3 similarity threshold returned
4. Only those relevant memories passed to AI for answer synthesis
5. Falls back to full-scan if no embeddings exist yet

This replaces the original approach of stuffing all memories into a single prompt, which doesn't scale beyond ~10 verified memories.

---

## Testing

Run the test suite:

```bash
pytest backend/tests/ -v
```

**81 tests** covering:
- `test_guardrail_service.py` — PII detection (13 patterns), confidence thresholds, full guardrail pipeline, flag-to-block logic
- `test_risk_service.py` — Risk assessment boundaries, role-based approval permissions
- `test_embedding_service.py` — Cosine similarity math, memory text construction
- `test_memory_service.py` — CRUD operations, approval flow, DB serialization
- `test_query_service.py` — Semantic retrieval, fallback query, memory formatting

---

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
| POST | /api/memory/{id}/verify-groundedness | Re-verify citations against source |
| POST | /api/chat/{id} | HITL chat with AI |
| POST | /api/query | Query verified knowledge (semantic search) |
| POST | /api/query/reindex | Rebuild vector index for all verified memories |
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

- ~~AI confidence is self-assessed~~ → Now verified via groundedness check against source docs
- ~~No way to search memories at scale~~ → Semantic search with Titan Embeddings added
- Change type matching is broad (two "Authentication" changes treated as same)
- SQLite doesn't handle concurrent writes (use PostgreSQL in production)
- English documents only
- Notifications are simulated (no email/Slack integration)
- Bedrock Guardrail required tuning (5 versions) to avoid false positives on security docs
- Groundedness verification uses same provider (Bedrock) — for production, consider a second model or retrieval-augmented verification
- Tribal knowledge (undocumented facts) requires contributor attestation workflow not yet implemented
- Vector store is in SQLite (sufficient for <10K memories); for production scale, consider OpenSearch or pgvector

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
- Groundedness verification with citations (independent claim-by-claim verification)
- Semantic search using Titan Embeddings + cosine similarity for memory retrieval
- Automated test suite (81 tests covering guardrails, risk, memory, embeddings, queries)

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
