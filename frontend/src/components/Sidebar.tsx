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
  Bell
} from "lucide-react";

interface SidebarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, setCurrentTab }) => {
  const navItems = [
    { id: "overview", label: "Overview", icon: LayoutDashboard },
    { id: "assets", label: "Applications & Assets", icon: Globe },
    { id: "assessments", label: "Security Assessments", icon: Crosshair },
    { id: "findings", label: "Vulnerabilities", icon: AlertTriangle },
    { id: "ai-analysis", label: "AI Agent Orchestration", icon: Cpu },
    { id: "remediation", label: "Remediation Center", icon: Wrench },
    { id: "reports", label: "Reports", icon: FileText },
    { id: "team", label: "Team & RBAC", icon: Users },
    { id: "settings", label: "Settings", icon: Settings },
  ];

  return (
    <aside className="w-64 border-r border-slate-800 bg-slate-900/40 flex flex-col justify-between shrink-0">
      <div>
        {/* Brand */}
        <div className="p-6 border-b border-slate-800 flex items-center space-x-3">
          <div className="p-2 bg-indigo-600 rounded-lg text-white shadow-lg shadow-indigo-500/20">
            <Shield className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-base font-bold tracking-tight text-white flex items-center gap-1.5">
              SecureMind <span className="text-indigo-400 font-extrabold">AI</span>
            </h1>
            <p className="text-[10px] text-slate-400 tracking-wider uppercase font-semibold">Autonomous AppSec</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="p-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setCurrentTab(item.id)}
                className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-xs font-medium transition-all ${
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
      </div>

      {/* Footer Info */}
      <div className="p-4 border-t border-slate-800 text-[11px] text-slate-500 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
          <span>Engine Active</span>
        </div>
        <span>v1.0.0</span>
      </div>
    </aside>
  );
};
