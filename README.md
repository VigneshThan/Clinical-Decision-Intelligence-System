# Clinical Intelligence Assistant

Clinical Intelligence Assistant is a decision-intelligence system for healthcare product analysts working on EHR workflows such as medication management, order routing, clinical documentation, and billing validation. The project simulates how a product analyst would review test failures, trace them to requirements, understand clinical or business impact, and recommend the next action before a release moves forward.

## Clinical Scenario

A healthcare organization is preparing an EHR release that touches medication ordering, urgent order routing, discharge documentation, and billing workflows. Regression testing has started to uncover failures, but the product analyst still needs to answer five questions quickly:

1. What is failing?
2. Why is it failing?
3. What requirement is impacted?
4. What is the clinical or business impact?
5. What should happen next?

This system is built to answer those questions clearly.

## Problem Statement

Traditional release dashboards often show counts, charts, and pass rates, but they do not help an analyst make a decision. In clinical systems, that gap matters because a failure can affect patient safety, documentation integrity, operational throughput, or revenue capture.

The challenge is not just tracking defects. It is connecting:

- failed clinical tests
- violated requirements
- root causes
- downstream impact
- next-step recommendations

## Solution Overview

The backend and frontend work together as a healthcare product analyst system rather than a generic engineering dashboard.

The system includes:

- realistic clinical test data across `Medication`, `Orders`, `Documentation`, and `Billing`
- issue tracking records linked to failed test scenarios
- a clinical analytics engine that groups failures by module and requirement
- decision-focused release scoring and risk prioritization
- a rule-based insight engine with optional OpenAI support
- workflow improvement and automation impact panels for operational thinking

## Backend Design

The FastAPI backend exposes four primary endpoints:

- `GET /dashboard-summary`
- `GET /issues`
- `GET /tests`
- `GET /insights`

These endpoints provide:

- top clinical risk summary
- realistic issue records
- test validation scenarios
- requirement impact data
- root cause summaries
- release confidence score
- AI-style decision insight
- UiPath automation impact

## Testing Strategy

The project simulates the testing mindset expected in healthcare product work.

Each failed test includes:

- test identifier
- EHR module
- requirement mapping
- severity
- root cause
- clinical or business impact
- recommended action

This supports requirement traceability and release validation in a way that feels close to real analyst work inside systems like MEDITECH Expanse.

## Insight Engine

The insight engine is designed to be specific, causal, and actionable.

Rule-based behavior:

- identifies the highest-risk module
- detects failure clusters
- summarizes dominant root causes
- counts impacted requirements
- produces a single decision-focused insight

Example output:

`Failures in the Medication module are primarily caused by validation rule misconfiguration after prescription workflow update, impacting multiple requirements and increasing patient safety risk. Immediate validation fixes and regression test expansion are recommended.`

Optional OpenAI behavior:

- if `OPENAI_API_KEY` is available and the OpenAI SDK is installed, the backend can generate the same style of structured insight with an LLM
- if not available, the system safely falls back to rule-based reasoning

## Automation Impact (UiPath)

The system also simulates operational improvement through automation.

It includes a backend response section for:

- manual triage time
- automated triage time
- time saved percentage
- automated actions such as Jira ticket logging, stakeholder notification, and targeted regression triggers

This reflects how product analysts often think beyond defect tracking and into workflow efficiency.

## Business Impact

The dashboard is designed to surface the types of impact that matter in healthcare delivery:

- patient safety risk when medication or urgent order workflows fail
- operational delay when order status updates do not reach downstream teams
- documentation integrity risk when signatures or audit trails are missing
- revenue leakage when billing mappings fail

## Frontend Experience

The React and Tailwind frontend is intentionally decision-focused instead of chart-heavy.

The dashboard includes:

- Clinical Risk Summary
- Failure -> Root Cause -> Recommended Action table
- Requirement Impact panel
- Workflow Improvement panel
- Release Confidence Score
- AI Insights panel
- Automation Impact panel

Additional views are available for issue tracking, test scenario review, and focused insights.

## How to Run

### Single Command

From the project root:

```bash
./run-dev.sh
```

This starts both:

- FastAPI backend on `http://localhost:8000`
- Vite frontend on `http://localhost:5173`

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

If you want to run backend and frontend separately, use the backend and frontend commands above.

If you want a single command from the project root, use:

```bash
./run-dev.sh
```

Backend runs on `http://localhost:8000` and frontend runs on Vite's default local port.

## Why This Project Matters

This project is meant to demonstrate more than frontend or backend implementation skill. It is meant to show that the builder understands:

- healthcare workflow validation
- requirement traceability
- release decision support
- root cause analysis
- automation thinking
- product analyst reasoning in a clinical environment
