import React, { useState, useEffect } from "react";
import { FileText, Download, Plus, RefreshCw, CheckCircle2, Clock, AlertTriangle, ShieldCheck } from "lucide-react";
import { api } from "@/services/api";

export const ReportsView: React.FC = () => {
  const [reports, setReports] = useState<any[]>([]);
  const [scans, setScans] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [selectedScanId, setSelectedScanId] = useState("");
  const [selectedType, setSelectedType] = useState("technical_full");
  const [generating, setGenerating] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [reportsRes, scansRes] = await Promise.all([
        api.reports.list(),
        api.scans.list(),
      ]);
      setReports(reportsRes.data.results || reportsRes.data || []);
      const scanList = scansRes.data.results || scansRes.data || [];
      setScans(scanList);
      if (scanList.length > 0 && !selectedScanId) {
        setSelectedScanId(scanList[0].id);
      }
    } catch (err: any) {
      console.warn("Could not fetch reports from live API, loading preview state.");
      setReports([
        {
          id: "rep-001",
          report_type: "technical_full",
          status: "completed",
          created_at: new Date().toISOString(),
          scan: { id: "scn-901", asset: { domain: "securemind.ai" } },
          metrics_summary: {
            total_findings: 3,
            critical: 0,
            high: 1,
            medium: 2,
            low: 0,
            confirmed_count: 2,
            target_domain: "securemind.ai"
          }
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedScanId) return;
    setGenerating(true);
    setMessage(null);
    try {
      await api.reports.generate(selectedScanId, selectedType);
      setShowGenerateModal(false);
      setMessage({ type: 'success', text: 'PDF security report compiled successfully.' });
      fetchData();
    } catch (err: any) {
      const errDetail = err.response?.data?.detail || err.message;
      setMessage({ type: 'error', text: `Failed to compile report: ${errDetail}` });
    } finally {
      setGenerating(false);
    }
  };

  const downloadReport = (reportId: string) => {
    const url = api.reports.downloadUrl(reportId);
    window.open(url, "_blank");
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <FileText className="w-5 h-5 text-indigo-400" />
            Security Assessment Reports
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Audit-grade %PDF-1.4 security reports compiling executive metrics, raw evidence, and code remediation diffs.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchData}
            className="p-2 text-slate-400 hover:text-white bg-slate-900 border border-slate-800 rounded-lg transition"
            title="Refresh"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={() => setShowGenerateModal(true)}
            className="flex items-center gap-2 px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold shadow-lg shadow-indigo-600/20 transition"
          >
            <Plus className="w-4 h-4" />
            Compile PDF Report
          </button>
        </div>
      </div>

      {message && (
        <div className={`p-4 rounded-xl text-xs font-medium border ${
          message.type === 'success' 
            ? 'bg-emerald-950/40 border-emerald-800 text-emerald-200' 
            : 'bg-rose-950/40 border-rose-800 text-rose-200'
        }`}>
          {message.text}
        </div>
      )}

      {/* Reports List */}
      <div className="bg-slate-900/40 border border-slate-800 rounded-xl overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-xs text-slate-400">Loading reports repository...</div>
        ) : reports.length === 0 ? (
          <div className="p-12 text-center space-y-3">
            <FileText className="w-8 h-8 text-slate-600 mx-auto" />
            <p className="text-xs text-slate-400">No security reports compiled yet.</p>
          </div>
        ) : (
          <div className="divide-y divide-slate-800">
            {reports.map((report) => {
              const metrics = report.metrics_summary || {};
              const domain = metrics.target_domain || report.scan?.asset?.domain || "Target Web App";
              return (
                <div key={report.id} className="p-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 hover:bg-slate-900/60 transition">
                  <div className="space-y-1.5">
                    <div className="flex items-center gap-2.5">
                      <span className="text-sm font-bold text-white tracking-tight">{domain}</span>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-indigo-950/80 text-indigo-400 border border-indigo-800/60">
                        {report.report_type.replace("_", " ")}
                      </span>
                      {report.status === 'completed' ? (
                        <span className="flex items-center gap-1 text-[11px] text-emerald-400 font-medium">
                          <CheckCircle2 className="w-3.5 h-3.5" /> Ready
                        </span>
                      ) : (
                        <span className="flex items-center gap-1 text-[11px] text-amber-400 font-medium">
                          <Clock className="w-3.5 h-3.5" /> {report.status}
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-4 text-xs text-slate-400">
                      <span>Compiled: {new Date(report.created_at).toLocaleDateString()}</span>
                      <span>Total Findings: <strong className="text-slate-200">{metrics.total_findings || 0}</strong></span>
                      {metrics.high > 0 && <span className="text-rose-400 font-semibold">{metrics.high} High</span>}
                      {metrics.medium > 0 && <span className="text-amber-400 font-semibold">{metrics.medium} Medium</span>}
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <button
                      onClick={() => downloadReport(report.id)}
                      className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-indigo-600 text-white rounded-lg text-xs font-semibold transition"
                    >
                      <Download className="w-3.5 h-3.5" />
                      Download PDF
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Generate Report Modal */}
      {showGenerateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 max-w-md w-full space-y-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-indigo-400" />
              Compile Audit-Grade Security Report
            </h3>
            <form onSubmit={handleGenerate} className="space-y-4">
              <div>
                <label className="text-xs text-slate-400 font-medium block mb-1">Select Completed Assessment</label>
                <select
                  value={selectedScanId}
                  onChange={(e) => setSelectedScanId(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white"
                  required
                >
                  {scans.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.asset_domain || s.asset?.domain || s.id} — {s.scan_type} ({s.status})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-xs text-slate-400 font-medium block mb-1">Report Profile</label>
                <select
                  value={selectedType}
                  onChange={(e) => setSelectedType(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white"
                >
                  <option value="technical_full">Full Technical Assessment Report (With Evidence & Code)</option>
                  <option value="executive">Executive Metrics Summary</option>
                  <option value="developer_remediation">Developer Remediation Guide</option>
                </select>
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowGenerateModal(false)}
                  className="px-3 py-1.5 text-xs text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={generating}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold transition"
                >
                  {generating ? "Compiling %PDF-1.4..." : "Compile & Save"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
