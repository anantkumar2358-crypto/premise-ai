import os
from fastapi import FastAPI, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, PlainTextResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List

from .models import (
    AnalysisRequest,
    AnalysisResponse,
    ResolveItemRequest,
    AnswerQuestionRequest,
    DiscoveryItem,
    ProbingQuestion
)
from .analyzer import run_full_analysis, calculate_health_score
from .data_profiler import profile_dataset
from .templates_data import TEMPLATES
from .report_generator import generate_markdown_report, generate_html_report

app = FastAPI(
    title="Premise: Blind Spot & Assumption Intelligence Engine",
    description="Analyzes project documents, datasets, and workflows to identify missing assumptions, overlooked constraints, and important unasked questions.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store for current analysis to support live status toggling
current_analysis_store: Dict[str, AnalysisResponse] = {}

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "Premise Blind Spot Intelligence Engine"}

@app.get("/api/templates")
def get_templates():
    """Returns summaries of preloaded industry templates."""
    summaries = []
    for k, v in TEMPLATES.items():
        summaries.append({
            "id": v["id"],
            "title": v["title"],
            "domain": v["domain"],
            "badge": v["badge"],
            "description": v["description"]
        })
    return summaries

@app.get("/api/templates/{template_id}")
def get_template(template_id: str):
    """Returns full template content for rapid loading."""
    if template_id not in TEMPLATES:
        raise HTTPException(status_code=404, detail="Template not found")
    return TEMPLATES[template_id]

@app.post("/api/analyze", response_model=AnalysisResponse)
def analyze_project(request: AnalysisRequest):
    """
    Primary endpoint: analyzes project documents, datasets, and workflows.
    Grounds discoveries with evidence, scores RPN, and provides actionable recommendations.
    """
    try:
        response = run_full_analysis(request)
        current_analysis_store["latest"] = response
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/profile-dataset")
def profile_dataset_endpoint(payload: Dict[str, str] = Body(...)):
    """Profiles tabular data without running full doc analysis."""
    content = payload.get("content", "")
    name = payload.get("name", "Dataset")
    summary, discoveries = profile_dataset(content, name)
    return {
        "summary": summary,
        "discoveries": discoveries
    }

@app.post("/api/resolve-item")
def resolve_item(req: ResolveItemRequest):
    """
    Updates status of a discovery item (e.g. open -> acknowledged -> resolved).
    Dynamically recalculates and returns updated health score and RPI.
    """
    latest = current_analysis_store.get("latest")
    if not latest:
        raise HTTPException(status_code=400, detail="No active analysis session found")

    target = None
    for disc in latest.discoveries:
        if disc.id == req.discovery_id:
            disc.status = req.status
            if req.notes:
                disc.user_notes = req.notes
            target = disc
            break

    if not target:
        raise HTTPException(status_code=404, detail="Discovery item not found")

    new_health, new_rpi = calculate_health_score(latest.discoveries, latest.probing_questions)
    latest.health_score = new_health
    latest.risk_priority_index = new_rpi

    return {
        "success": True,
        "discovery_id": target.id,
        "status": target.status,
        "health_score": new_health,
        "risk_priority_index": new_rpi
    }

@app.post("/api/answer-question")
def answer_question(req: AnswerQuestionRequest):
    """
    Records user answer to an unasked question and recalculates resilience score.
    """
    latest = current_analysis_store.get("latest")
    if not latest:
        raise HTTPException(status_code=400, detail="No active analysis session found")

    target = None
    for q in latest.probing_questions:
        if q.id == req.question_id:
            q.user_answer = req.answer
            q.is_resolved = True
            target = q
            break

    if not target:
        raise HTTPException(status_code=404, detail="Question not found")

    new_health, new_rpi = calculate_health_score(latest.discoveries, latest.probing_questions)
    latest.health_score = new_health
    latest.risk_priority_index = new_rpi

    return {
        "success": True,
        "question_id": target.id,
        "user_answer": target.user_answer,
        "health_score": new_health,
        "risk_priority_index": new_rpi
    }

@app.post("/api/export-report/markdown", response_class=PlainTextResponse)
def export_markdown(data: AnalysisResponse):
    """Generates markdown export of the audit report."""
    return generate_markdown_report(data)

@app.post("/api/export-report/html", response_class=HTMLResponse)
def export_html(data: AnalysisResponse):
    """Generates printable HTML export of the audit report."""
    return generate_html_report(data)

# Mount frontend static directory
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "static"))
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
