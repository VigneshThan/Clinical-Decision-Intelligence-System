import json
from collections import Counter, defaultdict
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SEVERITY_WEIGHTS = {"critical": 20, "high": 12, "medium": 6, "low": 2}
RISK_LEVELS = ((70, "High"), (40, "Medium"), (0, "Low"))


def load_tests() -> list[dict]:
    return json.loads((DATA_DIR / "test_results.json").read_text())


def load_issues() -> list[dict]:
    return json.loads((DATA_DIR / "issues.json").read_text())


def normalize_status(status: str) -> str:
    return status.strip().lower()


def failed_tests(tests: list[dict]) -> list[dict]:
    return [test for test in tests if normalize_status(test["status"]) == "failed"]


def severity_rank(severity: str) -> int:
    order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    return order.get(severity.lower(), 0)


def risk_level(score: int) -> str:
    for threshold, label in RISK_LEVELS:
        if score >= threshold:
            return label
    return "Low"


def module_grouped_failures(tests: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for test in failed_tests(tests):
        grouped[test["module"]].append(test)
    return dict(grouped)


def calculate_release_confidence(tests: list[dict]) -> dict:
    failures = failed_tests(tests)
    failure_weight = len(failures) * 4
    critical_weight = sum(
        SEVERITY_WEIGHTS.get(test["severity"].lower(), 0)
        for test in failures
        if test["severity"].lower() == "critical"
    )
    score = max(0, 100 - (failure_weight + critical_weight))

    return {
        "score": score,
        "explanation": (
            f"Release confidence starts at 100 and is reduced by {failure_weight} points for failure volume "
            f"and {critical_weight} points for critical severity exposure."
        ),
    }


def build_failure_clusters(tests: list[dict]) -> list[dict]:
    cluster_map: dict[str, dict] = {}
    for test in failed_tests(tests):
        cluster = test["failure_cluster"]
        entry = cluster_map.setdefault(
            cluster,
            {
                "cluster": cluster,
                "count": 0,
                "modules": set(),
                "tests": [],
            },
        )
        entry["count"] += 1
        entry["modules"].add(test["module"])
        entry["tests"].append(test["test_name"])

    results = []
    for entry in cluster_map.values():
        results.append(
            {
                "cluster": entry["cluster"],
                "count": entry["count"],
                "modules": sorted(entry["modules"]),
                "tests": entry["tests"],
            }
        )
    return sorted(results, key=lambda item: item["count"], reverse=True)


def build_requirement_violations(tests: list[dict]) -> list[dict]:
    requirement_map: dict[str, dict] = {}
    for test in failed_tests(tests):
        entry = requirement_map.setdefault(
            test["requirement_id"],
            {
                "requirement_id": test["requirement_id"],
                "requirement": test["requirement"],
                "affected_modules": set(),
                "linked_failed_tests": [],
                "highest_severity": "low",
            },
        )
        entry["affected_modules"].add(test["module"])
        entry["linked_failed_tests"].append(test["test_name"])
        if severity_rank(test["severity"]) > severity_rank(entry["highest_severity"]):
            entry["highest_severity"] = test["severity"]

    rows = []
    for item in requirement_map.values():
        rows.append(
            {
                "requirement_id": item["requirement_id"],
                "requirement": item["requirement"],
                "affected_modules": sorted(item["affected_modules"]),
                "linked_failed_tests": item["linked_failed_tests"],
                "highest_severity": item["highest_severity"],
            }
        )
    return sorted(rows, key=lambda item: severity_rank(item["highest_severity"]), reverse=True)


def build_root_cause_summaries(tests: list[dict]) -> list[dict]:
    cause_map = Counter(test["root_cause"] for test in failed_tests(tests))
    return [
        {"root_cause": root_cause, "count": count}
        for root_cause, count in cause_map.most_common()
    ]


def build_module_risk(tests: list[dict]) -> list[dict]:
    grouped = module_grouped_failures(tests)
    risk_rows = []
    total_failed = len(failed_tests(tests)) or 1

    for module, module_tests in grouped.items():
        critical_count = sum(1 for test in module_tests if test["severity"].lower() == "critical")
        score = sum(SEVERITY_WEIGHTS.get(test["severity"].lower(), 0) for test in module_tests)
        risk_rows.append(
            {
                "module": module,
                "failed_tests": len(module_tests),
                "critical_issues": critical_count,
                "risk_score": score,
                "risk_level": risk_level(score),
                "impact": module_tests[0]["impact"],
                "requirements_impacted": sorted({test["requirement_id"] for test in module_tests}),
                "failure_share": round((len(module_tests) / total_failed) * 100),
            }
        )

    return sorted(risk_rows, key=lambda item: item["risk_score"], reverse=True)


def build_failure_action_table(tests: list[dict]) -> list[dict]:
    return [
        {
            "test_id": test["test_id"],
            "module": test["module"],
            "failure": test["test_name"],
            "root_cause": test["root_cause"],
            "recommended_action": test["recommended_action"],
            "severity": test["severity"],
        }
        for test in failed_tests(tests)
    ]


def build_workflow_improvement_panel() -> dict:
    return {
        "before": [
            "Manual validation of EHR workflow changes during release review",
            "Missed requirement checks when regression scope is narrowed",
            "Root cause triage scattered across test logs and issue trackers",
        ],
        "after": [
            "Automated validation highlights failing workflows by module and severity",
            "Requirement impact is traceable from failed test to decision panel",
            "Recommended next actions are generated for product analysts and stakeholders",
        ],
    }


def build_automation_impact() -> dict:
    manual_minutes = 120
    automated_minutes = 20
    time_saved_percent = round(((manual_minutes - automated_minutes) / manual_minutes) * 100)

    return {
        "manual_triage_time": "2 hours",
        "automated_triage_time": "20 minutes",
        "time_saved_percent": time_saved_percent,
        "automated_actions": [
            "Auto-log Jira tickets for critical failures",
            "Notify stakeholders when patient-safety requirements are violated",
            "Trigger focused regression suite for impacted clinical modules",
        ],
        "operational_efficiency_gain": (
            "Automation reduces analyst coordination effort and shortens time from failure detection to action."
        ),
    }


def build_dashboard_summary(tests: list[dict]) -> dict:
    failures = failed_tests(tests)
    module_risk = build_module_risk(tests)
    top_module = module_risk[0] if module_risk else None

    return {
        "total_tests": len(tests),
        "failed_tests": len(failures),
        "critical_issues": sum(1 for test in failures if test["severity"].lower() == "critical"),
        "highest_risk_module": top_module["module"] if top_module else None,
        "risk_level": top_module["risk_level"] if top_module else "Low",
        "impact": top_module["impact"] if top_module else "No major impact detected",
        "failed_tests_count": top_module["failed_tests"] if top_module else 0,
    }


def build_insight_text(tests: list[dict]) -> str:
    module_risk = build_module_risk(tests)
    requirement_violations = build_requirement_violations(tests)
    top_module = module_risk[0] if module_risk else None
    if not top_module:
        return "No major failures are currently detected across monitored clinical workflows."

    matching_requirements = [
        item for item in requirement_violations if top_module["module"] in item["affected_modules"]
    ]
    dominant_test = next(
        test for test in failed_tests(tests) if test["module"] == top_module["module"]
    )
    requirement_count = len(matching_requirements)

    return (
        f"Failures in the {top_module['module']} module are primarily caused by "
        f"{dominant_test['root_cause'].lower()}, impacting {requirement_count} requirements and increasing "
        f"{dominant_test['impact'].lower()}. Immediate {dominant_test['recommended_action'].lower()} are recommended."
    )


def analyze_clinical_intelligence(tests: list[dict], issues: list[dict]) -> dict:
    release_confidence = calculate_release_confidence(tests)
    module_risk = build_module_risk(tests)
    return {
        "dashboard_summary": build_dashboard_summary(tests),
        "failure_action_table": build_failure_action_table(tests),
        "requirement_impact": build_requirement_violations(tests),
        "workflow_improvement": build_workflow_improvement_panel(),
        "release_confidence": release_confidence,
        "ai_insight": build_insight_text(tests),
        "automation_impact": build_automation_impact(),
        "failure_clusters": build_failure_clusters(tests),
        "root_cause_summaries": build_root_cause_summaries(tests),
        "module_risk": module_risk,
        "issues": issues,
    }
