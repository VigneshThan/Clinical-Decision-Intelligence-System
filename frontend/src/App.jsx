import { useEffect, useState } from "react";

const API_BASE = "http://localhost:8000";

const TAB_ITEMS = [
  { id: "dashboard", label: "Dashboard" },
  { id: "issues", label: "Issues" },
  { id: "tests", label: "Tests" },
  { id: "ask", label: "Ask the System" },
];

const RISK_STYLES = {
  High: "bg-rose-500 text-white",
  Medium: "bg-amber-400 text-slate-950",
  Low: "bg-emerald-400 text-slate-950",
};

const SEVERITY_STYLES = {
  critical: "bg-rose-100 text-rose-700 ring-1 ring-rose-200",
  high: "bg-amber-100 text-amber-700 ring-1 ring-amber-200",
  medium: "bg-sky-100 text-sky-700 ring-1 ring-sky-200",
  low: "bg-emerald-100 text-emerald-700 ring-1 ring-emerald-200",
};

function ShellCard({ title, eyebrow, children, className = "" }) {
  return (
    <section className={`rounded-[28px] border border-slate-200 bg-white p-6 shadow-[0_24px_70px_-40px_rgba(15,23,42,0.18)] ${className}`}>
      {(eyebrow || title) && (
        <div className="mb-5">
          {eyebrow ? <p className="text-xs uppercase tracking-[0.28em] text-sky-700">{eyebrow}</p> : null}
          {title ? <h2 className="mt-2 text-xl font-semibold text-slate-900">{title}</h2> : null}
        </div>
      )}
      {children}
    </section>
  );
}

function TabButton({ active, label, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`rounded-full px-4 py-2 text-sm font-medium transition ${
        active ? "bg-slate-900 text-white" : "bg-white text-slate-600 ring-1 ring-slate-200 hover:bg-slate-50"
      }`}
    >
      {label}
    </button>
  );
}

function RiskBadge({ label }) {
  return (
    <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${RISK_STYLES[label] || RISK_STYLES.Low}`}>
      {label}
    </span>
  );
}

function SeverityBadge({ severity }) {
  return (
    <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold uppercase ${SEVERITY_STYLES[severity] || SEVERITY_STYLES.medium}`}>
      {severity}
    </span>
  );
}

function SummaryMetric({ label, value, description, tone = "text-slate-900" }) {
  return (
    <div className="rounded-[24px] border border-slate-200 bg-slate-50 p-5">
      <p className="text-sm uppercase tracking-[0.2em] text-slate-500">{label}</p>
      <p className={`mt-4 text-4xl font-semibold ${tone}`}>{value}</p>
      <p className="mt-2 text-sm leading-6 text-slate-600">{description}</p>
    </div>
  );
}

function QuickAskCard({ question, setQuestion, onAsk, asking, openAskTab }) {
  const quickPrompts = [
    "What is the highest risk module?",
    "Why are tests failing in Medication?",
    "What should we fix first?",
  ];

  return (
    <ShellCard eyebrow="Quick Access" title="Ask the System from the dashboard">
      <div className="space-y-4">
        <p className="text-sm leading-6 text-slate-600">
          Use the assistant like a chatbot here, or open the full Ask the System page for a larger response view.
        </p>
        <div className="flex flex-wrap gap-2">
          {quickPrompts.map((prompt) => (
            <button
              key={prompt}
              onClick={() => setQuestion(prompt)}
              className="rounded-full bg-slate-100 px-4 py-2 text-sm text-slate-700 hover:bg-slate-200"
            >
              {prompt}
            </button>
          ))}
        </div>
        <textarea
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          className="min-h-28 w-full rounded-[24px] border border-slate-200 bg-white p-4 text-sm text-slate-900 outline-none placeholder:text-slate-400 focus:border-sky-300"
          placeholder="Ask a clinical question here."
        />
        <div className="flex flex-wrap gap-3">
          <button
            onClick={onAsk}
            disabled={asking}
            className="rounded-full bg-slate-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400"
          >
            {asking ? "Asking..." : "Ask Now"}
          </button>
          <button
            onClick={openAskTab}
            className="rounded-full bg-white px-5 py-3 text-sm font-semibold text-slate-700 ring-1 ring-slate-200 transition hover:bg-slate-50"
          >
            Open Full Ask the System
          </button>
        </div>
      </div>
    </ShellCard>
  );
}

