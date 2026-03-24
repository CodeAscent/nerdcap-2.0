import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { dashboardApi, systemApi, proposalsApi } from '../api/client';
import {
  FileText, CheckCircle, AlertTriangle,
  Zap, TrendingUp, Map, Activity,
  Plus, Star, Users, Server, Clock, Building
} from 'lucide-react';
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';
import { useAuthStore } from '../store/authStore';
import DistrictMap from '../components/DistrictMap';

const STATUS_COLORS: Record<string, string> = {
  pending:      'rgb(var(--slate-400))',
  analyzing:    '#60a5fa',
  analyzed:     '#a78bfa',
  under_review: '#fb923c',
  approved:     '#4ade80',
  rejected:     '#f87171',
  escalated:    '#fbbf24',
};

interface OfficerScore {
  user_id: string;
  name: string;
  department: string;
  district: string;
  score: number;
  proposals_decided: number;
  avg_response_time_hours: number;
}

interface DeveloperTracking {
  developer_id: string;
  name: string;
  company: string;
  total_proposals: number;
  approved_mw: number;
  pending_proposals: number;
  rejected_proposals: number;
  avg_trust_score: number;
}

interface KpiCardProps {
  label: string;
  value: string | number;
  icon: React.ComponentType<{ size?: number; className?: string }>;
  color: string;
}

function KpiCard({ label, value, icon: Icon, color }: KpiCardProps) {
  return (
    <div className={`kpi-card ${color}`}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide">{label}</span>
        <Icon size={16} className="text-slate-600" />
      </div>
      <span className="text-2xl font-extrabold text-slate-50">{value}</span>
    </div>
  );
}

function DashboardSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="h-8 w-48 bg-slate-800 rounded-xl" />
      <div className="grid grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => <div key={i} className="h-24 bg-slate-800 rounded-2xl" />)}
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="h-64 bg-slate-800 rounded-2xl" />
        <div className="h-64 bg-slate-800 rounded-2xl" />
      </div>
    </div>
  );
}

function EmptyState({ label }: { label: string }) {
  return (
    <div className="flex items-center justify-center h-[180px] text-slate-600 text-sm text-center">
      {label}
    </div>
  );
}

interface DashboardSummary {
  total_proposals?: number;
  total_approved_mw?: number;
  avg_trust_score?: number;
  conflict_rate_pct?: number;
  approved?: number;
  pending?: number;
  analyzing?: number;
  rejected?: number;
  escalated?: number;
  user_summary?: { role: string; count: number; color: string }[];
}

interface ConflictAlert {
  id: string;
  conflict_type: string;
  severity: string;
  source_department?: string;
  description?: string;
}

interface DistrictData {
  district: string;
  total_proposals: number;
  total_mw?: number;
}

interface Proposal {
  id: string;
  project_name: string;
  status: string;
  capacity_mw: number;
  created_at: string;
}

