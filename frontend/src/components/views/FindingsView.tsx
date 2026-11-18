import React, { useState } from "react";
import { AlertTriangle, ShieldAlert, CheckCircle, FileCode, Search, Filter, Eye } from "lucide-react";

export const FindingsView: React.FC = () => {
  const [selectedFinding, setSelectedFinding] = useState<any>(null);
  const [filterSeverity, setFilterSeverity] = useState<string>("ALL");

  const findings = [
    {
      id: "fnd-101",
      title: "Reflected Cross-Site Scripting (XSS) in Search Query",
      cwe: "CWE-79",
      cvss: 7.5,
      severity: "HIGH",
      verification: "Confirmed",
      confidence: 0.95,
      url: "https://securemind.ai/search?q=%3Cscript%3Ealert(1)%3C/script%3E",
      param: "q",
      scanner: "OWASP ZAP",
      request: "GET /search?q=%3Cscript%3Ealert(1)%3C/script%3E HTTP/1.1\nHost: securemind.ai\nUser-Agent: SecureMind-Scanner",
      response: "HTTP/1.1 200 OK\nContent-Type: text/html\n\n<h1>Search results for: <script>alert(1)</script></h1>",
      analysis: "The probe payload was reflected unescaped directly into the response DOM with a text/html content-type. No sanitization or CSP observed."
    },
    {
      id: "fnd-102",
      title: "Missing Content-Security-Policy (CSP) Header",
      cwe: "CWE-1021",
      cvss: 5.3,
      severity: "MEDIUM",
      verification: "Confirmed",
      confidence: 0.99,
      url: "https://securemind.ai/dashboard",
      param: "-",
      scanner: "OWASP ZAP",
      request: "GET /dashboard HTTP/1.1\nHost: securemind.ai",
      response: "HTTP/1.1 200 OK\nX-Frame-Options: SAMEORIGIN\nStrict-Transport-Security: max-age=31536000",
      analysis: "Response lacks a Content-Security-Policy header, leaving client browsers vulnerable to untrusted script injections."
    },
    {
      id: "fnd-103",
      title: "Nginx Version Exposure in Server Header",
      cwe: "CWE-200",
      cvss: 3.1,
      severity: "LOW",
      verification: "Confirmed",
      confidence: 1.0,
      url: "https://securemind.ai",
      param: "-",
      scanner: "Nuclei",
      request: "GET / HTTP/1.1\nHost: securemind.ai",
      response: "HTTP/1.1 200 OK\nServer: nginx/1.18.0 (Ubuntu)",
      analysis: "Detailed Nginx version '1.18.0' is leaked via standard HTTP response headers."
    },
    {
      id: "fnd-104",
      title: "Potential Blind SQL Injection (Time-based)",
      cwe: "CWE-89",
      cvss: 8.8,
      severity: "CRITICAL",
      verification: "False Positive",
      confidence: 0.90,
      url: "https://securemind.ai/api/v1/auth/verify?token=SLEEP(5)",
      param: "token",
      scanner: "Nuclei",
      request: "GET /api/v1/auth/verify?token=SLEEP(5) HTTP/1.1\nHost: securemind.ai",
      response: "HTTP/1.1 400 Bad Request\n{\"error\": \"Malformed token format.\"}",
      analysis: "Verification Agent analysis: Response delay was due to rate-limiting backoff, not database thread sleep. Server returned 400 Bad Request."
    }
  ];

  const filtered = filterSeverity === "ALL" 
    ? findings 
    : findings.filter(f => f.severity === filterSeverity);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Vulnerability Findings Repository</h2>
          <p className="text-xs text-slate-400 mt-1">Evidence-backed findings with automated false-positive verification.</p>
        </div>

        {/* Severity Filters */}
        <div className="flex items-center gap-1.5 p-1 bg-slate-900 border border-slate-800 rounded-lg text-xs">
          {["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW"].map((sev) => (
            <button
              key={sev}
              onClick={() => setFilterSeverity(sev)}
              className={`px-3 py-1.5 rounded-md font-medium transition ${
                filterSeverity === sev 
                  ? "bg-indigo-600 text-white shadow-sm" 
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              {sev}
            </button>
          ))}
        </div>
      </div>

      {/* Findings Table */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="border-b border-slate-800 bg-slate-900/80 text-slate-400 font-semibold">
              <th className="py-3 px-4">Severity</th>
              <th className="py-3 px-4">Vulnerability</th>
              <th className="py-3 px-4">Verification Status</th>
              <th className="py-3 px-4">Confidence</th>
              <th className="py-3 px-4">Source</th>
              <th className="py-3 px-4 text-right">Evidence</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-300">
            {filtered.map((finding) => (
              <tr key={finding.id} className="hover:bg-slate-800/30 transition">
                <td className="py-3 px-4">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    finding.severity === "CRITICAL" ? "bg-rose-500/10 text-rose-400 border border-rose-500/30" :
                    finding.severity === "HIGH" ? "bg-orange-500/10 text-orange-400 border border-orange-500/30" :
                    finding.severity === "MEDIUM" ? "bg-amber-500/10 text-amber-400 border border-amber-500/30" :
                    "bg-slate-800 text-slate-400"
                  }`}>
                    {finding.severity}
                  </span>
                </td>
                <td className="py-3 px-4">
                  <span className="font-semibold text-white block">{finding.title}</span>
                  <span className="text-[11px] text-slate-400 font-mono truncate max-w-sm block">{finding.url}</span>
                </td>
                <td className="py-3 px-4">
                  <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium ${
                    finding.verification === "Confirmed" ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" :
                    finding.verification === "False Positive" ? "bg-slate-800 text-slate-400 line-through" :
                    "bg-blue-500/10 text-blue-400 border border-blue-500/20"
                  }`}>
                    {finding.verification}
                  </span>
                </td>
                <td className="py-3 px-4 font-mono text-slate-300">
                  {(finding.confidence * 100).toFixed(0)}%
                </td>
                <td className="py-3 px-4 text-slate-400">{finding.scanner}</td>
                <td className="py-3 px-4 text-right">
                  <button 
                    onClick={() => setSelectedFinding(finding)}
                    className="p-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Evidence Drawer Modal */}
      {selectedFinding && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-3xl w-full p-6 space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-base font-bold text-white">{selectedFinding.title}</h3>
                <span className="text-xs text-indigo-400 font-mono">{selectedFinding.cwe} • CVSS {selectedFinding.cvss}</span>
              </div>
              <button onClick={() => setSelectedFinding(null)} className="text-slate-400 hover:text-white">✕</button>
            </div>

            {/* AI Verification Analysis */}
            <div className="p-4 rounded-lg bg-indigo-950/30 border border-indigo-800/40 text-xs">
              <span className="font-bold text-indigo-300 block mb-1">🤖 AI Verification Agent Analysis:</span>
              <p className="text-indigo-200/90 leading-relaxed">{selectedFinding.analysis}</p>
            </div>

            {/* HTTP Request */}
            <div>
              <span className="text-xs font-semibold text-slate-400 block mb-1">HTTP Request:</span>
              <pre className="p-3 bg-slate-950 border border-slate-800 rounded-lg text-[11px] font-mono text-slate-300 overflow-x-auto whitespace-pre">
                {selectedFinding.request}
              </pre>
            </div>

            {/* HTTP Response */}
            <div>
              <span className="text-xs font-semibold text-slate-400 block mb-1">HTTP Response Evidence:</span>
              <pre className="p-3 bg-slate-950 border border-slate-800 rounded-lg text-[11px] font-mono text-emerald-400/90 overflow-x-auto whitespace-pre">
                {selectedFinding.response}
              </pre>
            </div>

            <div className="flex justify-end pt-2">
              <button 
                onClick={() => setSelectedFinding(null)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-xs font-medium"
              >
                Close Evidence
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
