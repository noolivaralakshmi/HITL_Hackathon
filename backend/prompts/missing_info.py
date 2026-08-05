"""Prompt for detecting missing information in reasoning records."""


def build_missing_info_prompt(reasoning: str, change_type: str) -> str:
    """Build the missing information detection prompt."""
    return f"""You are an enterprise decision completeness auditor.

Given the following reasoning record that was reconstructed from organizational documents, identify what critical information is MISSING.

REASONING RECORD:
{reasoning}

CHANGE TYPE: {change_type}

Analyze for these gaps:
1. Is there a rollback strategy documented?
2. Are all assumptions explicitly stated?
3. Are rejected alternatives documented with clear reasons?
4. Is there an approval authority identified?
5. Are risk owners assigned?
6. Is there a success criteria or measurement plan?
7. Are dependencies on other systems documented?
8. Is there a communication plan?
9. Are compliance requirements addressed?
10. Is there a timeline with milestones?

For each missing item, provide:
- A clear warning message (start with a warning symbol)
- Severity: "critical" (blocks safe approval) or "warning" (should be addressed)
- Category: what type of information is missing

Return as valid JSON:
{{"missing_items": [{{"message": "No rollback strategy found", "severity": "critical", "category": "risk_management"}}]}}

RULES:
- Only flag truly missing information
- Do NOT flag items that ARE present in the reasoning
- Be specific about what is missing
- Prioritize safety-critical gaps
"""
