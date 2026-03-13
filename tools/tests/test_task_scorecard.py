import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from task_scorecard import main, score  # noqa: E402


def test_high_scores_recommend_agent():
    rec = score(2, 2, 2, 2, 2, 2)
    assert (rec.total, rec.mode, rec.autonomy) == (12, "agent", "L2-L3")


def test_middle_scores_recommend_close_supervision():
    assert score(1, 1, 1, 1, 1, 2).mode == "agent with close supervision"


def test_low_scores_recommend_human_led():
    assert score(1, 1, 1, 1, 1, 0).mode == "human leads, agent assists"


def test_high_blast_radius_caps_autonomy_even_with_a_high_total():
    rec = score(2, 2, 0, 2, 2, 2)
    assert rec.total == 10
    assert rec.mode == "agent with close supervision"
    assert any("blast radius" in r for r in rec.reasons)


def test_unverifiable_task_is_always_human_led():
    rec = score(2, 0, 2, 2, 2, 2)
    assert rec.mode == "human leads, agent assists"
    assert any("re-score" in r for r in rec.reasons)


def test_missing_spec_and_large_diff_produce_reasons():
    reasons = " ".join(score(0, 2, 2, 2, 0, 2).reasons)
    assert "acceptance criteria" in reasons and "slice" in reasons


@pytest.mark.parametrize("bad", [-1, 3, 1.5, None])
def test_rejects_values_outside_0_to_2(bad):
    with pytest.raises(ValueError):
        score(bad, 2, 2, 2, 2, 2)


def test_cli_prints_recommendation(capsys):
    assert (
        main(["--spec", "2", "--verify", "2", "--blast", "1", "--context", "2", "--review", "2", "--novelty", "1"]) == 0
    )
    assert "total 10/12 -> agent (autonomy L2-L3)" in capsys.readouterr().out
