"""Risk assessment and labeling service."""
from backend.config import ROLE_HIERARCHY


def assess_risk(confidence: float, missing_info_count: int, guardrail_result: dict) -> str:
    """Assess risk level based on confidence, missing info, and guardrails.

    Returns: LOW, MEDIUM, HIGH, or BLOCKED
    """
    # Guardrail-detected blocked content takes priority
    if guardrail_result.get("should_block"):
        return "BLOCKED"

    # Critical guardrail flags → HIGH risk
    critical_flags = [f for f in guardrail_result.get("flags", []) if f.get("severity") == "critical"]
    if critical_flags:
        return "HIGH"

    # Low confidence or many missing items → HIGH risk
    if confidence < 50 or missing_info_count > 5:
        return "HIGH"

    # Moderate confidence or some missing items → MEDIUM risk
    if confidence < 75 or missing_info_count > 2:
        return "MEDIUM"

    # Warning-level guardrail flags → MEDIUM
    warning_flags = [f for f in guardrail_result.get("flags", []) if f.get("severity") == "warning"]
    if warning_flags:
        return "MEDIUM"

    return "LOW"


def can_user_approve(user_role: str, risk_level: str) -> dict:
    """Check if a user with given role can approve at the given risk level.

    Returns dict with allowed (bool) and reason (str).
    """
    from backend.config import APPROVAL_RULES

    rule = APPROVAL_RULES.get(risk_level)
    if not rule:
        return {"allowed": False, "reason": f"Unknown risk level: {risk_level}"}

    # Blocked actions cannot be approved by anyone
    if rule["blocked"]:
        return {"allowed": False, "reason": "This action is blocked and cannot be approved."}

    # Check role hierarchy
    required_role = rule["required_role"]
    user_level = ROLE_HIERARCHY.get(user_role, -1)
    required_level = ROLE_HIERARCHY.get(required_role, 99)

    if user_level >= required_level:
        return {"allowed": True, "reason": f"User role '{user_role}' meets requirement for {risk_level} risk."}
    else:
        return {
            "allowed": False,
            "reason": f"Requires '{required_role}' role or higher. Your role '{user_role}' is insufficient for {risk_level} risk."
        }
