import React, { useState, useEffect } from "react";
import { Users, UserPlus, Shield, CheckCircle2, Mail, Crown, ShieldAlert, RefreshCw } from "lucide-react";
import { api } from "@/services/api";

export const TeamView: React.FC = () => {
  const [members, setMembers] = useState<any[]>([]);
  const [organizations, setOrganizations] = useState<any[]>([]);
  const [selectedOrgId, setSelectedOrgId] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState("developer");
  const [inviting, setInviting] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const orgsRes = await api.organizations.list();
      const orgList = orgsRes.data.results || orgsRes.data || [];
      setOrganizations(orgList);
      if (orgList.length > 0) {
        const orgId = orgList[0].id;
        setSelectedOrgId(orgId);
        const membersRes = await api.organizations.getMembers(orgId);
        setMembers(membersRes.data || []);
      }
    } catch (err: any) {
      console.warn("Could not fetch team from live API, loading preview state.");
      setMembers([
        {
          id: "mem-001",
          user: {
            id: "usr-01",
            email: "lead.analyst@cyberdefense.org",
            first_name: "Lead",
            last_name: "Analyst",
            role: "security_analyst"
          },
          role: "analyst",
          created_at: new Date().toISOString()
        },
        {
          id: "mem-002",
          user: {
            id: "usr-02",
            email: "dev.engineer@cyberdefense.org",
            first_name: "Dev",
            last_name: "Engineer",
            role: "developer"
          },
          role: "developer",
          created_at: new Date().toISOString()
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedOrgId || !inviteEmail) return;
    setInviting(true);
    setMessage(null);
    try {
      await api.organizations.inviteMember(selectedOrgId, {
        email: inviteEmail,
        role: inviteRole,
      });
      setShowInviteModal(false);
      setInviteEmail("");
      setMessage({ type: 'success', text: `Invitation sent to ${inviteEmail}.` });
      fetchData();
    } catch (err: any) {
      const errDetail = err.response?.data?.detail || err.message;
      setMessage({ type: 'error', text: `Failed to invite member: ${errDetail}` });
    } finally {
      setInviting(false);
    }
  };

  const roleBadge = (role: string) => {
    switch (role.toLowerCase()) {
      case "admin":
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-amber-950/80 text-amber-400 border border-amber-800/60">Admin</span>;
      case "analyst":
      case "security_analyst":
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-indigo-950/80 text-indigo-400 border border-indigo-800/60">Security Analyst</span>;
      case "developer":
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-emerald-950/80 text-emerald-400 border border-emerald-800/60">Developer</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-slate-800 text-slate-300">Viewer</span>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <Users className="w-5 h-5 text-indigo-400" />
            Team Members & Multi-Tenant RBAC
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Manage organization members, assign role permissions, and enforce cross-tenant data isolation.
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
            onClick={() => setShowInviteModal(true)}
            className="flex items-center gap-2 px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold shadow-lg shadow-indigo-600/20 transition"
          >
            <UserPlus className="w-4 h-4" />
            Invite Member
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

      {/* Members Table */}
      <div className="bg-slate-900/40 border border-slate-800 rounded-xl overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-xs text-slate-400">Loading organization team...</div>
        ) : members.length === 0 ? (
          <div className="p-12 text-center text-xs text-slate-400">No members listed.</div>
        ) : (
          <div className="divide-y divide-slate-800">
            {members.map((m) => {
              const u = m.user || {};
              const name = `${u.first_name || ""} ${u.last_name || ""}`.trim() || u.email || "Member";
              return (
                <div key={m.id} className="p-4 flex items-center justify-between hover:bg-slate-900/60 transition">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-full bg-indigo-900/60 border border-indigo-700/50 flex items-center justify-center text-white text-xs font-bold">
                      {name.substring(0, 2).toUpperCase()}
                    </div>
                    <div>
                      <span className="text-sm font-semibold text-white block">{name}</span>
                      <span className="text-xs text-slate-400 flex items-center gap-1">
                        <Mail className="w-3 h-3 text-slate-500" /> {u.email}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    {roleBadge(m.role || u.role || "viewer")}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Role Descriptions */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs text-slate-400 pt-2">
        <div className="p-3 bg-slate-900/30 border border-slate-800 rounded-lg space-y-1">
          <strong className="text-white block font-semibold">Org Admin</strong>
          <p className="text-[11px]">Full control over organization assets, scans, members, and configurations.</p>
        </div>
        <div className="p-3 bg-slate-900/30 border border-slate-800 rounded-lg space-y-1">
          <strong className="text-white block font-semibold">Security Analyst</strong>
          <p className="text-[11px]">Can approve intrusive active scans, verify vulnerabilities, and compile audit reports.</p>
        </div>
        <div className="p-3 bg-slate-900/30 border border-slate-800 rounded-lg space-y-1">
          <strong className="text-white block font-semibold">Developer</strong>
          <p className="text-[11px]">Can view verified findings, review code diffs, update remediation statuses, and request re-scans.</p>
        </div>
        <div className="p-3 bg-slate-900/30 border border-slate-800 rounded-lg space-y-1">
          <strong className="text-white block font-semibold">Viewer</strong>
          <p className="text-[11px]">Read-only access to findings summaries and security posture metrics.</p>
        </div>
      </div>

      {/* Invite Modal */}
      {showInviteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 max-w-md w-full space-y-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <UserPlus className="w-5 h-5 text-indigo-400" />
              Invite Team Member
            </h3>
            <form onSubmit={handleInvite} className="space-y-4">
              <div>
                <label className="text-xs text-slate-400 font-medium block mb-1">Email Address</label>
                <input
                  type="email"
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  placeholder="analyst@company.com"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white"
                  required
                />
              </div>

              <div>
                <label className="text-xs text-slate-400 font-medium block mb-1">Organization Role</label>
                <select
                  value={inviteRole}
                  onChange={(e) => setInviteRole(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white"
                >
                  <option value="developer">Developer</option>
                  <option value="analyst">Security Analyst</option>
                  <option value="admin">Organization Administrator</option>
                  <option value="viewer">Viewer (Read-Only)</option>
                </select>
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowInviteModal(false)}
                  className="px-3 py-1.5 text-xs text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={inviting}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold transition"
                >
                  {inviting ? "Inviting..." : "Send Invitation"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
