import React from "react";
import { Shield, AlertTriangle, CheckCircle2, Crosshair, Cpu, ArrowUpRight, Clock } from "lucide-react";

export const OverviewView: React.FC = () => {
  const stats = [
    { label: "Monitored Assets", value: "4", change: "+1 this week", icon: Shield, color: "text-indigo-400", bg: "bg-indigo-500/10" },
    { label: "Verified Vulnerabilities", value: "12", change: "3 False Positives Eliminated", icon: AlertTriangle, color: "text-amber-400", bg: "bg-amber-500/10" },
    { label: "Remediation Rate", value: "78%", change: "5 fixed recently", icon: CheckCircle2, color: "text-emerald-400", bg: "bg-emerald-500/10" },
    { label: "Active Assessments", value: "1 Running", change: "OWASP ZAP & Nuclei", icon: Crosshair, color: "text-blue-400", bg: "bg-blue-500/10" },
  ];

  const agentFleet = [
    { name: "Central Orchestrator", id: "SMAI-AI-ORC-001", status: "Active", task: "Supervising assessment pipeline" },
    { name: "01 Authorization Agent", id: "SMAI-AI-AGT-001", status: "Idle", task: "Verified DNS challenge for app.example.com" },
    { name: "02 Reconnaissance Agent", id: "SMAI-AI-AGT-002", status: "Idle", task: "Fingerprinted Next.js / Nginx stack" },
    { name: "03 Vulnerability Scanning Agent", id: "SMAI-AI-AGT-003", status: "Working", task: "Coordinating ZAP active scan" },
    { name: "04 Verification Agent", id: "SMAI-AI-AGT-004", status: "Working", task: "Inspecting HTTP response DOM reflection" },
    { name: "05 Risk Assessment Agent", id: "SMAI-AI-AGT-005", status: "Standby", task: "Awaiting verified finding stream" },
    { name: "06 Remediation Agent", id: "SMAI-AI-AGT-006", status: "Standby", task: "Prepared to generate TypeScript / Django patches" },
  ];

  return (
    <div className="space-y-8">
      {/* Top Welcome */}
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight">Security Posture Overview</h2>
        <p className="text-xs text-slate-400 mt-1">Autonomous multi-agent intelligence and dynamic application security testing status.</p>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, i) => {
          const Icon = stat.icon;
          return (
            <div key={i} className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-medium text-slate-400">{stat.label}</span>
                <div className={`p-2 rounded-lg ${stat.bg} ${stat.color}`}>
                  <Icon className="w-4 h-4" />
                </div>
              </div>
              <div>
                <span className="text-2xl font-bold text-white tracking-tight">{stat.value}</span>
                <p className="text-[11px] text-slate-500 mt-1">{stat.change}</p>
              </div>
            </div>
          );
        })}
      </div>

      {/* AI Agent Fleet Status */}
      <div className="p-6 rounded-xl bg-slate-900/60 border border-slate-800">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Cpu className="w-5 h-5 text-indigo-400" />
            <h3 className="text-sm font-semibold text-white">Coordinated AI Agent Fleet Status</h3>
          </div>
          <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
            7/7 Systems Nominal
          </span>
        </div>

        <div className="divide-y divide-slate-800/60">
          {agentFleet.map((agent, i) => (
            <div key={i} className="py-3.5 flex items-center justify-between text-xs">
              <div className="flex items-center gap-3">
                <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                <div>
                  <span className="font-semibold text-slate-200">{agent.name}</span>
                  <span className="text-slate-500 ml-2 font-mono text-[10px]">({agent.id})</span>
                </div>
              </div>
              <span className="text-slate-400 hidden sm:inline">{agent.task}</span>
              <span className={`px-2 py-0.5 rounded text-[11px] font-medium ${
                agent.status === "Working"
                  ? "bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 animate-pulse"
                  : "bg-slate-800 text-slate-400"
              }`}>
                {agent.status}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
