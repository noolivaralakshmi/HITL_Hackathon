"""Guardrail check service - PII, harmful content, unsupported claims."""
import re
import json
from backend.services.ai_service import run_guardrail_check


# Simple pattern-based PII detection (runs before AI check)
PII_PATTERNS = {
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "credit_card": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
    "phone_personal": r"\b\(\d{3}\)\s?\d{3}-\d{4}\b",
}


def check_pii_patterns(text: str) -> list:
    """Quick pattern-based PII detection."""
    flags = []
    for pii_type, pattern in PII_PATTERNS.items():
        matches = re.findall(pattern, text)
        if matches:
            flags.append({
                "type": "pii",
                "severity": "critical",
                "message": f"Potential PII detected: {pii_type} pattern found",
                "field": "reasoning"
            })
    return flags


def check_confidence_threshold(confidence: float) -> list:
    """Check if confidence is below safe threshold."""
    flags = []
    if confidence < 40:
        flags.append({
            "type": "low_confidence",
            "severity": "critical",
            "message": f"AI confidence is very low ({confidence}%). High risk of inaccurate reasoning.",
            "field": "confidence"
        })
    elif confidence < 60:
        flags.append({
            "type": "low_confidence",
            "severity": "warning",
            "message": f"AI confidence is moderate ({confidence}%). Review carefully.",
            "field": "confidence"
        })
    return flags


def run_guardrails(reasoning: dict, documents_text: str, confidence: float) -> dict:
    """Run all guardrail checks and return flags with overall assessment."""
    all_flags = []

    # 1. Pattern-based PII check
    reasoning_text = json.dumps(reasoning)
    all_flags.extend(check_pii_patterns(reasoning_text))

    # 2. Confidence threshold check
    all_flags.extend(check_confidence_threshold(confidence))

    # 3. AI-based guardrail check (unsupported claims, harmful content, hallucination)
    try:
        ai_check = run_guardrail_check(reasoning, documents_text)
        if "flags" in ai_check:
            all_flags.extend(ai_check["flags"])
    except Exception:
        # If AI check fails, add a warning
        all_flags.append({
            "type": "system_error",
            "severity": "warning",
            "message": "AI guardrail check unavailable. Manual review recommended.",
            "field": None
        })

    # Determine if content should be blocked
    has_blocked = any(f.get("severity") == "blocked" for f in all_flags)

    return {
        "flags": all_flags,
        "overall_safe": not has_blocked,
        "should_block": has_blocked,
        "risk_adjustment": "BLOCKED" if has_blocked else None
    }
