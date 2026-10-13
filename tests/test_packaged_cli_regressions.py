"""Regression tests for CSV boolean decoding and finite clinical-demo values."""
import csv

import pytest

from hrd_parp_triager_agent.cli import main as clinical_main
from hrd_parp_triager_agent.models import ClinicalCasePayload


def test_false_string_does_not_trigger_stat(tmp_path):
    source = tmp_path / "input.csv"
    target = tmp_path / "output.csv"
    source.write_text(
        "case_id,patient_synthetic_id,metric_primary,metric_secondary,is_stat,status_flag\n"
        "C1,SYNTH-1,10,3,False,NORMAL\n"
        "C2,SYNTH-2,10,3,True,NORMAL\n"
        "C3,SYNTH-3,10,3,invalid,NORMAL\n",
        encoding="utf-8",
    )
    assert clinical_main(["batch", "-i", str(source), "-o", str(target)]) == 0
    with target.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert [row["case_id"] for row in rows] == ["C1", "C2"]
    assert [int(row["stat_critical_alerts"]) for row in rows] == [0, 1]


@pytest.mark.parametrize("bad_value", [float("nan"), float("inf"), float("-inf")])
def test_nonfinite_demonstration_metric_rejected(bad_value):
    with pytest.raises(ValueError, match="finite"):
        ClinicalCasePayload(
            case_id="C1", patient_synthetic_id="SYNTH-1",
            primary_metric=bad_value, secondary_metric=3, status_flag="NORMAL",
        )
