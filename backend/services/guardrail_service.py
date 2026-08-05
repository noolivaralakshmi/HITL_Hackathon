"""Guardrail check service - local PII detection + AWS Bedrock Guardrails integration.

The AWS Bedrock Guardrail (ka5t8n9etx95) handles:
- PII ANONYMIZATION (replaces with placeholders, does NOT block)
- Credential BLOCKING (passwords, AWS keys, API keys)
- Content filtering (harmful, hate, violence)

This local service provides:
- Pre-upload PII scanning with redaction
- Confidence threshold checks
- Additional AI-based checks
"""
import re
import json
from backend.services.ai_service import run_guardrail_check


# ============================================================
# LOCAL PII PATTERNS - All set to WARNING or ANONYMIZE (never block)
# AWS Bedrock Guardrails handles blocking decisions
# ============================================================

PII_PATTERNS = {
    "ssn": {
        "pattern": r"\b\d{3}-\d{2}-\d{4}\b",
        "replacement": "###-##-####",
        "severity": "warning",
        "message": "Social Security Number detected and masked"
    },
    "credit_card": {
        "pattern": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
        "replacement": "####-####-####-####",
        "severity": "warning",
        "message": "Credit card number detected and masked"
    },
    "password_field": {
        "pattern": r"(?i)(password|passwd|pwd)\s*[:=]\s*\S+",
        "replacement": "[PASSWORD MASKED]",
        "severity": "critical",
        "message": "Password value detected and masked"
    },
    "password_quoted": {
        "pattern": r"(?i)(password|passwd|pwd)\s*[:=]\s*[\"'][^\"']+[\"']",
        "replacement": "[PASSWORD MASKED]",
        "severity": "critical",
        "message": "Password in quotes detected and masked"
    },
    "api_key": {
        "pattern": r"(?i)(api[_-]?key|apikey|api[_-]?secret|secret[_-]?key)\s*[:=]\s*\S+",
        "replacement": "[API KEY MASKED]",
        "severity": "critical",
        "message": "API key or secret detected and masked"
    },
    "aws_access_key": {
        "pattern": r"\b(AKIA[0-9A-Z]{16})\b",
        "replacement": "[AWS KEY MASKED]",
        "severity": "critical",
        "message": "AWS access key detected and masked"
    },
    "private_key": {
        "pattern": r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----",
        "replacement": "[PRIVATE KEY MASKED]",
        "severity": "critical",
        "message": "Private key detected and masked"
    },
    "email_personal": {
        "pattern": r"\b[A-Za-z0-9._%+-]+@(gmail|yahoo|hotmail|outlook|aol|icloud|protonmail)\.(com|net|org)\b",
        "replacement": "######@######",
        "severity": "warning",
        "message": "Personal email address detected and masked"
    },
    "phone_us": {
        "pattern": r"\b(\+1[\s-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b",
        "replacement": "(###) ###-####",
        "severity": "warning",
        "message": "Phone number detected and masked"
    },
    "ip_address": {
        "pattern": r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b",
        "replacement": "#.#.#.#",
        "severity": "warning",
        "message": "IP address detected and masked"
    },
    "drivers_license": {
        "pattern": r"(?i)(driver'?s?\s*license|DL)\s*#?\s*[:=]?\s*[A-Z0-9]{6,12}",
        "replacement": "[DRIVER LICENSE MASKED]",
        "severity": "warning",
        "message": "Driver's license number detected and masked"
    },
    "bank_account": {
        "pattern": r"(?i)(account\s*#?|acct\s*#?)\s*[:=]?\s*\d{8,17}",
        "replacement": "[BANK ACCOUNT MASKED]",
        "severity": "warning",
        "message": "Bank account number detected and masked"
    },
    "date_of_birth": {
        "pattern": r"(?i)(date\s*of\s*birth|DOB|born)\s*[:=]?\s*\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}",
        "replacement": "##/##/####",
        "severity": "warning",
        "message": "Date of birth detected and masked"
    },
}


