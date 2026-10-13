"""Regression coverage for signatures, metadata, and input handling."""
import pytest
from fastapi.testclient import TestClient

from agents.base import AuditTrail, SecurityException
from agents.models import SystemTaskPayload
from agents.supervisor import SystemSupervisor
from agents.api import app
from cli import main


def test_signature_verification_detects_tampering():
    trail = AuditTrail(secret_key="test-key")
    trail.log("worker", "supervisor", "FIRST", {"count": 1})
    trail.log("worker", "supervisor", "SECOND", {"count": 2})
    assert trail.verify_integrity()
    trail.logs[0]["timestamp"] = "2000-01-01T00:00:00Z"
    assert not trail.verify_integrity()


def test_signature_verification_detects_altered_hash_and_fields():
    trail = AuditTrail(secret_key="test-key")
    trail.log("worker", "supervisor", "FIRST", {"count": 1})
    trail.logs[0]["payload_hash"] = "0" * 64
    assert not trail.verify_integrity()
    trail.logs[0].pop("current_hash")
    assert not trail.verify_integrity()


def test_supervisor_rejects_phi_in_nested_attributes():
    supervisor = SystemSupervisor()
    payload = SystemTaskPayload(
        task_id="SYNTH-001", target_identifier="SAMPLE-01",
        primary_metric=5, attributes={"metadata": {"note": "MRN-994827"}}
    )
    with pytest.raises(SecurityException):
        supervisor.process_task(payload)


def test_api_returns_unprocessable_entity_for_blocked_identifiers():
    response = TestClient(app).post("/api/audit", json={
        "task_id": "MRN-994827", "target_identifier": "SYNTH-1", "primary_metric": 2
    })
    assert response.status_code == 422
    assert "994827" not in response.text


def test_api_returns_unprocessable_entity_for_phi_chat():
    response = TestClient(app).post("/api/chat", json={"query": "MRN-994827"})
    assert response.status_code == 422
    assert "994827" not in response.text


def test_batch_rejects_drive_path_on_non_windows(tmp_path):
    source = tmp_path / "batch.csv"
    source.write_text("task_id,target_identifier,primary_metric\nSYNTH-1,SAMPLE-1,10\n")
    assert main(["batch", "-i", str(source), "-o", "C:/Windows/evil_output.csv"]) == 1
