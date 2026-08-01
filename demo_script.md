# 7-Minute Demo Script — Change Impact Memory

---

## Minute 0-1: The Problem (talking, no screen)

> "Imagine a new engineer joins your team and asks: 'Why did we migrate to AWS instead of staying on-prem?' The architect who made that decision left 6 months ago. The reasoning is buried in scattered emails, meeting notes, and someone's head. That knowledge is gone forever."
>
> "Change Impact Memory solves this. AI reconstructs the reasoning. Humans verify it. Knowledge persists."

---

## Minute 1-2: Login & Dashboard (show screen)

1. Open http://localhost:5173
2. **Login as Archana (contributor)** — archana@company.com
3. Show the empty dashboard — "This is a contributor's view. They can create memory and ask knowledge."
4. Point out the stats cards — "Zero contributions, zero verified knowledge. Let's fix that."

---

## Minute 2-4: Create Memory (main demo)

5. Click **Create Memory**
6. **Drag & drop 5 migration files** (migration_proposal.txt, architecture_review.txt, risk_assessment.txt, security_review.txt, executive_approval.txt)
7. Click **Generate Memory** — wait for AI
8. **Talk while loading:** "The AI is analyzing all 5 documents using Amazon Bedrock Nova to reconstruct the full decision reasoning."
9. **Show results:**
   - "It detected Cloud Migration at high confidence"
   - "Found alternatives that were rejected — Azure, GCP, Hybrid, Colocation — with specific reasons why"
   - "Identified risks that were accepted"
   - "Flagged missing information — things the docs don't cover"
10. **Show guardrails:** "Notice the IP addresses were automatically masked. Our AWS Bedrock Guardrail detected them as sensitive infrastructure info."
11. **Show risk level:** "It's Medium Risk because there are gaps in the documentation"
12. Click **Send for Approval** → select Shanthi
13. "The contributor can't approve their own work. Separation of duties."

---

## Minute 4-5: Reviewer Approves

14. Click **Sign Out**
15. **Login as Shanthi (reviewer)** — shanthi@company.com
16. Show dashboard → **Pending Review tab** has 1 item
17. Click on the Cloud Migration memory
18. **Quick chat:** Type "What risks were accepted?" → show AI answers from evidence only
19. Click **Approve**
20. "Now this is verified organizational knowledge. It's searchable by everyone."

---

## Minute 5-6: Ask Knowledge (the payoff)

21. Click **Ask Knowledge** in nav
22. Ask: **"Why did we choose AWS over Azure?"**
23. Show the answer — decision, reason, rejected alternatives, evidence links
24. **Click an evidence link** → "This opens the original document from S3. Anyone can cross-verify."
25. Ask: **"What is our database backup strategy?"**
26. Show: "No verified memory found" → **"The system refuses to guess. It only answers from verified knowledge."**

---

## Minute 6-7: Trust & Safety (differentiator)

27. Go back to **Create Memory**
28. Upload **sensitive_document.txt**
29. Click Generate → show PII masking:
   - "SSNs replaced with hashes"
   - "Passwords masked"
   - "Credit cards redacted"
   - "None of this data was ever stored"
30. **Final statement:**

> "To summarize: AI reconstructs reasoning from documents. Humans verify before it becomes truth. Guardrails protect sensitive data. Everything is auditable. And the system refuses to answer what it doesn't know."
>
> "AI proposes. Humans verify. Knowledge persists."

---

## If Judges Ask Questions

**"What if the AI is wrong?"**
→ "That's why human review exists. The AI can't publish anything alone."

**"What about rollback?"**
→ Show the Rollback button. "Reviewers can revert any approved memory instantly."

**"How do you prevent duplicates?"**
→ "If someone uploads similar docs, the system warns that verified knowledge already exists."

**"What model do you use?"**
→ "Amazon Bedrock Nova 2 Lite via the Converse API, with AWS Bedrock Guardrails attached to every call."

**"What happens with PII?"**
→ "Two layers: local regex masking before Bedrock sees it, plus AWS Bedrock Guardrails for anonymization and blocking."

**"Can you undo an approval?"**
→ "Yes, rollback. It reverts to draft, removes from knowledge pool, and logs who did it and why."

**"How is risk calculated?"**
→ "Confidence score × missing information count × guardrail flags. Low confidence or many gaps = high risk."

---

## Pre-Demo Checklist

- [ ] Database is clean (no existing memories)
- [ ] Backend running: http://localhost:8000/api/health returns {"status":"healthy"}
- [ ] Frontend running: http://localhost:5173 shows login page
- [ ] 5 migration files ready to drag-and-drop
- [ ] sensitive_document.txt ready for PII demo
- [ ] Browser localStorage cleared (shows login page)
- [ ] AWS credentials valid (no clock skew)
