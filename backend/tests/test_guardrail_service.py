"""Tests for guardrail service - PII detection, confidence checks, and flag logic."""
import pytest
from unittest.mock import patch
from backend.services.guardrail_service import (
    detect_pii, redact_reasoning, check_confidence_threshold, run_guardrails
)


class TestDetectPII:
    """Tests for PII pattern detection and masking."""

    def test_detects_ssn(self):
        text = "Employee SSN is 123-45-6789"
        flags, redacted = detect_pii(text)
        assert len(flags) == 1
        assert flags[0]["pii_type"] == "ssn"
        assert "###-##-####" in redacted
        assert "123-45-6789" not in redacted

    def test_detects_credit_card(self):
        text = "Card number: 4111-2222-3333-4444"
        flags, redacted = detect_pii(text)
        assert any(f["pii_type"] == "credit_card" for f in flags)
        assert "4111" not in redacted

    def test_detects_password(self):
        text = "password: mysecretpassword123"
        flags, redacted = detect_pii(text)
        assert any(f["pii_type"] == "password_field" for f in flags)
        assert flags[0]["severity"] == "critical"
        assert "[PASSWORD MASKED]" in redacted

    def test_detects_api_key(self):
        text = "api_key=sk_live_abcdefghijk12345"
        flags, redacted = detect_pii(text)
        assert any(f["pii_type"] == "api_key" for f in flags)
        assert "[API KEY MASKED]" in redacted

    def test_detects_aws_key(self):
        text = "Access key: AKIAIOSFODNN7EXAMPLE"
        flags, redacted = detect_pii(text)
        assert any(f["pii_type"] == "aws_access_key" for f in flags)
        assert "[AWS KEY MASKED]" in redacted

    def test_detects_email(self):
        text = "Contact: john.doe@gmail.com"
        flags, redacted = detect_pii(text)
        assert any(f["pii_type"] == "email_personal" for f in flags)
        assert "john.doe@gmail.com" not in redacted

    def test_no_false_positives_on_clean_text(self):
        text = "The authentication system uses passkeys for enhanced security."
        flags, redacted = detect_pii(text)
        assert len(flags) == 0
        assert redacted == text

    def test_multiple_pii_types(self):
        text = "SSN: 111-22-3333, email: test@yahoo.com, password=secret"
        flags, redacted = detect_pii(text)
        pii_types = {f["pii_type"] for f in flags}
        assert "ssn" in pii_types
        assert "email_personal" in pii_types
        assert "password_field" in pii_types

    def test_counts_multiple_instances(self):
        text = "SSN: 111-22-3333 and another SSN: 444-55-6666"
        flags, redacted = detect_pii(text)
        ssn_flag = next(f for f in flags if f["pii_type"] == "ssn")
        assert ssn_flag["count"] == 2
        assert "2 instances" in ssn_flag["message"]


class TestRedactReasoning:
    """Tests for reasoning dict redaction."""

    def test_redacts_string_fields(self):
        reasoning = {
            "what_changed": "User SSN 123-45-6789 was exposed",
            "business_objective": "Improve security"
        }
        flags, cleaned = redact_reasoning(reasoning)
        assert len(flags) > 0
        assert "123-45-6789" not in cleaned["what_changed"]
        assert cleaned["business_objective"] == "Improve security"

    def test_redacts_list_fields(self):
        reasoning = {
            "risks_accepted": ["Password: admin123 might be exposed", "Normal risk"]
        }
        flags, cleaned = redact_reasoning(reasoning)
        assert any(f["severity"] == "critical" for f in flags)
        assert "admin123" not in str(cleaned["risks_accepted"])

    def test_preserves_non_string_values(self):
        reasoning = {
            "confidence": 95,
            "is_verified": True
        }
        flags, cleaned = redact_reasoning(reasoning)
        assert len(flags) == 0
        assert cleaned["confidence"] == 95
        assert cleaned["is_verified"] is True


