#!/usr/bin/env python3
"""
CLI tool for Premise: Project Blind Spot & Assumption Intelligence Engine.
Run automated audits on documents, datasets, and workflows in terminal or CI/CD pipelines.
"""

import sys
import argparse
import json
import os
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Ensure Windows terminal prints unicode cleanly
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from backend.app.models import AnalysisRequest
from backend.app.analyzer import run_full_analysis
from backend.app.report_generator import generate_markdown_report, generate_html_report
from backend.app.templates_data import TEMPLATES

def main():
    parser = argparse.ArgumentParser(
        description="Premise: Analyze project documents, datasets, or workflows to identify missing assumptions, overlooked constraints, and important unasked questions."
    )
    parser.add_argument("--doc", "-d", type=str, help="Path to project document (PRD, markdown, or text)")
    parser.add_argument("--dataset", "-s", type=str, help="Path to tabular dataset (CSV or JSON)")
    parser.add_argument("--workflow", "-w", type=str, help="Path to workflow definition or pipeline file")
    parser.add_argument("--domain", type=str, default="general", choices=["healthcare", "fintech", "ecommerce", "iot_edge", "ai_ml", "general"], help="Industry domain")
    parser.add_argument("--name", "-n", type=str, default="Project Audit", help="Project name")
    parser.add_argument("--template", "-t", type=str, choices=list(TEMPLATES.keys()), help="Load a pre-configured template")
    parser.add_argument("--out", "-o", type=str, default="audit_report.md", help="Output report file path (.md, .html, or .json)")
    parser.add_argument("--min-health", type=int, default=0, help="Minimum resilience health score (exit with code 1 if below threshold)")

    args = parser.parse_args()

    doc_text = None
    data_content = None
    wf_content = None
    proj_name = args.name
    domain = args.domain

    if args.template:
        tmpl = TEMPLATES[args.template]
        doc_text = tmpl["document_text"]
        data_content = tmpl["dataset_content"]
        wf_content = tmpl["workflow_content"]
        proj_name = tmpl["title"]
        domain = tmpl["domain"]
        print(f"Loaded template: {tmpl['title']} ({tmpl['badge']})")

    if args.doc:
        doc_path = Path(args.doc)
        if not doc_path.exists():
            print(f"Error: Document file not found at {args.doc}", file=sys.stderr)
            sys.exit(1)
        doc_text = doc_path.read_text(encoding="utf-8")

    if args.dataset:
        data_path = Path(args.dataset)
        if not data_path.exists():
            print(f"Error: Dataset file not found at {args.dataset}", file=sys.stderr)
            sys.exit(1)
        data_content = data_path.read_text(encoding="utf-8")

    if args.workflow:
        wf_path = Path(args.workflow)
        if not wf_path.exists():
            print(f"Error: Workflow file not found at {args.workflow}", file=sys.stderr)
            sys.exit(1)
        wf_content = wf_path.read_text(encoding="utf-8")

    if not doc_text and not data_content and not wf_content:
        print("Error: Please provide at least one input (--doc, --dataset, --workflow, or --template).", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    print(f"Auditing '{proj_name}' (Domain: {domain})...")

    request = AnalysisRequest(
        project_name=proj_name,
        document_text=doc_text,
        dataset_content=data_content,
        workflow_content=wf_content,
        domain=domain,
        api_key=os.environ.get("GEMINI_API_KEY")
    )

    response = run_full_analysis(request)

    print("\n" + "=" * 60)
    print(f"🛡️  PREMISE AUDIT SUMMARY: {response.project_name}")
    print("=" * 60)
    print(f"Resilience Health Score: {response.health_score}/100")
    print(f"Risk Priority Index (RPI): {response.risk_priority_index}")
    print(f"Total Discoveries: {len(response.discoveries)}")
    print(f"  - 🚨 Critical Showstoppers: {response.summary_stats.get('critical_count', 0)}")
    print(f"  - ⚠️  High Priority Risks:  {response.summary_stats.get('high_count', 0)}")
    print(f"  - ⚡ Medium Risks:         {response.summary_stats.get('medium_count', 0)}")
    print(f"  - ℹ️  Low / Informational:  {response.summary_stats.get('low_count', 0)}")
    print(f"Unknown Unknowns Identified: {len(response.probing_questions)}")
    print("=" * 60)

    # Save output
    out_path = Path(args.out)
    if out_path.suffix.lower() == ".json":
        out_path.write_text(response.model_dump_json(indent=2), encoding="utf-8")
    elif out_path.suffix.lower() in [".html", ".htm"]:
        out_path.write_text(generate_html_report(response), encoding="utf-8")
    else:
        out_path.write_text(generate_markdown_report(response), encoding="utf-8")

    print(f"Report generated successfully: {out_path.resolve()}")

    if args.min_health > 0 and response.health_score < args.min_health:
        print(f"\n[CI Gate Failed] Resilience score ({response.health_score}) is below required threshold ({args.min_health}).", file=sys.stderr)
        sys.exit(1)

    print("\nAudit completed with exit code 0.")

if __name__ == "__main__":
    main()
