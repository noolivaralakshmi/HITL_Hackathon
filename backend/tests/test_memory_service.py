"""Tests for memory service - CRUD operations and approval flow."""
import pytest
from unittest.mock import patch
from backend.database.connection import init_db, get_db
from backend.services.memory_service import (
    create_memory, get_memory, list_memories,
    update_memory, approve_memory, reject_memory,
    get_verified_memories
)


@pytest.fixture(autouse=True)
def setup_test_db(tmp_path, monkeypatch):
    """Use a temporary database for each test."""
    db_path = str(tmp_path / "test.db")
    monkeypatch.setattr("backend.config.DATABASE_PATH", db_path)
    monkeypatch.setattr("backend.database.connection.DATABASE_PATH", db_path)
    # Re-import to pick up new path
    init_db()
    yield db_path


class TestCreateMemory:
    """Tests for memory creation."""

    def test_creates_draft_memory(self):
        memory = create_memory("user-001")
        assert memory["id"] is not None
        assert memory["status"] == "DRAFT"

    def test_memory_retrievable_after_create(self):
        memory = create_memory("user-003")
        retrieved = get_memory(memory["id"])
        assert retrieved is not None
        assert retrieved["status"] == "DRAFT"
        assert retrieved["contributor_id"] == "user-003"


class TestUpdateMemory:
    """Tests for memory updates."""

    def test_updates_single_field(self):
        memory = create_memory("user-001")
        updated = update_memory(memory["id"], change_type="Authentication")
        assert updated["change_type"] == "Authentication"

    def test_updates_multiple_fields(self):
        memory = create_memory("user-001")
        updated = update_memory(
            memory["id"],
            change_type="Infrastructure",
            confidence=85,
            risk_level="LOW"
        )
        assert updated["change_type"] == "Infrastructure"
        assert updated["confidence"] == 85
        assert updated["risk_level"] == "LOW"

    def test_serializes_json_fields(self):
        memory = create_memory("user-001")
        reasoning = {"what_changed": "Test", "business_objective": "Demo"}
        updated = update_memory(memory["id"], reasoning=reasoning)
        assert updated["reasoning"]["what_changed"] == "Test"

    def test_updates_guardrail_flags(self):
        memory = create_memory("user-001")
        flags = [{"type": "pii", "severity": "warning", "message": "Email found"}]
        updated = update_memory(memory["id"], guardrail_flags=flags)
        assert len(updated["guardrail_flags"]) == 1
        assert updated["guardrail_flags"][0]["type"] == "pii"

    def test_updates_groundedness(self):
        memory = create_memory("user-001")
        groundedness = {
            "claims": [{"claim": "Test", "status": "SUPPORTED"}],
            "groundedness_score": {"percentage": 100}
        }
        updated = update_memory(memory["id"], groundedness=groundedness)
        assert updated["groundedness"]["groundedness_score"]["percentage"] == 100


class TestApproveMemory:
    """Tests for memory approval flow."""

    @patch("backend.services.embedding_service.index_memory")
    def test_approve_sets_verified(self, mock_index):
        mock_index.return_value = {"indexed": True}
        memory = create_memory("user-003")
        update_memory(memory["id"], status="DRAFT", risk_level="LOW")
        result = approve_memory(memory["id"], "user-001")
        assert result["status"] == "VERIFIED"
        assert result["approved_by"] == "user-001"
        assert result["approved_at"] is not None

    @patch("backend.services.embedding_service.index_memory")
    def test_approve_indexes_for_search(self, mock_index):
        mock_index.return_value = {"indexed": True}
        memory = create_memory("user-003")
        update_memory(memory["id"], change_type="Auth", reasoning={"what_changed": "Test"})
        approve_memory(memory["id"], "user-001")
        mock_index.assert_called_once()


class TestRejectMemory:
    """Tests for memory rejection."""

    def test_reject_sets_rejected(self):
        memory = create_memory("user-003")
        result = reject_memory(memory["id"], "user-001")
        assert result["status"] == "REJECTED"


class TestListMemories:
    """Tests for listing memories."""

    def test_list_all(self):
        create_memory("user-001")
        create_memory("user-002")
        memories = list_memories()
        assert len(memories) >= 2

    def test_list_filtered_by_status(self):
        m1 = create_memory("user-001")
        m2 = create_memory("user-002")
        update_memory(m1["id"], status="DRAFT")
        reject_memory(m2["id"], "user-001")
        drafts = list_memories("DRAFT")
        assert all(m["status"] == "DRAFT" for m in drafts)


class TestGetVerifiedMemories:
    """Tests for getting only verified memories."""

    @patch("backend.services.embedding_service.index_memory")
    def test_returns_only_verified(self, mock_index):
        mock_index.return_value = {"indexed": True}
        m1 = create_memory("user-001")
        m2 = create_memory("user-002")
        update_memory(m1["id"], change_type="Auth", reasoning={"what_changed": "test"})
        approve_memory(m1["id"], "user-001")
        # m2 stays as DRAFT
        verified = get_verified_memories()
        ids = [m["id"] for m in verified]
        assert m1["id"] in ids
        assert m2["id"] not in ids
