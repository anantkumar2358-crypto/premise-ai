import datetime
from typing import List, Dict, Any, Tuple
from .models import (
    AnalysisRequest,
    AnalysisResponse,
    DiscoveryItem,
    ProbingQuestion,
    SeverityLevel,
    DiscoveryCategory
)
from .data_profiler import profile_dataset
from .workflow_engine import analyze_workflow
from .heuristics_engine import run_heuristics_analysis
from .gemini_engine import analyze_with_gemini

def calculate_health_score(discoveries: List[DiscoveryItem], questions: List[ProbingQuestion]) -> Tuple[int, float]:
    """
    Computes resilience health score (0-100) and aggregate Risk Priority Index (RPI).
    Resolved items don't penalize the score.
    """
    base_score = 100.0
    total_rpn = 0.0

    penalty_map = {
        SeverityLevel.CRITICAL: 16.0,
        SeverityLevel.HIGH: 9.0,
        SeverityLevel.MEDIUM: 4.5,
        SeverityLevel.LOW: 1.5,
    }

    for disc in discoveries:
        if disc.status != "resolved":
            weight = 0.5 if disc.status == "acknowledged" else 1.0
            penalty = penalty_map.get(disc.severity, 4.0) * weight
            base_score -= penalty
            total_rpn += disc.rpn * weight

    # Probing questions penalty if unanswered
    unanswered_q = sum(1 for q in questions if not q.is_resolved and not q.user_answer)
    base_score -= min(15.0, unanswered_q * 2.5)

    health_score = max(0, min(100, int(round(base_score))))
    return health_score, round(total_rpn, 1)

def run_full_analysis(request: AnalysisRequest) -> AnalysisResponse:
    """
    Orchestrates multi-modal ingestion across project documents,
    datasets, and workflows. Combines data profiling, workflow parsing,
    expert heuristics, and Gemini LLM reasoning.
    """
    all_discoveries: List[DiscoveryItem] = []
    all_questions: List[ProbingQuestion] = []
    engine_used = "heuristics_offline"

    # 1. Profile Dataset (if provided)
    dataset_summary = None
    if request.dataset_content and request.dataset_content.strip():
        dataset_summary, data_disc = profile_dataset(
            request.dataset_content,
            name=request.dataset_name or "Project Dataset"
        )
        all_discoveries.extend(data_disc)

    # 2. Analyze Workflow (if provided)
    workflow_summary = None
    if request.workflow_content and request.workflow_content.strip():
        workflow_summary, wf_disc = analyze_workflow(request.workflow_content)
        all_discoveries.extend(wf_disc)

    # 3. Deterministic Heuristics
    heur_disc, heur_q = run_heuristics_analysis(
        request.document_text or "",
        domain=request.domain or "general"
    )
    all_discoveries.extend(heur_disc)
    all_questions.extend(heur_q)

    # 4. Gemini Cognitive Engine (if API key available)
    gemini_summary, gemini_disc, gemini_q = analyze_with_gemini(
        doc_text=request.document_text,
        dataset_summary=dataset_summary.model_dump() if dataset_summary else None,
        workflow_summary=workflow_summary.model_dump() if workflow_summary else None,
        domain=request.domain or "general",
        api_key=request.api_key
    )

    if gemini_disc or gemini_q:
        engine_used = "gemini_2.5_flash"
        # Prepend Gemini discoveries to give LLM high context prominence
        all_discoveries = gemini_disc + all_discoveries
        all_questions = gemini_q + all_questions

    # 5. Deduplication by title similarity
    seen_titles = set()
    unique_discoveries: List[DiscoveryItem] = []
    for d in all_discoveries:
        norm_title = "".join(filter(str.isalnum, d.title.lower()))[:30]
        if norm_title not in seen_titles:
            seen_titles.add(norm_title)
            unique_discoveries.append(d)

    # Sort discoveries by Risk Priority Number (RPN) descending
    unique_discoveries.sort(key=lambda x: x.rpn, reverse=True)

    # 6. Deduplicate questions
    seen_q = set()
    unique_questions: List[ProbingQuestion] = []
    for q in all_questions:
        norm_q = "".join(filter(str.isalnum, q.question.lower()))[:30]
        if norm_q not in seen_q:
            seen_q.add(norm_q)
            unique_questions.append(q)

    # 7. Compute health and metrics
    health_score, total_rpn = calculate_health_score(unique_discoveries, unique_questions)

    # Summary statistics
    stats = {
        "total_discoveries": len(unique_discoveries),
        "critical_count": sum(1 for d in unique_discoveries if d.severity == SeverityLevel.CRITICAL),
        "high_count": sum(1 for d in unique_discoveries if d.severity == SeverityLevel.HIGH),
        "medium_count": sum(1 for d in unique_discoveries if d.severity == SeverityLevel.MEDIUM),
        "low_count": sum(1 for d in unique_discoveries if d.severity == SeverityLevel.LOW),
        "missing_assumptions_count": sum(1 for d in unique_discoveries if d.category == DiscoveryCategory.MISSING_ASSUMPTION),
        "overlooked_constraints_count": sum(1 for d in unique_discoveries if d.category == DiscoveryCategory.OVERLOOKED_CONSTRAINT),
        "data_risks_count": sum(1 for d in unique_discoveries if d.category == DiscoveryCategory.DATA_RISK),
        "workflow_bottlenecks_count": sum(1 for d in unique_discoveries if d.category == DiscoveryCategory.WORKFLOW_BOTTLENECK),
        "unasked_questions_count": len(unique_questions),
        "total_rpn": total_rpn,
    }

    # Generate executive summary if not provided by Gemini
    if not gemini_summary:
        crit_n = stats["critical_count"]
        high_n = stats["high_count"]
        top_risks = [d.title for d in unique_discoveries[:3]]
        gemini_summary = (
            f"Audit conducted across {request.project_name}. Identified {len(unique_discoveries)} blind spots "
            f"({crit_n} Critical, {high_n} High Priority). Current architectural health index stands at {health_score}/100. "
            f"Primary failure modes center around: {', '.join(top_risks) if top_risks else 'System edge boundaries'}. "
            "Evidence-based mitigations, concurrency controls, and schema assertions should be applied before production deployment."
        )

    return AnalysisResponse(
        project_name=request.project_name or "Project Audit",
        timestamp=datetime.datetime.now().isoformat(),
        health_score=health_score,
        risk_priority_index=total_rpn,
        executive_summary=gemini_summary,
        discoveries=unique_discoveries,
        probing_questions=unique_questions,
        summary_stats=stats,
        dataset_profile=dataset_summary,
        workflow_profile=workflow_summary,
        engine_used=engine_used
    )