function DashboardView({ summary, question, setQuestion, onAsk, asking, openAskTab }) {
  return (
    <div className="space-y-6">
      <ShellCard eyebrow="Clinical Risk Summary" title="Release status at a glance">
        <div className="grid gap-4 xl:grid-cols-4">
          <SummaryMetric
            label="Highest Risk Module"
            value={summary.highest_risk_module}
            description="The module with the strongest concentration of failed clinical validation."
          />
          <SummaryMetric
            label="Risk Level"
            value={summary.risk_level}
            description="Severity-adjusted view of release risk."
            tone="text-rose-600"
          />
          <SummaryMetric
            label="Impact"
            value={summary.impact}
            description="Clinical or business consequence if this issue pattern reaches production."
            tone="text-amber-600"
          />
          <SummaryMetric
            label="Failed Tests"
            value={summary.failed_tests_count}
            description="Failed scenarios tied to the highest-risk module."
            tone="text-sky-700"
          />
        </div>
      </ShellCard>

      <ShellCard eyebrow="How To Use It" title="Ask questions instead of reading static analysis">
        <div className="grid gap-4 md:grid-cols-3">
          <div className="rounded-[22px] bg-slate-50 p-4">
            <p className="text-sm font-semibold text-slate-900">Ask what is failing</p>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              Example: Why are medication tests failing?
            </p>
          </div>
          <div className="rounded-[22px] bg-slate-50 p-4">
            <p className="text-sm font-semibold text-slate-900">Ask what is impacted</p>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              Example: Which requirements are violated?
            </p>
          </div>
          <div className="rounded-[22px] bg-slate-50 p-4">
            <p className="text-sm font-semibold text-slate-900">Ask what to do next</p>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              Example: What should we fix first?
            </p>
          </div>
        </div>
      </ShellCard>

      <QuickAskCard
        question={question}
        setQuestion={setQuestion}
        onAsk={onAsk}
        asking={asking}
        openAskTab={openAskTab}
      />
    </div>
  );
}

function IssuesView({ issues }) {
  return (
    <ShellCard eyebrow="Issue Tracking" title="Open clinical workflow issues">
      <div className="space-y-4">
        {issues.map((issue) => (
          <article key={issue.issue_id} className="rounded-[24px] border border-slate-200 bg-slate-50 p-5">
            <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.18em] text-slate-500">{issue.issue_id} • {issue.module}</p>
                <h3 className="mt-2 text-lg font-semibold text-slate-900">{issue.summary}</h3>
              </div>
              <SeverityBadge severity={issue.severity} />
            </div>
            <p className="mt-3 text-sm leading-6 text-slate-600">{issue.impact}</p>
            <div className="mt-4 grid gap-3 lg:grid-cols-3">
              <p className="rounded-2xl bg-white p-3 text-sm text-slate-700 ring-1 ring-slate-200">{issue.requirement}</p>
              <p className="rounded-2xl bg-white p-3 text-sm text-slate-700 ring-1 ring-slate-200">{issue.root_cause}</p>
              <p className="rounded-2xl bg-white p-3 text-sm text-slate-700 ring-1 ring-slate-200">{issue.recommended_action}</p>
            </div>
          </article>
        ))}
      </div>
    </ShellCard>
  );
}

