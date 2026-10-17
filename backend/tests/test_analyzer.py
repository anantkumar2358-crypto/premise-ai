import pytest
from backend.app.analyzer import run_full_analysis, calculate_health_score
from backend.app.models import AnalysisRequest, SeverityLevel
from backend.app.templates_data import TEMPLATES
from backend.app.report_generator import generate_markdown_report

def test_full_analysis_with_template():
    tmpl = TEMPLATES["healthcare_triage"]
    req = AnalysisRequest(
        project_name=tmpl["title"],
        document_text=tmpl["document_text"],
        dataset_content=tmpl["dataset_content"],
        dataset_name=tmpl["dataset_name"],
        workflow_content=tmpl["workflow_content"],
        domain=tmpl["domain"]
    )
    res = run_full_analysis(req)

    assert res.project_name == tmpl["title"]
    assert len(res.discoveries) > 0
    assert len(res.probing_questions) > 0
    assert res.health_score <= 100
    assert res.risk_priority_index > 0
    assert res.summary_stats["critical_count"] >= 1 or res.summary_stats["high_count"] >= 1

    # Verify report generation
    md_report = generate_markdown_report(res)
    assert "# 🛡️ Project Blind Spot" in md_report
    assert res.project_name in md_report

def test_health_score_recovery_on_resolve():
    tmpl = TEMPLATES["fintech_lending"]
    req = AnalysisRequest(
        project_name=tmpl["title"],
        document_text=tmpl["document_text"],
        dataset_content=tmpl["dataset_content"],
        workflow_content=tmpl["workflow_content"]
    )
    res = run_full_analysis(req)
    initial_score = res.health_score

    # Simulate resolving top 2 critical discoveries
    resolved_count = 0
    for d in res.discoveries:
        if d.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH] and resolved_count < 2:
            d.status = "resolved"
            resolved_count += 1

    new_score, _ = calculate_health_score(res.discoveries, res.probing_questions)
    assert new_score > initial_score, "Health score must improve when discoveries are resolved"
