import pytest
from hrd_parp_sentinel import BRCAMutationClassifierAgent, GenomicScarCalculatorAgent, PARPResponsePredictorAgent, HRDCoordinator, main


def test_sub_agents():
    a1 = BRCAMutationClassifierAgent()
    alerts1 = a1.evaluate({"metric_primary": 35.0})
    assert len(alerts1) == 1

    a2 = GenomicScarCalculatorAgent()
    alerts2 = a2.evaluate({"critical_flag": True})
    assert len(alerts2) == 1

    a3 = PARPResponsePredictorAgent()
    alerts3 = a3.evaluate({"status_text": "DISCORDANT_FINDING"})
    assert len(alerts3) == 1


def test_coordinator():
    coord = HRDCoordinator()
    dossier = coord.audit_case({"case_id": "TEST-100", "metric_primary": 10.0, "metric_secondary": 2.0})
    assert dossier["overall_status"] == "CONCORDANT_NORMAL"
    assert dossier["total_alerts"] == 0

    ans = coord.query_assistant("What are the guidelines?")
    assert "guidelines" in ans or "standards" in ans


def test_cli():
    assert main(["audit", "--case-id", "CLI-01"]) == 0
    assert main(["chat", "What", "is", "the", "system", "status?"]) == 0


def test_domain_registry():
    from hrd_parp_sentinel import DomainKnowledgeRegistry
    assert DomainKnowledgeRegistry.ZERO_PHI_COMPLIANCE is False
    assert "PRO" in DomainKnowledgeRegistry.SYSTEM_VERSION

def test_legacy_csv_aliases_and_advisory_status():
    coord = HRDCoordinator()
    normal = coord.audit_case({
        "case_id": "SYNTH-NORMAL", "metric_primary": "10",
        "metric_secondary": "2", "is_stat": "False", "status_flag": "NORMAL"
    })
    assert normal["overall_status"] == "CONCORDANT_NORMAL"
    flagged = coord.audit_case({
        "case_id": "SYNTH-ADVISORY", "metric_primary": "10",
        "metric_secondary": "2", "is_stat": "False", "status_flag": "DISCORDANT"
    })
    assert flagged["total_alerts"] == 1
    assert flagged["overall_status"] == "WARNING_ACTIVE"
    critical = coord.audit_case({
        "case_id": "SYNTH-STAT", "metric_primary": "10",
        "metric_secondary": "2", "is_stat": "True", "status_flag": "NORMAL"
    })
    assert critical["overall_status"] == "CRITICAL_ACTION_REQUIRED"
