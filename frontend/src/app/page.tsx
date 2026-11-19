"use client";

import React, { useState, useEffect } from "react";
import { Sidebar } from "@/components/Sidebar";
import { OverviewView } from "@/components/views/OverviewView";
import { AssetsView } from "@/components/views/AssetsView";
import { AssessmentsView } from "@/components/views/AssessmentsView";
import { FindingsView } from "@/components/views/FindingsView";
import { RemediationView } from "@/components/views/RemediationView";
import { ReportsView } from "@/components/views/ReportsView";
import { AIAnalysisView } from "@/components/views/AIAnalysisView";
import { TeamView } from "@/components/views/TeamView";
import { Bell, Shield, ChevronDown, UserCircle, LogIn, CheckCircle2, UserCheck } from "lucide-react";
import { api } from "@/services/api";

export default function Dashboard() {
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
      console.warn("Session check returned error, initializing demo admin.");
      try {
        const loginRes = await api.auth.login({
          email: "admin@securemind.ai",
          password: "SecureEnterprisePassword2026!",
        });
        localStorage.setItem("securemind_access_token", loginRes.data.access);
        localStorage.setItem("securemind_refresh_token", loginRes.data.refresh);
        const meRes = await api.auth.me();
        setCurrentUser(meRes.data);
      } catch (loginErr) {
        console.warn("Auto-login failed:", loginErr);
      }
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
    } catch (err: any) {
      const detail = err.response?.data?.detail || err.response?.data?.non_field_errors || err.message;
      setAuthError(`Authentication failed: ${detail}`);
    } finally {
      setAuthLoading(false);
    }
  };

  const quickSwitch = async (email: string, pass: string) => {
    setAuthEmail(email);
    setAuthPassword(pass);
    setAuthLoading(true);
    try {
      const res = await api.auth.login({ email, password: pass });
      localStorage.setItem("securemind_access_token", res.data.access);
      localStorage.setItem("securemind_refresh_token", res.data.refresh);
      const me = await api.auth.me();
      setCurrentUser(me.data);
      setShowAuthModal(false);
    } catch (e: any) {
      setAuthError(e.message);
    } finally {
      setAuthLoading(false);
    }
  };

  const renderContent = () => {
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
      {/* Sidebar Navigation */}
      <Sidebar currentTab={currentTab} setCurrentTab={setCurrentTab} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Header */}
        <header className="h-16 border-b border-slate-800 bg-slate-900/30 backdrop-blur px-8 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <span className="text-xs font-semibold text-slate-400">Organization:</span>
            <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs font-medium text-slate-200">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span>{displayOrg}</span>
              <ChevronDown className="w-3.5 h-3.5 text-slate-500" />
            </div>
          </div>

          <div className="flex items-center gap-4">
            <button className="p-2 text-slate-400 hover:text-white bg-slate-900/60 border border-slate-800 rounded-lg transition">
              <Bell className="w-4 h-4" />
            </button>
            <div
              onClick={() => setShowAuthModal(true)}
              className="flex items-center gap-2.5 pl-4 border-l border-slate-800 cursor-pointer hover:opacity-90 transition"
              title="Click to view session or switch user"
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

      {/* Authentication & User Switcher Modal */}
      {showAuthModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 max-w-md w-full space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <UserCheck className="w-5 h-5 text-indigo-400" />
                Active Session & RBAC Switcher
              </h3>
              <button onClick={() => setShowAuthModal(false)} className="text-slate-400 hover:text-white text-xs">✕</button>
            </div>

            <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg space-y-1 text-xs">
              <span className="text-slate-400 block">Logged In As:</span>
              <span className="text-white font-semibold block">{displayName} ({currentUser?.email || "admin@securemind.ai"})</span>
              <span className="text-indigo-400 font-mono text-[11px] block">{displayRole}</span>
            </div>

            {authError && (
              <div className="p-3 bg-rose-950/40 border border-rose-800 text-rose-200 text-xs rounded-lg">
                {authError}
              </div>
            )}

            <div className="space-y-2">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">1-Click Role Switch (Development Mode):</span>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <button
                  type="button"
                  onClick={() => quickSwitch("admin@securemind.ai", "SecureEnterprisePassword2026!")}
                  className="p-2.5 bg-slate-800 hover:bg-indigo-600 rounded-lg text-white font-medium text-left transition"
                >
                  <strong className="block text-indigo-300">Platform Admin</strong>
                  <span className="text-[10px] text-slate-400 block">admin@securemind.ai</span>
                </button>
                <button
                  type="button"
                  onClick={() => quickSwitch("lead.auditor.1795085943@securemind.ai", "SecureEnterprisePassword2026!")}
                  className="p-2.5 bg-slate-800 hover:bg-indigo-600 rounded-lg text-white font-medium text-left transition"
                >
                  <strong className="block text-indigo-300">Security Analyst</strong>
                  <span className="text-[10px] text-slate-400 block">auditor@securemind.ai</span>
                </button>
              </div>
            </div>

            <form onSubmit={handleLogin} className="space-y-3 pt-2 border-t border-slate-800">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Custom Sign-In:</span>
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Email</label>
                <input
                  type="email"
                  value={authEmail}
                  onChange={(e) => setAuthEmail(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white"
                  required
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Password</label>
                <input
                  type="password"
                  value={authPassword}
                  onChange={(e) => setAuthPassword(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white"
                  required
                />
              </div>
              <div className="flex justify-end gap-2 pt-2">
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
                  className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold transition"
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
