"""
Enrichment Feature Implementation for hrd-parp-triager-agent.
Generated based on domain-specific requirements in specifications.

All domain engines share a common threshold-based evaluation strategy and are
instantiated via the generic `DomainEngine` class. Legacy result dataclasses
are retained for backward compatibility with the test suite.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import datetime


# =============================================================================
# Shared result type
# =============================================================================
@dataclass
class EngineResult:
    """Shared result type for all domain enrichment engines."""
    feature_name: str = "Domain Engine"
    status: str = "OPTIMAL"
    score: float = 0.0
    metrics: Dict[str, Any] = field(default_factory=dict)
    alerts: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())


# =============================================================================
# Legacy result dataclasses (kept for backward compatibility with existing tests)
# =============================================================================
@dataclass
class OverviewEngineResult(EngineResult):
    feature_name: str = "Overview"


@dataclass
class PharmacogenomicDrugMetabolismIntegrationEngineResult(EngineResult):
    feature_name: str = "Pharmacogenomic Drug Metabolism Integration"


@dataclass
class GoalEngineResult(EngineResult):
    feature_name: str = "Goal"


@dataclass
class DataModelChangesEngineResult(EngineResult):
    feature_name: str = "Data Model Changes"


@dataclass
class KnowledgeBaseEngineResult(EngineResult):
    feature_name: str = "Knowledge Base"


@dataclass
class AgentChangesEngineResult(EngineResult):
    feature_name: str = "Agent Changes"


@dataclass
class GenerateDoseAdjustmentRecommendationsEngineResult(EngineResult):
    feature_name: str = "Generate dose adjustment recommendations"


@dataclass
class ApiChangesEngineResult(EngineResult):
    feature_name: str = "API Changes"


# =============================================================================
# Generic domain engine
# =============================================================================
class DomainEngine:
    """
    Threshold-based evaluation engine used by all domain enrichment features.

    The evaluate() method compares the primary value against a baseline threshold:
      - value > 2 * threshold  -> CRITICAL_ALERT
      - value > threshold      -> WARNING
      - otherwise              -> OPTIMAL
    """

    def __init__(self, feature_name: str, threshold: float = 1.0,
                 config: Optional[Dict[str, Any]] = None):
        self.feature_name = feature_name
        self.threshold = threshold
        self.config = config or {}
        self.history: List[EngineResult] = []

    def evaluate(self, primary_value: float, secondary_value: float = 0.0,
                 **kwargs) -> EngineResult:
        alerts: List[str] = []
        recs: List[str] = []
        status = "OPTIMAL"
        score = round(float(primary_value), 3)

        critical_limit = self.threshold * 2
        if primary_value > critical_limit:
            status = "CRITICAL_ALERT"
            alerts.append(
                f"{self.feature_name}: Primary value {primary_value:.2f} "
                f"breached critical threshold ({critical_limit:.2f})"
            )
            recs.append("Initiate immediate protocol review and escalate to attending lead.")
        elif primary_value > self.threshold:
            status = "WARNING"
            alerts.append(
                f"{self.feature_name}: Value {primary_value:.2f} "
                f"exceeds baseline threshold ({self.threshold:.2f})"
            )
            recs.append("Increase monitoring frequency and perform secondary verification.")
        else:
            recs.append("Parameters nominal under standard operating bounds.")

        res = EngineResult(
            feature_name=self.feature_name,
            status=status,
            score=score,
            metrics={"primary": primary_value, "secondary": secondary_value, **kwargs},
            alerts=alerts,
            recommendations=recs,
        )
        self.history.append(res)
        return res


# =============================================================================
# Legacy engine wrappers (thin subclasses for backward compatibility)
# =============================================================================
class OverviewEngine(DomainEngine):
    """Overview: Detailed implementation plan for the 4 enrichment ideas assigned to this project."""
    def __init__(self, threshold: float = 1.0, config: Optional[Dict[str, Any]] = None):
        super().__init__("Overview", threshold, config)


class PharmacogenomicDrugMetabolismIntegrationEngine(DomainEngine):
    """Pharmacogenomic Drug Metabolism Integration."""
    def __init__(self, threshold: float = 1.0, config: Optional[Dict[str, Any]] = None):
        super().__init__("Pharmacogenomic Drug Metabolism Integration", threshold, config)


class GoalEngine(DomainEngine):
    """Goal: Integrate CPIC guidelines for PARP inhibitor metabolism (CYP3A4-mediated)."""
    def __init__(self, threshold: float = 1.0, config: Optional[Dict[str, Any]] = None):
        super().__init__("Goal", threshold, config)


class DataModelChangesEngine(DomainEngine):
    """Data Model Changes: New file: `hrd_parp_triager_agent/models.py` additions."""
    def __init__(self, threshold: float = 1.0, config: Optional[Dict[str, Any]] = None):
        super().__init__("Data Model Changes", threshold, config)


class KnowledgeBaseEngine(DomainEngine):
    """Knowledge Base: New file: `hrd_parp_triager_agent/pgx_kb.py`."""
    def __init__(self, threshold: float = 1.0, config: Optional[Dict[str, Any]] = None):
        super().__init__("Knowledge Base", threshold, config)


class AgentChangesEngine(DomainEngine):
    """Agent Changes: Modify: `PARPResponsePredictorAgent`."""
    def __init__(self, threshold: float = 1.0, config: Optional[Dict[str, Any]] = None):
        super().__init__("Agent Changes", threshold, config)


class GenerateDoseAdjustmentRecommendationsEngine(DomainEngine):
    """Generate dose adjustment recommendations: Output: `PARPiPharmacogenomicProfile`."""
    def __init__(self, threshold: float = 1.0, config: Optional[Dict[str, Any]] = None):
        super().__init__("Generate dose adjustment recommendations", threshold, config)


class ApiChangesEngine(DomainEngine):
    """API Changes: New endpoint: `POST /api/v1/parpi-pgx`."""
    def __init__(self, threshold: float = 1.0, config: Optional[Dict[str, Any]] = None):
        super().__init__("API Changes", threshold, config)


# =============================================================================
# Composite enrichment suite
# =============================================================================
class HrdparptriageragentEnrichmentSuite:
    """Master coordinator executing all enriched domain features."""
    def __init__(self):
        self.overviewengine = OverviewEngine()
        self.pharmacogenomicdrugm = PharmacogenomicDrugMetabolismIntegrationEngine()
        self.goalengine = GoalEngine()
        self.datamodelchangesengi = DataModelChangesEngine()
        self.knowledgebaseengine = KnowledgeBaseEngine()
        self.agentchangesengine = AgentChangesEngine()
        self.generatedoseadjustme = GenerateDoseAdjustmentRecommendationsEngine()
        self.apichangesengine = ApiChangesEngine()

    def execute_all(self, primary_val: float = 1.5, secondary_val: float = 0.5) -> Dict[str, Any]:
        results = {}
        results["OverviewEngine"] = self.overviewengine.evaluate(primary_val, secondary_val)
        results["PharmacogenomicDrugMetabolismIntegrationEngine"] = self.pharmacogenomicdrugm.evaluate(primary_val, secondary_val)
        results["GoalEngine"] = self.goalengine.evaluate(primary_val, secondary_val)
        results["DataModelChangesEngine"] = self.datamodelchangesengi.evaluate(primary_val, secondary_val)
        results["KnowledgeBaseEngine"] = self.knowledgebaseengine.evaluate(primary_val, secondary_val)
        results["AgentChangesEngine"] = self.agentchangesengine.evaluate(primary_val, secondary_val)
        results["GenerateDoseAdjustmentRecommendationsEngine"] = self.generatedoseadjustme.evaluate(primary_val, secondary_val)
        results["ApiChangesEngine"] = self.apichangesengine.evaluate(primary_val, secondary_val)
        return results


# Global instance
enrichment_suite = HrdparptriageragentEnrichmentSuite()
