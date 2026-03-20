import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useParams, useNavigate } from 'react-router-dom';
import { proposalsApi } from '../api/client';
import { useAuthStore } from '../store/authStore';
import {
  Bot, CheckCircle2, XCircle, AlertTriangle, Download,
  Play, Loader2, Clock, ChevronRight, Shield, Hash, Trash2
} from 'lucide-react';
import {
  RadialBarChart, RadialBar, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid,
} from 'recharts';

const GRADE_CLASS: Record<string, string> = { A:'grade-a', B:'grade-b', C:'grade-c', D:'grade-d' };
const SEVERITY_CLASS: Record<string, string> = {
  low:'badge-slate', medium:'badge-amber', high:'badge-red', critical:'badge-red'
};

const AGENT_ICONS: Record<string, string> = {
  'Land Records Agent': '🏛️',
  'Eco-Compliance Agent': '🌿',
  'Environment Clearance Agent': '🔬',
  'Grid Infrastructure Agent': '⚡',
  'Cadastral Verification Agent': '🗺️',
  'FTM Council': '🧠',
  'Orchestrator': '🎯',
};

export default function ProposalDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const qc = useQueryClient();
  const [decisionNotes, setDecisionNotes] = useState('');
  const [decisionLoading, setDecisionLoading] = useState<string | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteLoading, setDeleteLoading] = useState(false);

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['proposal', id],
    queryFn: () => proposalsApi.get(id!),
    refetchInterval: (q: { state: { data?: { data?: { status?: string } } } }) => {
      const status = q.state.data?.data?.status;
      return status === 'analyzing' ? 3000 : false;
    },
  });

  const { data: auditData } = useQuery({
    queryKey: ['audit-log', id],
    queryFn: () => proposalsApi.auditLog(id!),
    enabled: !!id,
  });

  const analyzeMutation = useMutation({
    mutationFn: () => proposalsApi.analyze(id!),
    onSuccess: () => { refetch(); qc.invalidateQueries({ queryKey: ['proposals'] }); },
  });

  const makeDecision = async (action: string) => {
    setDecisionLoading(action);
    try {
      await proposalsApi.decision(id!, action, decisionNotes);
      refetch();
      qc.invalidateQueries({ queryKey: ['proposals'] });
    } finally {
      setDecisionLoading(null);
    }
  };

  const handleDelete = async () => {
    setDeleteLoading(true);
    try {
      await proposalsApi.delete(id!);
      qc.invalidateQueries({ queryKey: ['proposals'] });
      navigate('/proposals');
    } catch (error) {
      console.error('Failed to delete proposal:', error);
    } finally {
      setDeleteLoading(false);
      setShowDeleteConfirm(false);
    }
  };

  if (isLoading) return <div className="flex items-center justify-center h-64"><Loader2 size={24} className="animate-spin text-slate-600" /></div>;

  const p = data?.data;
  if (!p) return <div className="text-slate-500">Proposal not found</div>;

  const ts = p.trust_score;
  const council = p.council_decision_json;
  const agents: unknown[] = p.agent_results_json?.agents || [];
  const auditLogs: unknown[] = auditData?.data || [];

  const factorData = ts ? Object.entries(ts.factor_breakdown).map(([k, v]) => ({
    name: k.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase()),
    score: v,
    fill: '#22c55e',
  })) : [];

  const isAnalyzed = ['analyzed', 'under_review', 'approved', 'rejected', 'escalated'].includes(p.status);
  const canDecide = ['officer', 'admin'].includes(user?.role || '') && ['analyzed', 'under_review', 'escalated'].includes(p.status);
  const canDelete = user?.role === 'admin' && p.status === 'pending';

  return (
    <div className="space-y-6 animate-fade-up max-w-5xl">
      {/* Header */}
      <div className="flex items-start gap-4 justify-between">
        <div>
          <h1 className="page-title">Proposal Detail</h1>
          <p className="text-sm text-slate-500 font-mono mt-0.5">{p.id}</p>
        </div>
        <div className="flex items-center gap-2">
          {isAnalyzed && (
            <a href={proposalsApi.reportUrl(id!)} target="_blank" rel="noreferrer" className="btn-secondary">
              <Download size={14} />
              Download Report
            </a>
          )}
          {p.status === 'pending' && (
            <button
              onClick={() => analyzeMutation.mutate()}
              disabled={analyzeMutation.isPending}
              className="btn-primary"
            >
              {analyzeMutation.isPending ? <Loader2 size={14} className="animate-spin" /> : <Play size={14} />}
              Run AI Analysis
            </button>
          )}
          {canDelete && (
            <button
              onClick={() => setShowDeleteConfirm(true)}
              className="btn-danger"
            >
              <Trash2 size={14} />
              Delete Proposal
            </button>
          )}
        </div>
      </div>

      {/* Status bar */}
      <div className="card flex flex-wrap gap-6">
        {[
          { label: 'Type', value: p.project_type.toUpperCase() },
          { label: 'Capacity', value: `${p.capacity_mw} MW` },
          { label: 'District', value: p.district },
          { label: 'Status', value: <span className={getStageBadge(p.status)}>{p.status.replace(/_/g, ' ')}</span> },
          { label: 'Submitted', value: new Date(p.submitted_at).toLocaleDateString('en-IN') },
        ].map(({ label, value }) => (
          <div key={label}>
            <p className="text-xs text-slate-500 uppercase tracking-wide mb-0.5">{label}</p>
            <p className="text-sm font-semibold text-slate-200">{value as React.ReactNode}</p>
          </div>
        ))}
      </div>

      {/* Analyzing spinner */}
      {p.status === 'analyzing' && (
        <div className="card flex items-center gap-4 border-gov-800 bg-gov-950/30">
          <Loader2 size={20} className="animate-spin text-gov-400" />
          <div>
            <p className="font-semibold text-gov-300">AI Analysis In Progress</p>
            <p className="text-sm text-slate-500">5 agents running in parallel · FTM Council deliberating…</p>
          </div>
        </div>
      )}

      {/* Results grid */}
      {isAnalyzed && ts && (
        <div className="grid lg:grid-cols-2 gap-4">
          {/* Trust Score Gauge */}
          <div className="card text-center">
            <h3 className="section-title justify-center mb-6">
              <Shield size={16} className="text-nredcap-400" />
              Land Trust Score
            </h3>
            <div className="relative h-36 w-full max-w-[280px] mx-auto">
              <ResponsiveContainer width="100%" height="100%">
                <RadialBarChart cx="50%" cy="100%" innerRadius="75%" outerRadius="100%"
                  startAngle={180} endAngle={0} data={[{ score: ts.overall_score, fill: scoreColor(ts.overall_score) }]}>
                  <RadialBar dataKey="score" cornerRadius={6} />
                </RadialBarChart>
              </ResponsiveContainer>
              <div className="absolute left-0 right-0 bottom-2 flex items-baseline justify-center gap-1">
                <span className="text-4xl font-extrabold text-slate-50 tracking-tight">{ts.overall_score.toFixed(1)}</span>
                <span className="text-slate-500 font-medium">/100</span>
              </div>
            </div>
            <div className="mt-5">
              <span className={GRADE_CLASS[ts.grade] || 'badge-slate'}>Grade {ts.grade}</span>
            </div>
          </div>

          {/* Factor Breakdown */}
          <div className="card">
            <h3 className="section-title mb-4">Factor Breakdown</h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={factorData} layout="vertical" margin={{ left: 10, right: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                <XAxis type="number" domain={[0, 25]} tick={{ fill: '#64748b', fontSize: 10 }} />
                <YAxis dataKey="name" type="category" tick={{ fill: '#94a3b8', fontSize: 9 }} width={130} />
                <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', fontSize: 11 }} />
                <Bar dataKey="score" radius={[0, 4, 4, 0]} fill="#22c55e" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Agent Results */}
      {agents.length > 0 && (
        <div className="card">
          <h3 className="section-title mb-4">
            <Bot size={16} className="text-gov-400" />
            Agent Findings ({agents.length} agents)
          </h3>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {(agents as Array<{agent_name: string; confidence: number; flags: string[]; success: boolean}>).map((agent) => (
              <div key={agent.agent_name} className={`agent-card ${agent.success ? 'success' : 'error'}`}>
                <span className="text-lg">{AGENT_ICONS[agent.agent_name] || '🤖'}</span>
                <div className="min-w-0">
                  <p className="text-sm font-semibold text-slate-200 leading-tight">{agent.agent_name}</p>
                  <p className="text-xs text-slate-500 mt-0.5">Confidence: {agent.confidence}%</p>
                  {agent.flags?.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-1.5">
                      {agent.flags.slice(0, 2).map((flag: string) => (
                        <span key={flag} className="text-[9px] px-1.5 py-0.5 rounded-md bg-slate-800 text-slate-400 border border-slate-700">
                          {flag.replace(/_/g, ' ')}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Conflict Matrix */}
      {p.conflicts && p.conflicts.length > 0 && (
        <div className="card">
          <h3 className="section-title mb-4">
            <AlertTriangle size={16} className="text-amber-400" />
            Conflict Matrix ({p.conflicts.length} conflicts)
          </h3>
          <div className="table-wrapper">
            <table className="table">
              <thead><tr><th>Type</th><th>Severity</th><th>Department</th><th>Description</th></tr></thead>
              <tbody>
                {(p.conflicts as Array<{id: string; conflict_type: string; severity: string; source_department?: string; description?: string}>).map((c) => (
                  <tr key={c.id}>
                    <td>{c.conflict_type.replace(/_/g, ' ')}</td>
                    <td><span className={SEVERITY_CLASS[c.severity] || 'badge-slate'}>{c.severity}</span></td>
                    <td className="text-slate-500">{c.source_department || '—'}</td>
                    <td className="text-slate-500 max-w-xs">{c.description?.slice(0, 80) || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Council Summary */}
      {council?.council_summary && (
        <div className="card border-gov-800/60 bg-gov-950/20">
          <h3 className="section-title mb-3">
            <span>🧠</span>
            FTM Council Decision
          </h3>
          <p className="text-sm text-slate-300 leading-relaxed">{council.council_summary}</p>
          {council.recommended_actions?.length > 0 && (
            <div className="mt-4">
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Recommended Actions</p>
              <ul className="space-y-1.5">
                {(council.recommended_actions as string[]).map((action: string, i: number) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-slate-400">
                    <ChevronRight size={14} className="text-nredcap-500 shrink-0 mt-0.5" />
                    {action}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Officer Decision Panel */}
      {canDecide && (
        <div className="card border-amber-800/60 bg-amber-950/10">
          <h3 className="section-title mb-4">
            <Shield size={16} className="text-amber-400" />
            Officer Decision
          </h3>
          <div className="mb-4">
            <label className="label">Notes (optional)</label>
            <textarea
              className="input min-h-[80px] resize-none"
              placeholder="Add decision notes, conditions, or escalation reason…"
              value={decisionNotes}
              onChange={e => setDecisionNotes(e.target.value)}
            />
          </div>
          <div className="flex flex-wrap gap-3">
            <button onClick={() => makeDecision('approve')} disabled={!!decisionLoading} className="btn-primary">
              {decisionLoading === 'approve' ? <Loader2 size={14} className="animate-spin" /> : <CheckCircle2 size={14} />}
              Approve
            </button>
            <button onClick={() => makeDecision('reject')} disabled={!!decisionLoading} className="btn-danger">
              {decisionLoading === 'reject' ? <Loader2 size={14} className="animate-spin" /> : <XCircle size={14} />}
              Reject
            </button>
            <button onClick={() => makeDecision('escalate')} disabled={!!decisionLoading} className="btn-secondary">
              {decisionLoading === 'escalate' ? <Loader2 size={14} className="animate-spin" /> : <AlertTriangle size={14} />}
              Escalate
            </button>
            <button onClick={() => makeDecision('request_more_info')} disabled={!!decisionLoading} className="btn-ghost">
              {decisionLoading === 'request_more_info' ? <Loader2 size={14} className="animate-spin" /> : <Clock size={14} />}
              Request More Info
            </button>
          </div>
          {p.officer_notes && (
            <div className="mt-4 pt-4 border-t border-slate-800">
              <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">Previous Notes</p>
              <p className="text-sm text-slate-400">{p.officer_notes}</p>
            </div>
          )}
        </div>
      )}

      {/* Audit Trail */}
      {auditLogs.length > 0 && (
        <div className="card">
          <h3 className="section-title mb-4">
            <Hash size={16} className="text-slate-500" />
            Audit Trail ({auditLogs.length} entries)
          </h3>
          <div className="space-y-2">
            {(auditLogs as Array<{id: string; timestamp: string; agent_name: string; action: string; chain_hash: string}>).slice(-8).map((log) => (
              <div key={log.id} className="flex items-center gap-3 py-2 border-b border-slate-800 last:border-0 text-xs">
                <span className="text-slate-600 shrink-0 font-mono">
                  {new Date(log.timestamp).toLocaleTimeString('en-IN')}
                </span>
                <span className="font-medium text-slate-400">{log.agent_name}</span>
                <span className="text-slate-500">{log.action.replace(/_/g, ' ')}</span>
                <span className="ml-auto font-mono text-slate-700 text-[9px] bg-slate-800 px-2 py-0.5 rounded-md">
                  {log.chain_hash.slice(0, 12)}…
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="card max-w-md w-full mx-4 border-red-800/60 bg-slate-900">
            <h3 className="section-title text-red-400 mb-3">
              <AlertTriangle size={18} />
              Delete Proposal
            </h3>
            <p className="text-slate-300 mb-6">
              Are you sure you want to delete this pending proposal? This action cannot be undone.
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="btn-ghost"
                disabled={deleteLoading}
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                disabled={deleteLoading}
                className="btn-danger"
              >
                {deleteLoading ? <Loader2 size={14} className="animate-spin" /> : <Trash2 size={14} />}
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function scoreColor(score: number): string {
  if (score >= 85) return '#22c55e';
  if (score >= 70) return '#3b82f6';
  if (score >= 50) return '#f59e0b';
  return '#ef4444';
}

function getStageBadge(status: string): string {
  const map: Record<string, string> = {
    pending: 'badge-slate', analyzing: 'badge-blue', analyzed: 'badge-blue',
    under_review: 'badge-amber', approved: 'badge-green',
    rejected: 'badge-red', escalated: 'badge-amber',
  };
  return map[status] || 'badge-slate';
}
