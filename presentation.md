# Change Impact Memory
## Human-in-the-Loop AI for Enterprise Decision Intelligence

---

## Slide 1: The Problem

**Organizations lose decision context over time.**

- Why was a technology chosen?
- What alternatives were rejected and why?
- Who approved it? What risks were accepted?

Decision reasoning is scattered across emails, meeting notes, architecture docs, and people's heads.

When teams change, this knowledge is **permanently lost**.

---

## Slide 2: Our Solution

**Change Impact Memory** — An AI system that:

1. **Reconstructs** decision reasoning from fragmented documents
2. **Requires human validation** before anything becomes "truth"
3. **Preserves** verified decisions as searchable organizational knowledge

> "AI proposes. Humans verify. Knowledge persists."

---

## Slide 3: HITL Framework — 4 Core Layers

| Layer | What Happens | Example |
|-------|-------------|---------|
| 1. User Request | Contributor uploads documents | 5 docs about a cloud migration |
| 2. AI Draft | AI analyzes & generates reasoning (never auto-finalized) | Detects "Cloud Migration", 96% confidence |
| 3. Human Review | Reviewer approves, edits, or rejects | Reviewer validates assumptions & risks |
| 4. Action Log | Everything recorded immutably | Full audit trail of who did what |

**Key principle: AI never acts alone. Every output requires human approval.**

---

## Slide 4: Key HITL Features

### Risk Levels
Every AI action labeled: **LOW** / **MEDIUM** / **HIGH** / **BLOCKED**

### Role-Based Approval
- **Contributors** → Upload, edit, send for approval
- **Reviewers** → Approve, reject, rollback

### Guardrail Checks (AWS Bedrock Guardrails)
- PII Detection → SSN, credit cards masked automatically
- Content Safety → Hate/violence/harmful content blocked
- Credential Protection → AWS keys, passwords blocked

### Undo / Rollback
- Any verified memory can be reverted by a reviewer
- Removes from knowledge pool immediately
- Full snapshot history preserved

---

## Slide 5: Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                       │
│  Login → Dashboard → Create Memory → Ask Knowledge       │
└──────────────────────────┬──────────────────────────────┘
                           │ REST API
┌──────────────────────────┴──────────────────────────────┐
│                   BACKEND (FastAPI)                       │
│  Routes → Services → Guardrails → Memory Management      │
└───────┬──────────────────┬──────────────────┬───────────┘
        │                  │                  │
   ┌────┴────┐      ┌─────┴─────┐     ┌─────┴─────┐
   │ SQLite  │      │  Amazon   │     │   AWS S3   │
   │   DB    │      │  Bedrock  │     │  (Docs)    │
   │         │      │  (Nova)   │     │            │
   └─────────┘      └───────────┘     └────────────┘
                          │
                    ┌─────┴─────┐
                    │  Bedrock  │
                    │ Guardrails│
                    └───────────┘
```

---

## Slide 6: Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, TailwindCSS, Framer Motion |
| Backend | FastAPI (Python) |
| AI Model | Amazon Bedrock — Nova 2 Lite |
| Guardrails | AWS Bedrock Guardrails (PII, content safety) |
| Database | SQLite with FTS5 (full-text search) |
| Storage | AWS S3 (original documents with pre-signed URLs) |
| Auth | Role-based (SSO-style login) |

---

## Slide 7: Demo Flow

### Scenario: Password → Passkeys Authentication Migration

**Step 1:** Contributor uploads 5 documents
- Meeting notes, security review, architecture decision, risk assessment, approval email

**Step 2:** AI analyzes (Amazon Bedrock Nova)
- Detects: "Authentication" change type, 100% confidence
- Reconstructs full reasoning: what changed, why, alternatives rejected, risks accepted

**Step 3:** Guardrails run automatically
- PII check (IP addresses masked)
- Hallucination detection
- Risk level assigned: MEDIUM

**Step 4:** Contributor reviews & sends for approval
- Can edit reasoning, chat with AI for clarification
- Selects reviewer (Shanthi)

**Step 5:** Reviewer approves
- Memory becomes VERIFIED
- Now searchable in "Ask Knowledge"

**Step 6:** Anyone asks: "Why did we choose Passkeys?"
- Gets answer ONLY from verified memory
- With evidence links to original S3 documents

---

## Slide 8: Guardrails in Action

### What we protect against:

| Check | Action | Example |
|-------|--------|---------|
| SSN detected | Masked → ###-##-#### | Never stored or displayed |
| Credit card | Masked → ####-####-####-#### | Redacted in reasoning |
| AWS keys | **BLOCKED** | Document won't process |
| Private keys | **BLOCKED** | Stops immediately |
| Hallucination | Flagged for reviewer | "This claim not in source docs" |
| Low confidence | Risk → HIGH | Requires careful review |

**AWS Bedrock Guardrail ID:** ka5t8n9etx95
- Configured in AWS Console
- Attached to every Bedrock API call
- PII entities anonymized, credentials blocked

---

## Slide 9: Duplicate Detection & Knowledge Update

**Problem:** Multiple teams might document the same decision.

**Solution:**
- When AI detects same change type as existing VERIFIED memory → warns user
- User can "Update Existing Memory" with new documents
- Existing memory re-analyzed with combined evidence
- Goes back to DRAFT for re-review

**Result:** Single source of truth, always up to date.

---

## Slide 10: What Makes This Different

| Traditional Wiki | Change Impact Memory |
|-----------------|---------------------|
| Manual documentation | AI reconstructs from evidence |
| Anyone can edit anything | Role-based approval workflow |
| No verification | Human-verified before it's "truth" |
| Gets stale | Updated with new evidence |
| No audit trail | Every action logged |
| Search returns everything | Only verified knowledge returned |
| No guardrails | PII masked, harmful content blocked |

---

## Slide 11: Business Value

- **Knowledge Preservation** — Decisions survive team turnover
- **Faster Onboarding** — New team members query "why was X decided?"
- **Compliance Ready** — Immutable audit trail of every decision
- **Reduced Risk** — AI catches hallucinations before they become "truth"
- **Single Source of Truth** — No conflicting documents, one verified record

---

## Slide 12: Future Enhancements

- Slack/Teams integration (upload docs from chat)
- Automatic document ingestion from Confluence/SharePoint
- Multi-language support
- Decision dependency mapping (which decisions affect which)
- Expiry alerts ("This decision is 12 months old — still valid?")
- Integration with change management tools (ServiceNow, Jira)

---

## Slide 13: Live Demo

1. **Login** as Archana (contributor)
2. **Upload** cloud migration documents
3. **See** AI analysis with confidence & risk
4. **Review** guardrail checks
5. **Send** for approval to Shanthi
6. **Switch** to Shanthi (reviewer)
7. **Approve** the memory
8. **Ask** "Why did we migrate to cloud?"
9. **Click** evidence link → opens original doc from S3
10. **Rollback** demo (revert to draft)

---

## Slide 14: Team

| Name | Role |
|------|------|
| Vara Lakshmi | Reviewer |
| Shanthi | Reviewer |
| Archana | Contributor |
| Priyanka | Contributor |

---

## Thank You

**Change Impact Memory**
*AI proposes. Humans verify. Knowledge persists.*

GitHub: https://github.com/noolivaralakshmi/HITL_Hackathon
