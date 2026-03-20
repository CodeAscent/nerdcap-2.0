import { useQuery } from '@tanstack/react-query';
import { dashboardApi } from '../api/client';
import {
  FileText, CheckCircle, AlertTriangle,
  Zap, TrendingUp, Map, Activity
} from 'lucide-react';
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';

const STATUS_COLORS = {
  pending:      '#94a3b8',
  analyzing:    '#60a5fa',
  analyzed:     '#a78bfa',
  under_review: '#fb923c',
  approved:     '#4ade80',
  rejected:     '#f87171',
  escalated:    '#fbbf24',
};

export default function Dashboard() {
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

  const summary = summaryRes?.data;
  const alerts = alertsRes?.data || [];
  const districtData = (districtRes?.data || []).slice(0, 8);

  if (isLoading) return <DashboardSkeleton />;

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
      {/* Page header */}
      <div>
        <h1 className="page-title">RTGS Dashboard</h1>
        <p className="text-sm text-slate-500 mt-0.5">Real-time land allocation pipeline · Andhra Pradesh</p>
      </div>

      {/* KPI row */}
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
        {kpiCards.map(({ label, value, icon: Icon, color }) => (
          <div key={label} className={`kpi-card ${color}`}>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide">{label}</span>
              <Icon size={16} className="text-slate-600" />
            </div>
            <span className="text-2xl font-extrabold text-slate-50">{value}</span>
          </div>
        ))}
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Pipeline Pie */}
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
                <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', fontSize: 12 }} />
                <Legend iconType="circle" iconSize={8}
                  formatter={(value) => <span style={{ color: '#94a3b8', fontSize: 12 }}>{value}</span>} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <EmptyState label="No proposals yet. Submit a proposal to get started." />
          )}
        </div>

        {/* District bar */}
        <div className="card">
          <h3 className="section-title mb-4">
            <Map size={16} className="text-gov-400" />
            District Breakdown
          </h3>
          {districtData.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={districtData} margin={{ top: 0, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="district" tick={{ fill: '#64748b', fontSize: 10 }} />
                <YAxis tick={{ fill: '#64748b', fontSize: 10 }} />
                <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', fontSize: 12 }} />
                <Bar dataKey="total_proposals" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Proposals" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <EmptyState label="No district data yet." />
          )}
        </div>
      </div>

      {/* Conflict alerts */}
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
                {alerts.slice(0, 10).map((alert: {id: string; conflict_type: string; severity: string; source_department?: string; description?: string}) => (
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