class TestConfidenceThreshold:
    """Tests for confidence threshold checks."""

    def test_very_low_confidence_critical(self):
        flags = check_confidence_threshold(30)
        assert len(flags) == 1
        assert flags[0]["severity"] == "critical"
        assert "very low" in flags[0]["message"].lower()

    def test_moderate_confidence_warning(self):
        flags = check_confidence_threshold(55)
        assert len(flags) == 1
        assert flags[0]["severity"] == "warning"
        assert "moderate" in flags[0]["message"].lower()

    def test_high_confidence_no_flags(self):
        flags = check_confidence_threshold(85)
        assert len(flags) == 0

    def test_boundary_40_is_critical(self):
        flags = check_confidence_threshold(39)
        assert flags[0]["severity"] == "critical"

    def test_boundary_60_is_warning(self):
        flags = check_confidence_threshold(59)
        assert flags[0]["severity"] == "warning"

    def test_boundary_60_exactly_no_flag(self):
        flags = check_confidence_threshold(60)
        assert len(flags) == 0


class TestRunGuardrails:
    """Tests for the full guardrail pipeline - verifying the flag bug is fixed."""

    @patch("backend.services.guardrail_service.run_guardrail_check")
    def test_overall_safe_true_when_no_issues(self, mock_ai_check):
        mock_ai_check.return_value = {"flags": []}
        reasoning = {"what_changed": "Upgraded to passkeys"}
        result = run_guardrails(reasoning, "Clean document text", 90)
        assert result["overall_safe"] is True
        assert result["should_block"] is False
        assert result["risk_adjustment"] is None

    @patch("backend.services.guardrail_service.run_guardrail_check")
    def test_overall_safe_false_when_critical_flags(self, mock_ai_check):
        mock_ai_check.return_value = {
            "flags": [{
                "type": "hallucination",
                "severity": "critical",
                "message": "Claim contradicts source",
                "field": "what_changed"
            }]
        }
        reasoning = {"what_changed": "Something hallucinated"}
        result = run_guardrails(reasoning, "Document text", 90)
        assert result["overall_safe"] is False
        assert result["should_block"] is True
        assert result["risk_adjustment"] == "critical"

    @patch("backend.services.guardrail_service.run_guardrail_check")
    def test_blocks_on_credential_pii(self, mock_ai_check):
        mock_ai_check.return_value = {"flags": []}
        reasoning = {"what_changed": "password=supersecret123 was changed"}
        result = run_guardrails(reasoning, "Clean docs", 90)
        # Password detected = critical PII = should block
        assert result["should_block"] is True
        assert result["has_pii"] is True
        assert result["overall_safe"] is False

    @patch("backend.services.guardrail_service.run_guardrail_check")
    def test_warning_pii_does_not_block(self, mock_ai_check):
        mock_ai_check.return_value = {"flags": []}
        reasoning = {"what_changed": "User john@gmail.com requested the change"}
        result = run_guardrails(reasoning, "Clean docs", 90)
        # Email is warning severity, not critical
        assert result["should_block"] is False
        assert result["has_pii"] is True
        assert result["overall_safe"] is True
        assert result["risk_adjustment"] == "medium"

    @patch("backend.services.guardrail_service.run_guardrail_check")
    def test_low_confidence_triggers_blocking(self, mock_ai_check):
        mock_ai_check.return_value = {"flags": []}
        reasoning = {"what_changed": "Something uncertain"}
        result = run_guardrails(reasoning, "Docs", 25)
        # Very low confidence = critical flag from threshold check
        assert result["overall_safe"] is False
        assert result["should_block"] is True

    @patch("backend.services.guardrail_service.run_guardrail_check")
    def test_cleaned_reasoning_returned_when_pii(self, mock_ai_check):
        mock_ai_check.return_value = {"flags": []}
        reasoning = {"what_changed": "SSN 123-45-6789 found in document"}
        result = run_guardrails(reasoning, "Clean docs", 90)
        assert result["cleaned_reasoning"] is not None
        assert "123-45-6789" not in result["cleaned_reasoning"]["what_changed"]

    @patch("backend.services.guardrail_service.run_guardrail_check")
    def test_ai_check_failure_adds_warning(self, mock_ai_check):
        mock_ai_check.side_effect = Exception("Bedrock timeout")
        reasoning = {"what_changed": "Normal change"}
        result = run_guardrails(reasoning, "Docs", 90)
        assert any(f["type"] == "system_error" for f in result["flags"])
        # System error is warning, not critical - shouldn't block
        assert result["overall_safe"] is True
        assert result["should_block"] is False
