import pytest
from backend.app.workflow_engine import analyze_workflow
from backend.app.models import SeverityLevel, DiscoveryCategory

def test_workflow_idempotency_and_spof():
    wf_text = """
    1. User submits checkout form
    2. Backend charges user credit card via Stripe API
    3. Third-party SMS webhook pages delivery driver
    4. Manual officer review of flagged fraud risk
    5. Disburse warehouse order
    """
    summary, discoveries = analyze_workflow(wf_text)
    assert summary is not None
    assert summary.step_count == 5

    titles = [d.title.lower() for d in discoveries]
    # Check for idempotency risk on financial step
    assert any("idempotency" in t for t in titles)
    # Check for external API SPOF or timeout
    assert any("point of failure" in t or "bottleneck" in t or "timeout" in t for t in titles)
