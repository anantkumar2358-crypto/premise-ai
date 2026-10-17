import re
import uuid
from typing import List, Tuple
from .models import DiscoveryItem, ProbingQuestion, DiscoveryCategory, SeverityLevel

def run_heuristics_analysis(doc_text: str, domain: str = "general") -> Tuple[List[DiscoveryItem], List[ProbingQuestion]]:
    """
    Applies deep deterministic heuristics across engineering, compliance,
    economics, and architecture to uncover hidden assumptions and overlooked constraints.
    """
    discoveries: List[DiscoveryItem] = []
    probing_questions: List[ProbingQuestion] = []

    if not doc_text or not doc_text.strip():
        return discoveries, probing_questions

    text_lower = doc_text.lower()

    # Domain Detection: Timetabling & Combinatorial Scheduling
    has_scheduling = any(kw in text_lower for kw in [
        "timetable", "timetabling", "scheduling", "schedule", "or-tools", 
        "cp-sat", "constraint programming", "genetic algorithm", "solver", 
        "classroom", "faculty availability", "batch double-booking"
    ])

    # Rule 1: Missing Data Retention & Unbounded Storage/Egress Constraint
    has_storage = any(kw in text_lower for kw in ["cloud storage", "database table", "s3 bucket", "blob storage", "telemetry logs", "vector database", "audit logs"]) and not has_scheduling
    has_retention = any(kw in text_lower for kw in ["retention", "ttl", "purge", "prune", "archive", "expire", "lifecycle policy", "cleanup"])
    if has_storage and not has_retention:
        disc_id = f"heur-{uuid.uuid4().hex[:6]}"
        discoveries.append(DiscoveryItem(
            id=disc_id,
            title="Overlooked Data Lifecycle & Unbounded Storage Cost Constraint",
            category=DiscoveryCategory.OVERLOOKED_CONSTRAINT,
            severity=SeverityLevel.HIGH,
            impact_score=4,
            likelihood_score=5,
            detectability_score=3,
            rpn=60,
            summary=(
                "The system plans to ingest and persist records, logs, or telemetry without defining a data retention policy "
                "or automatic Time-To-Live (TTL). Implicitly assumes storage capacity is infinite and cloud egress/backup costs remain flat."
            ),
            evidence="Document describes data persistence and storage operations but contains no retention, archival, or TTL specifications.",
            location="Storage & Data Architecture",
            cognitive_bias="Linear Projection Fallacy & Unseen Compounding Costs",
            failure_scenario=(
                "After 12 months in production, database index sizes blow past RAM limits, queries slow from 20ms to 4500ms, "
                "and cloud infrastructure bills spike unexpectedly by 400% due to unpruned audit and telemetry logs."
            ),
            recommendation=(
                "Implement an explicit data retention and tiering matrix: 30-day hot storage, 90-day warm S3 tier, "
                "annual cold Glacier archival, and hard automated lifecycle deletion routines."
            ),
            action_items=[
                "Define formal data classification tiering (Hot, Warm, Cold, Delete).",
                "Attach AWS S3 Lifecycle Rules or MongoDB TTL indexes to high-frequency tables.",
                "Ensure retention policy aligns with regulatory requirements (e.g. 7-year tax records vs 30-day debug logs)."
            ],
            mitigation_code=(
                "-- PostgreSQL automated partition cleanup / TTL routine\n"
                "CREATE OR REPLACE PROCEDURE drop_old_telemetry_partitions()\n"
                "LANGUAGE plpgsql AS $$\n"
                "BEGIN\n"
                "  EXECUTE format('DROP TABLE IF EXISTS telemetry_log_%s;', \n"
                "                 to_char(NOW() - INTERVAL '90 days', 'YYYY_MM'));\n"
                "END; $$;"
            ),
            status="open"
        ))
        probing_questions.append(ProbingQuestion(
            id=f"q-{uuid.uuid4().hex[:6]}",
            question="What is the legal and technical cutoff date for user data retention before automated archival or purging?",
            why_it_matters="Without a clear TTL policy, database query speeds degrade over time and cloud storage costs compound uncontrollably.",
            related_discovery_id=disc_id,
            suggested_options=[
                "Enforce 30-day rolling TTL on raw logs; retain aggregated metrics indefinitely",
                "Retain hot data for 90 days, archive compressed cold data for 3 years, then hard delete",
                "Comply with statutory regulatory duration (e.g. 7 years for financial records) in immutable WORM storage"
            ]
        ))

    # Rule 2: LLM / AI Real-Time Latency & Token Cost Ceiling Assumption
    has_llm = any(kw in text_lower for kw in ["llm", "gemini", "gpt", "rag", "embedding", "ai agent", "generative ai", "prompt"])
    has_sla_cost = any(kw in text_lower for kw in ["token limit", "cost budget", "p99", "latency budget", "streaming", "caching", "cache-control"])
    if has_llm and not has_sla_cost:
        disc_id = f"heur-{uuid.uuid4().hex[:6]}"
        discoveries.append(DiscoveryItem(
            id=disc_id,
            title="Unchecked LLM Inference Latency & Runaway Token Economics",
            category=DiscoveryCategory.OVERLOOKED_CONSTRAINT,
            severity=SeverityLevel.HIGH,
            impact_score=4,
            likelihood_score=4,
            detectability_score=3,
            rpn=48,
            summary=(
                "The project leverages Generative AI / Large Language Models in synchronous user flows "
                "without a strict token budget, semantic caching tier, or P99 response time SLA. "
                "Assumes API latency is deterministic (<500ms) and API pricing remains negligible under traffic spikes."
            ),
            evidence="AI/LLM integration mentioned without token throttling, response timeout boundaries, or prompt size caps.",
            location="AI / Inference Architecture",
            cognitive_bias="Demo-to-Production Optimization Fallacy",
            failure_scenario=(
                "A burst of 5,000 concurrent user sessions causes prompt token consumption to exceed rate limits. "
                "P99 latency climbs to 14 seconds, users abandon sessions, and daily cloud bills skyrocket by thousands of dollars."
            ),
            recommendation=(
                "Implement a Semantic Cache (e.g. Redis / GPTCache) for frequent queries, enforce prompt token compression, "
                "and set a hard 4.0-second fallback with graceful degradation to pre-computed responses."
            ),
            action_items=[
                "Establish strict max_tokens constraints on both input prompts and completion outputs.",
                "Implement Redis Semantic Caching with cosine similarity threshold > 0.92.",
                "Enforce circuit-breaker fallback when LLM response exceeds 4500ms."
            ],
            mitigation_code=(
                "# Async LLM Call with Strict Timeout & Semantic Cache\n"
                "async def query_llm_with_guardrail(prompt: str) -> str:\n"
                "    cached = await semantic_cache.get(prompt)\n"
                "    if cached:\n"
                "        return cached\n"
                "    try:\n"
                "        return await asyncio.wait_for(client.models.generate_content(prompt), timeout=4.0)\n"
                "    except asyncio.TimeoutError:\n"
                "        return get_heuristic_fallback_response(prompt)"
            ),
            status="open"
        ))
        probing_questions.append(ProbingQuestion(
            id=f"q-{uuid.uuid4().hex[:6]}",
            question="What is the acceptable P99 latency threshold for user-facing AI responses before degrading to a fallback model?",
            why_it_matters="Generative models can experience multi-second variance during global provider congestion, freezing user sessions.",
            related_discovery_id=disc_id,
            suggested_options=[
                "Hard 3.0s timeout with fallback to fast lightweight heuristic classifier",
                "Stream responses word-by-word with progressive UI rendering (Time to First Token < 800ms)",
                "Pre-compute 80% of common responses offline using asynchronous batch pipelines"
            ]
        ))

    # Rule 3: Missing Emergency Override / Break-Glass Protocol
    has_automation = any(kw in text_lower for kw in ["auto-decision", "approve loan", "deny claim", "autonomous agent", "trading robot", "dispatch ambulance", "autonomous er"]) and not has_scheduling
    has_break_glass = any(kw in text_lower for kw in ["kill switch", "break glass", "emergency stop", "manual override", "circuit breaker", "pause button"])
    if has_automation and not has_break_glass:
        disc_id = f"heur-{uuid.uuid4().hex[:6]}"
        discoveries.append(DiscoveryItem(
            id=disc_id,
            title="Absence of an Emergency Human 'Break-Glass' Kill Switch",
            category=DiscoveryCategory.MISSING_ASSUMPTION,
            severity=SeverityLevel.CRITICAL,
            impact_score=5,
            likelihood_score=3,
            detectability_score=3,
            rpn=45,
            summary=(
                "The system executes automated business logic, approvals, or actions without providing an immediate "
                "operational kill-switch or emergency human pause mechanism. "
                "Assumes the automated logic will never encounter novel edge cases, corrupted data feeds, or adversarial exploits."
            ),
            evidence="Automated actions and decisioning defined without a manual kill-switch or operational pause protocol.",
            location="Operational Controls & Safety",
            cognitive_bias="Automation Bias & Illusion of Control",
            failure_scenario=(
                "A upstream vendor sends corrupted data, causing the automated system to erroneously approve 1,200 fraudulent transactions "
                "or lock out legitimate patients. On-call engineers have no single toggle to pause decisions without redeploying code."
            ),
            recommendation=(
                "Build a dynamic feature flag / distributed kill-switch in LaunchDarkly or Redis that halts automated mutations "
                "and routes 100% of volume to a safe manual review hold-queue within 500ms."
            ),
            action_items=[
                "Deploy a real-time feature flag: `AUTOMATED_DECISIONING_ENABLED` checked at execution entry.",
                "Create an authenticated Ops portal button: 'Emergency Halt & Drain Queue'.",
                "Conduct quarterly fire drills testing manual override procedures."
            ],
            mitigation_code=(
                "# Distributed Emergency Kill-Switch Guard\n"
                "async def execute_automated_action(order: dict):\n"
                "    is_active = await redis.get('CONFIG:AUTOMATION_KILL_SWITCH')\n"
                "    if is_active == b'HALTED':\n"
                "        logger.warning('Automation kill-switch engaged! Routing to manual queue.')\n"
                "        return await route_to_manual_quarantine(order)\n"
                "    return await run_automated_logic(order)"
            ),
            status="open"
        ))
        probing_questions.append(ProbingQuestion(
            id=f"q-{uuid.uuid4().hex[:6]}",
            question="If automated decisions begin failing at scale in production, what is the exact operational procedure to halt execution?",
            why_it_matters="Without an immediate kill switch, mitigating a runaway loop requires an emergency code deploy, wasting critical minutes.",
            related_discovery_id=disc_id,
            suggested_options=[
                "Global feature flag toggle via admin dashboard that reroutes traffic to manual review within 500ms",
                "Automated anomaly circuit breaker: trips automatically if error/anomaly rate exceeds 2% in a 5-minute window",
                "Gradual canary rollout: run automation in shadow mode for 30 days before granting mutation authority"
            ]
        ))

    # Rule 4: Data Privacy & Deletion Compliance (GDPR Article 17 / CCPA)
    has_pii = any(kw in text_lower for kw in ["customer pii", "patient data", "ssn", "social security", "credit card", "biometric", "passport"]) and not has_scheduling
    has_gdpr = any(kw in text_lower for kw in ["gdpr", "ccpa", "right to erasure", "delete account", "right to be forgotten", "privacy", "anonymiz"])
    if has_pii and not has_gdpr:
        disc_id = f"heur-{uuid.uuid4().hex[:6]}"
        discoveries.append(DiscoveryItem(
            id=disc_id,
            title="Overlooked Regulatory Constraint: Right to Erasure & PII Isolation",
            category=DiscoveryCategory.OVERLOOKED_CONSTRAINT,
            severity=SeverityLevel.HIGH,
            impact_score=4,
            likelihood_score=4,
            detectability_score=3,
            rpn=48,
            summary=(
                "The project ingests personal identifiable information (PII) without specifying an architecture for "
                "user data deletion (GDPR Art. 17 / CCPA Right to Delete). "
                "If PII is scattered across backups, vector databases, analytics warehouses, and logs, compliant deletion is nearly impossible."
            ),
            evidence="PII fields collected without an explicit user data deletion, pseudonymization, or crypto-shredding strategy.",
            location="Compliance & Data Privacy Architecture",
            cognitive_bias="Regulatory Blind Spot & Privacy As Afterthought",
            failure_scenario=(
                "A user submits a formal GDPR deletion request. Engineering realizes customer data is embedded inside immutable "
                "vector embeddings, database replicas, and data lake snapshots, risking statutory fines of up to 4% of annual global turnover."
            ),
            recommendation=(
                "Implement Crypto-Shredding (encrypt each user's PII with a dedicated customer key; deleting the key renders all scattered data irrecoverable) "
                "or centralize PII in an isolated, audited microservice."
            ),
            action_items=[
                "Separate PII into a dedicated tokenized vault with deterministic surrogate keys.",
                "Ensure vector embeddings use anonymized tokens rather than raw patient/customer identifiers.",
                "Automate cascading deletion jobs across all datastores upon customer account closure."
            ],
            mitigation_code=(
                "# Crypto-Shredding User Deletion Blueprint\n"
                "async def handle_user_erasure_request(user_id: str):\n"
                "    # Deleting the user-specific master encryption key permanently shreds all encrypted data\n"
                "    await kms_client.delete_key(key_alias=f'user-keys/{user_id}')\n"
                "    await user_vault_db.delete(user_id)\n"
                "    logger.info(f'Crypto-shredded PII for user: {user_id}')"
            ),
            status="open"
        ))
        probing_questions.append(ProbingQuestion(
            id=f"q-{uuid.uuid4().hex[:6]}",
            question="How will the system handle a statutory GDPR/CCPA 'Right to Erasure' request when data is replicated across analytics, caches, and backups?",
            why_it_matters="Deleting user records from primary databases does not delete them from embeddings, logs, and backups, creating legal exposure.",
            related_discovery_id=disc_id,
            suggested_options=[
                "Adopt Crypto-Shredding: delete the per-user encryption key to render all distributed copies instantly unreadable",
                "Maintain a centralized PII Vault with surrogate UUIDs across all downstream tables and vector indexes",
                "Execute scheduled daily cascading deletion microservices across primary DB and analytical lakehouse"
            ]
        ))

    # Rule 5: Concurrency, Double Spending & Race Conditions
    has_concurrency = any(kw in text_lower for kw in ["concurrent checkout", "distributed lock", "high-volume booking", "race condition", "double-spend"]) and not has_scheduling
    has_locks = any(kw in text_lower for kw in ["pessimistic lock", "optimistic lock", "distributed lock", "atomic", "compare-and-swap", "mutex", "serializable"])
    if has_concurrency and not has_locks:
        disc_id = f"heur-{uuid.uuid4().hex[:6]}"
        discoveries.append(DiscoveryItem(
            id=disc_id,
            title="Overlooked Concurrency Control & Double-Allocation Race Condition",
            category=DiscoveryCategory.OVERLOOKED_CONSTRAINT,
            severity=SeverityLevel.HIGH,
            impact_score=4,
            likelihood_score=4,
            detectability_score=3,
            rpn=48,
            summary=(
                "The project handles high-concurrency requests or shared resource allocation without specifying "
                "optimistic concurrency control (OCC), distributed locks, or database isolation levels. "
                "Assumes that consecutive database reads and writes occur in isolation."
            ),
            evidence="Concurrent user actions or shared state updates mentioned without explicit concurrency control mechanisms.",
            location="Transaction Management & Concurrency",
            cognitive_bias="Single-Threaded Mental Model Fallacy",
            failure_scenario=(
                "Two users concurrently click 'Reserve' for the exact same inventory item or appointment slot. "
                "Both requests read stock as 1, both succeed, resulting in overselling and customer disputes."
            ),
            recommendation=(
                "Use atomic conditional updates (`UPDATE inventory SET stock = stock - 1 WHERE id = :id AND stock > 0`) "
                "or optimistic locking with version columns (`WHERE version = :current_version`)."
            ),
            action_items=[
                "Add `version INT DEFAULT 1` column to all mutable transactional entities.",
                "Enforce atomic conditional SQL queries rather than in-memory read-then-write logic.",
                "Test concurrency using simulated parallel load testing (e.g., Locust or k6)."
            ],
            mitigation_code=(
                "-- Atomic Conditional Decrement Guardrail\n"
                "UPDATE inventory_items \n"
                "SET available_quantity = available_quantity - 1, version = version + 1 \n"
                "WHERE item_id = $1 AND available_quantity >= 1 AND version = $2;\n"
                "-- If rows_affected == 0, abort transaction with 409 Conflict."
            ),
            status="open"
        ))
        probing_questions.append(ProbingQuestion(
            id=f"q-{uuid.uuid4().hex[:6]}",
            question="What concurrency control model guarantees two users cannot claim or mutate the same shared resource simultaneously?",
            why_it_matters="In distributed or multi-container architectures, race conditions bypass standard application-level validations.",
            related_discovery_id=disc_id,
            suggested_options=[
                "Atomic SQL conditional updates with row-level locking (SELECT FOR UPDATE)",
                "Optimistic Concurrency Control (OCC) with version number checking and automatic retry",
                "Distributed Redis Redlock mutex with 2000ms TTL per critical resource"
            ]
        ))

    # Rule 6: Network Partition & Offline Disconnection Assumption
    has_mobile_edge = any(kw in text_lower for kw in ["mobile", "edge", "iot", "hospital", "warehouse", "clinic", "field", "offline", "sync", "device", "vehicle"])
    has_offline_handling = any(kw in text_lower for kw in ["local cache", "sqlite", "offline mode", "store-and-forward", "conflict resolution", "crdt"])
    if has_mobile_edge and not has_offline_handling:
        disc_id = f"heur-{uuid.uuid4().hex[:6]}"
        discoveries.append(DiscoveryItem(
            id=disc_id,
            title="Unrealistic Continuous Connectivity Assumption in Edge/Field Operations",
            category=DiscoveryCategory.MISSING_ASSUMPTION,
            severity=SeverityLevel.HIGH,
            impact_score=4,
            likelihood_score=4,
            detectability_score=3,
            rpn=48,
            summary=(
                "System operates in field/mobile/edge contexts but implicitly assumes uninterrupted internet connectivity. "
                "Does not specify local offline persistence, store-and-forward queues, or conflict resolution upon reconnection."
            ),
            evidence="Edge/mobile environment targeted without local offline storage or sync conflict protocols.",
            location="Client & Connectivity Architecture",
            cognitive_bias="Always-On Network Fallacy",
            failure_scenario=(
                "Clinicians or field agents enter hospital basements, elevators, or rural dead zones. "
                "The app freezes or drops unsaved patient data, causing operational paralysis."
            ),
            recommendation=(
                "Implement a Local-First architecture using SQLite/IndexedDB with an asynchronous Store-and-Forward queue "
                "and Conflict-free Replicated Data Types (CRDTs) or Last-Write-Wins timestamps."
            ),
            action_items=[
                "Store all user inputs locally in durable client storage before firing HTTP requests.",
                "Implement a background sync service worker that retries outbound payloads when connectivity resumes.",
                "Formulate explicit conflict resolution rules for multi-device concurrent edits."
            ],
            mitigation_code=(
                "// Service Worker Background Sync Pattern\n"
                "self.addEventListener('sync', (event) => {\n"
                "  if (event.tag === 'sync-queued-records') {\n"
                "    event.waitUntil(flushLocalIndexedDBQueueToServer());\n"
                "  }\n"
                "});"
            ),
            status="open"
        ))
        probing_questions.append(ProbingQuestion(
            id=f"q-{uuid.uuid4().hex[:6]}",
            question="When client devices experience a 15-minute network dead zone, how are locally queued actions reconciled with server state?",
            why_it_matters="Without store-and-forward reconciliation, field workers risk data loss or duplicate conflicting records upon reconnecting.",
            related_discovery_id=disc_id,
            suggested_options=[
                "Store-and-forward with client-side UUIDs and idempotent upsert on server",
                "Conflict-Free Replicated Data Types (CRDTs) for automated mathematical merge",
                "Explicit conflict flagging: flag diverged records for operator manual review"
            ]
        ))

    # Rule 7: Timetabling, Scheduling & Combinatorial Optimization Domain Heuristics
    has_scheduling = any(kw in text_lower for kw in [
        "timetable", "timetabling", "scheduling", "schedule", "or-tools", 
        "cp-sat", "constraint programming", "genetic algorithm", "solver", 
        "classroom", "faculty availability", "batch double-booking"
    ])
    if has_scheduling:
        # 1. Infeasibility / UNSAT Protocol
        disc_unsat = f"heur-{uuid.uuid4().hex[:6]}"
        discoveries.append(DiscoveryItem(
            id=disc_unsat,
            title="Absence of Infeasibility Resolution Protocol (The UNSAT Fallacy)",
            category=DiscoveryCategory.MISSING_ASSUMPTION,
            severity=SeverityLevel.CRITICAL,
            impact_score=5,
            likelihood_score=5,
            detectability_score=3,
            rpn=75,
            summary=(
                "The system assumes all input instances are mathematically feasible. "
                "In exact constraint programming (OR-Tools CP-SAT), if faculty blackout windows, "
                "room quotas, and batch hours create an over-constrained system, the solver terminates with INFEASIBLE. "
                "Without automated slack relaxation or Minimal Unsatisfiable Core (MUC) diagnosis, "
                "users receive zero timetable and no explanation of which specific constraint caused the deadlock."
            ),
            evidence="System guarantees '0 hard constraint clashes' but specifies no handling for over-constrained or INFEASIBLE problem instances.",
            location="Optimization Formulation & Constraint Engine",
            cognitive_bias="The Feasibility Fallacy & Illusion of Zero-Defect Inputs",
            failure_scenario=(
                "A department chair adds 2 faculty blackout windows and a 3-hour lab requirement. "
                "CP-SAT runs, finds the combination mathematically impossible, and returns INFEASIBLE. "
                "The web UI shows a generic error or hangs, leaving university administrators unable to generate schedules on deadline."
            ),
            recommendation=(
                "Implement a two-stage hierarchical solver or soft slack penalties: if the hard model is INFEASIBLE, "
                "automatically relax lowest-priority constraints (e.g. room capacity tolerance ±5% or soft blackout windows) "
                "and surface the exact conflicting constraint cluster (UNSAT core) to the user."
            ),
            action_items=[
                "Wrap CP-SAT with a fallback solver stage utilizing non-negative slack variables on soft-hard constraints.",
                "Implement QuickXplain or conflict-refiner to isolate the minimal set of mutually conflicting constraints.",
                "Display human-readable resolution guidance: e.g. 'Dr. Smith's Friday blackout conflicts with CS-301 Lab requirement'."
            ],
            mitigation_code=(
                "# CP-SAT Feasibility Fallback with Slack Penalties\n"
                "solver = cp_model.CpSolver()\n"
                "status = solver.Solve(model)\n"
                "if status == cp_model.INFEASIBLE:\n"
                "    logger.warning('Strict model INFEASIBLE. Activating hierarchical slack relaxation...')\n"
                "    relaxed_model = build_relaxed_model_with_slacks(base_constraints, penalty_weight=1000)\n"
                "    status = solver.Solve(relaxed_model)"
            ),
            status="open"
        ))
        probing_questions.append(ProbingQuestion(
            id=f"q-{uuid.uuid4().hex[:6]}",
            question="When faculty blackout hours and room capacities render the timetable mathematically INFEASIBLE, what is the automated recovery strategy?",
            why_it_matters="Real-world academic data is frequently over-constrained. Without automated relaxation, CP-SAT fails with 0 generated output.",
            related_discovery_id=disc_unsat,
            suggested_options=[
                "Automated hierarchical relaxation: convert lowest-priority blackout windows to high-penalty soft constraints",
                "Minimal Unsatisfiable Core (MUC) isolation: pinpoint and highlight the exact 2-3 conflicting rules to the administrator",
                "Interactive Conflict Wizard: guide the user to adjust the specific instructor availability or room assignment causing the deadlock"
            ]
        ))

        # 2. Dynamic Rescheduling & Churn Minimization (Warm-Start)
        disc_churn = f"heur-{uuid.uuid4().hex[:6]}"
        discoveries.append(DiscoveryItem(
            id=disc_churn,
            title="Omission of Dynamic Rescheduling & Timetable Churn Minimization",
            category=DiscoveryCategory.OVERLOOKED_CONSTRAINT,
            severity=SeverityLevel.HIGH,
            impact_score=4,
            likelihood_score=4,
            detectability_score=3,
            rpn=48,
            summary=(
                "The system models timetabling as a one-time static event. In practice, mid-semester events "
                "(faculty illness, room maintenance, emergency closures) require adjusting individual slots. "
                "Re-running global CP-SAT or Genetic Algorithms from scratch produces an entirely different optimal schedule, "
                "shuffling unaffected courses and causing university-wide chaos."
            ),
            evidence="Timetable generation is described globally without a mechanism for frozen slots, incremental repair, or disruption penalties.",
            location="Operational Lifecycle & Schedule Maintenance",
            cognitive_bias="Static World Fallacy (Ignoring Operational Churn)",
            failure_scenario=(
                "In Week 4, a physics lab undergoes emergency pipe repair. The registrar re-runs the generator to move 2 lab sections; "
                "the solver redistributes lectures across 1,800 students and 45 professors, invalidating everyone's published calendar."
            ),
            recommendation=(
                "Introduce 'Pinned / Frozen Slots' and an incremental delta objective: minimize slot displacement distance "
                "from the baseline timetable ($|\\text{Slot}_{\\text{new}} - \\text{Slot}_{\\text{baseline}}|$)."
            ),
            action_items=[
                "Add an `is_pinned: bool` attribute to scheduled slots allowing administrators to lock approved assignments.",
                "Formulate a disruption penalty objective in CP-SAT: `minimize sum(abs(new_slot[c] - old_slot[c]))`.",
                "Provide a local neighborhood search (LNS) repair mode for targeted single-slot adjustments."
            ],
            mitigation_code=(
                "# Minimal-Disruption Timetable Repair Objective\n"
                "disruption_penalties = []\n"
                "for course_id, baseline_slot in existing_timetable.items():\n"
                "    if course_id not in affected_courses:\n"
                "        # Strong penalty for moving an already published unaffected class\n"
                "        is_moved = model.NewBoolVar(f'moved_{course_id}')\n"
                "        model.Add(slot_vars[course_id] != baseline_slot).OnlyEnforceIf(is_moved)\n"
                "        disruption_penalties.append(is_moved * 500)\n"
                "model.Minimize(base_objective + sum(disruption_penalties))"
            ),
            status="open"
        ))
        probing_questions.append(ProbingQuestion(
            id=f"q-{uuid.uuid4().hex[:6]}",
            question="If a classroom or instructor becomes unavailable mid-semester, how does the system reschedule without reshuffling the entire university's existing timetable?",
            why_it_matters="Re-optimizing an NP-hard schedule globally completely reorganizes unrelated classes, creating logistical turmoil.",
            related_discovery_id=disc_churn,
            suggested_options=[
                "Frozen-slot constraint: lock all unaffected classes and solve only for displaced courses",
                "Disruption minimization objective: heavily penalize moving any class from its currently published day/time",
                "Manual swap-assist: suggest the top 3 least-disruptive room/slot swaps using local neighborhood search"
            ]
        ))

        # 3. Inter-Building Physical Transit Constraint
        disc_transit = f"heur-{uuid.uuid4().hex[:6]}"
        discoveries.append(DiscoveryItem(
            id=disc_transit,
            title="Overlooked Campus Inter-Building Transit Time & Walking Distance",
            category=DiscoveryCategory.OVERLOOKED_CONSTRAINT,
            severity=SeverityLevel.HIGH,
            impact_score=4,
            likelihood_score=4,
            detectability_score=3,
            rpn=48,
            summary=(
                "The model enforces zero room double-booking and room capacities, but assumes campus transit time is zero. "
                "If a student batch or professor is scheduled in Building A at 10:00-10:50 and Building D at 10:50-11:40 "
                "(a 15-minute walk across campus), chronic tardiness and lecture overlap are guaranteed."
            ),
            evidence="Room constraints only check seating capacity and room type, ignoring geographic building locations and inter-building transit gaps.",
            location="Room & Facility Allocation Model",
            cognitive_bias="Euclidean Distance Omission & Frictionless Reality Fallacy",
            failure_scenario=(
                "Freshmen have Chemistry in North Campus at 9:00-9:50 AM and Calculus in South Campus at 9:50-10:40 AM. "
                "200 students sprint across campus daily, arriving 15 minutes late to every calculus lecture."
            ),
            recommendation=(
                "Incorporate a Building Proximity Matrix: forbid consecutive period scheduling across distant building zones "
                "unless separated by a designated recess or lunch period."
            ),
            action_items=[
                "Add `building_id` or `campus_zone` metadata to all room entities.",
                "Define transit travel matrix: `travel_time[b1, b2]` in minutes.",
                "Add constraint: if `slot2 == slot1 + 1` for same batch/instructor, enforce `travel_time[room1.building, room2.building] <= gap_minutes`."
            ],
            mitigation_code=(
                "# Inter-Building Consecutive Period Transit Guardrail\n"
                "for t in range(total_periods - 1):\n"
                "    for b in student_batches:\n"
                "        room_t = batch_room_schedule[b, t]\n"
                "        room_next = batch_room_schedule[b, t+1]\n"
                "        # Forbid scheduling consecutive periods if walking transit exceeds period changeover window\n"
                "        model.AddForbiddenAssignments([room_t, room_next], distant_building_pairs)"
            ),
            status="open"
        ))
        probing_questions.append(ProbingQuestion(
            id=f"q-{uuid.uuid4().hex[:6]}",
            question="How does the system prevent back-to-back lectures from being assigned to classrooms in distant campus buildings with insufficient walking transit time?",
            why_it_matters="Even a conflict-free timetable fails operationally if students and professors cannot physically reach consecutive classes on time.",
            related_discovery_id=disc_transit,
            suggested_options=[
                "Zone-based clustering: restrict all classes of a batch on any given day to the same campus building or zone",
                "Building transit matrix constraint: enforce a minimum 15-minute gap period when switching campus sectors",
                "Soft penalty on inter-building travel: penalize distance in the optimization objective function"
            ]
        ))

        # 4. Combinatorial Solver Timeout & Gap Limits
        discoveries.append(DiscoveryItem(
            id=f"heur-{uuid.uuid4().hex[:6]}",
            title="Unbounded Combinatorial Run Time & Missing Solver Time Budget",
            category=DiscoveryCategory.OVERLOOKED_CONSTRAINT,
            severity=SeverityLevel.HIGH,
            impact_score=4,
            likelihood_score=4,
            detectability_score=3,
            rpn=48,
            summary=(
                "Exact constraint programming (CP-SAT) on multi-period, multi-room problems is NP-hard. "
                "As constraints (continuous lab blocks, room types, workload caps) compound, proving mathematical "
                "optimality can take hours or hang indefinitely. The specification omits a wall-clock time ceiling "
                "and relative optimality gap budget."
            ),
            evidence="System employs exact CP-SAT solver without specifying timeout parameters (max_time_in_seconds) or gap tolerances.",
            location="Solver Execution Architecture",
            cognitive_bias="Linear Search Time Assumption",
            failure_scenario=(
                "An administrator clicks 'Generate' for a 500-course semester. The solver encounters heavy combinatorial backtracking. "
                "The HTTP request times out at 60s, while the background Python process maxes out CPU cores indefinitely."
            ),
            recommendation=(
                "Configure `solver.parameters.max_time_in_seconds = 30.0` and `relative_gap_limit = 0.02` (stop when within 2% of optimal). "
                "Use progressive solution callbacks to return the best feasible solution found if time expires."
            ),
            action_items=[
                "Enforce strict 30-second solver timeout parameter on all web requests.",
                "Accept FEASIBLE near-optimal solutions if OPTIMAL cannot be proven within budget.",
                "Stream intermediate solver solutions via WebSocket to show progressive quality score improvements."
            ],
            mitigation_code=(
                "# CP-SAT Production Timeout & Gap Budget\n"
                "solver = cp_model.CpSolver()\n"
                "solver.parameters.max_time_in_seconds = 30.0\n"
                "solver.parameters.relative_gap_limit = 0.02  # Stop within 2% of mathematical optimum\n"
                "solver.parameters.num_workers = 8            # Parallel search workers"
            ),
            status="open"
        ))

    # Add general deep probing questions if list is short
    if len(probing_questions) < 3:
        probing_questions.append(ProbingQuestion(
            id=f"q-{uuid.uuid4().hex[:6]}",
            question="What is the operational recovery plan if the primary cloud region experiences an unannounced 6-hour blackout?",
            why_it_matters="Many cloud SLAs guarantee 99.9% but leave disaster recovery and multi-region failover entirely to the application team.",
            suggested_options=[
                "Active-Passive warm standby in secondary region with automated DNS failover (RTO < 15 min, RPO < 5 min)",
                "Full Multi-Region Active-Active deployment with distributed database replication (CockroachDB / Spanner)",
                "Documented business continuity plan: accept temporary read-only mode during regional outage"
            ]
        ))
        probing_questions.append(ProbingQuestion(
            id=f"q-{uuid.uuid4().hex[:6]}",
            question="How will you detect if the distribution of incoming user inputs has silently drifted from historical assumptions?",
            why_it_matters="Gradual behavioral or demographic drift degrades model performance and business logic silently without throwing errors.",
            suggested_options=[
                "Deploy statistical drift monitors (Evidently AI / Great Expectations) running daily Kolmogorov-Smirnov tests",
                "Instrument baseline feature distribution dashboards in Grafana with automated Slack alerts on divergence",
                "Establish weekly manual sample audits by domain experts comparing predictions against ground truth"
            ]
        ))

    return discoveries, probing_questions
