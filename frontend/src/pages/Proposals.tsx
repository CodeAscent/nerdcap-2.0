import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { proposalsApi } from '../api/client';
import { Plus, ChevronRight, Loader2 } from 'lucide-react';

const STATUS_BADGE: Record<string, string> = {
  pending:      'badge-slate',
  analyzing:    'badge-blue',
  analyzed:     'badge-blue',
  under_review: 'badge-amber',
  approved:     'badge-green',
  rejected:     'badge-red',
  escalated:    'badge-amber',
};

interface Proposal {
  id: string;
  project_type: string;
  capacity_mw: number;
  district: string;
  status: string;
  submitted_at: string;
}

export default function Proposals() {
  const { data, isLoading } = useQuery({
    queryKey: ['proposals'],
    queryFn: () => proposalsApi.list(),
    refetchInterval: 15000,
  });

  const proposals: Proposal[] = data?.data || [];

  return (
    <div className="space-y-5 animate-fade-up">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="page-title">Proposals</h1>
          <p className="text-sm text-slate-500 mt-0.5">{proposals.length} total submissions</p>
        </div>
        <Link to="/proposals/new" className="btn-primary">
          <Plus size={15} />
          New Proposal
        </Link>
      </div>

      <div className="card">
        {isLoading ? (
          <div className="flex items-center justify-center h-48">
            <Loader2 size={24} className="animate-spin text-slate-600" />
          </div>
        ) : proposals.length === 0 ? (
          <div className="text-center py-16">
            <div className="w-14 h-14 rounded-2xl bg-slate-800 flex items-center justify-center mx-auto mb-4">
              <Plus size={22} className="text-slate-600" />
            </div>
            <p className="text-slate-400 font-medium">No proposals yet</p>
            <p className="text-slate-600 text-sm mt-1">Submit your first renewable energy land proposal</p>
            <Link to="/proposals/new" className="btn-primary mt-5 inline-flex">
              Submit Proposal
            </Link>
          </div>
        ) : (
          <div className="table-wrapper">
            <table className="table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Type</th>
                  <th>Capacity</th>
                  <th>District</th>
                  <th>Status</th>
                  <th>Submitted</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {proposals.map(p => (
                  <tr key={p.id}>
                    <td className="text-slate-500 font-mono text-xs">{p.id.slice(0, 8)}…</td>
                    <td>
                      <span className={p.project_type === 'solar' ? 'badge-amber' : 'badge-blue'}>
                        {p.project_type.toUpperCase()}
                      </span>
                    </td>
                    <td>{p.capacity_mw} MW</td>
                    <td>{p.district}</td>
                    <td>
                      <span className={STATUS_BADGE[p.status] || 'badge-slate'}>
                        {p.status.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td className="text-slate-500">
                      {new Date(p.submitted_at).toLocaleDateString('en-IN')}
                    </td>
                    <td>
                      <Link to={`/proposals/${p.id}`} className="btn-ghost py-1.5 px-2.5">
                        <ChevronRight size={14} />
                      </Link>
                    </td>
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
