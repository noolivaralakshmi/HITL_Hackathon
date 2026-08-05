"""Prompt for groundedness verification - checks AI reasoning against source documents with citations."""


def build_groundedness_prompt(reasoning: str, documents: str) -> str:
    """Build the groundedness verification prompt.

    This prompt asks the model to verify each key claim in the reasoning
    against the source documents, providing direct quotes as citations.
    """
    return f"""You are a verification auditor. Your job is to check whether each claim in an AI-generated reasoning record is GROUNDED in the source documents.

REASONING RECORD TO VERIFY:
{reasoning}

SOURCE DOCUMENTS:
{documents}

TASK:
For each key claim in the reasoning record, determine if it is supported by a specific passage in the source documents.

For each claim, provide:
1. The claim text (summarized)
2. Whether it is SUPPORTED, PARTIALLY_SUPPORTED, or UNSUPPORTED
3. If supported: the exact quote from the source document (max 50 words) and which document it comes from
4. If unsupported: explain what is missing

GROUNDING RULES:
- A claim is SUPPORTED if a direct quote from a source document clearly states or strongly implies it
- A claim is PARTIALLY_SUPPORTED if the source provides some evidence but the reasoning extends beyond what is stated
- A claim is UNSUPPORTED if no source document contains evidence for the claim
- Do NOT count the reasoning record itself as a source
- Specific numbers, dates, names, and statistics MUST have a direct source quote
- General conclusions drawn from multiple pieces of evidence can be PARTIALLY_SUPPORTED

Return as valid JSON:
{{
  "claims": [
    {{
      "claim": "Brief description of the claim",
      "field": "Which reasoning field this comes from (e.g., what_changed, business_objective, risks_accepted)",
      "status": "SUPPORTED or PARTIALLY_SUPPORTED or UNSUPPORTED",
      "source_document": "Filename of supporting document or null",
      "source_quote": "Exact quote from document (max 50 words) or null",
      "explanation": "Why this status was assigned"
    }}
  ],
  "groundedness_score": {{
    "supported": 0,
    "partially_supported": 0,
    "unsupported": 0,
    "total": 0,
    "percentage": 0
  }},
  "summary": "Brief overall assessment of how well-grounded this reasoning is",
  "critical_gaps": ["List of the most concerning unsupported claims that reviewers should focus on"]
}}

IMPORTANT:
- Be thorough: check ALL major claims, not just a few
- Be precise: quote exactly from the source, don't paraphrase
- Be fair: if a claim is a reasonable inference from multiple sources, mark it PARTIALLY_SUPPORTED, not UNSUPPORTED
- Focus especially on: specific numbers, dates, names, decisions, and risk statements
"""
