import re
import uuid
from typing import Tuple, List, Optional
from .models import DiscoveryItem, DiscoveryCategory, SeverityLevel, WorkflowSummary

def analyze_workflow(content: str) -> Tuple[Optional[WorkflowSummary], List[DiscoveryItem]]:
    """
    Parses and audits workflow definitions, pipelines, and sequence maps.
    Detects single points of failure, missing idempotency, unhandled timeouts,
    compensation omissions, and unstated reliability assumptions.
    """
    if not content or not content.strip():
        return None, []

    text = content.strip()
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    # Extract steps (numbered lines, bullets, or arrows)
    steps: List[str] = []
    for line in lines:
        cleaned = re.sub(r"^[\d\.\-\*\>\#\s]+", "", line).strip()
        if cleaned and not cleaned.startswith("//") and not cleaned.startswith("```"):
            steps.append(cleaned)

    if not steps:
        steps = [text[:100]]

    discoveries: List[DiscoveryItem] = []
    spofs: List[str] = []
    unhandled_timeouts: List[str] = []
    has_fallback = False

    text_lower = text.lower()

    # Rule 1: Financial or Critical Mutation without Idempotency Key
    charge_keywords = ["charge", "pay", "payment", "billing", "credit", "debit", "transfer", "stripe", "checkout", "provision", "mint"]
    idempotent_keywords = ["idempotent", "idempotency", "deduplication", "dedup", "nonce", "transaction_id", "request_id"]

    for i, step in enumerate(steps, 1):
        step_lower = step.lower()
        if any(kw in step_lower for kw in charge_keywords):
            if not any(ikw in text_lower for ikw in idempotent_keywords):
                discoveries.append(DiscoveryItem(
                    id=f"wf-{uuid.uuid4().hex[:6]}",
                    title="Missing Idempotency Protection on Mutating Financial Step",
                    category=DiscoveryCategory.MISSING_ASSUMPTION,
                    severity=SeverityLevel.CRITICAL,
                    impact_score=5,
                    likelihood_score=4,
                    detectability_score=3,
                    rpn=60,
                    summary=(
                        f"Step {i} ('{step}') executes a state mutation or financial transaction, "
                        "but the workflow specifies no idempotency keys, deduplication cache, or transaction nonces. "
                        "The workflow implicitly assumes every network packet is delivered exactly once."
                    ),
                    evidence=f"Step {i}: '{step}' does not reference idempotency or deduplication mechanisms.",
                    location=f"Workflow Step {i}",
                    cognitive_bias="Exactly-Once Delivery Fallacy (Fallacy of Distributed Computing)",
                    failure_scenario=(
                        "During intermittent client-side timeouts or gateway retries, the customer's request is submitted twice. "
                        "The payment processor charges the user double, triggering dispute chargebacks and reputational damage."
                    ),
                    recommendation=(
                        "Generate a deterministic client idempotency key (UUIDv4 or hash of user_id + order_id) "
                        "and pass it in request headers with Redis deduplication locks before invoking external processors."
                    ),
                    action_items=[
                        "Require `Idempotency-Key` HTTP header on all charge and provisioning endpoints.",
                        "Store processed idempotency keys in Redis with 24h TTL and atomic SETNX check.",
                        "Return cached original response payload when duplicate key is detected."
                    ],
                    mitigation_code=(
                        "# Redis Distributed Idempotency Lock Guardrail\n"
                        "async def process_transaction(order_id: str, idempotency_key: str):\n"
                        "    lock_acquired = await redis.set(f'idemp:{idempotency_key}', 'LOCKED', nx=True, ex=300)\n"
                        "    if not lock_acquired:\n"
                        "        return await get_cached_order_response(idempotency_key)\n"
                        "    try:\n"
                        "        return await charge_payment_gateway(order_id)\n"
                        "    finally:\n"
                        "        await redis.set(f'idemp:{idempotency_key}', 'COMPLETED', ex=86400)"
                    ),
                    status="open"
                ))
                break

    # Rule 2: Synchronous External Dependency as Single Point of Failure (SPOF)
    external_keywords = ["webhook", "third-party", "vendor", "partner", "external api", "sms", "email", "bureau", "credit check", "ai api", "llm"]
    has_circuit_breaker = any(cb in text_lower for cb in ["circuit breaker", "fallback", "retry", "dead letter", "dlq", "sqs", "backoff"])
    if has_circuit_breaker:
        has_fallback = True

    for i, step in enumerate(steps, 1):
        step_lower = step.lower()
        if any(ek in step_lower for ek in external_keywords) and not has_circuit_breaker:
            spofs.append(step)
            discoveries.append(DiscoveryItem(
                id=f"wf-{uuid.uuid4().hex[:6]}",
                title=f"Unprotected External API Single Point of Failure in Step {i}",
                category=DiscoveryCategory.OVERLOOKED_CONSTRAINT,
                severity=SeverityLevel.HIGH,
                impact_score=4,
                likelihood_score=4,
                detectability_score=3,
                rpn=48,
                summary=(
                    f"Step {i} ('{step}') relies on an external synchronous dependency without an explicit fallback, "
                    "exponential backoff retry policy, or circuit breaker pattern. "
                    "Assumes external third-party services provide 100% zero-latency availability."
                ),
                evidence=f"Step {i}: '{step}' has no retry budget or circuit breaker defined.",
                location=f"Workflow Step {i}",
                cognitive_bias="Availability Fallacy & Zero-Latency Network Assumption",
                failure_scenario=(
                    "The upstream external service suffers a 45-second latency spike or 503 outage. "
                    "Your application server exhausts its connection pool waiting for responses, causing cascading system-wide outage."
                ),
                recommendation=(
                    "Wrap external service calls with an asynchronous Dead-Letter Queue (DLQ), "
                    "exponential backoff with jitter, and an aggressive 3-second connection timeout."
                ),
                action_items=[
                    "Implement a Circuit Breaker (e.g. Resilience4j, Tenacity, or PyBreaker) with 50% failure threshold trip.",
                    "Set hard 3000ms socket read timeout on external calls.",
                    "Define a graceful degraded user experience when external provider is down."
                ],
                mitigation_code=(
                    "# Tenacity Exponential Backoff with Jitter\n"
                    "from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception_type\n\n"
                    "@retry(\n"
                    "    stop=stop_after_attempt(3),\n"
                    "    wait=wait_exponential_jitter(initial=1, max=10, jitter=1),\n"
                    "    retry=retry_if_exception_type((TimeoutError, ConnectionError))\n"
                    ")\n"
                    "async def call_external_partner_service(payload: dict):\n"
                    "    async with httpx.AsyncClient(timeout=3.0) as client:\n"
                    "        return await client.post('https://partner.api/v1/verify', json=payload)"
                ),
                status="open"
            ))
            break

    # Rule 3: Human-in-the-Loop or Manual Verification Bottleneck without Timeout
    human_keywords = ["manual", "human", "reviewer", "approval", "manager review", "officer signoff", "triage review"]
    timeout_keywords = ["timeout", "sla", "auto-expire", "escalate", "escalation", "fallback after", "hours", "minutes"]

    for i, step in enumerate(steps, 1):
        step_lower = step.lower()
        if any(hk in step_lower for hk in human_keywords):
            if not any(tk in text_lower for tk in timeout_keywords):
                unhandled_timeouts.append(step)
                discoveries.append(DiscoveryItem(
                    id=f"wf-{uuid.uuid4().hex[:6]}",
                    title=f"Unbounded Human-in-the-Loop Bottleneck in Step {i}",
                    category=DiscoveryCategory.WORKFLOW_BOTTLENECK,
                    severity=SeverityLevel.HIGH,
                    impact_score=4,
                    likelihood_score=5,
                    detectability_score=2,
                    rpn=40,
                    summary=(
                        f"Step {i} ('{step}') introduces a manual human approval step with no specified SLA, "
                        "auto-escalation rule, or timeout policy. During holiday weekends, volume spikes, or staff illness, "
                        "records will accumulate indefinitely, breaching customer expectations."
                    ),
                    evidence=f"Step {i}: '{step}' has no timeout or auto-routing contingency.",
                    location=f"Workflow Step {i}",
                    cognitive_bias="Infinite Human Bandwidth Fallacy",
                    failure_scenario=(
                        "During a flash promotion or surge, queue volume surges 10x. "
                        "Because there is no escalation SLA or tier-2 fallback, customer orders stall for days, causing massive churn."
                    ),
                    recommendation=(
                        "Establish an explicit SLA (e.g. 15 minutes) with automated secondary routing, "
                        "provisional approval based on risk heuristics, or manager escalation on timer expiry."
                    ),
                    action_items=[
                        "Define maximum wait threshold (e.g., 2 hours).",
                        "Implement automated fallback action (e.g., provisional hold or escalation to next tier).",
                        "Instrument Queue Depth alerts that page ops when pending reviews exceed threshold."
                    ],
                    mitigation_code=(
                        "# Workflow Step SLA Escalation Timer\n"
                        "if review_duration > datetime.timedelta(hours=2):\n"
                        "    send_slack_alert(f'Queue SLA breached for Item {item_id}')\n"
                        "    route_to_backup_escalation_pool(item_id)"
                    ),
                    status="open"
                ))
                break

    # Rule 4: Distributed State Mutation without Rollback / Saga Compensation
    if len(steps) >= 3 and not any(rb in text_lower for rb in ["rollback", "compensation", "saga", "undo", "revert"]):
        discoveries.append(DiscoveryItem(
            id=f"wf-{uuid.uuid4().hex[:6]}",
            title="Absence of Compensating Transactions (Saga Pattern) for Partial Failure",
            category=DiscoveryCategory.MISSING_ASSUMPTION,
            severity=SeverityLevel.HIGH,
            impact_score=4,
            likelihood_score=3,
            detectability_score=3,
            rpn=36,
            summary=(
                "The workflow coordinates multiple sequential actions across distributed resources "
                "without defining compensating actions (reversals/refunds/cleanup) if late steps fail. "
                "Assumes the entire multi-step pipeline either succeeds or never enters a dirty state."
            ),
            evidence=f"Workflow contains {len(steps)} sequential steps with no failure compensation / rollback handlers.",
            location=f"Workflow Pipeline ({len(steps)} steps)",
            cognitive_bias="All-or-Nothing Monolithic Bias (Ignoring Partial Failure in Distributed Systems)",
            failure_scenario=(
                "Step 2 succeeds (credit charged), but Step 4 fails (inventory reservation unavailable). "
                "The system leaves the customer with deducted funds and no product, requiring manual database surgery."
            ),
            recommendation=(
                "Implement the Saga Pattern with explicit compensating transactions: "
                "if any downstream step fails, sequentially trigger the compensating action of all completed preceding steps."
            ),
            action_items=[
                "Document compensatory actions for every mutating step.",
                "Implement orchestrator with idempotency-safe undo methods.",
                "Store saga state log in durable storage before each transition."
            ],
            mitigation_code=(
                "# Saga Orchestration Compensating Action Blueprint\n"
                "try:\n"
                "    await payment_service.charge(user_id, amount)\n"
                "    await inventory_service.reserve(item_id)\n"
                "    await shipping_service.create_label(address)\n"
                "except ShippingError:\n"
                "    # Compensating actions in reverse order\n"
                "    await inventory_service.release(item_id)\n"
                "    await payment_service.refund(user_id, amount)"
            ),
            status="open"
        ))

    summary = WorkflowSummary(
        step_count=len(steps),
        steps=steps[:10],
        has_fallback=has_fallback,
        single_points_of_failure=spofs,
        unhandled_timeouts=unhandled_timeouts
    )

    return summary, discoveries
