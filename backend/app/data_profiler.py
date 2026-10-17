import io
import uuid
import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Any, Optional
from .models import DiscoveryItem, DiscoveryCategory, SeverityLevel, DatasetSummary

def profile_dataset(content: str, name: str = "Dataset") -> Tuple[Optional[DatasetSummary], List[DiscoveryItem]]:
    """
    Profiles tabular data (CSV or JSON string) and generates evidence-based
    discoveries regarding unstated data assumptions, missing constraints, and distribution risks.
    """
    if not content or not content.strip():
        return None, []

    df = None
    try:
        # Try CSV first
        df = pd.read_csv(io.StringIO(content.strip()))
    except Exception:
        try:
            # Try JSON
            df = pd.read_json(io.StringIO(content.strip()))
        except Exception as e:
            # Not valid tabular data
            return None, []

    if df is None or df.empty:
        return None, []

    total_rows = len(df)
    total_cols = len(df.columns)
    columns = list(df.columns)

    missing_percentages = {}
    data_types = {}
    anomalies = []
    discoveries: List[DiscoveryItem] = []

    for col in columns:
        missing_count = df[col].isnull().sum()
        pct = float((missing_count / total_rows) * 100) if total_rows > 0 else 0.0
        missing_percentages[col] = round(pct, 2)
        data_types[col] = str(df[col].dtype)

        # Rule 1: High missing rate (Silent Null Assumption)
        if pct > 15.0:
            severity = SeverityLevel.CRITICAL if pct > 40.0 else SeverityLevel.HIGH
            impact = 4 if pct > 40.0 else 3
            likelihood = 5
            detectability = 2
            rpn = impact * likelihood * detectability

            anomalies.append(f"Column '{col}' has {pct:.1f}% missing values.")
            discoveries.append(DiscoveryItem(
                id=f"data-{uuid.uuid4().hex[:6]}",
                title=f"Unstated Null Tolerance Assumption in '{col}'",
                category=DiscoveryCategory.DATA_RISK,
                severity=severity,
                impact_score=impact,
                likelihood_score=likelihood,
                detectability_score=detectability,
                rpn=rpn,
                summary=(
                    f"System or downstream consumers likely assume '{col}' is consistently present, "
                    f"yet {pct:.1f}% ({missing_count} of {total_rows}) of records contain null/missing values. "
                    "Without explicit fallback or imputation logic, this will trigger unhandled NullPointerExceptions or silent imputation distortions."
                ),
                evidence=f"Column '{col}' exhibits {pct:.1f}% null rate across {total_rows} sample records.",
                location=f"Dataset '{name}' -> Column '{col}'",
                cognitive_bias="Availability Heuristic & Happy Path Data Ingestion",
                failure_scenario=(
                    f"In production, incoming payloads without '{col}' bypass default filters, "
                    "causing microservices to crash or machine learning models to predict default fallbacks without auditing."
                ),
                recommendation=(
                    f"Formally declare null-handling policy for '{col}': enforce schema validation with reject-queues "
                    "or implement explicit semantic imputation (e.g., MICE, forward-fill, or explicit 'UNKNOWN' sentinel)."
                ),
                action_items=[
                    f"Add schema constraint validating non-nullity or valid default for '{col}' at API gateway.",
                    f"Verify whether missingness in '{col}' is Missing At Random (MAR) or Missing Not At Random (MNAR).",
                    "Add automated data contract alerts on null rate threshold breach (>5%)."
                ],
                mitigation_code=(
                    f"# Python / Pydantic schema validation guardrail\n"
                    f"from pydantic import BaseModel, Field\n\n"
                    f"class RecordValidator(BaseModel):\n"
                    f"    {col}: Optional[str] = Field(default=None)\n"
                    f"    @classmethod\n"
                    f"    def validate_missing(cls, v):\n"
                    f"        if v is None:\n"
                    f"            # Log telemetry and route to secondary triage\n"
                    f"            pass\n"
                    f"        return v"
                ),
                status="open"
            ))

        # Check numerical columns
        if pd.api.types.is_numeric_dtype(df[col]):
            non_null = df[col].dropna()
            if not non_null.empty:
                min_val = float(non_null.min())
                max_val = float(non_null.max())
                col_lower = col.lower()

                # Rule 2: Sentinel Negative Values in Non-Negative Domains
                non_neg_indicators = ["age", "income", "salary", "price", "amount", "count", "score", "heart_rate", "rate", "distance", "duration", "latency"]
                if any(ind in col_lower for ind in non_neg_indicators) and min_val < 0:
                    neg_count = int((non_null < 0).sum())
                    neg_pct = round((neg_count / len(non_null)) * 100, 1)
                    anomalies.append(f"Negative values detected in strictly non-negative column '{col}' (min: {min_val}).")
                    discoveries.append(DiscoveryItem(
                        id=f"data-{uuid.uuid4().hex[:6]}",
                        title=f"Overlooked Sentinel Values / Negative Numbers in '{col}'",
                        category=DiscoveryCategory.OVERLOOKED_CONSTRAINT,
                        severity=SeverityLevel.HIGH,
                        impact_score=4,
                        likelihood_score=4,
                        detectability_score=4,
                        rpn=64,
                        summary=(
                            f"Field '{col}' contains negative values (down to {min_val}, affecting {neg_pct}% of records). "
                            "Legacy systems frequently use -1, -99, or -999 as sentinel values for 'unrecorded', 'refused', or 'expired'. "
                            "If ingested as continuous numbers, arithmetic operations (averages, loss functions, risk scoring) will be drastically distorted."
                        ),
                        evidence=f"Column '{col}' minimum value is {min_val}; {neg_count} records contain values < 0.",
                        location=f"Dataset '{name}' -> Column '{col}' (Range: [{min_val}, {max_val}])",
                        cognitive_bias="Blind Numeric Trust & Omission of Data Lineage Verification",
                        failure_scenario=(
                            f"A user with an unrecorded {col} (-99) is calculated as having negative risk or negative income, "
                            "skewing risk calculations or causing severe business logic misfires."
                        ),
                        recommendation=(
                            f"Map negative sentinel codes in '{col}' to formal nullable enums or separate metadata columns "
                            "before numerical computation or training."
                        ),
                        action_items=[
                            f"Inspect upstream ETL systems to document all sentinel codes used for '{col}'.",
                            "Implement ingestion transform replacing negative sentinels with NaN or specialized flag.",
                            f"Add test assertions: `assert df['{col}'].min() >= 0` for clean production data pipelines."
                        ],
                        mitigation_code=(
                            f"# Data Cleaning Transformation Guardrail\n"
                            f"df['{col}_is_unrecorded'] = df['{col}'] < 0\n"
                            f"df['{col}_clean'] = df['{col}'].apply(lambda x: None if x < 0 else x)"
                        ),
                        status="open"
                    ))

                # Rule 3: Extreme Outliers / Unrealistic Bounds
                if "age" in col_lower and max_val > 120:
                    anomalies.append(f"Unrealistic maximum value in '{col}' ({max_val}).")
                    discoveries.append(DiscoveryItem(
                        id=f"data-{uuid.uuid4().hex[:6]}",
                        title=f"Unbounded Biological/Physical Constraint in '{col}'",
                        category=DiscoveryCategory.OVERLOOKED_CONSTRAINT,
                        severity=SeverityLevel.MEDIUM,
                        impact_score=3,
                        likelihood_score=3,
                        detectability_score=3,
                        rpn=27,
                        summary=f"Max value for '{col}' is {max_val}, which exceeds human biological limits (typical max ~120). Indicates test data contamination or missing sanity bounds.",
                        evidence=f"Max value observed: {max_val}",
                        location=f"Dataset '{name}' -> Column '{col}'",
                        cognitive_bias="Unverified Edge Bound Assumption",
                        failure_scenario="Outlier records distort variance normalization, skewing clustering models or generating invalid customer profiles.",
                        recommendation=f"Enforce domain boundary checks on '{col}' (e.g. 0 <= age <= 120) with reject quarantines for records violating physical invariants.",
                        action_items=[
                            f"Configure range assertion: 0 <= {col} <= 120.",
                            "Audit data sources for legacy placeholder values like '999'."
                        ],
                        mitigation_code=f"assert (df['{col}'].between(0, 120)).all(), 'Age records out of physical bounds!'",
                        status="open"
                    ))

        # Check categorical columns for extreme class imbalance / demographic skew / zero variance
        if not pd.api.types.is_numeric_dtype(df[col]) or df[col].nunique() <= 10:
            val_counts = df[col].value_counts(normalize=True)
            if len(val_counts) >= 1 and total_rows >= 5:
                top_class = val_counts.index[0]
                top_pct = float(val_counts.iloc[0] * 100)

                # Rule 4: Extreme Skew / Target Imbalance (Survivorship & Blind Spot Bias)
                if top_pct >= 85.0:
                    anomalies.append(f"Column '{col}' has extreme class skew ({top_pct:.1f}% '{top_class}').")
                    col_category = DiscoveryCategory.DATA_RISK
                    severity = SeverityLevel.HIGH if any(k in col.lower() for k in ["target", "label", "fraud", "approved", "default"]) else SeverityLevel.MEDIUM
                    discoveries.append(DiscoveryItem(
                        id=f"data-{uuid.uuid4().hex[:6]}",
                        title=f"Severe Class Imbalance & Survivorship Bias in '{col}'",
                        category=col_category,
                        severity=severity,
                        impact_score=4 if severity == SeverityLevel.HIGH else 3,
                        likelihood_score=4,
                        detectability_score=4,
                        rpn=64 if severity == SeverityLevel.HIGH else 36,
                        summary=(
                            f"Column '{col}' is dominated by category '{top_class}' at {top_pct:.1f}%. "
                            "This reveals an unstated assumption of uniform or balanced representation. "
                            "Models or rules built on this dataset will suffer from the accuracy paradox "
                            "(predicting the majority class achieves nominal high score while completely failing to identify rare events)."
                        ),
                        evidence=f"Top value '{top_class}' constitutes {top_pct:.1f}% of all {total_rows} rows.",
                        location=f"Dataset '{name}' -> Column '{col}'",
                        cognitive_bias="Survivorship Bias & Base Rate Neglect",
                        failure_scenario=(
                            "An automated decisioning engine deployed with this distribution achieves high baseline test accuracy "
                            "but incurs catastrophic false-negative rates in real production traffic when rare anomalies or edge cases occur."
                        ),
                        recommendation=(
                            "Do not use naive accuracy metrics. Implement Precision-Recall AUC (PR-AUC), stratified sampling, "
                            "or cost-sensitive loss weighting to penalize minority class classification errors."
                        ),
                        action_items=[
                            f"Benchmark model using F1-score / PR-AUC rather than ROC-AUC or raw accuracy on '{col}'.",
                            "Implement synthetic oversampling (SMOTE) or targeted collection of minority cohorts.",
                            "Establish human-in-the-loop review threshold for borderline minority classifications."
                        ],
                        mitigation_code=(
                            "# Cost-sensitive loss weighting calculation\n"
                            "from sklearn.utils.class_weight import compute_class_weight\n"
                            "import numpy as np\n\n"
                            f"classes = np.unique(df['{col}'])\n"
                            f"weights = compute_class_weight(class_weight='balanced', classes=classes, y=df['{col}'])\n"
                            "class_weight_dict = dict(zip(classes, weights))\n"
                            "print('Balanced Class Weights:', class_weight_dict)"
                        ),
                        status="open"
                    ))

    # Sample preview for UI
    preview_rows = df.head(5).replace({np.nan: None}).to_dict(orient="records")

    summary = DatasetSummary(
        row_count=total_rows,
        column_count=total_cols,
        columns=columns,
        missing_value_summary=missing_percentages,
        data_types=data_types,
        detected_anomalies=anomalies,
        sample_preview=preview_rows
    )

    return summary, discoveries
