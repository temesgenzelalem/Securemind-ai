import React, { useState } from "react";
import { 
  Shield, 
  Play, 
  Lock, 
  CheckCircle2, 
  AlertTriangle, 
  Cpu, 
  Wrench, 
  FileText, 
  Users, 
  ArrowRight, 
  Sparkles, 
  Globe, 
  Zap, 
  Check, 
  Search, 
  ExternalLink,
  ChevronRight,
  ShieldCheck,
  Code2,
  Terminal,
  Activity,
  Layers,
  FileCheck
} from "lucide-react";

interface LandingPageProps {
  onSelectRoleDemo: (email: string, roleName: string) => void;
  onEnterApp: () => void;
}

export const ROLE_DEMO_DATA = [
  {
    roleKey: "platform_admin",
    name: "Platform Super Administrator",
    badge: "Full Global Authority",
    badgeColor: "bg-purple-500/20 text-purple-300 border-purple-500/30",
    email: "admin@securemind.ai",
    avatar: "👑",
    modulesCount: 9,
    description: "Global system control across all organizations. Manages tenants, AI scan engines, and global audit governance.",
    visibleModules: [
      "Overview Dashboard", 
      "Applications & Assets", 
      "Security Assessments", 
      "Vulnerabilities", 
      "AI Agent Orchestration", 
      "Remediation Center", 
      "Reports", 
      "Team & RBAC", 
      "Global Settings"
    ],
    privileges: [
      "Bypass tenant boundaries for platform administration",
      "Configure global LLM reasoning providers",
      "Manage all organizations & platform users",
      "Full active scan execution & report generation"
    ]
  },
  {
    roleKey: "org_admin",
    name: "Organization Administrator",
    badge: "Workspace Governance",
    badgeColor: "bg-blue-500/20 text-blue-300 border-blue-500/30",
    email: "orgadmin@securemind.ai",
    avatar: "🏢",
    modulesCount: 8,
    description: "Workspace-level administrator. Manages team invitations, assigns member roles, and enforces testing scope limits.",
    visibleModules: [
      "Overview Dashboard", 
      "Applications & Assets", 
      "Security Assessments", 
      "Vulnerabilities", 
      "AI Agent Orchestration", 
      "Remediation Center", 
      "Reports", 
      "Team & RBAC"
    ],
    privileges: [
      "Invite and remove workspace team members",
      "Assign RBAC permissions to developers and analysts",
      "Register web assets and verify domain ownership",
      "Review organization security audit logs"
    ]
  },
  {
    roleKey: "security_analyst",
    name: "Security Analyst (DevSecOps Lead)",
    badge: "Offensive & Defensive AppSec",
    badgeColor: "bg-indigo-500/20 text-indigo-300 border-indigo-500/30",
    email: "analyst@securemind.ai",
    avatar: "🎯",
    modulesCount: 7,
    description: "Security assessment lead. Configures scan profiles, approves controlled active scans, verifies exploits, and downloads reports.",
    visibleModules: [
      "Overview Dashboard", 
      "Applications & Assets", 
      "Security Assessments", 
      "Vulnerabilities", 
      "AI Agent Orchestration", 
      "Remediation Center", 
      "Reports"
    ],
    privileges: [
      "Launch passive recon & active ZAP/Nuclei scans",
      "Provide human approval for controlled active scanning",
      "Inspect live AI Orchestrator execution telemetry",
      "Compile and download formal PDF compliance reports"
    ]
  },
  {
    roleKey: "developer",
    name: "Software Engineer / Developer",
    badge: "Code & Remediation",
    badgeColor: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
    email: "dev@securemind.ai",
    avatar: "💻",
    modulesCount: 4,
    description: "Remediation engineer. Directly reviews verified vulnerabilities, inspects AI-suggested code fixes, and updates triage status.",
    visibleModules: [
      "Overview Dashboard", 
      "Vulnerabilities", 
      "Remediation Center", 
      "Reports"
    ],
    privileges: [
      "Inspect detailed vulnerability proof-of-concept evidence",
      "Review AI-generated code patches with line diffs",
      "Update issue triage status (In Remediation / Resolved)",
      "View executive compliance progress reports"
    ]
  },
  {
    roleKey: "viewer",
    name: "Compliance Auditor / Viewer",
    badge: "Read-Only Stakeholder",
    badgeColor: "bg-amber-500/20 text-amber-300 border-amber-500/30",
    email: "viewer@securemind.ai",
    avatar: "👁️",
    modulesCount: 3,
    description: "Executive stakeholder & compliance auditor. Read-only access to risk posture, vulnerability metrics, and downloadable reports.",
    visibleModules: [
      "Overview Dashboard", 
      "Vulnerabilities (Read-Only)", 
      "Reports"
    ],
    privileges: [
      "Read-only visibility into vulnerability metrics",
      "Download audit-ready PDF compliance reports",
      "Inspect high-level executive security posture",
      "Zero mutation capability: scanning & settings disabled"
    ]
  }
];

