import pytest
from backend.app.data_profiler import profile_dataset
from backend.app.models import SeverityLevel, DiscoveryCategory

def test_profile_empty_dataset():
    summary, disc = profile_dataset("")
    assert summary is None
    assert len(disc) == 0

def test_profile_missing_values_and_sentinels():
    csv_data = """id,age,income,credit_score,approved
1,25,5000,700,yes
2,30,-99,650,yes
3,45,6000,-1,yes
4,,4000,720,yes
5,,3500,690,yes
6,,4500,710,yes
7,,5200,680,yes
8,50,4800,640,yes
9,35,7000,750,yes
10,28,3200,600,yes
"""
    summary, disc = profile_dataset(csv_data, name="TestLoanData")
    assert summary is not None
    assert summary.row_count == 10
    assert summary.column_count == 5

    # Should detect high missing values in age (4/10 = 40%)
    assert summary.missing_value_summary["age"] == 40.0

    # Should have discoveries for missing values in 'age', negative income sentinel, negative credit_score sentinel, and extreme class imbalance in 'approved'
    titles = [d.title for d in disc]
    assert any("age" in t.lower() for t in titles)
    assert any("income" in t.lower() or "sentinel" in t.lower() for t in titles)
    assert any("approved" in t.lower() or "imbalance" in t.lower() for t in titles)
