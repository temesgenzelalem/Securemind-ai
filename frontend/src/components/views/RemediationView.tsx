import React, { useState } from "react";
import { Wrench, CheckCircle2, Copy, ExternalLink, Code2, Sparkles } from "lucide-react";

export const RemediationView: React.FC = () => {
  const [remediations, setRemediations] = useState([
    {
      id: "rem-1",
      finding_title: "Reflected Cross-Site Scripting (XSS) in Search Query",
      framework: "Next.js / React (TypeScript)",
      status: "In Progress",
      explanation: "User input from the 'q' query parameter is rendered into the DOM without sanitization, allowing attackers to execute arbitrary JavaScript in the victim's session.",
      strategy: "Sanitize all reflected inputs using DOMPurify or let React JSX automatically escape string values. Avoid using dangerouslySetInnerHTML.",
      vulnerable_code: `// Vulnerable: Directly injecting unescaped search parameter\nexport default function SearchPage({ searchParams }: { searchParams: { q: string } }) {\n  return <div dangerouslySetInnerHTML={{ __html: \`Search for: \${searchParams.q}\` }} />;\n}`,
      secure_code: `// Secure: Safe React JSX string interpolation\nexport default function SearchPage({ searchParams }: { searchParams: { q: string } }) {\n  return (\n    <div>\n      <h2>Search for: {searchParams.q}</h2>\n    </div>\n  );\n}`,
      references: [
        "https://owasp.org/www-community/attacks/xss/",
        "https://nextjs.org/docs/app/building-your-application/data-fetching"
      ]
    },
    {
      id: "rem-2",
      finding_title: "Missing Content-Security-Policy (CSP) Header",
      framework: "Next.js Middleware",
      status: "Open",
      explanation: "Absence of a Content-Security-Policy header permits browsers to load malicious scripts, frames, and objects from arbitrary external origins.",
      strategy: "Implement a strict CSP policy in Next.js middleware with nonce-based script loading.",
      vulnerable_code: `// Missing security headers configuration in next.config.js or middleware.ts`,
      secure_code: `// middleware.ts\nimport { NextResponse } from 'next/server';\n\nexport function middleware(request: Request) {\n  const response = NextResponse.next();\n  response.headers.set(\n    'Content-Security-Policy',\n    "default-src 'self'; script-src 'self' 'nonce-xyz'; object-src 'none';"\n  );\n  return response;\n}`,
      references: [
        "https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP"
      ]
    }
  ]);

  const updateStatus = (id: string, newStatus: string) => {
    setRemediations(prev => prev.map(r => r.id === id ? { ...r, status: newStatus } : r));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-indigo-400" />
          AI Remediation Center
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Framework-tailored, copy-pasteable patches and defensive engineering recommendations.
        </p>
      </div>

      {/* Remediation Cards */}
      <div className="space-y-6">
        {remediations.map((rem) => (
          <div key={rem.id} className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 space-y-4">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-slate-800/80 pb-4">
              <div>
                <span className="text-xs font-mono text-indigo-400 font-semibold">{rem.framework}</span>
                <h3 className="text-base font-bold text-white mt-0.5">{rem.finding_title}</h3>
              </div>

              {/* Status Switcher */}
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-400">Status:</span>
                <select 
                  value={rem.status} 
                  onChange={(e) => updateStatus(rem.id, e.target.value)}
                  className="bg-slate-950 border border-slate-700 text-slate-200 text-xs rounded px-2.5 py-1"
                >
                  <option value="Open">Open</option>
                  <option value="In Progress">In Progress</option>
                  <option value="Fixed">Fixed</option>
                  <option value="Accepted Risk">Accepted Risk</option>
                </select>
              </div>
            </div>

            {/* Explanation & Strategy */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div className="p-3 bg-slate-950 rounded-lg border border-slate-800/80">
                <span className="font-semibold text-slate-300 block mb-1">Vulnerability Explanation:</span>
                <p className="text-slate-400 leading-relaxed">{rem.explanation}</p>
              </div>
              <div className="p-3 bg-indigo-950/20 rounded-lg border border-indigo-900/40">
                <span className="font-semibold text-indigo-300 block mb-1">Recommended Fix Strategy:</span>
                <p className="text-indigo-200/80 leading-relaxed">{rem.strategy}</p>
              </div>
            </div>

            {/* Code Diff Comparison */}
            <div className="space-y-2">
              <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                <Code2 className="w-4 h-4 text-indigo-400" />
                Tailored Code Patch
              </span>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {/* Vulnerable */}
                <div>
                  <span className="text-[11px] font-mono text-rose-400 block mb-1">✕ Vulnerable Pattern</span>
                  <pre className="p-3 bg-slate-950 border border-rose-900/40 rounded-lg text-[11px] font-mono text-rose-300/80 overflow-x-auto whitespace-pre">
                    {rem.vulnerable_code}
                  </pre>
                </div>
                {/* Secure */}
                <div>
                  <span className="text-[11px] font-mono text-emerald-400 block mb-1">✓ Secure Replacement</span>
                  <pre className="p-3 bg-slate-950 border border-emerald-900/40 rounded-lg text-[11px] font-mono text-emerald-300/90 overflow-x-auto whitespace-pre">
                    {rem.secure_code}
                  </pre>
                </div>
              </div>
            </div>

            {/* References */}
            <div className="pt-2 flex items-center gap-3 text-xs text-slate-500">
              <span>Official References:</span>
              {rem.references.map((ref, idx) => (
                <a key={idx} href={ref} target="_blank" rel="noreferrer" className="text-indigo-400 hover:underline flex items-center gap-1">
                  <span>Documentation #{idx + 1}</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
