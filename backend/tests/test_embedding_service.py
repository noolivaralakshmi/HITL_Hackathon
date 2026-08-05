"""Tests for embedding service - vector operations and memory text building."""
import pytest
from backend.services.embedding_service import (
    cosine_similarity, build_memory_text_for_embedding
)


class TestCosineSimilarity:
    """Tests for vector similarity computation."""

    def test_identical_vectors(self):
        assert cosine_similarity([1, 0, 0], [1, 0, 0]) == 1.0

    def test_orthogonal_vectors(self):
        assert cosine_similarity([1, 0, 0], [0, 1, 0]) == 0.0

    def test_opposite_vectors(self):
        assert cosine_similarity([1, 0, 0], [-1, 0, 0]) == -1.0

    def test_similar_vectors(self):
        # Vectors pointing in roughly the same direction
        sim = cosine_similarity([1, 1, 0], [1, 0.5, 0])
        assert 0.9 < sim < 1.0

    def test_zero_vector_returns_zero(self):
        assert cosine_similarity([0, 0, 0], [1, 1, 1]) == 0.0

    def test_high_dimensional(self):
        # Simulate 1024-dim vectors
        vec_a = [1.0] * 512 + [0.0] * 512
        vec_b = [1.0] * 512 + [0.0] * 512
        assert cosine_similarity(vec_a, vec_b) == pytest.approx(1.0)

    def test_partially_overlapping(self):
        vec_a = [1.0] * 512 + [0.0] * 512
        vec_b = [0.0] * 512 + [1.0] * 512
        assert cosine_similarity(vec_a, vec_b) == 0.0


class TestBuildMemoryText:
    """Tests for building embedding-friendly text from memory records."""

    def test_includes_change_type(self):
        memory = {"change_type": "Authentication", "reasoning": {}}
        text = build_memory_text_for_embedding(memory)
        assert "Authentication" in text

    def test_includes_reasoning_fields(self):
        memory = {
            "change_type": "Infrastructure",
            "reasoning": {
                "what_changed": "Migrated to Kubernetes",
                "business_objective": "Reduce costs",
                "technical_objective": "Improve scalability",
            }
        }
        text = build_memory_text_for_embedding(memory)
        assert "Migrated to Kubernetes" in text
        assert "Reduce costs" in text
        assert "Improve scalability" in text

    def test_includes_alternatives(self):
        memory = {
            "reasoning": {
                "alternatives_considered": [
                    {"name": "ECS", "rejected_reason": "Vendor lock-in"},
                    {"name": "Bare metal", "rejected_reason": "Too expensive"},
                ]
            }
        }
        text = build_memory_text_for_embedding(memory)
        assert "ECS" in text
        assert "Vendor lock-in" in text
        assert "Bare metal" in text

    def test_includes_risks(self):
        memory = {
            "reasoning": {
                "risks_accepted": ["Downtime during migration", "Training needed"]
            }
        }
        text = build_memory_text_for_embedding(memory)
        assert "Downtime during migration" in text
        assert "Training needed" in text

    def test_includes_decision_makers(self):
        memory = {
            "reasoning": {
                "decision_makers": ["CTO Alice", "VP Bob"]
            }
        }
        text = build_memory_text_for_embedding(memory)
        assert "CTO Alice" in text
        assert "VP Bob" in text

    def test_handles_json_string_reasoning(self):
        import json
        memory = {
            "change_type": "Security",
            "reasoning": json.dumps({
                "what_changed": "Added WAF",
                "business_objective": "Block attacks"
            })
        }
        text = build_memory_text_for_embedding(memory)
        assert "Added WAF" in text
        assert "Block attacks" in text

    def test_handles_empty_memory(self):
        memory = {"reasoning": {}}
        text = build_memory_text_for_embedding(memory)
        assert text == ""  # No fields to include

    def test_handles_missing_reasoning(self):
        memory = {"change_type": "Test"}
        text = build_memory_text_for_embedding(memory)
        assert "Test" in text
