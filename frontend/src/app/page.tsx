import React from "react";
import { Shield, Cpu, Activity, AlertTriangle, CheckCircle, Terminal } from "lucide-react";

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Top Navbar */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-indigo-600 rounded-lg text-white shadow-lg shadow-indigo-500/20">
            <Shield className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
              SecureMind <span className="text-indigo-400">AI</span>
            </h1>
            <p className="text-xs text-slate-400">Agentic Security Analysis & Remediation</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
            System Operational
          </span>
          <button className="px-4 py-2 text-xs font-medium bg-indigo-600 hover:bg-indigo-500 text-white rounded-md transition shadow">
            Sign In
          </button>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-6 py-12">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-4xl font-extrabold tracking-tight sm:text-5xl text-white mb-4">
            Autonomous Cybersecurity Powered by <span className="text-indigo-400">Coordinated AI</span>
          </h2>
          <p className="text-lg text-slate-400">
            SecureMind AI couples industry standard scanning engines (OWASP ZAP & Nuclei) with 6 specialized AI agents to discover, verify, prioritize, and remediate web application vulnerabilities.
          </p>
        </div>

        {/* System Architecture Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
          <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl">
            <div className="w-10 h-10 bg-indigo-500/10 text-indigo-400 rounded-lg flex items-center justify-center mb-4">
              <Cpu className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Central AI Orchestrator</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Plans, delegates, and supervises assessments across 6 specialized agents: Authorization, Reconnaissance, Vulnerability Scanning, Verification, Risk, and Remediation.
            </p>
          </div>

          <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl">
            <div className="w-10 h-10 bg-emerald-500/10 text-emerald-400 rounded-lg flex items-center justify-center mb-4">
              <CheckCircle className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Evidence-Based Verification</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Filters out false positives by cross-referencing HTTP request/response payloads before reporting findings to development teams.
            </p>
          </div>

          <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl">
            <div className="w-10 h-10 bg-purple-500/10 text-purple-400 rounded-lg flex items-center justify-center mb-4">
              <Terminal className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Framework-Tailored Fixes</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Provides practical, copy-pasteable code patches and security guidance directly customized for your application stack (Next.js, Django, Laravel).
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-6 px-6 text-center text-xs text-slate-500">
        SecureMind AI &copy; 2026. Document ID: SMAI-SRS-001. Built for SaaS and Self-Hosted Operations.
      </footer>
    </div>
  );
}
