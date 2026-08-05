"""Risk assessment and labeling service."""


def assess_risk(confidence: float, missing_info_count: int, guardrail_result: dict) -> str:
    """Assess risk level based on confidence, missing info, and guardrails."""
    if guardrail_result.get("should_block"):
        return "BLOCKED"

    critical_flags = [f for f in guardrail_result.get("flags", []) if f.get("severity") == "critical"]
    if critical_flags:
        return "HIGH"

    if confidence < 50 or missing_info_count > 5:
        return "HIGH"

    if confidence < 75 or missing_info_count > 2:
        return "MEDIUM"

    warning_flags = [f for f in guardrail_result.get("flags", []) if f.get("severity") == "warning"]
    if warning_flags:
        return "MEDIUM"

    return "LOW"


def can_user_approve(user_role: str, risk_level: str) -> dict:
    """Check if a user with given role can approve at the given risk level.

    In the new model:
    - contributor+reviewer can approve any risk level
    - contributor cannot approve
    """
    if risk_level == "BLOCKED":
        return {"allowed": False, "reason": "This action is blocked and cannot be approved."}

    if user_role == "contributor+reviewer":
        return {"allowed": True, "reason": "User has reviewer permissions."}

    return {"allowed": False, "reason": "Only reviewers can approve memories."}
