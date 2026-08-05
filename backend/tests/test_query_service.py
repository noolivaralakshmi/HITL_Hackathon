"""Tests for query service - semantic search and fallback logic."""
import pytest
from unittest.mock import patch, MagicMock
from backend.services.query_service import (
    fallback_query, format_memories_for_query, semantic_retrieve
)


class TestFallbackQuery:
    """Tests for keyword-based fallback query."""

    def test_finds_matching_memory(self):
        memories = [{
            "id": "mem-1",
            "change_type": "Authentication",
            "reasoning": {
                "what_changed": "Migrated from passwords to passkeys",
                "business_objective": "Reduce phishing attacks",
                "alternatives_considered": [
                    {"name": "MFA Tokens", "rejected_reason": "Too expensive"}
                ],
                "evidence": [{"document": "SecurityReview.pdf", "supports": "Stats"}]
            },
            "confidence": 95,
            "approved_by": "user-001",
        }]
        # "passkeys" (no punctuation, >3 chars) should match
        result = fallback_query("Tell me about passkeys migration", memories)
        assert result["found"] is True
        assert "passkeys" in result["answer"]["decision"].lower()
        assert result["search_method"] == "keyword_fallback"

    def test_returns_not_found_when_no_match(self):
        memories = [{
            "id": "mem-1",
            "change_type": "Authentication",
            "reasoning": {"what_changed": "Passkeys"},
            "confidence": 95,
        }]
        # Use a query whose 4+ char words don't appear in the reasoning JSON
        result = fallback_query("How does billing integration work?", memories)
        assert result["found"] is False

    def test_skips_short_words(self):
        """Words ≤ 3 chars should not match."""
        memories = [{
            "id": "mem-1",
            "change_type": "Auth",
            "reasoning": {"what_changed": "A B C D"},
            "confidence": 50,
        }]
        # "why" and "the" are ≤ 3 chars, should not match
        result = fallback_query("why the x", memories)
        assert result["found"] is False

    def test_includes_rejected_alternatives(self):
        memories = [{
            "id": "mem-1",
            "change_type": "Infrastructure",
            "reasoning": {
                "what_changed": "Moved to Kubernetes",
                "business_objective": "Scale better",
                "alternatives_considered": [
                    {"name": "ECS", "rejected_reason": "Vendor lock-in"},
                    {"name": "Nomad", "rejected_reason": "Small community"},
                ],
                "evidence": []
            },
            "confidence": 88,
            "approved_by": "user-002",
        }]
        result = fallback_query("Why kubernetes instead of alternatives?", memories)
        assert result["found"] is True
        assert len(result["answer"]["rejected_alternatives"]) == 2


class TestFormatMemories:
    """Tests for memory formatting for AI context."""

    def test_formats_basic_memory(self):
        memories = [{
            "id": "mem-123",
            "change_type": "Security",
            "confidence": 90,
            "approved_by": "user-001",
            "approved_at": "2025-01-15",
            "reasoning": {"what_changed": "Added WAF"}
        }]
        text = format_memories_for_query(memories)
        assert "mem-123" in text
        assert "Security" in text
        assert "90%" in text
        assert "Added WAF" in text

    def test_includes_similarity_score(self):
        memories = [{
            "id": "mem-456",
            "change_type": "Auth",
            "confidence": 85,
            "approved_by": "admin",
            "approved_at": "2025-02-01",
            "reasoning": {},
            "_similarity": 0.92,
        }]
        text = format_memories_for_query(memories)
        assert "0.92" in text
        assert "Relevance Score" in text

    def test_handles_string_reasoning(self):
        import json
        memories = [{
            "id": "mem-789",
            "change_type": "DB",
            "confidence": 70,
            "approved_by": "user",
            "approved_at": "2025-03-01",
            "reasoning": json.dumps({"what_changed": "Migrated to Aurora"})
        }]
        text = format_memories_for_query(memories)
        assert "Migrated to Aurora" in text


class TestSemanticRetrieve:
    """Tests for semantic search retrieval with mocked embeddings."""

    @patch("backend.services.query_service.get_memory")
    @patch("backend.services.embedding_service.semantic_search")
    def test_returns_verified_memories_above_threshold(self, mock_search, mock_get):
        mock_search.return_value = [
            {"memory_id": "mem-1", "similarity": 0.85, "text_content": "Auth change"},
            {"memory_id": "mem-2", "similarity": 0.45, "text_content": "Infra change"},
            {"memory_id": "mem-3", "similarity": 0.2, "text_content": "Unrelated"},  # Below threshold
        ]
        mock_get.side_effect = lambda mid: {
            "mem-1": {"id": "mem-1", "status": "VERIFIED", "reasoning": {}},
            "mem-2": {"id": "mem-2", "status": "VERIFIED", "reasoning": {}},
            "mem-3": {"id": "mem-3", "status": "VERIFIED", "reasoning": {}},
        }.get(mid)

        results = semantic_retrieve("authentication question")
        assert len(results) == 2  # mem-3 filtered by 0.3 threshold
        assert results[0]["_similarity"] == 0.85

    @patch("backend.services.query_service.get_memory")
    @patch("backend.services.embedding_service.semantic_search")
    def test_filters_non_verified(self, mock_search, mock_get):
        mock_search.return_value = [
            {"memory_id": "mem-1", "similarity": 0.9, "text_content": "Draft"},
        ]
        mock_get.return_value = {"id": "mem-1", "status": "DRAFT", "reasoning": {}}

        results = semantic_retrieve("question")
        assert len(results) == 0  # DRAFT should be excluded

    @patch("backend.services.embedding_service.semantic_search")
    def test_returns_empty_on_search_failure(self, mock_search):
        mock_search.side_effect = Exception("Bedrock error")
        results = semantic_retrieve("question")
        assert results == []

    @patch("backend.services.embedding_service.semantic_search")
    def test_returns_empty_when_no_results(self, mock_search):
        mock_search.return_value = []
        results = semantic_retrieve("something obscure")
        assert results == []
