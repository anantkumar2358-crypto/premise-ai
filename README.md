# 🛡️ Premise: Project Blind Spot & Assumption Intelligence Engine

> **Intelligent multi-asset auditor that interrogates project specifications, datasets, and workflow pipelines to uncover missing assumptions, overlooked constraints, and critical questions teams never thought to ask.**

---

## 🎯 Executive Overview

Modern engineering, data, and product teams suffer from cognitive biases during system design:
* **The Happy-Path Fallacy**: Assuming external APIs and network connections never timeout or drop packets.
* **The Exactly-Once Illusion**: Mutating financial, provisioning, or notification state without distributed idempotency keys.
* **Survivorship Bias & Data Lineage Neglect**: Training ML models or writing business rules on historical approved records while ignoring sentinel codes (`-1`, `-99`) and silent missingness.
* **Compounding Overhead Blind Spots**: Persisting logs and vector embeddings indefinitely without retention policies, TTLs, or cost budgets.

**Premise** is an intelligent audit engine designed to act as a World-Class Principal Architect, Compliance Auditor, and Devil's Advocate. It ingests:
1. **Project Documents**: PRDs, Architecture Decision Records (ADRs), System Specifications, RFPs.
2. **Datasets**: Tabular CSVs, JSON arrays, data dictionaries, schema contracts.
3. **Workflows & Pipelines**: Step-by-step business flows, DAGs, sequence diagrams, YAML configs.

It outputs prioritized, evidence-grounded discoveries with concrete blast-radius failure scenarios and executable defensive guardrails.

---

## 🚀 Key Features

### 1. Multi-Modal Artifact Ingestion
* **Document Ingestion**: Analyzes text and markdown specs for architectural boundaries, scale ceilings, and regulatory exposure.
* **Automated Data Profiler**: Inspects tabular records for null-tolerance assumptions, extreme class imbalances, sentinel code contamination, and biological/physical range violations.
* **Workflow & Pipeline Auditor**: Identifies Single Points of Failure (SPOFs), missing idempotency on mutating calls, unhandled timeout branches, and absence of compensating Saga transactions.

### 2. Multi-Dimensional Prioritization (RPN Engine)
Every finding is scored using the standard **Risk Priority Number (RPN)** framework:
$$\text{RPN} = \text{Impact (1-5)} \times \text{Likelihood (1-5)} \times \text{Detectability/Invisibility (1-5)}$$
* 🚨 **CRITICAL (RPN 60–125)**: Immediate threat to viability, safety, or launch.
* ⚠️ **HIGH (RPN 36–59)**: Substantial architectural debt, compliance breach, 5x cost overrun.
* ⚡ **MEDIUM (RPN 16–35)**: Operational friction, edge-case degradation.
* ℹ️ **LOW (RPN 1–15)**: Hardening recommendations and defensive documentation.

### 3. Evidence-Grounded Recommendations
Findings are never vague:
* **Exact Evidence Excerpt**: Direct quote or data statistic from the ingested artifact.
* **Cognitive Bias Identified**: Diagnostic of *why* the author missed it (e.g. *Availability Heuristic*, *Base Rate Neglect*).
* **Production Failure Scenario**: Concrete operational failure narrative.
* **Remediation Checklist**: 3-step actionable remediation tasks.
* **Defensive Guardrail Snippet**: Copy-pasteable Python, SQL, or configuration code.

### 4. Interactive What-If Simulation & Probing Interview
* **Resilience Health Score (0-100)**: Dynamically calculated based on open risk severity.
* **Live Mitigation**: Mark discoveries as resolved or record implementation decisions to watch your resilience score rebound in real-time.
* **"Unknown Unknowns" Interview**: Interactive probing questions allowing stakeholders to formulate and document strategic decisions.

