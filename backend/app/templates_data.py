"""
Pre-configured industry templates for testing and demonstration.
Includes realistic project documents (PRDs), datasets (CSV), and workflow pipelines.
"""

TEMPLATES = {
    "timetable_generator": {
        "id": "timetable_generator",
        "title": "Intelligent College Timetable Generator",
        "domain": "general",
        "badge": "OR-Tools CP-SAT & Genetic Algorithm",
        "description": "Automated, conflict-free college timetabling system powered by Google OR-Tools CP-SAT and Adaptive Genetic Algorithms.",
        "document_title": "System Specification: Intelligent College Timetable Generator",
        "document_text": """# Intelligent College Timetable Generator

An automated, conflict-free college and university timetabling system powered by **Google OR-Tools CP-SAT (Exact Constraint Programming)** and an **Adaptive Genetic Algorithm (Evolutionary Metaheuristic)**.

The system simultaneously balances faculty availability, classroom capacities, student batches, course weekly quotas, continuous lab blocks, and multi-objective soft optimization goals (minimizing student and instructor idle gaps, balancing daily workloads, and maximizing classroom utilization).

---

## 🌟 Key Capabilities & Features

- **Dual-Engine Intelligent Solver**:
  - **Google OR-Tools CP-SAT Solver**: Mathematically provably optimal constraint programming engine guaranteeing **0 hard constraint clashes**.
  - **Advanced Genetic Algorithm**: Evolutionary metaheuristic with domain-aware repair mutation and elitism for flexible Pareto optimization.
- **Strict Hard Constraint Enforcement**:
  - **No Faculty Double-Booking**: An instructor cannot be in two classrooms at the same time.
  - **No Student Batch Double-Booking**: A student section cannot attend two lectures simultaneously.
  - **No Room Overlap**: A classroom or lab can host at most one class per time period.
  - **Classroom Seating Capacity**: Rooms are strictly verified to ensure capacity >= batch size.
  - **Room Type Matching**: Laboratory sessions (Computer, Electronics, Physics) are strictly routed to matching lab facilities, and theory classes to lecture halls.
  - **Faculty Availability & Blackout Windows**: Respects designated unavailable hours (e.g., department meetings, research blocks).
  - **Consecutive Multi-Period Blocks**: 2-hour or 3-hour lab sessions are scheduled as contiguous blocks on the same day without crossing lunch or day boundaries.
  - **Faculty Daily Workload Limits**: Caps max daily teaching hours per instructor.
- **Multi-Objective Soft Optimization**:
  - **Minimizing Student Idle Gaps**: Eliminates awkward gaps between morning and afternoon lectures.
  - **Minimizing Faculty Idle Wait Time**: Consolidates instructor schedules.
  - **Daily Workload Balancing**: Distributes course lectures evenly across Monday–Friday.
  - **Maximizing Resource Utilization**: Compact classroom and laboratory scheduling.
  - **Faculty Preferred Slots**: Prioritizes scheduling professors during their preferred time windows.
- **Interactive Web Studio**:
  - Perspective switching: Batch Timetable, Faculty Schedules, and Room Occupancy.
  - Conflict Auditor: Automated audit engine verifying every constraint with live clash reporting.
  - Interactive Slot Move & Swap: Click any class card to preview or move slots with real-time clash re-validation.
  - Optimization Weight Tuning: Interactive sliders to adjust optimization priorities in real time.
- **Multi-Format Document Exports**:
  - Excel (.xlsx): Formatted, color-coded multi-tab workbook with Executive Summary, Batch grids, Faculty schedules, and Room occupancy.
  - PDF (.pdf): Publication-grade landscape timetable report designed with ReportLab.
""",
        "dataset_name": "timetable_courses_and_rooms.csv",
        "dataset_content": """course_code,course_name,batch_id,batch_size,faculty_id,weekly_hours,is_lab,room_type_needed
CS201,Data Structures,CSE-A,65,FAC-101,4,0,lecture_hall
CS202,Database Systems,CSE-A,65,FAC-102,3,0,lecture_hall
CS203,Data Structures Lab,CSE-A,65,FAC-101,2,1,computer_lab
AI301,Machine Learning,AI-DS,70,FAC-103,4,0,lecture_hall
AI302,ML GPU Lab,AI-DS,70,FAC-103,3,1,gpu_ai_lab
EC301,Digital Signal Processing,ECE,55,FAC-104,4,0,lecture_hall
EC302,DSP Hardware Lab,ECE,55,FAC-104,2,1,circuits_lab
BS401,Corporate Finance,MBA-1,80,FAC-105,3,0,executive_amphitheater
BS402,Financial Modeling Lab,MBA-1,80,FAC-105,2,1,bloomberg_lab
CS204,Operating Systems,CSE-B,60,FAC-106,3,0,lecture_hall
""",
        "workflow_content": """1. Administrator configures faculty availability blackout slots and classroom capacities
2. Solver pre-processor verifies hard constraint matrix and building room types
3. Google OR-Tools CP-SAT solver computes exact conflict-free timetable guaranteeing 0 clashes
4. Adaptive Genetic Algorithm metaheuristic optimizes soft goals (minimizing student idle gaps)
5. Conflict auditor executes comprehensive rule verification
6. Exporters compile color-coded multi-sheet Excel (.xlsx) and publication-grade PDF (.pdf)
"""
    },
    "healthcare_triage": {
        "id": "healthcare_triage",
        "title": "MedAI: Real-Time Emergency Clinical Triage Engine",
        "domain": "healthcare",
        "badge": "Clinical AI / Critical Safety",
        "description": "Hospital emergency department clinical decision support system evaluating incoming patient vitals to prioritize trauma beds.",
        "document_title": "PRD: MedAI Autonomous ER Patient Prioritization System v2.1",
        "document_text": """# Product Requirement Document (PRD): MedAI Clinical Triage System

## 1. Executive Overview
MedAI is an intelligent, real-time emergency room decision-support platform designed to streamline triage in level-1 trauma centers. By ingesting real-time physiological vitals and electronic health records (EHR), MedAI automatically assigns Emergency Severity Index (ESI Levels 1 to 5) to incoming patients within 60 seconds of arrival.

## 2. Core Functional Requirements
- **FR-1 Vitals Ingestion**: System continuously ingests heart rate, blood pressure, SpO2 (oxygen saturation), respiratory rate, and age from wireless triage monitors.
- **FR-2 Automated Triage Scoring**: A deep ensemble model computes triage priority. High priority scores (ESI 1 & 2) automatically reserve trauma bay beds and notify attending physicians.
- **FR-3 Cloud Processing**: All inference is processed in our multi-tenant AWS cloud cluster to leverage high-performance GPUs and vector embeddings.
- **FR-4 Attending Physician Notification**: An automated SMS alert is dispatched to on-call emergency physicians when a Level 1 patient arrives.

## 3. Architecture & Operational Assumptions
- The hospital's emergency department Wi-Fi network maintains 99.99% uptime with uniform coverage throughout triage bays, ambulances, and decontamination chambers.
- Medical staff will trust the AI recommendation and prioritize patients according to model rankings without manual re-calculation.
- Historical patient EHR data is clean, comprehensive, and accurately reflects regional demographics.
- Third-party SMS gateway delivery latency is under 500ms nationwide.
- The system stores all patient vitals, clinical notes, and inference explanations in the cloud database indefinitely for retrospective research and model retraining.
""",
        "dataset_name": "er_patient_vitals_sample.csv",
        "dataset_content": """patient_id,age,heart_rate,systolic_bp,oxygen_saturation,triage_category,insurance_status
PT-1001,45,88,124,98.5,ESI_4,insured
PT-1002,62,115,165,92.0,ESI_2,insured
PT-1003,29,74,118,99.0,ESI_5,insured
PT-1004,-1,95,130,95.0,ESI_3,uninsured
PT-1005,71,130,85,88.0,ESI_1,insured
PT-1006,53,-99,140,,ESI_3,insured
PT-1007,84,68,110,91.5,ESI_2,insured
PT-1008,38,82,122,98.0,ESI_4,insured
PT-1009,142,105,155,93.5,ESI_2,uninsured
PT-1010,50,78,126,97.0,ESI_4,insured
PT-1011,67,140,78,86.0,ESI_1,insured
PT-1012,31,70,115,99.5,ESI_5,insured
PT-1013,58,92,132,,ESI_3,insured
PT-1014,75,110,145,90.5,ESI_2,insured
PT-1015,22,65,112,99.0,ESI_5,insured
""",
        "workflow_content": """1. Nurse attaches wireless pulse oximeter and BP cuff to patient at triage bay
2. IoT gateway streams raw sensor data to cloud API endpoint via hospital Wi-Fi
3. MedAI Cloud Model generates ESI priority tier (1-5) and trauma bay recommendation
4. System automatically calls third-party SMS gateway to page attending physician on-call
5. Patient is queued in trauma bay allocation dashboard
"""
    },

    "fintech_lending": {
        "id": "fintech_lending",
        "title": "CrediFlow: Subprime Instant Loan Underwriting Pipeline",
        "domain": "fintech",
        "badge": "FinTech / High Concurrency",
        "description": "Algorithmic micro-lending pipeline granting instant credit approvals and direct deposit disbursement in under 45 seconds.",
        "document_title": "System Specification: CrediFlow Autonomous Underwriting Engine v3.0",
        "document_text": """# Technical Specification: CrediFlow Underwriting Engine

## 1. System Objective
CrediFlow provides instant automated loan decisions for working-class applicants. The platform promises 'Funds in Your Account in 60 Seconds' by automating credit bureau ingestion, alternative fraud scoring, and immediate ACH / card push disbursement.

## 2. Decision Logic & Pipeline
- **Step 1**: User submits online application (income, employer, SSN, bank credentials).
- **Step 2**: Backend calls Experian and Plaid APIs synchronously to pull FICO score and 90-day bank transactions.
- **Step 3**: XGBoost underwriting model scores default probability. Applicants with risk score < 0.28 are approved instantly up to $2,500.
- **Step 4**: Payment processor initiates real-time debit card push payment to applicant's checking account.

## 3. Assumptions & Operating Parameters
- Credit bureau API will always respond within 800ms. If the bureau is slow, request threads block until response arrives.
- Historical loan repayment dataset used for model training contains zero survivorship bias (trained on historical approved borrowers).
- Applicants will never exploit simultaneous multi-device submissions to withdraw funds multiple times.
- State-by-state maximum APR caps and Fair Credit Reporting Act (FCRA) adverse action explanation letters can be handled via standard batch emails once a month.
""",
        "dataset_name": "loan_training_distribution.csv",
        "dataset_content": """applicant_id,monthly_income,credit_score,existing_debt,defaulted_past_3yr,loan_approved
AP-801,4200,680,12000,0,1
AP-802,3100,610,8500,0,1
AP-803,5500,720,4000,0,1
AP-804,-99,590,15000,0,1
AP-805,2800,580,22000,1,0
AP-806,6200,750,1500,0,1
AP-807,3900,640,9000,0,1
AP-808,4800,690,6500,0,1
AP-809,3500,-1,11000,0,1
AP-810,5100,710,5000,0,1
AP-811,4400,670,7200,0,1
AP-812,3200,630,9500,0,1
AP-813,5900,740,3000,0,1
AP-814,4100,660,8200,0,1
AP-815,2900,600,13000,0,1
""",
        "workflow_content": """1. Applicant clicks 'Submit Application' on web or mobile client
2. Backend server validates form fields and contacts credit bureau via synchronous REST API
3. Machine learning underwriting service evaluates applicant default probability
4. If approved, payment service immediately charges $25 underwriting fee via Stripe
5. Disburse $2,500 loan proceeds to applicant bank account via instant push-to-card
6. Send confirmation SMS to user
"""
    },

    "ecommerce_flash_sale": {
        "id": "ecommerce_flash_sale",
        "title": "HyperCart: Black Friday Distributed Checkout Workflow",
        "domain": "ecommerce",
        "badge": "High Throughput / E-Commerce",
        "description": "High-volume flash sale order processing pipeline handling 50,000 checkout requests per second across global regions.",
        "document_title": "Architecture Doc: HyperCart Multi-Region Flash Checkout Orchestrator",
        "document_text": """# Architecture Document: HyperCart Global Flash Sale Platform

## 1. System Goals
Support peak surge traffic during annual Black Friday promotions, scaling up to 75,000 requests/second with sub-second checkout completion.

## 2. Distributed Workflow
1. User clicks 'Complete Purchase'
2. Web gateway routes request to regional Kubernetes cluster
3. Payment service charges customer credit card via Stripe API
4. Inventory service decrements available stock in central PostgreSQL database
5. Fulfillment service creates warehouse pick ticket and shipping label
6. Notification service dispatches confirmation email with order receipt

## 3. Performance & Capacity Assumptions
- Central PostgreSQL database can handle synchronous row updates with standard row-level locking during peak traffic.
- If Stripe payment succeeds, the subsequent inventory deduction step will always succeed because stock was verified during cart addition 5 minutes earlier.
- In the rare event a warehouse is out of stock after payment is processed, warehouse operators will resolve it during morning packing shifts.
- Cloud network latency between European regional clusters and US East database is negligible (< 10ms).
""",
        "dataset_name": "",
        "dataset_content": "",
        "workflow_content": """1. Client submits checkout payload with credit card token
2. Charge customer card via external payment gateway (Stripe)
3. Decrement product inventory count in database
4. Generate shipping label and dispatch warehouse packing order
5. Send email receipt and trigger SMS delivery tracking
"""
    },

    "iot_fleet_telemetry": {
        "id": "iot_fleet_telemetry",
        "title": "FleetPulse: Commercial Autonomous Edge Telematics",
        "domain": "iot_edge",
        "badge": "IoT Edge / Telematics",
        "description": "Predictive maintenance and telemetry pipeline for 100,000 connected freight vehicles traversing cross-country highways.",
        "document_title": "System Specification: FleetPulse Edge Telematics & Predictive Maintenance",
        "document_text": """# FleetPulse Edge Telematics Architecture Specification

## 1. System Mission
FleetPulse monitors engine thermals, brake pad wear, tire pressure, and ADAS camera feeds across 100,000 commercial Class-8 long-haul freight trucks to predict mechanical failure before roadside breakdowns occur.

## 2. Ingestion & Edge Architecture
- Each truck has an onboard Linux compute unit connected to the CAN bus.
- Telemetry is sampled at 50Hz and uploaded to cloud MQTT brokers via 4G/5G cellular modems.
- Cloud microservices process streaming data using Kafka and Flink, storing all raw time-series metrics in Amazon DynamoDB.

## 3. Operational Assumptions
- Trucks maintain steady 4G cellular coverage along all Interstate and secondary freight corridors.
- Onboard vehicle clocks are perfectly synchronized with NTP time servers at all times.
- The flash storage on edge gateways can support continuous unbuffered debug logging 24 hours a day for 5 years without wearing out NAND flash cells.
- Data ingestion costs and DynamoDB write capacity units will scale linearly with fleet expansion without hitting provisioned throughput limits.
""",
        "dataset_name": "",
        "dataset_content": "",
        "workflow_content": """1. Onboard sensor microcontroller polls engine CAN bus every 20ms
2. Edge device serializes telemetry into JSON packets
3. Edge device publishes packet to cloud MQTT broker over cellular connection
4. Cloud Kafka consumer deserializes telemetry and updates real-time predictive failure model
5. If failure probability > 85%, send push notification to fleet dispatcher
"""
    }
}