export const LandingPage: React.FC<LandingPageProps> = ({ onSelectRoleDemo, onEnterApp }) => {
  const [showRoleModal, setShowRoleModal] = useState(false);
  const [selectedRoleDetail, setSelectedRoleDetail] = useState(ROLE_DEMO_DATA[0]);

  const handleLaunchRole = (email: string, roleName: string) => {
    setShowRoleModal(false);
    onSelectRoleDemo(email, roleName);
  };

  return (
    <div className="min-h-screen bg-[#07090e] text-slate-100 flex flex-col font-sans selection:bg-indigo-500 selection:text-white">
      {/* Background Glows & Grid */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-[-10%] left-[20%] w-[650px] h-[650px] bg-indigo-600/10 rounded-full blur-[130px]" />
        <div className="absolute top-[30%] right-[10%] w-[550px] h-[550px] bg-cyan-500/10 rounded-full blur-[140px]" />
        <div className="absolute bottom-[10%] left-[10%] w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-[120px]" />
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#1f293710_1px,transparent_1px),linear-gradient(to_bottom,#1f293710_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]" />
      </div>

      {/* Navbar */}
      <header className="relative z-20 border-b border-slate-800/80 bg-[#07090e]/80 backdrop-blur-md sticky top-0">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
            <div className="p-2 bg-gradient-to-tr from-indigo-600 via-indigo-500 to-cyan-400 rounded-lg text-white shadow-lg shadow-indigo-500/30">
              <Shield className="w-5 h-5" />
            </div>
            <div>
              <span className="text-base font-extrabold tracking-tight text-white flex items-center gap-1.5">
                SecureMind <span className="text-indigo-400">AI</span>
              </span>
              <span className="text-[9px] uppercase tracking-wider text-slate-400 font-semibold block">
                Autonomous AppSec Platform
              </span>
            </div>
          </div>

          <nav className="hidden md:flex items-center space-x-8 text-xs font-medium text-slate-300">
            <a href="#features" className="hover:text-indigo-400 transition">Features</a>
            <a href="#how-it-works" className="hover:text-indigo-400 transition">How It Works</a>
            <a href="#agents" className="hover:text-indigo-400 transition">6-Agent Architecture</a>
            <a href="#roles" className="hover:text-indigo-400 transition">RBAC Roles</a>
            <a href="http://localhost:8001/api/docs/" target="_blank" rel="noreferrer" className="hover:text-indigo-400 transition flex items-center gap-1">
              <span>API Docs</span>
              <ExternalLink className="w-3 h-3 text-slate-500" />
            </a>
          </nav>

          <div className="flex items-center space-x-3">
            <button 
              onClick={() => setShowRoleModal(true)}
              className="px-3.5 py-1.5 rounded-lg border border-indigo-500/30 bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-300 text-xs font-semibold flex items-center gap-1.5 transition"
            >
              <Users className="w-3.5 h-3.5" />
              <span>Role Demos</span>
            </button>
            <button 
              onClick={onEnterApp}
              className="px-4 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/30 transition flex items-center gap-1.5"
            >
              <span>Launch Console</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative z-10 pt-16 pb-20 md:pt-24 md:pb-28 overflow-hidden">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            
            {/* Left Column: Headlines & CTA */}
            <div className="lg:col-span-7 space-y-6">
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-950/70 border border-indigo-500/30 text-indigo-300 text-xs font-medium shadow-inner">
                <Sparkles className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
                <span>Agentic AI-Powered Web Application Security & Remediation</span>
              </div>

              <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold text-white tracking-tight leading-[1.12]">
                Autonomous AppSec, <br />
                <span className="bg-gradient-to-r from-indigo-400 via-cyan-300 to-emerald-400 bg-clip-text text-transparent">
                  Orchestrated by Specialized AI Agents
                </span>
              </h1>

              <p className="text-slate-300 text-sm md:text-base leading-relaxed max-w-2xl">
                SecureMind AI replaces slow, manual penetration tests with ONE Central AI Orchestrator 
                coordinating exactly SIX specialized agents. Featuring cryptographic domain verification, 
                multi-hop SSRF firewall protection, OWASP ZAP & Nuclei scanning, and verified secure code remediation.
              </p>

              {/* Action Buttons */}
              <div className="pt-2 flex flex-wrap items-center gap-3">
                <button 
                  onClick={() => setShowRoleModal(true)}
                  className="px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-600 via-indigo-500 to-cyan-500 hover:from-indigo-500 hover:to-cyan-400 text-white text-sm font-bold shadow-lg shadow-indigo-500/25 flex items-center gap-2 transition transform hover:-translate-y-0.5"
                >
                  <Play className="w-4 h-4 fill-current" />
                  <span>Get Started — Select Role Demo</span>
                </button>
                <a 
                  href="#how-it-works"
                  className="px-5 py-3 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-slate-800 text-slate-200 text-sm font-semibold flex items-center gap-2 transition"
                >
                  <Terminal className="w-4 h-4 text-cyan-400" />
                  <span>How It Works</span>
                </a>
              </div>

              {/* Quick Role Switch Pills */}
              <div className="pt-4 border-t border-slate-800/80">
                <span className="text-[11px] font-semibold tracking-wider uppercase text-slate-400 block mb-2.5">
                  1-Click Role Access (Try Specific RBAC View):
                </span>
                <div className="flex flex-wrap gap-2">
                  {ROLE_DEMO_DATA.map((r) => (
                    <button
                      key={r.roleKey}
                      onClick={() => handleLaunchRole(r.email, r.name)}
                      className="px-2.5 py-1.5 rounded-lg bg-slate-900/90 border border-slate-800 hover:border-indigo-500/50 hover:bg-slate-850 text-slate-300 hover:text-white text-xs font-medium flex items-center gap-1.5 transition"
                    >
                      <span>{r.avatar}</span>
                      <span>{r.name.split(" ")[0]}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Security Trust Badges */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-4 text-xs text-slate-400">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  <span>Cryptographic Ownership</span>
                </div>
                <div className="flex items-center gap-2">
                  <Lock className="w-4 h-4 text-cyan-400" />
                  <span>Multi-Hop SSRF Guard</span>
                </div>
                <div className="flex items-center gap-2">
                  <Activity className="w-4 h-4 text-indigo-400" />
                  <span>ZAP & Nuclei Engine</span>
                </div>
                <div className="flex items-center gap-2">
                  <Code2 className="w-4 h-4 text-purple-400" />
                  <span>Verified Code Patches</span>
                </div>
              </div>
            </div>

            {/* Right Column: Hero High-Tech Visual Cockpit / Image */}
            <div className="lg:col-span-5 relative">
              <div className="relative rounded-2xl border border-slate-800 bg-slate-950/70 p-4 shadow-2xl backdrop-blur-xl overflow-hidden group">
                
                {/* Glowing border accent */}
                <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500/20 via-cyan-500/20 to-purple-500/20 rounded-2xl blur opacity-75 group-hover:opacity-100 transition duration-1000" />

                <div className="relative rounded-xl overflow-hidden bg-slate-900/80 border border-slate-800/80 space-y-3">
                  
                  {/* Top Bar of Preview */}
                  <div className="bg-slate-950 px-4 py-2.5 border-b border-slate-800 flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <div className="w-2.5 h-2.5 rounded-full bg-rose-500/80" />
                      <div className="w-2.5 h-2.5 rounded-full bg-amber-500/80" />
                      <div className="w-2.5 h-2.5 rounded-full bg-emerald-500/80" />
                      <span className="text-slate-400 font-mono text-[11px] ml-2">securemind.orchestrator.telemetry</span>
                    </div>
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
                      LIVE ENGINE
                    </span>
                  </div>

                  {/* Hero Graphic Image or Fallback Visual Display */}
                  <div className="relative aspect-[16/10] bg-[#090d16] flex items-center justify-center p-1 overflow-hidden">
                    <img 
                      src="/images/hero-cyber-ai.svg" 
                      alt="SecureMind AI Central Orchestration and 6 Autonomous Agents" 
                      className="w-full h-full object-cover rounded-lg shadow-inner"
                    />
                  </div>

                  {/* Real-time Telemetry Status Ticker */}
                  <div className="p-3 bg-slate-950/90 border-t border-slate-800 text-[11px] font-mono space-y-1.5">
                    <div className="flex items-center justify-between text-slate-400">
                      <span>SSRF Egress Firewall:</span>
                      <span className="text-emerald-400 font-bold">100% BLOCKED (RFC1918 / 169.254.169.254)</span>
                    </div>
                    <div className="flex items-center justify-between text-slate-400">
                      <span>Exploit Reproducibility:</span>
                      <span className="text-cyan-400 font-bold">98.4% Confidence (HTTP Evidence Logged)</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* SECTION 1: CORE FEATURES ("1 futures") */}
      <section id="features" className="relative z-10 py-20 border-t border-slate-800/80 bg-slate-950/50">
        <div className="max-w-7xl mx-auto px-6 space-y-12">
          
          <div className="text-center max-w-3xl mx-auto space-y-3">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-cyan-950/60 border border-cyan-500/30 text-cyan-300 text-xs font-semibold">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Core Platform Capabilities</span>
            </div>
            <h2 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">
              Enterprise Web Security Features
            </h2>
            <p className="text-sm text-slate-400">
              Engineered with deterministic safety bounds, zero hallucination checks, and military-grade tenant isolation.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            
            {/* Feature 1 */}
            <div className="p-6 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-indigo-500/40 transition group hover:shadow-xl hover:shadow-indigo-500/10 space-y-4">
              <div className="w-12 h-12 rounded-lg bg-indigo-600/20 border border-indigo-500/30 text-indigo-400 flex items-center justify-center group-hover:scale-110 transition">
                <Cpu className="w-6 h-6" />
              </div>
              <h3 className="text-base font-bold text-white group-hover:text-indigo-300 transition">
                ONE Central Orchestrator & 6 Specialized Agents
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Rather than an unpredictable single chat prompt, SecureMind coordinates 6 purpose-built agents 
                with strict Pydantic JSON schemas, isolated task context, and verifiable reasoning steps.
              </p>
              <div className="text-[11px] font-mono text-indigo-400 flex items-center gap-1">
                <span>Pydantic v2 Validated</span>
                <ChevronRight className="w-3 h-3" />
              </div>
            </div>

            {/* Feature 2 */}
            <div className="p-6 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-cyan-500/40 transition group hover:shadow-xl hover:shadow-cyan-500/10 space-y-4">
              <div className="w-12 h-12 rounded-lg bg-cyan-600/20 border border-cyan-500/30 text-cyan-400 flex items-center justify-center group-hover:scale-110 transition">
                <Activity className="w-6 h-6" />
              </div>
              <h3 className="text-base font-bold text-white group-hover:text-cyan-300 transition">
                Autonomous DAST Pipeline (ZAP & Nuclei)
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Orchestrates OWASP ZAP spidering and Nuclei vulnerability template scanning under strict execution boundaries. 
                Collects, deduplicates, and normalizes all findings into a unified data structure.
              </p>
              <div className="text-[11px] font-mono text-cyan-400 flex items-center gap-1">
                <span>Deterministic Scope Limits</span>
                <ChevronRight className="w-3 h-3" />
              </div>
            </div>

            {/* Feature 3 */}
            <div className="p-6 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-emerald-500/40 transition group hover:shadow-xl hover:shadow-emerald-500/10 space-y-4">
              <div className="w-12 h-12 rounded-lg bg-emerald-600/20 border border-emerald-500/30 text-emerald-400 flex items-center justify-center group-hover:scale-110 transition">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <h3 className="text-base font-bold text-white group-hover:text-emerald-300 transition">
                Cryptographic Ownership & Multi-Hop SSRF Guard
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Requires DNS TXT or HTTP token proof before testing. Multi-hop redirect validator recursively inspects 
                IPv4/IPv6 destinations, immediately dropping loopback (127.0.0.1) and cloud metadata (169.254.169.254).
              </p>
              <div className="text-[11px] font-mono text-emerald-400 flex items-center gap-1">
                <span>Zero-Trust SSRF Defense</span>
                <ChevronRight className="w-3 h-3" />
              </div>
            </div>

            {/* Feature 4 */}
            <div className="p-6 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-purple-500/40 transition group hover:shadow-xl hover:shadow-purple-500/10 space-y-4">
              <div className="w-12 h-12 rounded-lg bg-purple-600/20 border border-purple-500/30 text-purple-400 flex items-center justify-center group-hover:scale-110 transition">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <h3 className="text-base font-bold text-white group-hover:text-purple-300 transition">
                Zero-Hallucination Evidence Verification
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Eliminates false alarms. The Verification Agent replays non-destructive HTTP requests with controlled 
                payloads to confirm actual exploitability before marking vulnerabilities as verified.
              </p>
              <div className="text-[11px] font-mono text-purple-400 flex items-center gap-1">
                <span>Proof-of-Concept Replay</span>
                <ChevronRight className="w-3 h-3" />
              </div>
            </div>

            {/* Feature 5 */}
            <div className="p-6 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-amber-500/40 transition group hover:shadow-xl hover:shadow-amber-500/10 space-y-4">
              <div className="w-12 h-12 rounded-lg bg-amber-600/20 border border-amber-500/30 text-amber-400 flex items-center justify-center group-hover:scale-110 transition">
                <AlertTriangle className="w-6 h-6" />
              </div>
              <h3 className="text-base font-bold text-white group-hover:text-amber-300 transition">
                Transparent Risk Scoring (No Fake CVSS)
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Computes risk using an explainable formula: Impact × Likelihood × Confidence. 
                Provides auditable rationales for every score rather than hallucinating arbitrary CVSS metrics.
              </p>
              <div className="text-[11px] font-mono text-amber-400 flex items-center gap-1">
                <span>Mathematical Transparency</span>
                <ChevronRight className="w-3 h-3" />
              </div>
            </div>

            {/* Feature 6 */}
            <div className="p-6 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-rose-500/40 transition group hover:shadow-xl hover:shadow-rose-500/10 space-y-4">
              <div className="w-12 h-12 rounded-lg bg-rose-600/20 border border-rose-500/30 text-rose-400 flex items-center justify-center group-hover:scale-110 transition">
                <Code2 className="w-6 h-6" />
              </div>
              <h3 className="text-base font-bold text-white group-hover:text-rose-300 transition">
                Actionable Remediation & ReportLab PDF Reports
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Delivers ready-to-merge secure code diffs and framework-specific patches. One-click compiles formal 
                PDF compliance reports directly on the backend using ReportLab.
              </p>
              <div className="text-[11px] font-mono text-rose-400 flex items-center gap-1">
                <span>%PDF-1.4 On-Demand Export</span>
                <ChevronRight className="w-3 h-3" />
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* SECTION 2: HOW IT WORKS ("2 how it work") */}
      <section id="how-it-works" className="relative z-10 py-20 border-t border-slate-800/80">
        <div className="max-w-7xl mx-auto px-6 space-y-14">
          
          <div className="text-center max-w-3xl mx-auto space-y-3">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-950/60 border border-indigo-500/30 text-indigo-300 text-xs font-semibold">
              <Layers className="w-3.5 h-3.5" />
              <span>End-to-End Workflow</span>
            </div>
            <h2 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">
              How SecureMind AI Works
            </h2>
            <p className="text-sm text-slate-400">
              From cryptographic authorization to automated remediation in 4 deterministic steps.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            
            {/* Step 1 */}
            <div className="p-6 rounded-xl bg-slate-900/40 border border-slate-800 relative space-y-3">
              <div className="w-9 h-9 rounded-lg bg-indigo-600 text-white font-mono font-bold flex items-center justify-center text-sm shadow">
                01
              </div>
              <h4 className="text-sm font-bold text-white">Register & Verify Asset</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                User registers web target URL. SecureMind issues a cryptographic DNS TXT token or HTTP well-known file challenge. 
                Testing is strictly blocked until ownership is confirmed.
              </p>
              <div className="pt-2 text-[10px] font-mono text-indigo-400 bg-slate-950 p-2 rounded border border-slate-800">
                DNS: _securemind-challenge.target
              </div>
            </div>

            {/* Step 2 */}
            <div className="p-6 rounded-xl bg-slate-900/40 border border-slate-800 relative space-y-3">
              <div className="w-9 h-9 rounded-lg bg-cyan-600 text-white font-mono font-bold flex items-center justify-center text-sm shadow">
                02
              </div>
              <h4 className="text-sm font-bold text-white">Enforce Scope & SSRF Firewall</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Define permitted paths, ports, and subdomains. SSRF firewall checks every destination IP address and 
                revalidates all HTTP 301/302 redirects up to 3 hops.
              </p>
              <div className="pt-2 text-[10px] font-mono text-cyan-400 bg-slate-950 p-2 rounded border border-slate-800">
                SSRF Guard: Drops RFC1918 / Loopback
              </div>
            </div>

            {/* Step 3 */}
            <div className="p-6 rounded-xl bg-slate-900/40 border border-slate-800 relative space-y-3">
              <div className="w-9 h-9 rounded-lg bg-purple-600 text-white font-mono font-bold flex items-center justify-center text-sm shadow">
                03
              </div>
              <h4 className="text-sm font-bold text-white">6-Agent Swarm Orchestration</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Central Orchestrator triggers Authorization, Recon, Vulnerability Scanning (ZAP/Nuclei), 
                Verification (evidence replay), and Risk Assessment.
              </p>
              <div className="pt-2 text-[10px] font-mono text-purple-400 bg-slate-950 p-2 rounded border border-slate-800">
                Central Orchestrator -&gt; 6 Agents
              </div>
            </div>

            {/* Step 4 */}
            <div className="p-6 rounded-xl bg-slate-900/40 border border-slate-800 relative space-y-3">
              <div className="w-9 h-9 rounded-lg bg-emerald-600 text-white font-mono font-bold flex items-center justify-center text-sm shadow">
                04
              </div>
              <h4 className="text-sm font-bold text-white">Remediate & Export PDF</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Remediation Agent outputs exact code patches for developers. DevSecOps leads download 
                cryptographically auditable ReportLab PDF compliance reports.
              </p>
              <div className="pt-2 text-[10px] font-mono text-emerald-400 bg-slate-950 p-2 rounded border border-slate-800">
                Actionable Patch + %PDF-1.4 Report
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* SECTION 3: 6-AGENT ARCHITECTURE */}
      <section id="agents" className="relative z-10 py-20 border-t border-slate-800/80 bg-slate-950/60">
        <div className="max-w-7xl mx-auto px-6 space-y-12">
          
          <div className="text-center max-w-3xl mx-auto space-y-3">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-purple-950/60 border border-purple-500/30 text-purple-300 text-xs font-semibold">
              <Cpu className="w-3.5 h-3.5" />
              <span>Autonomous Multi-Agent Architecture</span>
            </div>
            <h2 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">
              The 6 Specialized AI Agents
            </h2>
            <p className="text-sm text-slate-400">
              Users interact with ONE unified platform workflow, not six disconnected chatbots.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            
            <div className="p-5 rounded-xl bg-slate-900/70 border border-slate-800 space-y-2.5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-emerald-400">SMAI-AI-AGT-001</span>
                <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">Gatekeeper</span>
              </div>
              <h4 className="text-sm font-bold text-white">1. Authorization Agent</h4>
              <p className="text-xs text-slate-400">
                Verifies cryptographic ownership records, checks authorization expiration dates, and ensures operations stay strictly in-scope.
              </p>
            </div>

            <div className="p-5 rounded-xl bg-slate-900/70 border border-slate-800 space-y-2.5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-cyan-400">SMAI-AI-AGT-002</span>
                <span className="px-2 py-0.5 rounded text-[10px] bg-cyan-500/10 text-cyan-300 border border-cyan-500/20">Mapper</span>
              </div>
              <h4 className="text-sm font-bold text-white">2. Reconnaissance Agent</h4>
              <p className="text-xs text-slate-400">
                Performs passive technology fingerprinting, discovers permitted application entry points, and maps parameter attack surfaces.
              </p>
            </div>

            <div className="p-5 rounded-xl bg-slate-900/70 border border-slate-800 space-y-2.5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-indigo-400">SMAI-AI-AGT-003</span>
                <span className="px-2 py-0.5 rounded text-[10px] bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">Coordinator</span>
              </div>
              <h4 className="text-sm font-bold text-white">3. Vulnerability Scanning Agent</h4>
              <p className="text-xs text-slate-400">
                Controls approved OWASP ZAP spiders and Nuclei template scanners, normalizes raw outputs, and tags findings by CWE.
              </p>
            </div>

            <div className="p-5 rounded-xl bg-slate-900/70 border border-slate-800 space-y-2.5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-purple-400">SMAI-AI-AGT-004</span>
                <span className="px-2 py-0.5 rounded text-[10px] bg-purple-500/10 text-purple-300 border border-purple-500/20">Verifier</span>
              </div>
              <h4 className="text-sm font-bold text-white">4. Verification Agent</h4>
              <p className="text-xs text-slate-400">
                Analyzes scanner evidence and executes deterministic HTTP replay probes to confirm whether flaws are genuinely reproducible.
              </p>
            </div>

            <div className="p-5 rounded-xl bg-slate-900/70 border border-slate-800 space-y-2.5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-amber-400">SMAI-AI-AGT-005</span>
                <span className="px-2 py-0.5 rounded text-[10px] bg-amber-500/10 text-amber-300 border border-amber-500/20">Evaluator</span>
              </div>
              <h4 className="text-sm font-bold text-white">5. Risk Assessment Agent</h4>
              <p className="text-xs text-slate-400">
                Computes severity from Impact, Likelihood, and Exploit Confidence with transparent rationale. Never hallucinates official CVSS.
              </p>
            </div>

            <div className="p-5 rounded-xl bg-slate-900/70 border border-slate-800 space-y-2.5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-rose-400">SMAI-AI-AGT-006</span>
                <span className="px-2 py-0.5 rounded text-[10px] bg-rose-500/10 text-rose-300 border border-rose-500/20">Remediator</span>
              </div>
              <h4 className="text-sm font-bold text-white">6. Remediation Agent</h4>
              <p className="text-xs text-slate-400">
                Generates context-aware, production-ready code patches in Python, TypeScript, and Go. Never alters production systems autonomously.
              </p>
            </div>

          </div>
        </div>
      </section>

      {/* SECTION 4: ROLE MATRIX & GET STARTED ("find the each role demo and make role based access control each roles should found there only") */}
      <section id="roles" className="relative z-10 py-20 border-t border-slate-800/80">
        <div className="max-w-7xl mx-auto px-6 space-y-12">
          
          <div className="text-center max-w-3xl mx-auto space-y-3">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-950/60 border border-emerald-500/30 text-emerald-300 text-xs font-semibold">
              <Users className="w-3.5 h-3.5" />
              <span>Strict Role-Based Access Control</span>
            </div>
            <h2 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">
              Test Each Role Demo Live
            </h2>
            <p className="text-sm text-slate-400">
              SecureMind AI enforces strict RBAC at the API and UI level. Select any role below to launch the live platform 
              and experience the interface tailored strictly to that role's permissions.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {ROLE_DEMO_DATA.map((role) => (
              <div 
                key={role.roleKey}
                className="p-6 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition flex flex-col justify-between space-y-5"
              >
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-2xl">{role.avatar}</span>
                    <span className={`text-[10px] px-2.5 py-1 rounded-full border font-semibold tracking-wide ${role.badgeColor}`}>
                      {role.badge}
                    </span>
                  </div>

                  <div>
                    <h3 className="text-base font-bold text-white">{role.name}</h3>
                    <p className="text-[11px] font-mono text-slate-500">{role.email}</p>
                  </div>

                  <p className="text-xs text-slate-400 leading-relaxed">
                    {role.description}
                  </p>

                  <div className="space-y-2 pt-2 border-t border-slate-800/60">
                    <span className="text-[10px] font-bold tracking-wider uppercase text-slate-500 block">
                      Visible Modules ({role.visibleModules.length}):
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {role.visibleModules.map((mod) => (
                        <span key={mod} className="text-[10px] px-2 py-0.5 rounded bg-slate-950 text-slate-300 border border-slate-800 font-mono">
                          {mod}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="pt-4">
                  <button
                    onClick={() => handleLaunchRole(role.email, role.name)}
                    className="w-full py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/20 flex items-center justify-center gap-2 transition"
                  >
                    <span>Launch Demo as {role.name.split(" ")[0]}</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>

        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-slate-800 bg-[#05070a] py-12 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-2">
            <Shield className="w-4 h-4 text-indigo-400" />
            <span className="font-bold text-slate-300">SecureMind AI Platform</span>
            <span>—</span>
            <span>Version 1.0.0</span>
          </div>
          <div className="flex items-center space-x-6 text-[11px]">
            <span>FastAPI / Django REST Framework</span>
            <span>Next.js 14 / TypeScript</span>
            <span>OWASP ZAP &amp; Nuclei</span>
            <span>Pydantic v2 Agent Swarm</span>
          </div>
        </div>
      </footer>

      {/* ROLE DEMO SELECTION MODAL (Triggered by "Get Started" or "Sign Up") */}
      {showRoleModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-2xl w-full p-6 space-y-6 shadow-2xl relative">
            
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div className="flex items-center gap-2.5">
                <div className="p-2 bg-indigo-600/20 border border-indigo-500/30 rounded-lg text-indigo-400">
                  <Users className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white">Select Your Live Demo Role</h3>
                  <p className="text-xs text-slate-400">Choose a role to explore tailored permissions and UI views.</p>
                </div>
              </div>
              <button 
                onClick={() => setShowRoleModal(false)}
                className="text-slate-400 hover:text-white text-lg p-1"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3 max-h-[60vh] overflow-y-auto pr-1">
              {ROLE_DEMO_DATA.map((r) => (
                <div 
                  key={r.roleKey}
                  onClick={() => handleLaunchRole(r.email, r.name)}
                  className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 hover:border-indigo-500/50 hover:bg-slate-900 cursor-pointer transition flex items-center justify-between group"
                >
                  <div className="flex items-center gap-3.5">
                    <span className="text-2xl p-2 bg-slate-900 rounded-lg border border-slate-800">{r.avatar}</span>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-bold text-white group-hover:text-indigo-400 transition">{r.name}</span>
                        <span className={`text-[10px] px-2 py-0.5 rounded border font-semibold ${r.badgeColor}`}>
                          {r.badge}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 mt-0.5">{r.description}</p>
                      <span className="text-[10px] text-slate-500 font-mono mt-1 block">
                        Visible Modules: {r.visibleModules.slice(0, 4).join(", ")} + {r.visibleModules.length - 4} more
                      </span>
                    </div>
                  </div>
                  <button className="px-3 py-1.5 rounded-lg bg-indigo-600/20 group-hover:bg-indigo-600 text-indigo-300 group-hover:text-white border border-indigo-500/30 text-xs font-semibold transition shrink-0 ml-4 flex items-center gap-1">
                    <span>Launch</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>

            <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
              <span>All 5 demo accounts auto-authenticate with zero manual credential entry.</span>
              <button 
                onClick={() => setShowRoleModal(false)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-medium"
              >
                Close
              </button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
};
