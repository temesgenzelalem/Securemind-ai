import React, { useState } from "react";
import { Crosshair, Play, CheckCircle2, Clock, AlertTriangle, Shield, Check, X } from "lucide-react";

export const AssessmentsView: React.FC = () => {
  const [showLaunchModal, setShowLaunchModal] = useState(false);

  const assessments = [
    {
      id: "scn-902",
      asset: "securemind.ai",
      type: "Comprehensive Template Scan",
      status: "Running",
      current_stage: "04 Verification Agent: Correlating HTTP responses",
      progress: 68,
      findings_count: 7,
      started_at: "2026-11-18 11:20:15",
      requires_approval: false,
    },
    {
      id: "scn-901",
      asset: "api.securemind.ai",
      type: "Passive Reconnaissance",
      status: "Completed",
      current_stage: "Consolidated Final Assessment",
      progress: 100,
      findings_count: 3,
      started_at: "2026-11-17 18:45:00",
      requires_approval: false,
    },
    {
      id: "scn-900",
      asset: "staging.clientapp.org",
      type: "Controlled Active Scan",
      status: "Awaiting Approval",
      current_stage: "Human-in-the-loop sign-off required for active payloads",
      progress: 0,
      findings_count: 0,
      started_at: "Pending",
      requires_approval: true,
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Security Assessments</h2>
          <p className="text-xs text-slate-400 mt-1">Autonomous DAST and template-based vulnerability assessment pipeline.</p>
        </div>
        <button 
          onClick={() => setShowLaunchModal(true)}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold flex items-center gap-2 transition shadow-md shadow-indigo-500/20"
        >
          <Play className="w-4 h-4 fill-current" />
          <span>Launch Assessment</span>
        </button>
      </div>

      {/* Assessments List */}
      <div className="space-y-4">
        {assessments.map((scan) => (
          <div key={scan.id} className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-3">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
              <div className="flex items-center gap-3">
                <div className="p-2.5 bg-indigo-500/10 text-indigo-400 rounded-lg">
                  <Crosshair className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white">{scan.asset}</h3>
                  <span className="text-[11px] text-slate-400">{scan.type} • ID: {scan.id}</span>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <span className={`px-2.5 py-1 rounded-full text-[11px] font-medium ${
                  scan.status === "Running" ? "bg-blue-500/10 text-blue-400 border border-blue-500/20 animate-pulse" :
                  scan.status === "Completed" ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" :
                  "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                }`}>
                  {scan.status}
                </span>

                {scan.requires_approval && (
                  <button className="px-3 py-1 bg-amber-600 hover:bg-amber-500 text-white rounded text-[11px] font-semibold transition">
                    Approve Scan
                  </button>
                )}
              </div>
            </div>

            {/* Live Pipeline Stage */}
            <div className="bg-slate-950 p-3 rounded-lg border border-slate-800/80 text-xs flex items-center justify-between">
              <span className="text-slate-400">Current Pipeline Stage: <strong className="text-indigo-300 font-semibold">{scan.current_stage}</strong></span>
              <span className="font-mono text-slate-300">{scan.progress}%</span>
            </div>

            {/* Progress Bar */}
            <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
              <div 
                className={`h-full transition-all duration-500 ${scan.status === "Completed" ? "bg-emerald-500" : "bg-indigo-500"}`} 
                style={{ width: `${scan.progress}%` }}
              ></div>
            </div>
          </div>
        ))}
      </div>

      {/* Launch Modal */}
      {showLaunchModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-lg w-full p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Shield className="w-5 h-5 text-indigo-400" />
                Configure New Assessment
              </h3>
              <button onClick={() => setShowLaunchModal(false)} className="text-slate-400 hover:text-white">✕</button>
            </div>

            <div className="space-y-4 text-xs">
              <div>
                <label className="text-slate-400 font-semibold block mb-1">Target Application:</label>
                <select className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200">
                  <option>securemind.ai (Verified • 84 days remaining)</option>
                  <option>api.securemind.ai (Verified • 72 days remaining)</option>
                </select>
              </div>

              <div>
                <label className="text-slate-400 font-semibold block mb-1">Scan Profile:</label>
                <div className="space-y-2">
                  <label className="flex items-start gap-3 p-3 rounded-lg bg-slate-950 border border-slate-800 cursor-pointer">
                    <input type="radio" name="profile" defaultChecked className="mt-0.5 text-indigo-600" />
                    <div>
                      <span className="font-bold text-white block">Passive Reconnaissance</span>
                      <span className="text-slate-400 text-[11px]">Zero-impact analysis: headers, technology detection, and observed endpoints.</span>
                    </div>
                  </label>
                  <label className="flex items-start gap-3 p-3 rounded-lg bg-slate-950 border border-slate-800 cursor-pointer">
                    <input type="radio" name="profile" className="mt-0.5 text-indigo-600" />
                    <div>
                      <span className="font-bold text-white block">Controlled Active Scan (Safe Payloads)</span>
                      <span className="text-slate-400 text-[11px]">Probes for XSS, SQLi, and configuration flaws with non-disruptive payloads.</span>
                    </div>
                  </label>
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-3">
              <button 
                onClick={() => setShowLaunchModal(false)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-xs font-medium"
              >
                Cancel
              </button>
              <button 
                onClick={() => setShowLaunchModal(false)}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-xs font-semibold"
              >
                Start Assessment
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
