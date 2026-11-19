"use client";

import React, { useState, useEffect } from "react";
import { Sidebar } from "@/components/Sidebar";
import { LandingPage, ROLE_DEMO_DATA } from "@/components/landing/LandingPage";
import { OverviewView } from "@/components/views/OverviewView";
import { AssetsView } from "@/components/views/AssetsView";
import { AssessmentsView } from "@/components/views/AssessmentsView";
import { FindingsView } from "@/components/views/FindingsView";
import { RemediationView } from "@/components/views/RemediationView";
import { ReportsView } from "@/components/views/ReportsView";
import { AIAnalysisView } from "@/components/views/AIAnalysisView";
import { TeamView } from "@/components/views/TeamView";
import { 
  Bell, 
  Shield, 
  ChevronDown, 
  UserCircle, 
  LogIn, 
  CheckCircle2, 
  UserCheck, 
  Lock, 
  ExternalLink,
  Sparkles,
  ArrowLeft,
  LayoutDashboard
} from "lucide-react";
import { api } from "@/services/api";

const ROLE_ALLOWED_TABS: Record<string, string[]> = {
  platform_admin: ["overview", "assets", "assessments", "findings", "ai-analysis", "remediation", "reports", "team", "settings"],
  org_admin: ["overview", "assets", "assessments", "findings", "ai-analysis", "remediation", "reports", "team"],
  security_analyst: ["overview", "assets", "assessments", "findings", "ai-analysis", "remediation", "reports"],
  developer: ["overview", "findings", "remediation", "reports"],
  viewer: ["overview", "findings", "reports"],
};

