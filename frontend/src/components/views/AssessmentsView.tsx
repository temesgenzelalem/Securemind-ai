import React, { useState, useEffect } from "react";
import { Crosshair, Play, CheckCircle2, Clock, AlertTriangle, Shield, RefreshCw } from "lucide-react";
import { api } from "@/services/api";

export const AssessmentsView: React.FC = () => {
  const [assessments, setAssessments] = useState<any[]>([]);
  const [assets, setAssets] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showLaunchModal, setShowLaunchModal] = useState(false);
  const [selectedAssetId, setSelectedAssetId] = useState("");
  const [selectedProfile, setSelectedProfile] = useState("passive");
  const [launching, setLaunching] = useState(false);
  const [launchError, setLaunchError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [scansRes, assetsRes] = await Promise.all([
        api.scans.list(),
        api.assets.list()
      ]);
      setAssessments(scansRes.data.results || scansRes.data || []);
      const assetList = assetsRes.data.results || assetsRes.data || [];
      setAssets(assetList);
      if (assetList.length > 0 && !selectedAssetId) {
        const verifiedAsset = assetList.find((a: any) => a.is_authorized || a.verification_status === "verified");
        setSelectedAssetId(verifiedAsset ? verifiedAsset.id : assetList[0].id);
      }
    } catch (err: any) {
      console.warn("Could not fetch scans from live API, loading preview state.");
      setAssessments([
        {
          id: "scn-901",
          asset_domain: "securemind.ai",
          scan_type: "passive",
          status: "completed",
          findings_count: 3,
          created_at: "2026-11-18T10:00:00Z"
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleLaunch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAssetId) return;
    setLaunching(true);
    setLaunchError(null);
    try {
      await api.scans.create({
        asset: selectedAssetId,
        scan_type: selectedProfile,
      });
      setShowLaunchModal(false);
      fetchData();
    } catch (err: any) {
      const data = err.response?.data;
      const errDetail = typeof data === 'object' && data !== null
        ? Object.entries(data).map(([k, v]) => Array.isArray(v) ? `${k}: ${v.join(' ')}` : `${k}: ${v}`).join(' | ')
        : (err.message || 'Unknown error');
      setLaunchError(`Failed to start scan: ${errDetail}`);
    } finally {
      setLaunching(false);
    }
  };

  const handleApprove = async (scanId: string) => {
    try {
      await api.scans.approve(scanId);
      fetchData();
    } catch (err: any) {
      alert("Approval failed: " + err.message);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Security Assessments</h2>
          <p className="text-xs text-slate-400 mt-1">Autonomous DAST and template-based vulnerability assessment pipeline.</p>
        </div>
        <div className="flex items-center gap-3">
          <button 
            onClick={fetchData}
            className="p-2 text-slate-400 hover:text-white bg-slate-900 border border-slate-800 rounded-lg transition"
            title="Refresh assessments"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-indigo-400' : ''}`} />
          </button>
          <button 
            onClick={() => setShowLaunchModal(true)}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold flex items-center gap-2 transition shadow-md shadow-indigo-500/20"
          >
            <Play className="w-4 h-4 fill-current" />
            <span>Launch Assessment</span>
          </button>
        </div>
      </div>

      {/* Assessments List */}
      <div className="space-y-4">
        {assessments.length === 0 ? (
          <div className="p-8 text-center text-slate-500 bg-slate-900/40 rounded-xl border border-slate-800">
            No assessments registered yet. Launch an assessment to begin security testing.
          </div>
        ) : (
          assessments.map((scan) => {
            const isApproved = scan.is_approved;
            const requiresApproval = scan.requires_approval && !isApproved;

            return (
              <div key={scan.id} className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-3">
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
                  <div className="flex items-center gap-3">
                    <div className="p-2.5 bg-indigo-500/10 text-indigo-400 rounded-lg">
                      <Crosshair className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="text-sm font-bold text-white">{scan.asset_domain}</h3>
                      <span className="text-[11px] text-slate-400 uppercase font-mono">
                        {scan.scan_type?.replace('_', ' ')} • ID: {scan.id?.substring(0, 8)}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className={`px-2.5 py-1 rounded-full text-[11px] font-medium uppercase ${
                      scan.status === "running" ? "bg-blue-500/10 text-blue-400 border border-blue-500/20 animate-pulse" :
                      scan.status === "completed" ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" :
                      scan.status === "failed" ? "bg-rose-500/10 text-rose-400 border border-rose-500/20" :
                      "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                    }`}>
                      {scan.status}
                    </span>

                    {requiresApproval && (
                      <button 
                        onClick={() => handleApprove(scan.id)}
                        className="px-3 py-1 bg-amber-600 hover:bg-amber-500 text-white rounded text-[11px] font-semibold transition"
                      >
                        Approve Intrusive Scan
                      </button>
                    )}
                  </div>
                </div>

                <div className="bg-slate-950 p-3 rounded-lg border border-slate-800/80 text-xs flex items-center justify-between">
                  <span className="text-slate-400">Findings Detected: <strong className="text-indigo-300 font-semibold">{scan.findings_count || 0}</strong></span>
                  <span className="text-slate-500 font-mono text-[11px]">Started: {scan.created_at ? new Date(scan.created_at).toLocaleTimeString() : 'N/A'}</span>
                </div>
              </div>
            );
          })
        )}
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

            <form onSubmit={handleLaunch} className="space-y-4 text-xs">
              <div>
                <label className="text-slate-400 font-semibold block mb-1">Target Application:</label>
                {assets.length === 0 ? (
                  <p className="text-amber-400">No verified assets found. Please register and verify an asset first.</p>
                ) : (
                  <select 
                    value={selectedAssetId} 
                    onChange={(e) => {
                      setSelectedAssetId(e.target.value);
                      setLaunchError(null);
                    }}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200"
                  >
                    {assets.map((ast) => {
                      const isAuth = ast.is_authorized || ast.verification_status === "verified";
                      return (
                        <option key={ast.id} value={ast.id}>
                          {ast.domain} {isAuth ? "✓ [Verified]" : "⚠️ [Pending Verification]"}
                        </option>
                      );
                    })}
                  </select>
                )}
              </div>

              {(() => {
                const currentAsset = assets.find((a) => a.id === selectedAssetId);
                const isCurrentAuthorized = currentAsset?.is_authorized || currentAsset?.verification_status === "verified";
                if (currentAsset && !isCurrentAuthorized) {
                  return (
                    <div className="p-3 bg-amber-500/10 border border-amber-500/30 rounded-lg text-amber-400 text-[11px] leading-relaxed">
                      ⚠️ Target asset <strong>{currentAsset.domain}</strong> has not completed domain ownership verification.
                      Please complete the DNS or HTTP challenge in <strong>Applications & Assets</strong> before launching an assessment.
                    </div>
                  );
                }
                return null;
              })()}

              {launchError && (
                <div className="p-3 bg-rose-500/10 border border-rose-500/30 rounded-lg text-rose-400 text-[11px]">
                  {launchError}
                </div>
              )}

              <div>
                <label className="text-slate-400 font-semibold block mb-1">Scan Profile:</label>
                <div className="space-y-2">
                  <label className="flex items-start gap-3 p-3 rounded-lg bg-slate-950 border border-slate-800 cursor-pointer">
                    <input 
                      type="radio" 
                      name="profile" 
                      value="passive"
                      checked={selectedProfile === "passive"}
                      onChange={() => setSelectedProfile("passive")}
                      className="mt-0.5 text-indigo-600" 
                    />
                    <div>
                      <span className="font-bold text-white block">Passive Reconnaissance</span>
                      <span className="text-slate-400 text-[11px]">Zero-impact analysis: headers, technology detection, and observed endpoints.</span>
                    </div>
                  </label>
                  <label className="flex items-start gap-3 p-3 rounded-lg bg-slate-950 border border-slate-800 cursor-pointer">
                    <input 
                      type="radio" 
                      name="profile" 
                      value="controlled_active"
                      checked={selectedProfile === "controlled_active"}
                      onChange={() => setSelectedProfile("controlled_active")}
                      className="mt-0.5 text-indigo-600" 
                    />
                    <div>
                      <span className="font-bold text-white block">Controlled Active Scan (Safe Payloads)</span>
                      <span className="text-slate-400 text-[11px]">Probes for XSS, SQLi, and configuration flaws. Requires human sign-off.</span>
                    </div>
                  </label>
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-3">
                <button 
                  type="button"
                  onClick={() => setShowLaunchModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-xs font-medium"
                >
                  Cancel
                </button>
                {(() => {
                  const currentAsset = assets.find((a) => a.id === selectedAssetId);
                  const isCurrentAuthorized = currentAsset?.is_authorized || currentAsset?.verification_status === "verified";
                  return (
                    <button 
                      type="submit"
                      disabled={launching || assets.length === 0 || !isCurrentAuthorized}
                      className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-xs font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {launching ? "Dispatching..." : "Start Assessment"}
                    </button>
                  );
                })()}
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