def detect_pii(text: str) -> tuple:
    """Detect PII in text and return (flags, redacted_text).

    Returns:
        tuple: (list of flag dicts, masked text string)
    """
    flags = []
    redacted = text

    for pii_type, config in PII_PATTERNS.items():
        matches = re.findall(config["pattern"], text)
        if matches:
            flags.append({
                "type": "pii",
                "severity": config["severity"],
                "message": f"{config['message']} ({len(matches)} instance{'s' if len(matches) > 1 else ''})",
                "field": f"pii_{pii_type}",
                "pii_type": pii_type,
                "count": len(matches)
            })
            redacted = re.sub(config["pattern"], config["replacement"], redacted)

    return flags, redacted


def redact_reasoning(reasoning: dict) -> tuple:
    """Scan and mask PII from all fields in reasoning dict."""
    all_flags = []
    cleaned = {}

    for key, value in reasoning.items():
        if isinstance(value, str):
            flags, redacted = detect_pii(value)
            for f in flags:
                f["field"] = key
            all_flags.extend(flags)
            cleaned[key] = redacted

        elif isinstance(value, list):
            cleaned_list = []
            for item in value:
                if isinstance(item, str):
                    flags, redacted = detect_pii(item)
                    for f in flags:
                        f["field"] = key
                    all_flags.extend(flags)
                    cleaned_list.append(redacted)
                elif isinstance(item, dict):
                    cleaned_item = {}
                    for k, v in item.items():
                        if isinstance(v, str):
                            flags, redacted = detect_pii(v)
                            for f in flags:
                                f["field"] = f"{key}.{k}"
                            all_flags.extend(flags)
                            cleaned_item[k] = redacted
                        else:
                            cleaned_item[k] = v
                    cleaned_list.append(cleaned_item)
                else:
                    cleaned_list.append(item)
            cleaned[key] = cleaned_list
        else:
            cleaned[key] = value

    return all_flags, cleaned


def check_pii_in_documents(documents_text: str) -> tuple:
    """Check uploaded documents for PII before processing."""
    flags, redacted = detect_pii(documents_text)
    for f in flags:
        f["field"] = "uploaded_documents"
        f["message"] = f"[In uploaded documents] {f['message']}"
    return flags, redacted


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
    """Run all guardrail checks.

    Local checks: PII masking (warning level), confidence thresholds
    AWS Bedrock Guardrail: handles blocking decisions for credentials/harmful content
    """
    all_flags = []

    # 1. PII detection and masking in reasoning (warning only, never blocks)
    pii_flags, cleaned_reasoning = redact_reasoning(reasoning)
    all_flags.extend(pii_flags)

    # 2. Confidence threshold check
    all_flags.extend(check_confidence_threshold(confidence))

    # 3. AI-based guardrail check (unsupported claims, harmful content, hallucination)
    try:
        ai_check = run_guardrail_check(cleaned_reasoning, documents_text)
        if "flags" in ai_check:
            all_flags.extend(ai_check["flags"])
    except Exception:
        all_flags.append({
            "type": "system_error",
            "severity": "warning",
            "message": "AI guardrail check unavailable. Manual review recommended.",
            "field": None
        })

    # Derive safety status from actual flags
    has_pii = any(f.get("type") == "pii" for f in all_flags)
    has_critical = any(f.get("severity") == "critical" for f in all_flags)
    has_warning = any(f.get("severity") == "warning" for f in all_flags)

    # Block if critical non-PII issues found (credentials, hallucination, unsupported claims)
    # PII flags with critical severity (passwords, API keys) are masked locally,
    # but the content should still be blocked from proceeding unreviewed
    blocking_flags = [
        f for f in all_flags
        if f.get("severity") == "critical" and f.get("type") != "pii"
    ]
    # Credential PII (passwords, API keys, private keys) should also block
    credential_pii_flags = [
        f for f in all_flags
        if f.get("type") == "pii" and f.get("severity") == "critical"
    ]

    has_blocked = len(blocking_flags) > 0 or len(credential_pii_flags) > 0
    overall_safe = not has_critical

    # Determine risk adjustment based on flag severity
    risk_adjustment = None
    if has_blocked:
        risk_adjustment = "critical"
    elif has_critical:
        risk_adjustment = "high"
    elif has_warning:
        risk_adjustment = "medium"

    return {
        "flags": all_flags,
        "overall_safe": overall_safe,
        "should_block": has_blocked,
        "has_pii": has_pii,
        "risk_adjustment": risk_adjustment,
        "cleaned_reasoning": cleaned_reasoning if has_pii else None,
    }
