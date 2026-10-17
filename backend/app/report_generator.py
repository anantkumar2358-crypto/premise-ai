"""
Generates exportable executive audit reports in Markdown, HTML, and JSON formats.
"""

from typing import Dict, Any
from .models import AnalysisResponse, SeverityLevel

def generate_markdown_report(data: AnalysisResponse) -> str:
    md = []
    md.append(f"# 🛡️ Project Blind Spot & Assumption Audit Report")
    md.append(f"**Project**: {data.project_name}")
    md.append(f"**Date**: {data.timestamp[:10]} | **Engine**: `{data.engine_used}`")
    md.append(f"**Resilience Health Score**: `{data.health_score}/100` | **Risk Priority Index (RPI)**: `{data.risk_priority_index}`\n")
    
    md.append("---")
    md.append("## 1. Executive Summary")
    md.append(data.executive_summary + "\n")

    md.append("## 2. Risk Distribution")
    s = data.summary_stats
    md.append(f"- **Critical Showstoppers (RPN > 60)**: {s.get('critical_count', 0)}")
    md.append(f"- **High Priority Risks (RPN 36-59)**: {s.get('high_count', 0)}")
    md.append(f"- **Medium Priority Risks (RPN 16-35)**: {s.get('medium_count', 0)}")
    md.append(f"- **Low / Informational**: {s.get('low_count', 0)}")
    md.append(f"- **Missing Assumptions Detected**: {s.get('missing_assumptions_count', 0)}")
    md.append(f"- **Overlooked Constraints**: {s.get('overlooked_constraints_count', 0)}")
    md.append(f"- **Dataset Anomalies / Risks**: {s.get('data_risks_count', 0)}")
    md.append(f"- **Workflow Single Points of Failure**: {s.get('workflow_bottlenecks_count', 0)}\n")

    md.append("---")
    md.append("## 3. Prioritized Blind Spots & Discoveries")

    for idx, d in enumerate(data.discoveries, 1):
        sev_icon = "🚨" if d.severity == SeverityLevel.CRITICAL else ("⚠️" if d.severity == SeverityLevel.HIGH else "⚡")
        md.append(f"### {idx}. {sev_icon} [{d.severity.upper()}] {d.title}")
        md.append(f"- **Category**: `{d.category.value}` | **RPN Score**: `{d.rpn}` (Impact: {d.impact_score}/5, Likelihood: {d.likelihood_score}/5, Invisibility: {d.detectability_score}/5)")
        md.append(f"- **Location**: `{d.location}`")
        if d.cognitive_bias:
            md.append(f"- **Cognitive Bias Identified**: *{d.cognitive_bias}*")
        md.append(f"- **Status**: `{d.status.upper()}`")
        md.append(f"\n**Evidence Grounding**:")
        md.append(f"> \"{d.evidence}\"\n")
        md.append(f"**Summary**:\n{d.summary}\n")
        md.append(f"**Failure Scenario Blast Radius**:\n{d.failure_scenario}\n")
        md.append(f"**Evidence-Based Recommendation**:\n{d.recommendation}\n")
        if d.action_items:
            md.append("**Actionable Remediation Checklist**:")
            for act in d.action_items:
                md.append(f"- [ ] {act}")
            md.append("")
        if d.mitigation_code:
            md.append("**Defensive Guardrail Snippet**:")
            md.append(f"```python\n{d.mitigation_code}\n```\n")
        md.append("---")

    if data.probing_questions:
        md.append("## 4. Critical Unasked Questions (\"Unknown Unknowns\")")
        for q_idx, q in enumerate(data.probing_questions, 1):
            md.append(f"### Q{q_idx}: {q.question}")
            md.append(f"**Strategic Implication**: {q.why_it_matters}\n")
            if q.suggested_options:
                md.append("**Evaluated Strategic Paths**:")
                for opt in q.suggested_options:
                    md.append(f"- {opt}")
                md.append("")
            if q.user_answer:
                md.append(f"**Project Decision Recorded**: *{q.user_answer}*\n")
            md.append("---")

    return "\n".join(md)

def generate_html_report(data: AnalysisResponse) -> str:
    md_content = generate_markdown_report(data)
    # Simple clean styling wrapper for printing or browser rendering
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{data.project_name} - Audit Report</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #1e293b; max-width: 900px; margin: 40px auto; padding: 0 20px; }}
    h1 {{ color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 12px; }}
    h2 {{ color: #1e293b; margin-top: 30px; border-bottom: 1px solid #cbd5e1; padding-bottom: 8px; }}
    h3 {{ color: #334155; margin-top: 24px; }}
    blockquote {{ border-left: 4px solid #3b82f6; margin: 12px 0; padding: 8px 16px; background-color: #f8fafc; color: #475569; font-style: italic; }}
    pre {{ background: #0f172a; color: #f8fafc; padding: 16px; border-radius: 8px; overflow-x: auto; font-family: 'Consolas', monospace; font-size: 13px; }}
    code {{ background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-family: monospace; font-size: 13px; }}
    pre code {{ background: transparent; padding: 0; }}
    .badge {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; }}
    @media print {{ body {{ max-width: 100%; margin: 20px; }} }}
  </style>
</head>
<body>
<pre style="white-space: pre-wrap; font-family: inherit; background: transparent; color: inherit; padding: 0;">
{md_content}
</pre>
</body>
</html>
"""
    return html
