# Change Impact Memory
## Human-in-the-Loop AI for Enterprise Decision Intelligence

---

## The Problem

**Organizations lose decision context over time.**

- Why was a technology chosen over alternatives?
- What risks were knowingly accepted?
- Who approved it and based on what evidence?

Decision reasoning lives in scattered emails, meeting notes, Slack threads, and people's heads.

When teams rotate, this institutional knowledge is **permanently lost**.

> "We know WHAT was decided. We forgot WHY."

---

## Our Solution

**Change Impact Memory** — An AI-powered system that:

1. **Reconstructs** decision reasoning from fragmented documents
2. **Enforces human validation** before anything becomes organizational truth
3. **Preserves** verified decisions as searchable knowledge

The AI does the heavy lifting. Humans hold the pen.

> "AI proposes. Humans verify. Knowledge persists."

---

## How It Works — The HITL Framework

| Layer | What Happens |
|-------|-------------|
| 1. User Request | Upload relevant documents (meeting notes, reviews, emails) |
| 2. AI Draft | AI reconstructs reasoning — never auto-finalized |
| 3. Human Review | Reviewer approves, edits, or rejects with full context |
| 4. Action Log | Immutable audit trail of every decision |

**Core principle:** AI never acts autonomously. Every output requires explicit human approval before it enters the knowledge base.

---

## Key Safety Features

### Risk Labels
Every AI-generated draft is labeled: **LOW** / **MEDIUM** / **HIGH** / **BLOCKED**

Based on: AI confidence × missing information × guardrail flags

### Role-Based Approval
- **Contributors** → Upload docs, review AI output, send for approval
- **Reviewers** → Approve, reject, or rollback verified knowledge

Contributors cannot approve their own work. Separation of duties enforced.

### AWS Bedrock Guardrails
- **PII Detection** → SSNs, credit cards auto-masked (never stored)
- **Content Safety** → Harmful/violent content blocked
- **Credential Protection** → AWS keys, passwords, API secrets blocked at API level

### Undo / Rollback
- Reviewers can revert any verified memory
- Immediately removed from knowledge pool
- Full snapshot history preserved for audit

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

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | React 18, TailwindCSS, Framer Motion | Fast, responsive, modern UX |
| Backend | FastAPI (Python) | Async, auto-docs, type-safe |
| AI Model | Amazon Bedrock — Nova 2 Lite | Low latency, enterprise-grade |
| Guardrails | AWS Bedrock Guardrails | PII anonymization, content safety |
| Database | SQLite + FTS5 | Zero-config, portable, full-text search |
| Storage | AWS S3 | Pre-signed URLs for document access |
| Auth | Role-based SSO-style | Contributor vs Reviewer separation |

---

## Guardrails — Defense in Depth

**Two layers of protection:**

### Layer 1: Local (Application Code)
- Regex-based PII scanning on document upload
- Masks before content reaches AI
- IP addresses → `#.#.#.#`, SSNs → `###-##-####`

### Layer 2: AWS Bedrock Guardrails (Cloud)
- Configured in AWS Console — no code changes needed to update rules
- PII entities: SSN, credit card, bank account, passport → **anonymized**
- Credentials: AWS keys, private keys → **blocked entirely**
- Content: hate, violence, sexual, misconduct → **blocked**

| Detected | Action | Displayed As |
|----------|--------|-------------|
| SSN | Anonymized | ###-##-#### |
| Credit card | Anonymized | ####-####-####-#### |
| IP address | Masked locally | #.#.#.# |
| AWS access key | BLOCKED | Request fails |
| Harmful content | BLOCKED | Request fails |

---

## Duplicate Detection & Knowledge Updates

**Problem:** Different teams may document the same decision separately.

**Solution:**
- AI detects matching change type against existing verified memories
- Warns: "This knowledge already exists"
- Option to **merge new documents** into existing memory
- Re-analyzes with combined evidence
- Goes back for re-review

**Result:** One source of truth. Always current. Never duplicated.

---

## Demo Scenario: Enterprise Cloud Migration

**Documents uploaded:**
1. Migration proposal (budget, timeline)
2. Architecture review (alternatives rejected)
3. Risk assessment (5 risks identified)
4. Security review (network architecture)
5. Executive approval email

**AI produces:**
- Change type: Cloud Migration (100% confidence)
- Full reasoning: what changed, why, alternatives considered, risks accepted
- Evidence citations linked to original documents
- Missing information flagged (4 gaps)

**Human review:**
- Reviewer validates reasoning
- Chats with AI for clarification
- Approves → enters verified knowledge

**Anyone can now ask:**
> "Why did we migrate from on-prem to cloud?"
> → Answer with evidence links to original documents

---

## What Makes This Different

| Traditional Approach | Change Impact Memory |
|---------------------|---------------------|
| Manual documentation | AI reconstructs from evidence |
| Anyone edits anything | Role-based approval workflow |
| No verification | Human-verified truth only |
| Gets stale over time | Updated with new evidence |
| No audit trail | Every action immutably logged |
| Search returns everything | Only verified knowledge returned |
| No content safety | PII masked, credentials blocked |
| Single point of failure | Rollback with snapshot restore |

---

## Business Value

| Benefit | Impact |
|---------|--------|
| **Knowledge Preservation** | Decisions survive team turnover |
| **Faster Onboarding** | New members query "why was X decided?" |
| **Compliance** | Immutable audit trail for every decision |
| **Reduced Risk** | AI catches unsupported claims before approval |
| **Single Source of Truth** | No conflicting versions |
| **Cross-Verification** | Evidence links to original S3 documents |

---

## Live Demo

1. Login as a **contributor**
2. Upload cloud migration documents (5 files)
3. Watch AI analyze → confidence score, risk level
4. See guardrail checks (PII masking, hallucination flags)
5. Review reasoning record
6. Send for approval → select reviewer
7. Switch to **reviewer** account
8. See pending review on dashboard
9. Approve the memory
10. Ask: "Why did we migrate to cloud?" → verified answer with evidence links
11. Demonstrate rollback capability

---

## Future Roadmap

- Slack/Teams integration — upload docs from chat
- Auto-ingestion from Confluence, SharePoint, Google Drive
- Decision dependency mapping — "which decisions affect which"
- Expiry alerts — "This decision is 12 months old, still valid?"
- Multi-language document support
- Integration with change management (ServiceNow, Jira)
- RAG-based retrieval for larger knowledge bases

---

## Summary

**Change Impact Memory** solves the enterprise knowledge loss problem by combining:

- **Generative AI** (Amazon Bedrock) to reconstruct reasoning
- **Human-in-the-Loop** to ensure accuracy and accountability
- **AWS Guardrails** to protect sensitive information
- **Role-based workflow** to enforce separation of duties
- **Immutable audit trail** for compliance and trust

> *The AI does the heavy lifting. Humans hold the pen. Knowledge persists.*

---

## Q&A

GitHub: github.com/noolivaralakshmi/HITL_Hackathon
