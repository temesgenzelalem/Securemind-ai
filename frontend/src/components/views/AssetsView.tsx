import React, { useState } from "react";
import { Globe, Plus, CheckCircle, Clock, AlertTriangle, ShieldCheck, Copy, ExternalLink } from "lucide-react";

export const AssetsView: React.FC = () => {
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedChallenge, setSelectedChallenge] = useState<any>(null);

  const assets = [
    {
      id: "ast-1",
      name: "Production Portal",
      domain: "securemind.ai",
      base_url: "https://securemind.ai",
      status: "Verified",
      expires_in: "84 days",
      verified_at: "2026-11-18",
      token: "securemind-verify=a8f9c1e4d2b70498"
    },
    {
      id: "ast-2",
      name: "Customer API Gateway",
      domain: "api.securemind.ai",
      base_url: "https://api.securemind.ai",
      status: "Verified",
      expires_in: "72 days",
      verified_at: "2026-11-06",
      token: "securemind-verify=3e71d9bc4a5f8201"
    },
    {
      id: "ast-3",
      name: "Staging Application",
      domain: "staging.clientapp.org",
      base_url: "https://staging.clientapp.org",
      status: "Pending Verification",
      expires_in: "Unverified",
      verified_at: null,
      token: "securemind-verify=7d82f0ab1c49e211"
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Applications & Assets</h2>
          <p className="text-xs text-slate-400 mt-1">Manage web targets, configure scopes, and complete domain ownership challenges.</p>
        </div>
        <button 
          onClick={() => setShowAddModal(true)}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold flex items-center gap-2 transition shadow-md shadow-indigo-500/20"
        >
          <Plus className="w-4 h-4" />
          <span>Register New Asset</span>
        </button>
      </div>

      {/* Assets Table */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="border-b border-slate-800 bg-slate-900/80 text-slate-400 font-semibold">
              <th className="py-3 px-4">Application</th>
              <th className="py-3 px-4">Domain</th>
              <th className="py-3 px-4">Ownership Status</th>
              <th className="py-3 px-4">Authorization Window</th>
              <th className="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-300">
            {assets.map((asset) => (
              <tr key={asset.id} className="hover:bg-slate-800/30 transition">
                <td className="py-3 px-4 font-semibold text-white flex items-center gap-2">
                  <Globe className="w-4 h-4 text-indigo-400" />
                  <span>{asset.name}</span>
                </td>
                <td className="py-3 px-4 font-mono text-[11px] text-slate-400">{asset.domain}</td>
                <td className="py-3 px-4">
                  {asset.status === "Verified" ? (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      <CheckCircle className="w-3.5 h-3.5" />
                      Verified
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20">
                      <Clock className="w-3.5 h-3.5" />
                      Pending Challenge
                    </span>
                  )}
                </td>
                <td className="py-3 px-4 text-slate-400">{asset.expires_in}</td>
                <td className="py-3 px-4 text-right space-x-2">
                  <button 
                    onClick={() => setSelectedChallenge(asset)}
                    className="px-2.5 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-[11px] font-medium transition"
                  >
                    Challenge Details
                  </button>
                  {asset.status !== "Verified" && (
                    <button className="px-2.5 py-1.5 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-[11px] font-medium transition">
                      Verify Now
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Challenge Modal */}
      {selectedChallenge && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-lg w-full p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-indigo-400" />
                Domain Verification Challenge
              </h3>
              <button onClick={() => setSelectedChallenge(null)} className="text-slate-400 hover:text-white">✕</button>
            </div>

            <p className="text-xs text-slate-400 leading-relaxed">
              To prevent unauthorized scanning, prove ownership of <span className="font-semibold text-white">{selectedChallenge.domain}</span> by adding the following DNS TXT record:
            </p>

            <div className="space-y-3 bg-slate-950 p-4 rounded-lg border border-slate-800 text-xs font-mono">
              <div>
                <span className="text-slate-500">Record Type:</span>
                <span className="text-indigo-400 font-bold ml-2">TXT</span>
              </div>
              <div>
                <span className="text-slate-500">Host / Name:</span>
                <span className="text-slate-200 ml-2">_securemind-challenge.{selectedChallenge.domain}</span>
              </div>
              <div className="break-all">
                <span className="text-slate-500">Value / Token:</span>
                <div className="mt-1 p-2 bg-slate-900 rounded border border-slate-700 text-emerald-400 flex items-center justify-between">
                  <span>{selectedChallenge.token}</span>
                  <Copy className="w-3.5 h-3.5 cursor-pointer text-slate-400 hover:text-white" />
                </div>
              </div>
            </div>

            <div className="pt-2 flex justify-end gap-3">
              <button 
                onClick={() => setSelectedChallenge(null)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-xs font-medium"
              >
                Close
              </button>
              <button className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-xs font-medium">
                Validate DNS Record
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
