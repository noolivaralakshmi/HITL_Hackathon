"""Prompt for guardrail checks on AI output."""


def build_guardrail_prompt(reasoning: str, documents: str) -> str:
    """Build the guardrail check prompt."""
    return f"""You are a content safety and quality auditor for an enterprise AI system.

Analyze the following AI-generated reasoning record for potential issues:

REASONING RECORD:
{reasoning}

SOURCE DOCUMENTS:
{documents}

CHECK FOR:
1. PII (Personal Identifiable Information):
   - SSNs, credit card numbers, personal phone numbers
   - Home addresses, personal email addresses
   - Note: Business emails and names of decision-makers in a business context are ACCEPTABLE

2. Unsupported Claims:
   - Statements in the reasoning that are NOT supported by any source document
   - Conclusions that go beyond what the evidence shows
   - Invented details or fabricated specifics

3. Harmful Content:
   - Discriminatory reasoning or bias
   - Unsafe recommendations
   - Content that could cause harm if acted upon

4. Hallucination Detection:
   - Claims that directly CONTRADICT the source documents
   - Specific numbers, dates, or names that don't appear in sources

Return as valid JSON:
{{"flags": [{{"type": "pii or unsupported_claim or harmful_content or hallucination", "severity": "warning or critical or blocked", "message": "Description of the issue", "field": "which reasoning field has the issue"}}], "overall_safe": true, "summary": "Brief safety assessment"}}

RULES:
- Only flag genuine issues, not false positives
- Business context names/emails are acceptable
- "blocked" severity means content MUST NOT be approved
- "critical" severity means requires admin review
- "warning" severity means reviewer should address
"""