function TestsView({ tests }) {
  return (
    <ShellCard eyebrow="Clinical Testing" title="Simulated EHR validation scenarios">
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm text-slate-700">
          <thead className="border-b border-slate-200 text-slate-500">
            <tr>
              <th className="py-3 pr-4 font-medium">Test ID</th>
              <th className="py-3 pr-4 font-medium">Module</th>
              <th className="py-3 pr-4 font-medium">Test Name</th>
              <th className="py-3 pr-4 font-medium">Requirement</th>
              <th className="py-3 pr-4 font-medium">Status</th>
              <th className="py-3 font-medium">Impact</th>
            </tr>
          </thead>
          <tbody>
            {tests.map((test) => (
              <tr key={test.test_id} className="border-b border-slate-100 align-top">
                <td className="py-4 pr-4 font-semibold text-slate-900">{test.test_id}</td>
                <td className="py-4 pr-4">{test.module}</td>
                <td className="py-4 pr-4">{test.test_name}</td>
                <td className="py-4 pr-4">{test.requirement}</td>
                <td className="py-4 pr-4">
                  <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${test.status === "failed" ? "bg-rose-100 text-rose-700" : "bg-emerald-100 text-emerald-700"}`}>
                    {test.status}
                  </span>
                </td>
                <td className="py-4 text-slate-600">{test.impact}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </ShellCard>
  );
}

function AskSystemView({ question, setQuestion, response, onAsk, asking }) {
  const prompts = [
    "What is the highest risk module?",
    "Why are tests failing in Medication?",
    "Which requirements are violated?",
    "What should we fix first?",
  ];

  return (
    <div className="space-y-6">
      <ShellCard eyebrow="Ask The System" title="Query the clinical product analyst assistant">
        <div className="space-y-4">
          <div className="flex flex-wrap gap-2">
            {prompts.map((prompt) => (
              <button
                key={prompt}
                onClick={() => setQuestion(prompt)}
                className="rounded-full bg-slate-100 px-4 py-2 text-sm text-slate-700 hover:bg-slate-200"
              >
                {prompt}
              </button>
            ))}
          </div>
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            className="min-h-36 w-full rounded-[24px] border border-slate-200 bg-white p-4 text-sm text-slate-900 outline-none placeholder:text-slate-400 focus:border-sky-300"
            placeholder="Ask about failures, requirements, risk, or what to fix first."
          />
          <button
            onClick={onAsk}
            disabled={asking}
            className="rounded-full bg-slate-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400"
          >
            {asking ? "Asking..." : "Ask"}
          </button>
        </div>
      </ShellCard>

      <ShellCard eyebrow="Response" title="Agent answer">
        {!response ? (
          <p className="text-slate-600">Ask a question to get a focused clinical analysis.</p>
        ) : (
          <div className="space-y-6">
            <div className="rounded-[24px] bg-sky-50 p-5">
              <p className="text-xs uppercase tracking-[0.18em] text-sky-700">Answer</p>
              <p className="mt-3 text-base leading-8 text-slate-800">{response.answer}</p>
            </div>

            <div className="rounded-[24px] bg-rose-50 p-5">
              <p className="text-xs uppercase tracking-[0.18em] text-rose-700">Priority Decision</p>
              <p className="mt-3 text-base leading-8 font-medium text-slate-900">{response.priority_decision}</p>
            </div>

            <div className="grid gap-4 xl:grid-cols-2">
              <div className="rounded-[24px] border border-slate-200 bg-slate-50 p-5">
                <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Root Causes</p>
                <div className="mt-3 space-y-2">
                  {response.details.root_causes.map((item) => (
                    <p key={item} className="rounded-2xl bg-white p-3 text-sm leading-6 text-slate-700">
                      {item}
                    </p>
                  ))}
                </div>
              </div>

              <div className="rounded-[24px] border border-slate-200 bg-slate-50 p-5">
                <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Requirements Impact</p>
                <div className="mt-3 flex flex-wrap gap-2">
                  {response.details.impacted_requirements.map((item) => (
                    <span key={item} className="rounded-full bg-white px-3 py-2 text-xs text-slate-700 ring-1 ring-slate-200">
                      {item}
                    </span>
                  ))}
                </div>
              </div>

              <div className="rounded-[24px] border border-slate-200 bg-slate-50 p-5">
                <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Risk Level</p>
                <div className="mt-3 flex items-center gap-3">
                  <RiskBadge label={response.details.risk_level} />
                  <p className="text-sm text-slate-600">
                    {response.details.failed_tests} failed tests in scope for {response.details.affected_module}
                  </p>
                </div>
                <p className="mt-3 text-sm text-slate-600">
                  Regression detected: {response.details.regression_detected ? "Yes" : "No"}
                </p>
              </div>

              <div className="rounded-[24px] border border-slate-200 bg-slate-50 p-5">
                <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Recommended Actions</p>
                <div className="mt-3 space-y-2">
                  {response.details.recommended_actions.map((item) => (
                    <p key={item} className="rounded-2xl bg-white p-3 text-sm leading-6 text-slate-700">
                      {item}
                    </p>
                  ))}
                </div>
              </div>
            </div>

            <div className="rounded-[24px] bg-emerald-50 p-5">
              <p className="text-xs uppercase tracking-[0.18em] text-emerald-700">Analyst Summary</p>
              <p className="mt-3 text-base leading-8 text-slate-800">{response.analyst_summary}</p>
            </div>
          </div>
        )}
      </ShellCard>
    </div>
  );
}

function App() {
  const [page, setPage] = useState("dashboard");
  const [issues, setIssues] = useState([]);
  const [tests, setTests] = useState([]);
  const [dashboardSummary, setDashboardSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [question, setQuestion] = useState("Why are tests failing in Medication?");
  const [response, setResponse] = useState(null);
  const [asking, setAsking] = useState(false);

  useEffect(() => {
    Promise.all([
      fetch(`${API_BASE}/dashboard-summary`).then((res) => res.json()),
      fetch(`${API_BASE}/issues`).then((res) => res.json()),
      fetch(`${API_BASE}/tests`).then((res) => res.json()),
    ])
      .then(([summaryData, issuesData, testsData]) => {
        setDashboardSummary(summaryData);
        setIssues(issuesData.issues || []);
        setTests(testsData.tests || []);
        setError("");
      })
      .catch(() => {
        setError("Unable to load clinical intelligence data. Start the FastAPI backend on port 8000.");
      })
      .finally(() => setLoading(false));
  }, []);

  const askSystem = async () => {
    if (!question.trim()) {
      return;
    }

    setAsking(true);
    try {
      const res = await fetch(`${API_BASE}/agent/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      setResponse(data);
    } catch {
      setResponse({
        answer: "The agent query service is unavailable right now.",
        details: {
          failed_tests: 0,
          root_causes: [],
          impacted_requirements: [],
          risk_level: "Low",
          recommended_actions: ["Confirm the backend is running and retry the question."],
        },
      });
    } finally {
      setAsking(false);
    }
  };

  return (
    <div className="min-h-screen bg-[linear-gradient(180deg,#f8fbff_0%,#eef5fb_100%)] text-slate-900">
      <div className="mx-auto max-w-7xl px-5 py-8 md:px-8 lg:px-10">
        <header className="rounded-[36px] border border-slate-200 bg-white p-6 shadow-[0_30px_80px_-50px_rgba(14,30,56,0.25)] md:p-8">
          <div className="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
            <div className="max-w-4xl">
              <p className="text-sm uppercase tracking-[0.35em] text-sky-700">Clinical Intelligence Assistant</p>
              <h1 className="mt-4 text-4xl font-semibold leading-tight text-slate-900 md:text-5xl">
                Query-driven decision support for clinical product analysis.
              </h1>
              <p className="mt-4 max-w-3xl text-base leading-7 text-slate-600">
                Ask the system what is failing, why it is failing, which requirements are impacted, and what action should happen next.
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              {TAB_ITEMS.map((item) => (
                <TabButton key={item.id} active={page === item.id} label={item.label} onClick={() => setPage(item.id)} />
              ))}
            </div>
          </div>
        </header>

        <div className="mt-8">
          {loading ? (
            <ShellCard title="Loading clinical intelligence system">
              <p className="text-slate-600">Collecting release summary, issue list, and test scenarios.</p>
            </ShellCard>
          ) : error || !dashboardSummary ? (
            <ShellCard title="Backend connection required">
              <p className="text-slate-600">{error}</p>
            </ShellCard>
          ) : (
            <>
              {page === "dashboard" ? (
                <DashboardView
                  summary={dashboardSummary}
                  question={question}
                  setQuestion={setQuestion}
                  onAsk={askSystem}
                  asking={asking}
                  openAskTab={() => setPage("ask")}
                />
              ) : null}
              {page === "issues" ? <IssuesView issues={issues} /> : null}
              {page === "tests" ? <TestsView tests={tests} /> : null}
              {page === "ask" ? (
                <AskSystemView
                  question={question}
                  setQuestion={setQuestion}
                  response={response}
                  onAsk={askSystem}
                  asking={asking}
                />
              ) : null}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
