"""Tests for risk assessment and approval permission service."""
import pytest
from backend.services.risk_service import assess_risk, can_user_approve


class TestAssessRisk:
    """Tests for risk level assessment logic."""

    def test_blocked_when_should_block(self):
        result = assess_risk(90, 0, {"should_block": True, "flags": []})
        assert result == "BLOCKED"

    def test_high_when_critical_flags(self):
        guardrail = {
            "should_block": False,
            "flags": [{"severity": "critical", "type": "hallucination"}]
        }
        result = assess_risk(90, 0, guardrail)
        assert result == "HIGH"

    def test_high_when_low_confidence(self):
        result = assess_risk(40, 0, {"should_block": False, "flags": []})
        assert result == "HIGH"

    def test_high_when_many_missing_items(self):
        result = assess_risk(90, 6, {"should_block": False, "flags": []})
        assert result == "HIGH"

    def test_medium_when_moderate_confidence(self):
        result = assess_risk(60, 1, {"should_block": False, "flags": []})
        assert result == "MEDIUM"

    def test_medium_when_some_missing_items(self):
        result = assess_risk(90, 3, {"should_block": False, "flags": []})
        assert result == "MEDIUM"

    def test_medium_when_warning_flags(self):
        guardrail = {
            "should_block": False,
            "flags": [{"severity": "warning", "type": "pii"}]
        }
        result = assess_risk(90, 0, guardrail)
        assert result == "MEDIUM"

    def test_low_when_all_good(self):
        result = assess_risk(90, 0, {"should_block": False, "flags": []})
        assert result == "LOW"

    def test_blocked_takes_priority_over_everything(self):
        guardrail = {
            "should_block": True,
            "flags": [{"severity": "critical"}, {"severity": "warning"}]
        }
        result = assess_risk(10, 10, guardrail)
        assert result == "BLOCKED"

    def test_boundary_confidence_50(self):
        # Exactly 50 triggers MEDIUM, not HIGH (< 50 = HIGH)
        result = assess_risk(50, 0, {"should_block": False, "flags": []})
        assert result == "MEDIUM"

    def test_boundary_confidence_75(self):
        # Exactly 75 is not < 75, so falls through to LOW if no flags
        result = assess_risk(75, 0, {"should_block": False, "flags": []})
        assert result == "LOW"


class TestCanUserApprove:
    """Tests for role-based approval permissions."""

    def test_reviewer_can_approve_low(self):
        result = can_user_approve("contributor+reviewer", "LOW")
        assert result["allowed"] is True

    def test_reviewer_can_approve_medium(self):
        result = can_user_approve("contributor+reviewer", "MEDIUM")
        assert result["allowed"] is True

    def test_reviewer_can_approve_high(self):
        result = can_user_approve("contributor+reviewer", "HIGH")
        assert result["allowed"] is True

    def test_reviewer_cannot_approve_blocked(self):
        result = can_user_approve("contributor+reviewer", "BLOCKED")
        assert result["allowed"] is False
        assert "blocked" in result["reason"].lower()

    def test_contributor_cannot_approve(self):
        result = can_user_approve("contributor", "LOW")
        assert result["allowed"] is False
        assert "reviewer" in result["reason"].lower()

    def test_contributor_cannot_approve_any_level(self):
        for level in ["LOW", "MEDIUM", "HIGH"]:
            result = can_user_approve("contributor", level)
            assert result["allowed"] is False
