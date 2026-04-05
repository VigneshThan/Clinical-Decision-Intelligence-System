import os
from collections import Counter

from services.issue_analyzer import failed_tests, load_tests

SUPPORTED_MODULES = ("Medication", "Documentation", "Orders", "Billing")
SEVERITY_SCORES = {"critical": 4, "high": 3, "medium": 2, "low": 1}


def detect_module(question: str) -> str | None:
    lowered = question.lower()
    for module in SUPPORTED_MODULES:
        if module.lower() in lowered:
            return module
    return None


def detect_intent(question: str) -> str:
    lowered = question.lower()
    if "highest risk" in lowered or "risk" in lowered:
        return "risk"
    if "requirement" in lowered or "violated" in lowered:
        return "requirements"
    if "fix first" in lowered or "priority" in lowered or "should we fix" in lowered or "action" in lowered:
        return "actions"
    return "failures"


def filter_relevant_tests(question: str, tests: list[dict]) -> tuple[str | None, list[dict]]:
    module = detect_module(question)
    filtered = [test for test in failed_tests(tests) if not module or test["module"] == module]
    return module, filtered or failed_tests(tests)


def summarize_root_causes(tests: list[dict]) -> list[str]:
    counts = Counter(test["root_cause"] for test in tests)
    return [cause for cause, _count in counts.most_common(3)]


def summarize_requirements(tests: list[dict]) -> list[str]:
    requirements = []
    for test in tests:
        if test["requirement"] not in requirements:
            requirements.append(test["requirement"])
    return requirements[:5]


def summarize_actions(tests: list[dict]) -> list[str]:
    actions = []
    for test in tests:
        if test["recommended_action"] not in actions:
            actions.append(test["recommended_action"])
    return actions[:4]


def count_by_module(tests: list[dict]) -> Counter:
    return Counter(test["module"] for test in tests)


def patient_safety_related(test: dict) -> bool:
    clinical_text = f"{test['impact']} {test.get('clinical_impact_detail', '')}".lower()
    return any(
        phrase in clinical_text
        for phrase in ("patient safety", "life-threatening", "unsafe", "duplicate treatments", "harm")
    )


def priority_score(test: dict, module_counts: Counter) -> int:
    score = SEVERITY_SCORES.get(test["severity"].lower(), 0) * 10
    if patient_safety_related(test):
        score += 40
    if test.get("regression"):
        score += 20
    score += module_counts.get(test["module"], 0) * 5
    return score


def top_priority_test(tests: list[dict]) -> dict:
    module_counts = count_by_module(tests)
    return max(tests, key=lambda test: priority_score(test, module_counts))


def assess_risk_level(tests: list[dict]) -> str:
    if any(patient_safety_related(test) and test["severity"].lower() == "critical" for test in tests):
        return "High"
    if any(test["severity"].lower() == "critical" for test in tests):
        return "High"
    if any(test["severity"].lower() == "high" for test in tests):
        return "Medium"
    return "Low"


def regression_detected(tests: list[dict]) -> bool:
    return any(test.get("regression") for test in tests)


def analyst_style_answer(intent: str, module: str | None, tests: list[dict]) -> str:
    lead_test = top_priority_test(tests)
    scoped_module = module or lead_test["module"]
    lead_cause = lead_test["root_cause"]
    impact_detail = lead_test.get("clinical_impact_detail", lead_test["impact"])
    regression_note = " This is a regression from a previous release." if regression_detected(tests) else ""

    if intent == "risk":
        return (
            f"The highest current risk sits in the {scoped_module} module, where {lead_cause.lower()} is affecting "
            f"clinically sensitive workflow controls. {impact_detail}{regression_note}"
        )
    if intent == "requirements":
        return (
            f"The most impacted requirements are in {scoped_module}, where failures are breaking expected clinical safeguards. "
            f"The main driver is {lead_cause.lower()}.{regression_note}"
        )
    if intent == "actions":
        return (
            f"The first fix should target the {lead_test['module']} workflow because {lead_test['failure'].lower()} is tied to "
            f"{lead_cause.lower()} and carries the strongest clinical impact.{regression_note}"
        )
    return (
        f"Failures in the {scoped_module} module are caused by {lead_cause.lower()}, which is leading to "
        f"{impact_detail.lower()}.{regression_note}"
    )


