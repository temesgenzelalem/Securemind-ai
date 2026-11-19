import React from "react";
import { 
  Shield, 
  LayoutDashboard, 
  Globe, 
  Crosshair, 
  AlertTriangle, 
  Cpu, 
  Wrench, 
  FileText, 
  Users, 
  Settings,
  ArrowLeft,
  UserCheck,
  Lock
} from "lucide-react";

interface SidebarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  userRole?: string;
  onSwitchRole?: () => void;
  onReturnHome?: () => void;
}

const ALL_NAV_ITEMS = [
  { id: "overview", label: "Overview", icon: LayoutDashboard, minRole: "viewer" },
  { id: "assets", label: "Applications & Assets", icon: Globe, minRole: "security_analyst" },
  { id: "assessments", label: "Security Assessments", icon: Crosshair, minRole: "security_analyst" },
  { id: "findings", label: "Vulnerabilities", icon: AlertTriangle, minRole: "viewer" },
  { id: "ai-analysis", label: "AI Agent Orchestration", icon: Cpu, minRole: "security_analyst" },
  { id: "remediation", label: "Remediation Center", icon: Wrench, minRole: "developer" },
  { id: "reports", label: "Reports", icon: FileText, minRole: "viewer" },
  { id: "team", label: "Team & RBAC", icon: Users, minRole: "org_admin" },
  { id: "settings", label: "Settings", icon: Settings, minRole: "platform_admin" },
];

const ROLE_ALLOWED_TABS: Record<string, string[]> = {
  platform_admin: ["overview", "assets", "assessments", "findings", "ai-analysis", "remediation", "reports", "team", "settings"],
  org_admin: ["overview", "assets", "assessments", "findings", "ai-analysis", "remediation", "reports", "team"],
  security_analyst: ["overview", "assets", "assessments", "findings", "ai-analysis", "remediation", "reports"],
  developer: ["overview", "findings", "remediation", "reports"],
  viewer: ["overview", "findings", "reports"],
};

const ROLE_LABELS: Record<string, { label: string; color: string }> = {
  platform_admin: { label: "Platform Admin", color: "bg-purple-500/20 text-purple-300 border-purple-500/30" },
  org_admin: { label: "Org Admin", color: "bg-blue-500/20 text-blue-300 border-blue-500/30" },
  security_analyst: { label: "Security Analyst", color: "bg-indigo-500/20 text-indigo-300 border-indigo-500/30" },
  developer: { label: "Developer", color: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30" },
  viewer: { label: "Auditor / Viewer", color: "bg-amber-500/20 text-amber-300 border-amber-500/30" },
};

export const Sidebar: React.FC<SidebarProps> = ({ 
  currentTab, 
  setCurrentTab, 
  userRole = "platform_admin",
  onSwitchRole,
  onReturnHome
}) => {
  const allowedTabs = ROLE_ALLOWED_TABS[userRole] || ROLE_ALLOWED_TABS.viewer;
  const navItems = ALL_NAV_ITEMS.filter((item) => allowedTabs.includes(item.id));
  const roleMeta = ROLE_LABELS[userRole] || ROLE_LABELS.viewer;

  return (
    <aside className="w-64 border-r border-slate-800 bg-slate-900/60 backdrop-blur-md flex flex-col justify-between shrink-0">
      <div>
        {/* Brand */}
        <div className="p-5 border-b border-slate-800">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2.5">
              <div className="p-2 bg-gradient-to-tr from-indigo-600 to-cyan-500 rounded-lg text-white shadow-lg shadow-indigo-500/25">
                <Shield className="w-5 h-5" />
              </div>
              <div>
                <h1 className="text-sm font-bold tracking-tight text-white flex items-center gap-1.5">
                  SecureMind <span className="text-indigo-400 font-extrabold">AI</span>
                </h1>
                <p className="text-[9px] text-slate-400 tracking-wider uppercase font-semibold">Autonomous AppSec</p>
              </div>
            </div>
            {onReturnHome && (
              <button 
                onClick={onReturnHome}
                title="Return to Landing Page"
                className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded transition"
              >
                <ArrowLeft className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* Active Role Card & RBAC Switcher */}
          <div className="bg-slate-950/80 p-2.5 rounded-lg border border-slate-800/80 space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="text-[10px] text-slate-400 font-medium">RBAC Active Role</span>
              <button 
                onClick={onSwitchRole}
                className="text-[10px] text-indigo-400 hover:text-indigo-300 font-semibold underline flex items-center gap-1"
              >
                <UserCheck className="w-3 h-3" />
                <span>Switch Role</span>
              </button>
            </div>
            <div className="flex items-center gap-2">
              <span className={`text-[10px] px-2 py-0.5 rounded border font-semibold tracking-wide ${roleMeta.color}`}>
                {roleMeta.label}
              </span>
              <span className="text-[10px] text-slate-500 font-mono">
                {navItems.length} modules
              </span>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <div className="p-3">
          <p className="px-3 pb-2 text-[10px] font-semibold tracking-wider uppercase text-slate-500">
            Authorized Navigation
          </p>
          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = currentTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setCurrentTab(item.id)}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                    active
                      ? "bg-indigo-600/15 text-indigo-400 border border-indigo-500/30 shadow-sm"
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/40"
                  }`}
                >
                  <Icon className={`w-4 h-4 ${active ? "text-indigo-400" : "text-slate-500"}`} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Hidden Modules Indicator for Restricted Roles */}
          {ALL_NAV_ITEMS.length > navItems.length && (
            <div className="mt-4 px-3 py-2 rounded border border-dashed border-slate-800/80 text-[10px] text-slate-500 flex items-center gap-1.5">
              <Lock className="w-3 h-3 text-slate-600 shrink-0" />
              <span>{ALL_NAV_ITEMS.length - navItems.length} modules hidden by RBAC policy</span>
            </div>
          )}
        </div>
      </div>

      {/* Footer Info */}
      <div className="p-3 border-t border-slate-800 text-[10px] text-slate-400 flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>Engine Active</span>
        </div>
        <span className="font-mono text-slate-500">v1.0.0</span>
      </div>
    </aside>
  );
};
