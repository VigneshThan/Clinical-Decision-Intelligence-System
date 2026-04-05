import os

from services.issue_analyzer import analyze_clinical_intelligence, load_issues, load_tests


def build_rule_based_insight() -> str:
    tests = load_tests()
    issues = load_issues()
    analysis = analyze_clinical_intelligence(tests, issues)
    return analysis["ai_insight"]


def build_ai_insight() -> dict:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"source": "rule-based", "insight": build_rule_based_insight()}

    try:
        from openai import OpenAI
    except ImportError:
        return {"source": "rule-based", "insight": build_rule_based_insight()}

    tests = load_tests()
    issues = load_issues()
    analysis = analyze_clinical_intelligence(tests, issues)
    summary = analysis["dashboard_summary"]
    top_module = summary["highest_risk_module"]
    prompt = (
        "You are a healthcare product analyst assistant. Produce one concise, specific, causal, actionable insight. "
        "Do not use generic wording. Mention the top failing module, likely cause, impacted requirements, clinical or "
        "business impact, and the next action.\n\n"
        f"Top module: {top_module}\n"
        f"Risk level: {summary['risk_level']}\n"
        f"Failure count: {summary['failed_tests_count']}\n"
        f"Rule-based summary: {analysis['ai_insight']}"
    )

    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        temperature=0.2,
    )
    return {"source": "openai", "insight": response.output_text.strip()}