def build_priority_decision(tests: list[dict]) -> str:
    lead_test = top_priority_test(tests)
    module = lead_test["module"]
    severity = lead_test["severity"].lower()
    safety_phrase = "patient safety" if patient_safety_related(lead_test) else "clinical workflow"
    regression_phrase = " regression" if lead_test.get("regression") else ""
    return (
        f"Block release due to {severity}{regression_phrase} failure in the {module} module affecting "
        f"{lead_test['failure'].lower()}, because it poses immediate {safety_phrase} risk."
    )


def build_analyst_summary(tests: list[dict]) -> str:
    lead_test = top_priority_test(tests)
    stakeholder_text = ", ".join(lead_test.get("stakeholders", [])[:3])
    regression_text = " This is a regression from a previous release." if lead_test.get("regression") else ""
    return (
        f"Stakeholders including {stakeholder_text} should treat {lead_test['module']} as the leading release concern. "
        f"The failure affects {lead_test['requirement'].lower()} and should be resolved before go-live.{regression_text}"
    )


def build_rule_based_response(question: str) -> dict:
    tests = load_tests()
    intent = detect_intent(question)
    module, relevant_tests = filter_relevant_tests(question, tests)
    lead_test = top_priority_test(relevant_tests)

    return {
        "answer": analyst_style_answer(intent, module, relevant_tests),
        "details": {
            "affected_module": module or lead_test["module"],
            "failed_tests": len(relevant_tests),
            "root_causes": summarize_root_causes(relevant_tests),
            "impacted_requirements": summarize_requirements(relevant_tests),
            "risk_level": assess_risk_level(relevant_tests),
            "regression_detected": regression_detected(relevant_tests),
            "recommended_actions": summarize_actions(relevant_tests),
        },
        "priority_decision": build_priority_decision(relevant_tests),
        "analyst_summary": build_analyst_summary(relevant_tests),
    }


def build_openai_response(question: str) -> dict | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        from openai import OpenAI
    except ImportError:
        return None

    tests = load_tests()
    module, relevant_tests = filter_relevant_tests(question, tests)
    lead_test = top_priority_test(relevant_tests)
    details = {
        "affected_module": module or lead_test["module"],
        "failed_tests": len(relevant_tests),
        "root_causes": summarize_root_causes(relevant_tests),
        "impacted_requirements": summarize_requirements(relevant_tests),
        "risk_level": assess_risk_level(relevant_tests),
        "regression_detected": regression_detected(relevant_tests),
        "recommended_actions": summarize_actions(relevant_tests),
    }
    priority_decision = build_priority_decision(relevant_tests)
    analyst_summary = build_analyst_summary(relevant_tests)

    prompt = (
        "You are a clinical product analyst working on an EHR system. Analyze the provided failures and answer the user question. "
        "Be specific, causal, and actionable.\n\n"
        f"Question: {question}\n"
        f"Structured details: {details}\n"
        f"Priority decision: {priority_decision}\n"
        f"Stakeholder summary: {analyst_summary}\n"
        "If regression_detected is true, explicitly say: This is a regression from a previous release."
    )

    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt,
        temperature=0.2,
    )

    return {
        "answer": response.output_text.strip(),
        "details": details,
        "priority_decision": priority_decision,
        "analyst_summary": analyst_summary,
    }


def run_agent_query(question: str) -> dict:
    openai_result = build_openai_response(question)
    if openai_result:
        return openai_result
    return build_rule_based_response(question)