### 5. Dual Cognitive Engine: Gemini 2.5 Flash + Deterministic Heuristics
* **Gemini 2.5 Flash Integration**: Deep semantic reasoning powered by the official `google-genai` SDK for synthesis of non-obvious cross-domain risks.
* **Deterministic Offline Engine**: Expert rule engine ensuring instant, reliable offline operation without requiring an API key.

---

## 🛠️ Architecture

```
d:\CODE\Google AI Studio\p7\
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI server, REST routes, static file serving
│   │   ├── models.py            # Pydantic schemas (DiscoveryItem, ProbingQuestion, etc.)
│   │   ├── analyzer.py          # Master analysis coordinator & dynamic health scoring
│   │   ├── data_profiler.py     # Tabular dataset anomaly & sentinel code detector
│   │   ├── workflow_engine.py   # Pipeline auditor (idempotency, SPOFs, Sagas)
│   │   ├── heuristics_engine.py # Deterministic domain risk knowledge base
│   │   ├── gemini_engine.py     # Gemini 2.5 Flash SDK integration
│   │   ├── report_generator.py  # Markdown and HTML executive report exporter
│   │   └── templates_data.py    # Pre-built industry templates (Healthcare, FinTech, E-Commerce, IoT)
│   └── tests/
│       ├── test_analyzer.py
│       ├── test_data_profiler.py
│       └── test_workflow.py
├── frontend/
│   └── static/
│       ├── index.html           # Modern responsive dashboard with 5x5 Risk Matrix
│       ├── app.js               # Reactive state manager, filter engine, live health recalculator
│       └── styles.css           # Custom styling, glow effects, and matrix cell layout
├── cli.py                       # CLI tool for terminal and CI/CD quality gates
├── run.py                       # Server runner with automatic port discovery
├── requirements.txt
└── README.md
```

---

## 🏁 Quickstart Guide

### 1. Installation
```powershell
pip install -r requirements.txt
```

### 2. Launch the Web Application
```powershell
python run.py
```
Open **`http://localhost:8001`** in your browser.
* Explore the interactive **5x5 Risk Heatmap Matrix**.
* Test pre-built templates:
  * 🩺 **MedAI Clinical Triage**: Clinical AI, SpO2 sensor bias, emergency break-glass, unbounded telemetry.
  * 💳 **CrediFlow Subprime Lending**: Instant approval, survivorship bias, negative sentinels, idempotency.
  * ⚡ **HyperCart Flash Sale**: High throughput, database locking, distributed saga rollback omissions.
  * 🚗 **FleetPulse IoT Telematics**: Cellular dead zones, clock drift, flash memory wear.
* Enter a custom Google Gemini API Key in the settings modal or run completely offline with built-in heuristics.

### 3. Run Automated Audits via CLI
Premise can run in terminal workflows and CI/CD build pipelines:

```powershell
# Run audit using a template
python cli.py --template fintech_lending --out fintech_audit.md

# Audit custom files
python cli.py --doc specs/prd.md --dataset data/training.csv --workflow pipeline.txt --min-health 70 --out report.md
```
*(If `--min-health` is specified, the CLI returns exit code `1` if the project resilience score falls below the required threshold, enabling automated pull request gating!)*

### 4. Run Test Suite
```powershell
python -m pytest backend/tests -v
```

---

## 📊 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check endpoint |
| `GET` | `/api/templates` | Lists all pre-configured industry templates |
| `GET` | `/api/templates/{id}` | Returns document, dataset, and workflow for a specific template |
| `POST` | `/api/analyze` | Executes multi-modal audit and returns prioritized discoveries |
| `POST` | `/api/profile-dataset` | Standalone tabular dataset anomaly profiler |
| `POST` | `/api/resolve-item` | Marks discovery item as resolved/acknowledged and recalculates health score |
| `POST` | `/api/answer-question` | Submits strategic decision for unasked question and recalculates health score |
| `POST` | `/api/export-report/markdown` | Generates structured Markdown audit report |
| `POST` | `/api/export-report/html` | Generates printable HTML audit report |
