"""Guardrail check service - PII detection, redaction, harmful content, unsupported claims."""
import re
import json
from backend.services.ai_service import run_guardrail_check


# ============================================================
# PII PATTERNS - Comprehensive detection
# ============================================================

PII_PATTERNS = {
    "ssn": {
        "pattern": r"\b\d{3}-\d{2}-\d{4}\b",
        "replacement": "[SSN REDACTED]",
        "severity": "blocked",
        "message": "Social Security Number detected and redacted"
    },
    "ssn_no_dash": {
        "pattern": r"\b\d{9}\b(?!\d)",
        "replacement": "[SSN REDACTED]",
        "severity": "blocked",
        "message": "Possible SSN (9 consecutive digits) detected and redacted"
    },
    "credit_card": {
        "pattern": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
        "replacement": "[CREDIT CARD REDACTED]",
        "severity": "blocked",
        "message": "Credit card number detected and redacted"
    },
    "password_field": {
        "pattern": r"(?i)(password|passwd|pwd)\s*[:=]\s*\S+",
        "replacement": "[PASSWORD REDACTED]",
        "severity": "blocked",
        "message": "Password value detected and redacted"
    },
    "password_quoted": {
        "pattern": r"(?i)(password|passwd|pwd)\s*[:=]\s*[\"'][^\"']+[\"']",
        "replacement": "[PASSWORD REDACTED]",
        "severity": "blocked",
        "message": "Password in quotes detected and redacted"
    },
    "api_key": {
        "pattern": r"(?i)(api[_-]?key|apikey|api[_-]?secret|secret[_-]?key)\s*[:=]\s*\S+",
        "replacement": "[API KEY REDACTED]",
        "severity": "blocked",
        "message": "API key or secret detected and redacted"
    },
    "aws_access_key": {
        "pattern": r"\b(AKIA[0-9A-Z]{16})\b",
        "replacement": "[AWS KEY REDACTED]",
        "severity": "blocked",
        "message": "AWS access key detected and redacted"
    },
    "private_key": {
        "pattern": r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----",
        "replacement": "[PRIVATE KEY REDACTED]",
        "severity": "blocked",
        "message": "Private key detected and redacted"
    },
    "email_personal": {
        "pattern": r"\b[A-Za-z0-9._%+-]+@(gmail|yahoo|hotmail|outlook|aol|icloud|protonmail)\.(com|net|org)\b",
        "replacement": "[PERSONAL EMAIL REDACTED]",
        "severity": "critical",
        "message": "Personal email address detected and redacted"
    },
    "phone_us": {
        "pattern": r"\b(\+1[\s-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b",
        "replacement": "[PHONE REDACTED]",
        "severity": "warning",
        "message": "Phone number detected (verify if business or personal)"
    },
    "ip_address": {
        "pattern": r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b",
        "replacement": "[IP ADDRESS REDACTED]",
        "severity": "warning",
        "message": "IP address detected (may be sensitive infrastructure info)"
    },
    "drivers_license": {
        "pattern": r"(?i)(driver'?s?\s*license|DL)\s*#?\s*[:=]?\s*[A-Z0-9]{6,12}",
        "replacement": "[DRIVER LICENSE REDACTED]",
        "severity": "blocked",
        "message": "Driver's license number detected and redacted"
    },
    "bank_account": {
        "pattern": r"(?i)(account\s*#?|acct\s*#?)\s*[:=]?\s*\d{8,17}",
        "replacement": "[BANK ACCOUNT REDACTED]",
        "severity": "blocked",
        "message": "Bank account number detected and redacted"
    },
    "date_of_birth": {
        "pattern": r"(?i)(date\s*of\s*birth|DOB|born)\s*[:=]?\s*\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}",
        "replacement": "[DOB REDACTED]",
        "severity": "critical",
        "message": "Date of birth detected and redacted"
    },
}


def detect_pii(text: str) -> tuple:
    """Detect PII in text and return (flags, redacted_text).

    Returns:
        tuple: (list of flag dicts, redacted text string)
    """
    flags = []
    redacted = text

    for pii_type, config in PII_PATTERNS.items():
        matches = re.findall(config["pattern"], text)
        if matches:
            # Add flag
            flags.append({
                "type": "pii",
                "severity": config["severity"],
                "message": f"{config['message']} ({len(matches)} instance{'s' if len(matches) > 1 else ''})",
                "field": f"pii_{pii_type}",
                "pii_type": pii_type,
                "count": len(matches)
            })
            # Redact in text
            redacted = re.sub(config["pattern"], config["replacement"], redacted)

    return flags, redacted


def redact_reasoning(reasoning: dict) -> tuple:
    """Scan and redact PII from all fields in reasoning dict.

    Returns:
        tuple: (list of flags, cleaned reasoning dict)
    """
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
    """Check uploaded documents for PII before processing.

    Returns:
        tuple: (list of flags, redacted documents text)
    """
    flags, redacted = detect_pii(documents_text)
    # Mark these as document-level PII
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
    """Run all guardrail checks: PII detection + redaction, confidence, AI checks.

    This function:
    1. Scans for PII patterns and REDACTS them from the reasoning
    2. Checks confidence thresholds
    3. Runs AI-based guardrail checks (hallucination, unsupported claims)
    4. Returns flags, redacted reasoning, and overall safety assessment
    """
    all_flags = []

    # 1. PII detection and redaction in reasoning
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

    # Determine if content should be blocked
    has_blocked = any(f.get("severity") == "blocked" for f in all_flags)
    has_pii = any(f.get("type") == "pii" for f in all_flags)

    return {
        "flags": all_flags,
        "overall_safe": not has_blocked,
        "should_block": has_blocked,
        "has_pii": has_pii,
        "risk_adjustment": "BLOCKED" if has_blocked else None,
        "cleaned_reasoning": cleaned_reasoning if has_pii else None,
    }
