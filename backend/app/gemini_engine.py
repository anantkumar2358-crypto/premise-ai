import os
import json
import logging
from typing import List, Tuple, Optional, Dict, Any
from google import genai
from google.genai import types
from .models import DiscoveryItem, ProbingQuestion, DiscoveryCategory, SeverityLevel

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are a Principal Enterprise Systems Architect, Risk Auditor, and Devil's Advocate for software engineering, data science, and business systems.

Your objective:
Thoroughly analyze the provided project documentation, dataset profile, and workflow definition to uncover:
1. MISSING ASSUMPTIONS: Critical operational, scale, user behavior, network, or data assumptions the creators took for granted without stating or verifying.
2. OVERLOOKED CONSTRAINTS: Hard technical, financial, legal/regulatory, concurrency, biological, or organizational boundaries that will trigger production failures.
3. CRITICAL UNASKED QUESTIONS: Deep, probing questions that illuminate "unknown unknowns" and second-order consequences.

For every discovery:
- Ground it with an exact quotation or reference snippet from the input.
- Assign an Impact Score (1-5: 1=negligible, 5=catastrophic/fatal to project).
- Assign a Likelihood Score (1-5: 1=rare edge case, 5=almost certain in production).
- Assign a Detectability/Subtlety Score (1-5: 1=immediately visible in testing, 5=silent/insidious until production scale).
- Calculate RPN (Risk Priority Number = Impact * Likelihood * Detectability, range 1 to 125).
- Identify the Cognitive Bias that caused the author to miss this (e.g., Happy Path Fallacy, Survivorship Bias, Availability Heuristic, Illusion of Control).
- Describe a concrete, realistic Failure Scenario in production.
- Provide an Evidence-Based Recommendation with 3 actionable checklist items and a defensive code/configuration/policy snippet.

You MUST respond strictly with a valid JSON object matching this schema:
{
  "executive_summary": "High-level risk narrative summarizing the primary blind spots and architectural exposure.",
  "discoveries": [
    {
      "id": "gemini-disc-1",
      "title": "Short punchy title of discovery",
      "category": "missing_assumption" | "overlooked_constraint" | "unasked_question" | "data_risk" | "workflow_bottleneck",
      "severity": "critical" | "high" | "medium" | "low",
      "impact_score": 1-5,
      "likelihood_score": 1-5,
      "detectability_score": 1-5,
      "rpn": integer,
      "summary": "Clear explanation of the unstated assumption or overlooked constraint",
      "evidence": "Direct quote or data point grounding this finding",
      "location": "Document section, dataset column, or workflow step",
      "cognitive_bias": "Name of cognitive bias",
      "failure_scenario": "Narrative of production breakdown",
      "recommendation": "Concrete mitigation strategy",
      "action_items": ["Action 1", "Action 2", "Action 3"],
      "mitigation_code": "Defensive code, SQL, or config snippet"
    }
  ],
  "probing_questions": [
    {
      "id": "q-1",
      "question": "Deep probing question highlighting an unknown unknown",
      "why_it_matters": "Why answering this is critical to project viability",
      "related_discovery_id": "gemini-disc-1",
      "suggested_options": ["Option A", "Option B", "Option C"]
    }
  ]
}
"""

def analyze_with_gemini(
    doc_text: Optional[str],
    dataset_summary: Optional[Dict[str, Any]],
    workflow_summary: Optional[Dict[str, Any]],
    domain: str = "general",
    api_key: Optional[str] = None
) -> Tuple[Optional[str], List[DiscoveryItem], List[ProbingQuestion]]:
    """
    Invokes Gemini 2.5 Flash using google-genai SDK to perform deep blind spot analysis.
    Returns (executive_summary, discoveries, probing_questions).
    """
    effective_api_key = api_key or os.environ.get("GEMINI_API_KEY")
    if not effective_api_key:
        return None, [], []

    try:
        client = genai.Client(api_key=effective_api_key)

        prompt_parts = [
            f"### Domain Context: {domain}\n",
        ]

        if doc_text and doc_text.strip():
            prompt_parts.append(f"### PROJECT DOCUMENTATION:\n{doc_text}\n")

        if dataset_summary:
            prompt_parts.append(f"### DATASET PROFILE & ANOMALIES:\n{json.dumps(dataset_summary, indent=2)}\n")

        if workflow_summary:
            prompt_parts.append(f"### WORKFLOW & PIPELINE DEFINITION:\n{json.dumps(workflow_summary, indent=2)}\n")

        user_content = "\n".join(prompt_parts)

        # Try gemini-2.5-flash or gemini-1.5-flash
        model_name = "gemini-2.5-flash"
        
        response = client.models.generate_content(
            model=model_name,
            contents=user_content,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
                temperature=0.2
            )
        )

        raw_text = response.text
        if not raw_text:
            return None, [], []

        data = json.loads(raw_text)
        exec_summary = data.get("executive_summary", "")

        discoveries: List[DiscoveryItem] = []
        for d in data.get("discoveries", []):
            try:
                # Ensure severity matches RPN if needed
                impact = int(d.get("impact_score", 3))
                likelihood = int(d.get("likelihood_score", 3))
                detectability = int(d.get("detectability_score", 3))
                rpn = impact * likelihood * detectability

                severity_str = d.get("severity", "medium").lower()
                if severity_str not in ["critical", "high", "medium", "low"]:
                    severity_str = "critical" if rpn >= 60 else ("high" if rpn >= 36 else ("medium" if rpn >= 16 else "low"))

                cat_str = d.get("category", "missing_assumption").lower()
                if cat_str not in [c.value for c in DiscoveryCategory]:
                    cat_str = DiscoveryCategory.MISSING_ASSUMPTION.value

                item = DiscoveryItem(
                    id=str(d.get("id", f"gemini-{len(discoveries)+1}")),
                    title=str(d.get("title", "Identified Blind Spot")),
                    category=DiscoveryCategory(cat_str),
                    severity=SeverityLevel(severity_str),
                    impact_score=impact,
                    likelihood_score=likelihood,
                    detectability_score=detectability,
                    rpn=rpn,
                    summary=str(d.get("summary", "")),
                    evidence=str(d.get("evidence", "Contextual architectural analysis")),
                    location=str(d.get("location", "Architecture Specification")),
                    cognitive_bias=d.get("cognitive_bias"),
                    failure_scenario=str(d.get("failure_scenario", "")),
                    recommendation=str(d.get("recommendation", "")),
                    action_items=d.get("action_items", []),
                    mitigation_code=d.get("mitigation_code"),
                    status="open"
                )
                discoveries.append(item)
            except Exception as item_err:
                logger.warning(f"Failed to parse discovery item: {item_err}")
                continue

        probing_questions: List[ProbingQuestion] = []
        for q in data.get("probing_questions", []):
            try:
                pq = ProbingQuestion(
                    id=str(q.get("id", f"q-{len(probing_questions)+1}")),
                    question=str(q.get("question", "")),
                    why_it_matters=str(q.get("why_it_matters", "")),
                    related_discovery_id=q.get("related_discovery_id"),
                    suggested_options=q.get("suggested_options", [])
                )
                probing_questions.append(pq)
            except Exception as q_err:
                logger.warning(f"Failed to parse probing question: {q_err}")
                continue

        return exec_summary, discoveries, probing_questions

    except Exception as e:
        logger.error(f"Gemini API analysis failed: {e}")
        return None, [], []
