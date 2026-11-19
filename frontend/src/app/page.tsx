"use client";

import React, { useState } from "react";
import { Sidebar } from "@/components/Sidebar";
import { OverviewView } from "@/components/views/OverviewView";
import { AssetsView } from "@/components/views/AssetsView";
import { AssessmentsView } from "@/components/views/AssessmentsView";
import { FindingsView } from "@/components/views/FindingsView";
import { RemediationView } from "@/components/views/RemediationView";
import { ReportsView } from "@/components/views/ReportsView";
import { AIAnalysisView } from "@/components/views/AIAnalysisView";
import { TeamView } from "@/components/views/TeamView";
import { Bell, Shield, ChevronDown, UserCircle } from "lucide-react";

export default function Dashboard() {
  const [currentTab, setCurrentTab] = useState<string>("overview");

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
              <span className="w-2 h-2 rounded-full bg-indigo-500"></span>
              <span>Primary Workspace</span>
              <ChevronDown className="w-3.5 h-3.5 text-slate-500" />
            </div>
          </div>

          <div className="flex items-center gap-4">
            <button className="p-2 text-slate-400 hover:text-white bg-slate-900/60 border border-slate-800 rounded-lg transition">
              <Bell className="w-4 h-4" />
            </button>
            <div className="flex items-center gap-2.5 pl-4 border-l border-slate-800">
              <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-white text-xs font-bold">
                JD
              </div>
              <div className="hidden sm:block text-left">
                <span className="text-xs font-semibold text-white block">DevSecOps Lead</span>
                <span className="text-[10px] text-indigo-400 block font-mono">Platform Admin</span>
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
    </div>
  );
}
