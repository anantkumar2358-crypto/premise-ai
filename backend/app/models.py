from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class DiscoveryCategory(str, Enum):
    MISSING_ASSUMPTION = "missing_assumption"
    OVERLOOKED_CONSTRAINT = "overlooked_constraint"
    UNASKED_QUESTION = "unasked_question"
    DATA_RISK = "data_risk"
    WORKFLOW_BOTTLENECK = "workflow_bottleneck"

class SeverityLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class DiscoveryItem(BaseModel):
    id: str = Field(..., description="Unique identifier for discovery")
    title: str = Field(..., description="Concise headline of the discovery")
    category: DiscoveryCategory = Field(..., description="Type of discovery")
    severity: SeverityLevel = Field(..., description="Calculated severity level")
    impact_score: int = Field(..., ge=1, le=5, description="Impact from 1 (minor) to 5 (catastrophic)")
    likelihood_score: int = Field(..., ge=1, le=5, description="Likelihood from 1 (rare) to 5 (almost certain)")
    detectability_score: int = Field(..., ge=1, le=5, description="Invisibility/Subtlety from 1 (obvious) to 5 (completely hidden)")
    rpn: int = Field(..., description="Risk Priority Number: Impact x Likelihood x Detectability (1 to 125)")
    summary: str = Field(..., description="Clear explanation of the unstated assumption or overlooked constraint")
    evidence: str = Field(..., description="Exact quote, data column/metric, or workflow step grounding this finding")
    location: str = Field(..., description="Section, line, column, or step reference")
    cognitive_bias: Optional[str] = Field(None, description="Cognitive bias that likely led to this blind spot")
    failure_scenario: str = Field(..., description="Concrete realistic failure scenario if unaddressed")
    recommendation: str = Field(..., description="Evidence-based actionable recommendation")
    action_items: List[str] = Field(default_factory=list, description="Concrete step-by-step resolution tasks")
    mitigation_code: Optional[str] = Field(None, description="Code, SQL, configuration, or contract clause snippet")
    status: str = Field("open", description="Status: open, acknowledged, or resolved")
    user_notes: Optional[str] = Field(None, description="User comments or mitigations recorded")

class ProbingQuestion(BaseModel):
    id: str = Field(..., description="Unique question ID")
    question: str = Field(..., description="Important unasked question")
    why_it_matters: str = Field(..., description="Rationale and hidden implications")
    related_discovery_id: Optional[str] = Field(None, description="Linked discovery item ID")
    suggested_options: List[str] = Field(default_factory=list, description="Common strategic choices or answers")
    user_answer: Optional[str] = Field(None, description="User-provided answer or decision")
    is_resolved: bool = Field(False, description="Whether the question has been addressed")

class AnalysisRequest(BaseModel):
    project_name: str = Field("Untitled Project", description="Name of project")
    document_text: Optional[str] = Field(None, description="PRD, specification, or strategy doc content")
    document_title: Optional[str] = Field("Project Document", description="Document title")
    dataset_content: Optional[str] = Field(None, description="CSV or JSON tabular data content")
    dataset_name: Optional[str] = Field("Dataset", description="Dataset identifier")
    workflow_content: Optional[str] = Field(None, description="Workflow definition, steps, or pipeline description")
    workflow_type: Optional[str] = Field("steps", description="Format: steps, dag, or text")
    domain: Optional[str] = Field("general", description="Domain: fintech, healthcare, ecommerce, iot_edge, ai_ml, general")
    api_key: Optional[str] = Field(None, description="Optional Gemini API Key")

class DatasetSummary(BaseModel):
    row_count: int
    column_count: int
    columns: List[str]
    missing_value_summary: Dict[str, float]
    data_types: Dict[str, str]
    detected_anomalies: List[str]
    sample_preview: List[Dict[str, Any]]

class WorkflowSummary(BaseModel):
    step_count: int
    steps: List[str]
    has_fallback: bool
    single_points_of_failure: List[str]
    unhandled_timeouts: List[str]

class AnalysisResponse(BaseModel):
    project_name: str
    timestamp: str
    health_score: int = Field(..., ge=0, le=100, description="Project Resilience Score (100 is ideal, 0 is critical risk)")
    risk_priority_index: float
    executive_summary: str
    discoveries: List[DiscoveryItem]
    probing_questions: List[ProbingQuestion]
    summary_stats: Dict[str, Any]
    dataset_profile: Optional[DatasetSummary] = None
    workflow_profile: Optional[WorkflowSummary] = None
    engine_used: str = Field("gemini", description="gemini or heuristics_offline")

class ResolveItemRequest(BaseModel):
    discovery_id: str
    status: str
    notes: Optional[str] = None

class AnswerQuestionRequest(BaseModel):
    question_id: str
    answer: str