function DeveloperDashboard({ myProposals }: { summary?: DashboardSummary; myProposals: Proposal[] }) {
  const pendingCount = myProposals.filter(p => p.status === 'pending' || p.status === 'analyzing').length;
  const approvedCount = myProposals.filter(p => p.status === 'approved').length;
  const rejectedCount = myProposals.filter(p => p.status === 'rejected').length;
  const approvedMw = myProposals
    .filter(p => p.status === 'approved')
    .reduce((sum, p) => sum + (p.capacity_mw || 0), 0);

  const recentProposals = myProposals.slice(0, 3);

  return (
    <div className="space-y-6 animate-fade-up">
      <div>
        <h1 className="page-title">Developer Dashboard</h1>
        <p className="text-sm text-slate-500 mt-0.5">Your proposal summary and quick actions</p>
      </div>

      <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
        <KpiCard
          label="My Proposals"
          value={myProposals.length}
          icon={FileText}
          color="blue"
        />
        <KpiCard
          label="Pending / Analyzing"
          value={pendingCount}
          icon={Clock}
          color="amber"
        />
        <KpiCard
          label="Approved MW"
          value={`${approvedMw} MW`}
          icon={Zap}
          color="green"
        />
        <KpiCard
          label="Approved / Rejected"
          value={`${approvedCount} / ${rejectedCount}`}
          icon={TrendingUp}
          color="purple"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="card">
          <h3 className="section-title mb-4">
            <Star size={16} className="text-nredcap-400" />
            Quick Actions
          </h3>
          <div className="space-y-3">
            <Link
              to="/proposals/new"
              className="flex items-center gap-3 p-3 rounded-xl bg-slate-800/50 hover:bg-slate-800 transition-colors"
            >
              <div className="w-10 h-10 rounded-lg bg-nredcap-500/20 flex items-center justify-center">
                <Plus size={18} className="text-nredcap-400" />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-200">Submit New Proposal</p>
                <p className="text-xs text-slate-500">Start a new renewable energy project</p>
              </div>
            </Link>
            <Link
              to="/recommendations"
              className="flex items-center gap-3 p-3 rounded-xl bg-slate-800/50 hover:bg-slate-800 transition-colors"
            >
              <div className="w-10 h-10 rounded-lg bg-gov-500/20 flex items-center justify-center">
                <Star size={18} className="text-gov-400" />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-200">View Recommendations</p>
                <p className="text-xs text-slate-500">Find optimal sites for your projects</p>
              </div>
            </Link>
          </div>
        </div>

        <div className="card">
          <h3 className="section-title mb-4">
            <Activity size={16} className="text-nredcap-400" />
            Recent Activity
          </h3>
          {recentProposals.length === 0 ? (
            <EmptyState label="No proposals yet. Submit your first proposal to get started." />
          ) : (
            <div className="space-y-3">
              {recentProposals.map((proposal) => (
                <Link
                  key={proposal.id}
                  to={`/proposals/${proposal.id}`}
                  className="flex items-center justify-between p-3 rounded-xl bg-slate-800/50 hover:bg-slate-800 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <FileText size={16} className="text-slate-500" />
                    <div>
                      <p className="text-sm font-medium text-slate-200 truncate max-w-[200px]">
                        {proposal.project_name}
                      </p>
                      <p className="text-xs text-slate-500">
                        {proposal.capacity_mw} MW · {new Date(proposal.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <span
                    className={`text-xs px-2 py-1 rounded-full ${
                      proposal.status === 'approved'
                        ? 'bg-green-500/20 text-green-400'
                        : proposal.status === 'rejected'
                        ? 'bg-red-500/20 text-red-400'
                        : 'bg-slate-500/20 text-slate-400'
                    }`}
                  >
                    {proposal.status}
                  </span>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function OfficerDashboard({
  summary,
  alerts,
  districtData,
  officerScores,
  developerTracking,
}: {
  summary?: DashboardSummary;
  alerts: ConflictAlert[];
  districtData: DistrictData[];
  officerScores: OfficerScore[];
  developerTracking: DeveloperTracking[];
}) {
  const kpiCards = [
    { label: 'Total Proposals', value: summary?.total_proposals ?? 0, icon: FileText, color: 'blue' },
    { label: 'Approved MW', value: `${summary?.total_approved_mw ?? 0} MW`, icon: Zap, color: 'green' },
    { label: 'Avg Trust Score', value: `${summary?.avg_trust_score ?? 0}/100`, icon: TrendingUp, color: 'purple' },
    { label: 'Conflict Rate', value: `${summary?.conflict_rate_pct ?? 0}%`, icon: AlertTriangle, color: 'amber' },
  ];

  const pieData = [
    { name: 'Approved', value: summary?.approved ?? 0, color: STATUS_COLORS.approved },
    { name: 'Pending', value: (summary?.pending ?? 0) + (summary?.analyzing ?? 0), color: STATUS_COLORS.pending },
    { name: 'Rejected', value: summary?.rejected ?? 0, color: STATUS_COLORS.rejected },
    { name: 'Escalated', value: summary?.escalated ?? 0, color: STATUS_COLORS.escalated },
  ].filter(d => d.value > 0);

  return (
    <div className="space-y-6 animate-fade-up">
      <div>
        <h1 className="page-title">RTGS Dashboard</h1>
        <p className="text-sm text-slate-500 mt-0.5">Real-time land allocation pipeline · Andhra Pradesh</p>
      </div>

      <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
        {kpiCards.map(({ label, value, icon, color }) => (
          <KpiCard key={label} label={label} value={value} icon={icon} color={color} />
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="card">
          <h3 className="section-title mb-4">
            <Activity size={16} className="text-nredcap-400" />
            Proposal Pipeline
          </h3>
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={55} outerRadius={85}
                  paddingAngle={3} dataKey="value" stroke="none">
                  {pieData.map((entry) => (
                    <Cell key={entry.name} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: 'rgb(var(--slate-800))', border: '1px solid rgb(var(--slate-700))', borderRadius: '12px', fontSize: 12 }} />
                <Legend iconType="circle" iconSize={8}
                  formatter={(value) => <span style={{ color: 'rgb(var(--slate-400))', fontSize: 12 }}>{value}</span>} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <EmptyState label="No proposals yet. Submit a proposal to get started." />
          )}
        </div>

        <div className="card">
          <h3 className="section-title mb-4">
            <Map size={16} className="text-gov-400" />
            District Breakdown
          </h3>
          {districtData.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={districtData} margin={{ top: 0, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgb(var(--slate-800))" />
                <XAxis dataKey="district" tick={{ fill: '#64748b', fontSize: 10 }} />
                <YAxis tick={{ fill: '#64748b', fontSize: 10 }} />
                <Tooltip contentStyle={{ background: 'rgb(var(--slate-800))', border: '1px solid rgb(var(--slate-700))', borderRadius: '12px', fontSize: 12 }} />
                <Bar dataKey="total_proposals" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Proposals" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <EmptyState label="No district data yet." />
          )}
        </div>
      </div>

      <div className="card">
        <h3 className="section-title mb-4">
          <Map size={16} className="text-nredcap-400" />
          District Map
        </h3>
        <div className="h-[350px] rounded-xl overflow-hidden">
          <DistrictMap districtData={districtData} metric="proposals" />
        </div>
      </div>

      <div className="card">
        <h3 className="section-title mb-4">
          <AlertTriangle size={16} className="text-amber-400" />
          Active Conflict Alerts
          {alerts.length > 0 && (
            <span className="badge-amber ml-2">{alerts.length}</span>
          )}
        </h3>
        {alerts.length === 0 ? (
          <div className="flex items-center gap-2 text-nredcap-400 text-sm">
            <CheckCircle size={15} />
            No active high-severity conflicts
          </div>
        ) : (
          <div className="table-wrapper">
            <table className="table">
              <thead>
                <tr>
                  <th>Conflict Type</th>
                  <th>Severity</th>
                  <th>Department</th>
                  <th>Description</th>
                </tr>
              </thead>
              <tbody>
                {alerts.slice(0, 10).map((alert) => (
                  <tr key={alert.id}>
                    <td>{alert.conflict_type?.replace(/_/g, ' ')}</td>
                    <td>
                      <span className={alert.severity === 'critical' ? 'badge-red' : 'badge-amber'}>
                        {alert.severity}
                      </span>
                    </td>
                    <td className="text-slate-500">{alert.source_department || '—'}</td>
                    <td className="text-slate-500 max-w-xs truncate">{alert.description || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="card">
          <h3 className="section-title mb-4">
            <Users size={16} className="text-purple-400" />
            Officer Leaderboard
          </h3>
          {officerScores.length === 0 ? (
            <EmptyState label="No officer scores yet. Scores will appear after officers make decisions." />
          ) : (
            <div className="space-y-2">
              {officerScores.slice(0, 5).map((officer, idx) => (
                <div key={officer.user_id} className="flex items-center justify-between p-3 rounded-lg bg-slate-800/50">
                  <div className="flex items-center gap-3">
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                      idx === 0 ? 'bg-yellow-500/20 text-yellow-400' :
                      idx === 1 ? 'bg-slate-400/20 text-slate-300' :
                      idx === 2 ? 'bg-amber-600/20 text-amber-400' :
                      'bg-slate-700 text-slate-400'
                    }`}>
                      {idx + 1}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-200">{officer.name}</p>
                      <p className="text-xs text-slate-500">{officer.district}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-bold text-purple-400">{officer.score.toFixed(1)}</p>
                    <p className="text-xs text-slate-500">{officer.proposals_decided} decisions</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="card">
          <h3 className="section-title mb-4">
            <Building size={16} className="text-blue-400" />
            Developer Tracking
          </h3>
          {developerTracking.length === 0 ? (
            <EmptyState label="No developer data yet. Track developers after proposals are submitted." />
          ) : (
            <div className="space-y-2">
              {developerTracking.slice(0, 5).map((dev) => (
                <div key={dev.developer_id} className="flex items-center justify-between p-3 rounded-lg bg-slate-800/50">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center">
                      <Building size={14} className="text-blue-400" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-200">{dev.name}</p>
                      <p className="text-xs text-slate-500">{dev.company || 'Independent'}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-bold text-green-400">{dev.approved_mw} MW</p>
                    <p className="text-xs text-slate-500">
                      {dev.total_proposals} proposals · Trust: {dev.avg_trust_score?.toFixed(0) || 'N/A'}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function AdminDashboard({
  summary,
  alerts,
  districtData,
  systemHealth,
  officerScores,
  developerTracking,
}: {
  summary?: DashboardSummary;
  alerts: ConflictAlert[];
  districtData: DistrictData[];
  systemHealth?: { status: string; services?: Record<string, string> };
  officerScores: OfficerScore[];
  developerTracking: DeveloperTracking[];
}) {
  const kpiCards = [
    { label: 'Total Proposals', value: summary?.total_proposals ?? 0, icon: FileText, color: 'blue' },
    { label: 'Approved MW', value: `${summary?.total_approved_mw ?? 0} MW`, icon: Zap, color: 'green' },
    { label: 'Avg Trust Score', value: `${summary?.avg_trust_score ?? 0}/100`, icon: TrendingUp, color: 'purple' },
    { label: 'Conflict Rate', value: `${summary?.conflict_rate_pct ?? 0}%`, icon: AlertTriangle, color: 'amber' },
  ];

  const pieData = [
    { name: 'Approved', value: summary?.approved ?? 0, color: STATUS_COLORS.approved },
    { name: 'Pending', value: (summary?.pending ?? 0) + (summary?.analyzing ?? 0), color: STATUS_COLORS.pending },
    { name: 'Rejected', value: summary?.rejected ?? 0, color: STATUS_COLORS.rejected },
    { name: 'Escalated', value: summary?.escalated ?? 0, color: STATUS_COLORS.escalated },
  ].filter(d => d.value > 0);

  const userSummary = summary?.user_summary || [];

  const services = systemHealth?.services || {};

  return (
    <div className="space-y-6 animate-fade-up">
      <div>
        <h1 className="page-title">Admin Dashboard</h1>
        <p className="text-sm text-slate-500 mt-0.5">System-wide metrics and administration</p>
      </div>

      <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
        {kpiCards.map(({ label, value, icon, color }) => (
          <KpiCard key={label} label={label} value={value} icon={icon} color={color} />
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="card">
          <h3 className="section-title mb-4">
            <Server size={16} className="text-nredcap-400" />
            System Health
          </h3>
          <div className="space-y-2">
            {Object.entries(services).map(([service, status]) => (
              <div key={service} className="flex items-center justify-between p-2 rounded-lg bg-slate-800/50">
                <span className="text-sm text-slate-400 capitalize">{service.replace(/_/g, ' ')}</span>
                <span
                  className={`text-xs px-2 py-1 rounded-full ${
                    status === 'healthy'
                      ? 'bg-green-500/20 text-green-400'
                      : 'bg-red-500/20 text-red-400'
                  }`}
                >
                  {status}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <h3 className="section-title mb-4">
            <Users size={16} className="text-gov-400" />
            User Summary
          </h3>
          <div className="space-y-2">
            {userSummary.map(({ role, count, color }) => (
              <div key={role} className="flex items-center justify-between p-2 rounded-lg bg-slate-800/50">
                <span className="text-sm text-slate-400">{role}</span>
                <span className={`text-sm font-semibold text-${color}-400`}>{count}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <h3 className="section-title mb-4">
            <Activity size={16} className="text-nredcap-400" />
            Proposal Pipeline
          </h3>
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={180}>
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={40} outerRadius={65}
                  paddingAngle={3} dataKey="value" stroke="none">
                  {pieData.map((entry) => (
                    <Cell key={entry.name} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: 'rgb(var(--slate-800))', border: '1px solid rgb(var(--slate-700))', borderRadius: '12px', fontSize: 12 }} />
                <Legend iconType="circle" iconSize={8}
                  formatter={(value) => <span style={{ color: 'rgb(var(--slate-400))', fontSize: 11 }}>{value}</span>} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <EmptyState label="No proposals yet." />
          )}
        </div>
      </div>

      <div className="card">
        <h3 className="section-title mb-4">
          <Map size={16} className="text-gov-400" />
          District Breakdown
        </h3>
        {districtData.length > 0 ? (
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={districtData} margin={{ top: 0, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgb(var(--slate-800))" />
              <XAxis dataKey="district" tick={{ fill: '#64748b', fontSize: 10 }} />
              <YAxis tick={{ fill: '#64748b', fontSize: 10 }} />
              <Tooltip contentStyle={{ background: 'rgb(var(--slate-800))', border: '1px solid rgb(var(--slate-700))', borderRadius: '12px', fontSize: 12 }} />
              <Bar dataKey="total_proposals" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Proposals" />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <EmptyState label="No district data yet." />
        )}
      </div>

      <div className="card">
        <h3 className="section-title mb-4">
          <Map size={16} className="text-nredcap-400" />
          District Map
        </h3>
        <div className="h-[350px] rounded-xl overflow-hidden">
          <DistrictMap districtData={districtData} metric="mw" />
        </div>
      </div>

      <div className="card">
        <h3 className="section-title mb-4">
          <AlertTriangle size={16} className="text-amber-400" />
          Active Conflict Alerts
          {alerts.length > 0 && (
            <span className="badge-amber ml-2">{alerts.length}</span>
          )}
        </h3>
        {alerts.length === 0 ? (
          <div className="flex items-center gap-2 text-nredcap-400 text-sm">
            <CheckCircle size={15} />
            No active high-severity conflicts
          </div>
        ) : (
          <div className="table-wrapper">
            <table className="table">
              <thead>
                <tr>
                  <th>Conflict Type</th>
                  <th>Severity</th>
                  <th>Department</th>
                  <th>Description</th>
                </tr>
              </thead>
              <tbody>
                {alerts.slice(0, 10).map((alert) => (
                  <tr key={alert.id}>
                    <td>{alert.conflict_type?.replace(/_/g, ' ')}</td>
                    <td>
                      <span className={alert.severity === 'critical' ? 'badge-red' : 'badge-amber'}>
                        {alert.severity}
                      </span>
                    </td>
                    <td className="text-slate-500">{alert.source_department || '—'}</td>
                    <td className="text-slate-500 max-w-xs truncate">{alert.description || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="card">
          <h3 className="section-title mb-4">
            <Users size={16} className="text-purple-400" />
            Officer Leaderboard
          </h3>
          {officerScores.length === 0 ? (
            <EmptyState label="No officer scores yet." />
          ) : (
            <div className="space-y-2">
              {officerScores.slice(0, 5).map((officer, idx) => (
                <div key={officer.user_id} className="flex items-center justify-between p-3 rounded-lg bg-slate-800/50">
                  <div className="flex items-center gap-3">
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                      idx === 0 ? 'bg-yellow-500/20 text-yellow-400' :
                      idx === 1 ? 'bg-slate-400/20 text-slate-300' :
                      idx === 2 ? 'bg-amber-600/20 text-amber-400' :
                      'bg-slate-700 text-slate-400'
                    }`}>
                      {idx + 1}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-200">{officer.name}</p>
                      <p className="text-xs text-slate-500">{officer.district}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-bold text-purple-400">{officer.score.toFixed(1)}</p>
                    <p className="text-xs text-slate-500">{officer.proposals_decided} decisions</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="card">
          <h3 className="section-title mb-4">
            <Building size={16} className="text-blue-400" />
            Developer Tracking
          </h3>
          {developerTracking.length === 0 ? (
            <EmptyState label="No developer data yet." />
          ) : (
            <div className="space-y-2">
              {developerTracking.slice(0, 5).map((dev) => (
                <div key={dev.developer_id} className="flex items-center justify-between p-3 rounded-lg bg-slate-800/50">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center">
                      <Building size={14} className="text-blue-400" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-200">{dev.name}</p>
                      <p className="text-xs text-slate-500">{dev.company || 'Independent'}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-bold text-green-400">{dev.approved_mw} MW</p>
                    <p className="text-xs text-slate-500">
                      {dev.total_proposals} proposals · Trust: {dev.avg_trust_score?.toFixed(0) || 'N/A'}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const { user } = useAuthStore();
  const userRole = user?.role || 'developer';

  const { data: summaryRes, isLoading } = useQuery({
    queryKey: ['dashboard-summary'],
    queryFn: () => dashboardApi.summary(),
    refetchInterval: 30000,
  });

  const { data: alertsRes } = useQuery({
    queryKey: ['conflict-alerts'],
    queryFn: () => dashboardApi.conflictAlerts(),
  });

  const { data: districtRes } = useQuery({
    queryKey: ['district-map'],
    queryFn: () => dashboardApi.districtMap(),
  });

  const { data: systemHealthRes } = useQuery({
    queryKey: ['system-health'],
    queryFn: () => systemApi.health(),
    enabled: userRole === 'admin',
  });

  const { data: myProposalsRes } = useQuery({
    queryKey: ['my-proposals'],
    queryFn: () => proposalsApi.list(),
    enabled: userRole === 'developer',
  });

  const { data: officerScoresRes } = useQuery({
    queryKey: ['officer-scores'],
    queryFn: () => dashboardApi.officerScores(),
    enabled: userRole === 'officer' || userRole === 'admin',
  });

  const { data: developerTrackingRes } = useQuery({
    queryKey: ['developer-tracking'],
    queryFn: () => dashboardApi.developerTracking(),
    enabled: userRole === 'officer' || userRole === 'admin',
  });

  const summary = summaryRes?.data;
  const alerts = alertsRes?.data || [];
  const districtData = (districtRes?.data || []).slice(0, 8);
  const systemHealth = systemHealthRes?.data;
  const myProposals = myProposalsRes?.data || [];
  const officerScores = officerScoresRes?.data || [];
  const developerTracking = developerTrackingRes?.data || [];

  if (isLoading) return <DashboardSkeleton />;

  switch (userRole) {
    case 'developer':
      return <DeveloperDashboard summary={summary} myProposals={myProposals} />;
    case 'officer':
      return (
        <OfficerDashboard
          summary={summary}
          alerts={alerts}
          districtData={districtData}
          officerScores={officerScores}
          developerTracking={developerTracking}
        />
      );
    case 'admin':
      return (
        <AdminDashboard
          summary={summary}
          alerts={alerts}
          districtData={districtData}
          systemHealth={systemHealth}
          officerScores={officerScores}
          developerTracking={developerTracking}
        />
      );
    default:
      return <DeveloperDashboard summary={summary} myProposals={myProposals} />;
  }
}