export default function Dashboard() {
  const [viewMode, setViewMode] = useState<"landing" | "app">("landing");
  const [currentTab, setCurrentTab] = useState<string>("overview");
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authEmail, setAuthEmail] = useState("admin@securemind.ai");
  const [authPassword, setAuthPassword] = useState("SecureEnterprisePassword2026!");
  const [authLoading, setAuthLoading] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);

  const fetchSession = async () => {
    try {
      const res = await api.auth.me();
      setCurrentUser(res.data);
    } catch (e) {
      // Unauthenticated visitor: Do not silently log in as super admin.
      setCurrentUser(null);
    }
  };

  useEffect(() => {
    fetchSession();
  }, []);

  const handleLogin = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setAuthLoading(true);
    setAuthError(null);
    try {
      const res = await api.auth.login({
        email: authEmail,
        password: authPassword,
      });
      localStorage.setItem("securemind_access_token", res.data.access);
      localStorage.setItem("securemind_refresh_token", res.data.refresh);
      const me = await api.auth.me();
      setCurrentUser(me.data);
      setShowAuthModal(false);
      setViewMode("app");
    } catch (err: any) {
      const detail = err.response?.data?.detail || err.response?.data?.non_field_errors || err.message;
      setAuthError(`Authentication failed: ${detail}`);
    } finally {
      setAuthLoading(false);
    }
  };

  const quickSwitch = async (email: string, pass: string = "SecureEnterprisePassword2026!") => {
    setAuthEmail(email);
    setAuthPassword(pass);
    setAuthLoading(true);
    setAuthError(null);
    try {
      const res = await api.auth.login({ email, password: pass });
      localStorage.setItem("securemind_access_token", res.data.access);
      localStorage.setItem("securemind_refresh_token", res.data.refresh);
      const me = await api.auth.me();
      setCurrentUser(me.data);
      setShowAuthModal(false);
      setViewMode("app");

      // Verify that currentTab is allowed for this role
      const allowed = ROLE_ALLOWED_TABS[me.data.role] || ROLE_ALLOWED_TABS.viewer;
      if (!allowed.includes(currentTab)) {
        setCurrentTab("overview");
      }
    } catch (e: any) {
      setAuthError(e.message || "Failed to switch role.");
    } finally {
      setAuthLoading(false);
    }
  };

  const handleSelectRoleFromLanding = (email: string, roleName: string) => {
    quickSwitch(email);
  };

  // If visitor is on Landing Page
  if (viewMode === "landing") {
    return (
      <LandingPage 
        onSelectRoleDemo={handleSelectRoleFromLanding}
        onEnterApp={() => setViewMode("app")}
      />
    );
  }

  // RBAC Access Control Guard
  const userRole = currentUser?.role || "platform_admin";
  const allowedTabs = ROLE_ALLOWED_TABS[userRole] || ROLE_ALLOWED_TABS.viewer;
  const isTabAllowed = allowedTabs.includes(currentTab);

  const renderContent = () => {
    if (!isTabAllowed) {
      return (
        <div className="p-12 text-center bg-slate-900/60 border border-slate-800 rounded-xl space-y-4 max-w-lg mx-auto mt-12 backdrop-blur-md">
          <div className="w-12 h-12 bg-rose-500/10 border border-rose-500/30 text-rose-400 rounded-xl flex items-center justify-center mx-auto">
            <Lock className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-white">Access Restricted by RBAC Policy</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Your current active role (<span className="text-indigo-400 font-semibold">{userRole}</span>) does not have permission 
            to access the <span className="text-white font-semibold capitalize">{currentTab.replace("-", " ")}</span> module.
          </p>
          <div className="pt-2 flex justify-center gap-3">
            <button 
              onClick={() => setCurrentTab("overview")} 
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-xs font-semibold"
            >
              Return to Overview
            </button>
            <button 
              onClick={() => setShowAuthModal(true)} 
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold"
            >
              Switch Role Demo
            </button>
          </div>
        </div>
      );
    }

    switch (currentTab) {
      case "overview":
        return <OverviewView />;
      case "assets":
        return <AssetsView />;
      case "assessments":
        return <AssessmentsView />;
      case "findings":
        return <FindingsView />;
      case "remediation":
        return <RemediationView />;
      case "ai-analysis":
        return <AIAnalysisView />;
      case "reports":
        return <ReportsView />;
      case "team":
        return <TeamView />;
      case "settings":
      default:
        return (
          <div className="p-12 text-center bg-slate-900/40 border border-slate-800 rounded-xl space-y-3">
            <Shield className="w-10 h-10 text-indigo-400 mx-auto" />
            <h3 className="text-base font-bold text-white capitalize">{currentTab.replace("-", " ")} Module</h3>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              Integrated with the Django REST Framework backend API v1 endpoints. Real-time updates and RBAC policies active.
            </p>
          </div>
        );
    }
  };

  const displayName = currentUser ? (currentUser.full_name || currentUser.email) : "Platform Admin";
  const displayRole = currentUser ? currentUser.role.replace("_", " ").toUpperCase() : "PLATFORM ADMIN";
  const displayOrg = currentUser?.current_organization_name || "Primary Workspace";
  const initials = displayName.substring(0, 2).toUpperCase();

  return (
    <div className="flex h-screen bg-slate-950 overflow-hidden font-sans">
      {/* Sidebar Navigation (With Strict RBAC Filtering) */}
      <Sidebar 
        currentTab={currentTab} 
        setCurrentTab={setCurrentTab} 
        userRole={userRole}
        onSwitchRole={() => setShowAuthModal(true)}
        onReturnHome={() => setViewMode("landing")}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Header */}
        <header className="h-16 border-b border-slate-800 bg-slate-900/30 backdrop-blur px-8 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-4">
            {/* Return to Landing Page Button */}
            <button
              onClick={() => setViewMode("landing")}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 hover:border-indigo-500/50 hover:bg-slate-800 text-slate-300 hover:text-white text-xs font-medium transition"
              title="Return to the public landing page"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Landing Page</span>
            </button>

            <div className="h-4 w-px bg-slate-800" />

            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-slate-400">Workspace:</span>
              <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs font-medium text-slate-200">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                <span>{displayOrg}</span>
                <ChevronDown className="w-3.5 h-3.5 text-slate-500" />
              </div>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {/* Quick RBAC Role Badge & Switcher Button */}
            <button
              onClick={() => setShowAuthModal(true)}
              className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-indigo-950/60 border border-indigo-500/30 text-indigo-300 hover:bg-indigo-900/50 text-xs font-semibold transition"
            >
              <UserCheck className="w-3.5 h-3.5 text-cyan-400" />
              <span>Role Demo: {displayRole}</span>
            </button>

            <button className="p-2 text-slate-400 hover:text-white bg-slate-900/60 border border-slate-800 rounded-lg transition">
              <Bell className="w-4 h-4" />
            </button>

            {/* User Profile Avatar */}
            <div
              onClick={() => setShowAuthModal(true)}
              className="flex items-center gap-2.5 pl-4 border-l border-slate-800 cursor-pointer hover:opacity-90 transition"
              title="Click to view session or switch user role"
            >
              <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-white text-xs font-bold shadow-md shadow-indigo-600/30">
                {initials}
              </div>
              <div className="hidden sm:block text-left">
                <span className="text-xs font-semibold text-white block">{displayName}</span>
                <span className="text-[10px] text-indigo-400 block font-mono font-medium">{displayRole}</span>
              </div>
            </div>
          </div>
        </header>

        {/* Scrollable Dashboard Body */}
        <main className="flex-1 overflow-y-auto p-8">
          <div className="max-w-7xl mx-auto">
            {renderContent()}
          </div>
        </main>
      </div>

      {/* Authentication & 5-Role Demo Switcher Modal */}
      {showAuthModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 max-w-lg w-full space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <UserCheck className="w-5 h-5 text-indigo-400" />
                Live RBAC Role Demo Switcher
              </h3>
              <button onClick={() => setShowAuthModal(false)} className="text-slate-400 hover:text-white text-xs">✕</button>
            </div>

            <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg space-y-1 text-xs">
              <span className="text-slate-400 block">Current Logged-in Identity:</span>
              <span className="text-white font-semibold block">{displayName} ({currentUser?.email || "admin@securemind.ai"})</span>
              <span className="text-indigo-400 font-mono text-[11px] block">{displayRole}</span>
            </div>

            {authError && (
              <div className="p-3 bg-rose-950/40 border border-rose-800 text-rose-200 text-xs rounded-lg">
                {authError}
              </div>
            )}

            {/* 1-Click Role Switch for All 5 Roles */}
            <div className="space-y-2">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
                Instant 1-Click Role Switch:
              </span>
              <div className="space-y-1.5 max-h-[40vh] overflow-y-auto pr-1">
                {ROLE_DEMO_DATA.map((r) => {
                  const isCurrent = currentUser?.role === r.roleKey;
                  return (
                    <button
                      key={r.roleKey}
                      type="button"
                      disabled={authLoading}
                      onClick={() => quickSwitch(r.email)}
                      className={`w-full p-2.5 rounded-lg border text-left transition flex items-center justify-between ${
                        isCurrent 
                          ? "bg-indigo-600/20 border-indigo-500/50 text-white" 
                          : "bg-slate-950/70 border-slate-800 hover:bg-slate-850 hover:border-indigo-500/30 text-slate-300"
                      }`}
                    >
                      <div className="flex items-center gap-2.5">
                        <span className="text-lg">{r.avatar}</span>
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-bold text-white">{r.name}</span>
                            <span className={`text-[9px] px-1.5 py-0.2 rounded border font-semibold ${r.badgeColor}`}>
                              {r.badge}
                            </span>
                          </div>
                          <span className="text-[10px] text-slate-500 font-mono block">
                            {r.modulesCount} modules • {r.email}
                          </span>
                        </div>
                      </div>
                      {isCurrent ? (
                        <span className="text-[10px] text-emerald-400 font-semibold px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20">
                          Active
                        </span>
                      ) : (
                        <span className="text-[10px] text-indigo-400 font-semibold">
                          Switch →
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Custom Sign-In Form */}
            <form onSubmit={handleLogin} className="space-y-2.5 pt-3 border-t border-slate-800">
              <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">Custom Sign-In:</span>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-[10px] text-slate-400 block mb-0.5">Email</label>
                  <input
                    type="email"
                    value={authEmail}
                    onChange={(e) => setAuthEmail(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1 text-xs text-white outline-none focus:border-indigo-500"
                    required
                  />
                </div>
                <div>
                  <label className="text-[10px] text-slate-400 block mb-0.5">Password</label>
                  <input
                    type="password"
                    value={authPassword}
                    onChange={(e) => setAuthPassword(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1 text-xs text-white outline-none focus:border-indigo-500"
                    required
                  />
                </div>
              </div>
              <div className="flex justify-end gap-2 pt-1">
                <button
                  type="button"
                  onClick={() => setShowAuthModal(false)}
                  className="px-3 py-1.5 text-xs text-slate-400 hover:text-white"
                >
                  Close
                </button>
                <button
                  type="submit"
                  disabled={authLoading}
                  className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-xs font-semibold transition"
                >
                  {authLoading ? "Authenticating..." : "Sign In"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
