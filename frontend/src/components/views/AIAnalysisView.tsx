import React, { useState, useEffect } from "react";
import { Cpu, ShieldAlert, Sparkles, CheckCircle2, Clock, Code2, ChevronDown, ChevronRight, Activity, Terminal } from "lucide-react";
import { api } from "@/services/api";

export const AIAnalysisView: React.FC = () => {
  const [executions, setExecutions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const specializedAgents = [
    {
      id: "SMAI-AI-AGT-001",
      name: "Authorization Agent",
      role: "Validates target asset verification status, domain boundaries, and human sign-off policies.",
      model: "Pydantic Deterministic Guard",
      stage: "Pre-Scan Validation"
    },
    {
      id: "SMAI-AI-AGT-002",
      name: "Reconnaissance Agent",
      role: "Fingerprints server technologies, web frameworks, and analyzes HTTP security headers.",
      model: "Heuristic + Gemini Flash",
      stage: "Stack Discovery"
    },
    {
      id: "SMAI-AI-AGT-003",
      name: "Vulnerability Scanning Agent",
      role: "Supervises OWASP ZAP and Nuclei engines, applying rate-limiting and timeouts.",
      model: "Process Orchestrator",
      stage: "DAST Coordination"
    },
    {
      id: "SMAI-AI-AGT-004",
      name: "Verification Agent",
      role: "Inspects raw HTTP request/response proofs to verify reproducibility and eliminate false positives.",
      model: "Evidence Signature Matcher",
      stage: "Evidence Verification"
    },
    {
      id: "SMAI-AI-AGT-005",
      name: "Risk Assessment Agent",
      role: "Evaluates business impact, maps severity to priority, and preserves standard CVSS v3.1 metrics.",
      model: "Contextual Risk Evaluator",
      stage: "Risk Prioritization"
    },
    {
      id: "SMAI-AI-AGT-006",
      name: "Remediation Agent",
      role: "Synthesizes framework-specific before/after code diffs and step-by-step mitigation guidance.",
      model: "Code Synthesis Engine",
      stage: "Actionable Patches"
    }
  ];

  const fetchExecutions = async () => {
    setLoading(true);
    try {
      const res = await api.agents.listExecutions();
      setExecutions(res.data.results || res.data || []);
    } catch (err: any) {
      console.warn("Could not fetch live agent telemetry, loading preview baseline.");
      setExecutions([
        {
          id: "exec-001",
          agent_name: "verification",
          status: "completed",
          execution_time_seconds: 0.142,
          tokens_used: 120,
          model_used: "deterministic-heuristic",
          created_at: new Date().toISOString(),
          input_payload: {
            finding_title: "Reflected Cross-Site Scripting (XSS)",
            parameter: "q",
            payload_used: "<script>alert(1)</script>"
          },
          output_payload: {
            verification_status: "confirmed",
            confidence_score: 0.95,
            is_false_positive: false,
            execution_evidence_observed: true
          }
        },
        {
          id: "exec-002",
          agent_name: "remediation",
          status: "completed",
          execution_time_seconds: 0.285,
          tokens_used: 350,
          model_used: "gemini-2.5-flash",
          created_at: new Date().toISOString(),
          input_payload: {
            finding_title: "Missing Content Security Policy (CSP)",
            detected_framework: "Next.js"
          },
          output_payload: {
            remediation_strategy: "Configure Content-Security-Policy HTTP header in next.config.js",
            developer_action_items: ["Review header config", "Test in staging", "Deploy"]
          }
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExecutions();
  }, []);

  const toggleExpand = (id: string) => {
    setExpandedId(prev => prev === id ? null : id);
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <Cpu className="w-5 h-5 text-indigo-400" />
          Central AI Orchestrator & 6 Specialized Agents
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          One unified orchestrator supervising 6 Pydantic v2 schema-validated agents for defensive security analysis.
        </p>
      </div>

      {/* 6 Specialized Agents Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {specializedAgents.map((agent, idx) => (
          <div key={agent.id} className="p-4 bg-slate-900/40 border border-slate-800 rounded-xl space-y-2.5 hover:border-slate-700 transition">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-950/80 text-indigo-400 border border-indigo-800/60 font-semibold">
                {agent.id}
              </span>
              <span className="text-[10px] text-slate-500 font-medium">{agent.stage}</span>
            </div>
            <h3 className="text-sm font-bold text-white tracking-tight flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
              {agent.name}
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              {agent.role}
            </p>
            <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-500">
              <span>Engine:</span>
              <span className="text-slate-300 font-mono text-[10px]">{agent.model}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Live Agent Execution Telemetry */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
            <Activity className="w-4 h-4 text-emerald-400" />
            Agent Execution Telemetry Log
          </h3>
          <span className="text-xs text-slate-400">Strict Pydantic Input/Output Schemas</span>
        </div>

        <div className="bg-slate-900/40 border border-slate-800 rounded-xl overflow-hidden divide-y divide-slate-800">
          {loading ? (
            <div className="p-8 text-center text-xs text-slate-400">Loading agent telemetry...</div>
          ) : executions.length === 0 ? (
            <div className="p-12 text-center text-xs text-slate-400">No agent executions logged yet.</div>
          ) : (
            executions.map((exec) => {
              const isExpanded = expandedId === exec.id;
              return (
                <div key={exec.id} className="hover:bg-slate-900/60 transition">
                  <div
                    onClick={() => toggleExpand(exec.id)}
                    className="p-4 flex items-center justify-between cursor-pointer select-none"
                  >
                    <div className="flex items-center gap-3">
                      {isExpanded ? (
                        <ChevronDown className="w-4 h-4 text-slate-400" />
                      ) : (
                        <ChevronRight className="w-4 h-4 text-slate-400" />
                      )}
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-bold text-white uppercase tracking-wider">
                            {exec.agent_name.replace("_", " ")} Agent
                          </span>
                          <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-emerald-950 text-emerald-400 border border-emerald-800/60 flex items-center gap-1">
                            <CheckCircle2 className="w-2.5 h-2.5" /> {exec.status}
                          </span>
                        </div>
                        <span className="text-[11px] text-slate-400 block mt-0.5">
                          Logged: {new Date(exec.created_at).toLocaleTimeString()} | Duration: <strong className="text-slate-300">{exec.execution_time_seconds}s</strong>
                        </span>
                      </div>
                    </div>

                    <div className="text-right text-xs text-slate-400 font-mono text-[11px]">
                      {exec.model_used || "deterministic"}
                    </div>
                  </div>

                  {isExpanded && (
                    <div className="p-4 bg-slate-950/60 border-t border-slate-800 space-y-3 font-mono text-xs">
                      <div>
                        <span className="text-[10px] uppercase font-semibold text-slate-500 tracking-wider block mb-1">
                          Validated Input Payload (Pydantic Schema)
                        </span>
                        <pre className="p-3 bg-slate-950 border border-slate-800 rounded-lg text-slate-300 overflow-x-auto text-[11px]">
                          {JSON.stringify(exec.input_payload, null, 2)}
                        </pre>
                      </div>
                      <div>
                        <span className="text-[10px] uppercase font-semibold text-indigo-400 tracking-wider block mb-1">
                          Validated Output Payload
                        </span>
                        <pre className="p-3 bg-slate-950 border border-indigo-950 rounded-lg text-indigo-200 overflow-x-auto text-[11px]">
                          {JSON.stringify(exec.output_payload, null, 2)}
                        </pre>
                      </div>
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};
