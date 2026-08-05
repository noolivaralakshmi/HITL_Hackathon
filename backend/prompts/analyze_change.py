"""Prompt for analyzing documents and detecting change type + reasoning."""


def build_analyze_prompt(documents: str) -> str:
    """Build the document analysis prompt with documents injected."""
    return f"""You are an enterprise decision analyst specializing in reconstructing organizational decision reasoning from fragmented evidence.

Analyze every uploaded document below. Your job is to:
1. Identify what type of organizational change occurred
2. Assess your confidence level
3. Reconstruct the complete decision reasoning

CHANGE TYPE DETECTION:
Identify the primary change type. Possible types:
- Authentication
- Infrastructure
- Cloud Migration
- Architecture
- Security Policy
- Product Feature
- Business Process
- Data Management
- Compliance
- Organizational Structure
- Other

REASONING STRUCTURE:
Create the most appropriate reasoning structure for the detected change type.
Do NOT use a fixed template. Choose sections dynamically based on what the evidence supports.

ALWAYS include these core sections:
- what_changed: Clear description of the change (before to after)
- business_objective: Why from a business perspective
- technical_objective: Why from a technical perspective
- alternatives_considered: Each with name and rejection reason
- risks_accepted: List of known risks that were accepted
- assumptions: List of assumptions made
- evidence: Which documents support which conclusions
- decision_makers: Who was involved (if found)
- timeline: When things happened (if found)

CRITICAL RULES:
- NEVER invent information. If something is not in the documents, mark it as "NOT FOUND"
- Always cite which document supports each claim
- Provide confidence as a percentage (0-100)
- List detection_reasons: specific signals that led to your change type classification

Return your analysis as valid JSON with this structure:
{{"change_type": "string", "confidence": number, "detection_reasons": ["reason1", "reason2"], "reasoning": {{"what_changed": "string", "business_objective": "string", "technical_objective": "string", "alternatives_considered": [{{"name": "string", "rejected_reason": "string"}}], "risks_accepted": ["string"], "assumptions": ["string"], "evidence": [{{"document": "string", "supports": "string"}}], "decision_makers": ["string or NOT FOUND"], "timeline": "string or NOT FOUND", "additional_context": "string"}}}}

DOCUMENTS TO ANALYZE:
{documents}
"""
