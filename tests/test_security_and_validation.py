"""
Security and input validation tests for hrd-parp-triager-agent.
"""
import sys
import math
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import PHIGuard, AuditLogger, AuditTrail, SecurityException
from agents.models import SystemTaskPayload, UrgencyLevel


class TestPHIGuard:
    """Tests for the Zero-PHI Outbound Interceptor."""

    def test_mrn_detection(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Patient MRN-994827 blood culture positive")

    def test_mrn_lowercase(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Record for mrn-12345678 requires review")

    def test_ssn_detection(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("SSN 123-45-6789 on file")

    def test_phone_detection(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Call patient at 555-123-4567")

    def test_email_detection(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Email sent to patient@example.com")

    def test_dob_detection(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("DOB: 01/15/1985 recorded")

    def test_patient_name_detection(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Patient Name John Smith admitted")

    def test_generic_name_detection(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Jane Smith case review")

    def test_clean_text_passes(self):
        PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")

    def test_empty_string_passes(self):
        PHIGuard.assert_no_phi("")

    def test_none_handling(self):
        PHIGuard.assert_no_phi(None)

    def test_redact_phi(self):
        redacted = PHIGuard.redact_phi("Patient MRN-994827 needs follow-up")
        assert "REDACTED_IDENTIFIER" in redacted
        assert "MRN-" not in redacted


class TestInputValidation:
    """Tests for payload input validation."""

    def test_nan_rejected(self):
        with pytest.raises(Exception):  # ValidationError
            SystemTaskPayload(
                task_id="T1",
                target_identifier="KEY-01",
                primary_metric=float("nan"),
            )

    def test_positive_inf_rejected(self):
        with pytest.raises(Exception):
            SystemTaskPayload(
                task_id="T1",
                target_identifier="KEY-01",
                primary_metric=float("inf"),
            )

    def test_negative_inf_rejected(self):
        with pytest.raises(Exception):
            SystemTaskPayload(
                task_id="T1",
                target_identifier="KEY-01",
                secondary_metric=float("-inf"),
            )

    def test_empty_task_id_rejected(self):
        with pytest.raises(Exception):
            SystemTaskPayload(
                task_id="   ",
                target_identifier="KEY-01",
                primary_metric=10.0,
            )

    def test_empty_target_rejected(self):
        with pytest.raises(Exception):
            SystemTaskPayload(
                task_id="T1",
                target_identifier="",
                primary_metric=10.0,
            )

    def test_whitespace_stripped(self):
        payload = SystemTaskPayload(
            task_id="  T1  ",
            target_identifier="  KEY-01  ",
            primary_metric=10.0,
        )
        assert payload.task_id == "T1"
        assert payload.target_identifier == "KEY-01"

    def test_valid_payload_accepted(self):
        payload = SystemTaskPayload(
            task_id="T1",
            target_identifier="KEY-01",
            primary_metric=10.0,
            secondary_metric=5.0,
            status_descriptor="NOMINAL",
            is_critical_flag=False,
        )
        assert payload.primary_metric == 10.0
        assert payload.secondary_metric == 5.0


class TestAuditTrail:
    """Tests for the HMAC-SHA256 audit trail."""

    def test_ephemeral_key_generation(self):
        """Without AUDIT_SECRET_KEY, a random key is generated."""
        # Remove env var if present
        original = os.environ.pop("AUDIT_SECRET_KEY", None)
        try:
            trail = AuditTrail()
            assert len(trail.secret_key) > 0
        finally:
            if original is not None:
                os.environ["AUDIT_SECRET_KEY"] = original

    def test_custom_key_used(self):
        """When a key is provided, it is used."""
        trail = AuditTrail(secret_key="my-test-key")
        assert trail.secret_key == b"my-test-key"

    def test_env_key_used(self):
        """When AUDIT_SECRET_KEY env var is set, it is used."""
        os.environ["AUDIT_SECRET_KEY"] = "env-test-key"
        try:
            trail = AuditTrail()
            assert trail.secret_key == b"env-test-key"
        finally:
            os.environ.pop("AUDIT_SECRET_KEY", None)

    def test_audit_chain_integrity(self):
        trail = AuditTrail(secret_key="test-key")
        trail.log("actor1", "tier1", "EVENT_A", {"data": 1})
        trail.log("actor2", "tier2", "EVENT_B", {"data": 2})
        assert trail.verify_integrity() is True
        assert len(trail.get_trail()) == 2

    def test_genesis_block_reference(self):
        trail = AuditTrail(secret_key="test-key")
        entry = trail.log("actor1", "tier1", "EVENT_A", {"data": 1})
        assert entry["prev_hash"] == "GENESIS_BLOCK_0000000000000000"

    def test_chained_hashes(self):
        trail = AuditTrail(secret_key="test-key")
        e1 = trail.log("a", "t", "E1", {"x": 1})
        e2 = trail.log("a", "t", "E2", {"x": 2})
        assert e2["prev_hash"] == e1["current_hash"]


class TestCLIBatchSecurity:
    """Tests for CLI batch processing security features."""

    def test_batch_path_traversal_protection(self, tmp_path):
        """Output outside cwd and outside temp should be rejected."""
        from cli import main
        # Create a valid input file
        input_file = tmp_path / "input.csv"
        input_file.write_text("task_id,target_identifier,primary_metric\nT1,KEY-01,10.0\n")

        # Try to write to a path outside both cwd and system temp (e.g., root of C:)
        outside_path = Path("C:/Windows/evil_output.csv")
        result = main(["batch", "-i", str(input_file), "-o", str(outside_path)])
        assert result == 1  # Should fail with error

    def test_batch_missing_input_file(self):
        from cli import main
        result = main(["batch", "-i", "/nonexistent/path/file.csv"])
        assert result == 1

    def test_batch_valid_processing(self, tmp_path):
        from cli import main
        input_file = tmp_path / "input.csv"
        input_file.write_text("task_id,target_identifier,primary_metric\nT1,KEY-01,10.0\n")
        output_file = tmp_path / "output.csv"
        result = main(["batch", "-i", str(input_file), "-o", str(output_file)])
        assert result == 0
        assert output_file.exists()
